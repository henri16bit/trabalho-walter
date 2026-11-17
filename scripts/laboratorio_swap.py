"""Experimento limitado de swap, somente em um runner GNU/Linux remoto.

Usa dois serviços transitórios sequenciais: a mesma carga de 128 MiB,
com memory.max de 256 MiB (controle) e 64 MiB (pressão). Cada serviço
tem no máximo 256 MiB de swap e 60 segundos de vida. Não cria swap,
não muda sysctl e não provoca esgotamento global da RAM.
"""

import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shlex
import signal
import subprocess
import sys
import time

MIB = 1024 * 1024
CARGA = 128 * MIB
LIMITES = {"controle": 256 * MIB, "pressao": 64 * MIB}
RAIZ = Path(__file__).resolve().parent.parent
CGROUP = Path("/sys/fs/cgroup")


def agora():
    return datetime.now(timezone.utc).isoformat()


def ler(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as erro:
        return f"INDISPONIVEL: {type(erro).__name__}: {erro}\n"


def pares(texto):
    dados = {}
    for linha in texto.splitlines():
        campos = linha.replace(":", "").split()
        if len(campos) >= 2 and campos[1].isdigit():
            dados[campos[0]] = int(campos[1])
    return dados


def salvar_json(path, dados):
    Path(path).write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def carga(fase, pasta):
    import mmap
    import resource

    resource.setrlimit(resource.RLIMIT_AS, (512 * MIB, 512 * MIB))
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    relativo = next(l[3:] for l in ler("/proc/self/cgroup").splitlines() if l.startswith("0::"))
    cg = (CGROUP / relativo.lstrip("/")).resolve()
    if not cg.is_relative_to(CGROUP) or not cg.name.startswith("unirp-swap-"):
        raise RuntimeError("Carga recusada: fora do cgroup exclusivo do experimento")
    if int(ler(cg / "memory.max")) != LIMITES[fase] or int(ler(cg / "memory.swap.max")) != 256 * MIB:
        raise RuntimeError("Carga recusada: limites do cgroup divergentes")
    if (cg / "memory.zswap.max").exists() and int(ler(cg / "memory.zswap.max")) != 0:
        raise RuntimeError("Carga recusada: limite de zswap do teste nao confirmado")
    pagina = os.sysconf("SC_PAGE_SIZE")
    campos = ["memory.current", "memory.max", "memory.peak", "memory.swap.current",
              "memory.swap.max", "memory.swap.peak", "memory.zswap.max",
              "memory.stat", "memory.events", "memory.swap.events",
              "memory.pressure", "io.stat", "io.pressure", "cpu.stat"]

    def amostra(etapa, **extras):
        r = resource.getrusage(resource.RUSAGE_SELF)
        dados = {"data_utc": agora(), "fase": fase, "etapa": etapa, "pid": os.getpid(),
                 "cgroup": str(cg), "pagina_bytes": pagina, "carga_bytes": CARGA,
                 "status": ler("/proc/self/status"), "io_processo": ler("/proc/self/io"),
                 "vmstat": ler("/proc/vmstat"), "meminfo": ler("/proc/meminfo"),
                 "swaps": ler("/proc/swaps"), "minflt": r.ru_minflt, "majflt": r.ru_majflt,
                 "cgroup_arquivos": {nome: ler(cg / nome) for nome in campos}, **extras}
        with (pasta / f"{fase}_amostras.jsonl").open("a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(dados, ensure_ascii=False) + "\n")
        (pasta / f"{fase}_etapa.txt").write_text(etapa, encoding="utf-8")
        print(f"{agora()} fase={fase} etapa={etapa} PID={os.getpid()} "
              f"RSS_kB={pares(dados['status']).get('VmRSS')} "
              f"VmSwap_kB={pares(dados['status']).get('VmSwap')} "
              f"swap_cgroup_bytes={dados['cgroup_arquivos']['memory.swap.current'].strip()}", flush=True)

    amostra("antes")
    memoria = mmap.mmap(-1, CARGA, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS,
                        prot=mmap.PROT_READ | mmap.PROT_WRITE)
    memoria.madvise(mmap.MADV_NOHUGEPAGE)
    inicio = time.perf_counter()
    for pos in range(0, CARGA, pagina):
        memoria[pos] = (pos // pagina) % 251 + 1
    amostra("alocada", alocacao_segundos=time.perf_counter() - inicio)
    time.sleep(4)
    passagens = []
    esperado = sum(i % 251 + 1 for i in range(0, CARGA // pagina))
    for numero in range(1, 4):
        r0 = resource.getrusage(resource.RUSAGE_SELF)
        inicio = time.perf_counter()
        cpu = time.process_time()
        soma = 0
        for pos in range(0, CARGA, pagina):
            valor = memoria[pos]
            soma += valor
            memoria[pos] = valor
        dados = {"passagem": numero, "segundos": time.perf_counter() - inicio,
                 "cpu_segundos": time.process_time() - cpu,
                 "major_faults": resource.getrusage(resource.RUSAGE_SELF).ru_majflt - r0.ru_majflt,
                 "checksum": soma}
        if soma != esperado:
            raise RuntimeError("Conteudo das paginas divergiu apos releitura")
        passagens.append(dados)
        print(json.dumps(dados), flush=True)
        amostra(f"passagem_{numero}", **dados)
        time.sleep(0.3)
    amostra("apos_releituras", passagens=passagens)
    time.sleep(4)
    memoria.close()
    amostra("liberada")
    print("Carga liberada; encerramento normal.", flush=True)


class Coleta:
    def __init__(self):
        nome = datetime.now(timezone.utc).strftime("swap_linux_%Y%m%dT%H%M%SZ_") + str(os.getpid())
        self.pasta = RAIZ / "evidencias" / nome
        self.pasta.mkdir(parents=True)
        (RAIZ / ".coleta_swap").write_text(str(self.pasta), encoding="utf-8")
        self.unidades = []
        self.comandos = (self.pasta / "comandos.tsv").open("w", encoding="utf-8", newline="")
        self.tabela = csv.writer(self.comandos, delimiter="\t")
        self.tabela.writerow(["arquivo", "codigo_saida", "inicio_utc", "comando"])

    def comando(self, nome, args, exigir=True):
        inicio = agora()
        try:
            r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=15, check=False)
            texto = r.stdout.decode("utf-8", errors="replace")
            codigo = r.returncode
        except (OSError, subprocess.TimeoutExpired) as erro:
            texto, codigo = f"{type(erro).__name__}: {erro}\n", 124
        (self.pasta / nome).write_text(texto, encoding="utf-8")
        self.tabela.writerow([nome, codigo, inicio, shlex.join(args)])
        self.comandos.flush()
        if exigir and codigo:
            raise RuntimeError(f"Comando falhou ({codigo}): {shlex.join(args)}; veja {nome}")
        return texto

    def sistema(self, momento):
        self.comando(f"free_{momento}.txt", ["free", "-h"])
        self.comando(f"free_bytes_{momento}.txt", ["free", "-b"])
        self.comando(f"swaps_{momento}.txt", ["cat", "/proc/swaps"])
        self.comando(f"vmstat_{momento}.txt", ["cat", "/proc/vmstat"])
        self.comando(f"memstat_{momento}.txt", ["memstat"], exigir=False)

    def executar_fase(self, fase):
        unidade = f"unirp-swap-{fase}-{os.getpid()}.service"
        self.unidades.append(unidade)
        self.sistema(f"{fase}_antes")
        args = ["sudo", "-n", "systemd-run", "--unit=" + unidade,
                "--uid=" + str(os.getuid()), "--gid=" + str(os.getgid()),
                "--property=Type=exec", "--property=RemainAfterExit=yes",
                "--property=MemoryAccounting=yes", "--property=IOAccounting=yes",
                f"--property=MemoryMax={LIMITES[fase]}", "--property=MemorySwapMax=268435456",
                "--property=OOMPolicy=kill", "--property=TasksMax=8",
                "--property=RuntimeMaxSec=60", "--property=TimeoutStopSec=3",
                "--property=NoNewPrivileges=yes", "--property=PrivateTmp=yes",
                "--property=LimitAS=536870912", "--property=LimitCPU=20",
                "--property=StandardOutput=append:" + str(self.pasta / f"{fase}_carga.txt"),
                "--property=StandardError=append:" + str(self.pasta / f"{fase}_carga.txt")]
        if (CGROUP / "system.slice/memory.zswap.max").exists():
            args.append("--property=MemoryZSwapMax=0")
        args += ["/usr/bin/python3", "-u", str(Path(__file__).resolve()), "--carga", fase, str(self.pasta)]
        self.comando(f"{fase}_iniciar.txt", args)
        self.comando(f"{fase}_configuracao.txt", ["systemctl", "show", unidade])
        visto = set()
        inicio = time.monotonic()
        while time.monotonic() - inicio < 70:
            etapa = ler(self.pasta / f"{fase}_etapa.txt").strip()
            if etapa in ("alocada", "apos_releituras") and etapa not in visto:
                visto.add(etapa)
                self.sistema(f"{fase}_{etapa}")
                self.comando(f"{fase}_{etapa}_unidade.txt", ["systemctl", "show", unidade])
            status = subprocess.run(["systemctl", "show", unidade, "--property=SubState", "--value"],
                                    capture_output=True, text=True, timeout=5, check=True).stdout.strip()
            if status in ("exited", "failed", "dead"):
                break
            time.sleep(0.2)
        else:
            raise RuntimeError(f"Tempo maximo do monitor excedido: {unidade}")
        status = self.comando(f"{fase}_resultado_unidade.txt", ["systemctl", "show", unidade,
                    "--property=Result,ExecMainCode,ExecMainStatus,SubState,ControlGroup"])
        self.comando(f"{fase}_journal.txt", ["sudo", "-n", "journalctl", "-u", unidade, "--no-pager"], exigir=False)
        linhas = [json.loads(l) for l in (self.pasta / f"{fase}_amostras.jsonl").read_text(encoding="utf-8").splitlines()]
        if "ExecMainStatus=0" not in status or "Result=success" not in status or linhas[-1]["etapa"] != "liberada":
            raise RuntimeError(f"A fase {fase} nao terminou normalmente; veja logs e eventos")
        for linha in linhas:
            eventos = pares(linha["cgroup_arquivos"]["memory.events"])
            if eventos.get("oom", 0) or eventos.get("oom_kill", 0):
                raise RuntimeError(f"Evento OOM na fase {fase}; nao ampliar a carga")
        self.comando(f"{fase}_parar.txt", ["sudo", "-n", "systemctl", "stop", unidade])
        self.unidades.remove(unidade)
        self.sistema(f"{fase}_depois")
        return linhas

    def fechar(self):
        for unidade in self.unidades:
            self.comando(f"limpeza_{unidade}.txt", ["sudo", "-n", "systemctl", "stop", unidade], exigir=False)
        self.comandos.close()


def resumir(coleta, fases):
    resultados = []
    for fase, linhas in fases.items():
        antes = linhas[0]
        depois = next(l for l in linhas if l["etapa"] == "apos_releituras")
        passagens = depois["passagens"]
        v0, v1 = pares(antes["vmstat"]), pares(depois["vmstat"])
        def io_total(linha, chave):
            return sum(int(c.split("=", 1)[1]) for c in linha["cgroup_arquivos"]["io.stat"].split() if c.startswith(chave + "="))
        resultados.append({"fase": fase, "pid": antes["pid"], "carga_MiB": 128,
            "limite_RAM_MiB": LIMITES[fase] // MIB,
            "pico_swap_cgroup_bytes_amostrado": max(int(l["cgroup_arquivos"]["memory.swap.current"]) for l in linhas),
            "pico_VmSwap_KiB_amostrado": max(pares(l["status"]).get("VmSwap", 0) for l in linhas),
            "releituras_segundos": sum(p["segundos"] for p in passagens),
            "releituras_cpu_segundos": sum(p["cpu_segundos"] for p in passagens),
            "major_faults_releituras": sum(p["major_faults"] for p in passagens),
            "pswpin_global_delta": v1["pswpin"] - v0["pswpin"],
            "pswpout_global_delta": v1["pswpout"] - v0["pswpout"],
            "io_cgroup_rbytes_delta": io_total(depois, "rbytes") - io_total(antes, "rbytes"),
            "io_cgroup_wbytes_delta": io_total(depois, "wbytes") - io_total(antes, "wbytes"),
            "oom_kill": pares(depois["cgroup_arquivos"]["memory.events"]).get("oom_kill", 0)})
    salvar_json(coleta.pasta / "resumo.json", resultados)
    with (coleta.pasta / "comparacao.csv").open("w", newline="", encoding="utf-8") as arquivo:
        tabela = csv.DictWriter(arquivo, fieldnames=list(resultados[0]))
        tabela.writeheader()
        tabela.writerows(resultados)
    texto = ["EXPERIMENTO REAL DE SWAP - Ubuntu remoto / cgroup v2", agora(),
             "Mesma carga: 128 MiB anonimos; tres releituras com escrita, uma por pagina.",
             "Sem esgotar RAM global. Limites: controle=256 MiB; pressao=64 MiB.",
             "Cada unidade: swap<=256 MiB, tempo<=60 s, CPU<=20 s, AS<=512 MiB."]
    for item in resultados:
        texto += ["", f"FASE {item['fase'].upper()} - PID {item['pid']}"]
        texto += [f"{chave}: {valor}" for chave, valor in item.items() if chave not in ("fase", "pid")]
    controle, pressao = resultados
    demonstrado = pressao["pico_swap_cgroup_bytes_amostrado"] > 0 and pressao["pswpin_global_delta"] > 0 and pressao["pswpout_global_delta"] > 0
    texto += ["", "Swap e movimentacao observados: " + ("SIM" if demonstrado else "NAO; registrar limitacao"),
              f"Razao de tempo pressao/controle: {pressao['releituras_segundos']/controle['releituras_segundos']:.3f}",
              "Tempos de uma execucao; nao sao benchmark geral nem isolam toda causa de espera.",
              "pswpin/out sao globais. io.stat e major faults apoiam a interpretacao,",
              "mas io.stat tambem inclui logs/metadados. Veja amostras e arquivos brutos."]
    (coleta.pasta / "resumo.txt").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(texto), flush=True)


def main():
    if platform.system() != "Linux" or os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("Execute este experimento pelo workflow swap-linux.yml no Ubuntu remoto.")
    coleta = Coleta()
    try:
        origem = {"data_utc": agora(), "run_url": f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
                  "commit": os.environ["GITHUB_SHA"], "carga_bytes": CARGA, "limites_RAM": LIMITES,
                  "limite_swap_por_unidade": 256 * MIB, "timeout_por_unidade_s": 60}
        salvar_json(coleta.pasta / "origem.json", origem)
        coleta.comando("distribuicao.txt", ["cat", "/etc/os-release"])
        coleta.comando("sistema.txt", ["uname", "-a"])
        coleta.comando("systemd.txt", ["systemd-run", "--version"])
        coleta.comando("zswap.txt", ["cat", "/sys/module/zswap/parameters/enabled"], exigir=False)
        coleta.comando("swappiness.txt", ["cat", "/proc/sys/vm/swappiness"])
        coleta.comando("sudo.txt", ["sudo", "-n", "true"])
        memoria = pares(ler("/proc/meminfo"))
        if memoria.get("MemAvailable", 0) < 1024 * 1024 or memoria.get("SwapFree", 0) < 512 * 1024:
            raise RuntimeError("Carga dispensada: requer pelo menos 1 GiB RAM disponivel e 512 MiB swap livre")
        if "memory" not in ler(CGROUP / "cgroup.controllers").split():
            raise RuntimeError("Controlador memory do cgroup v2 indisponivel")
        for pai in (CGROUP / "system.slice", CGROUP):
            for limite, atual, margem in [("memory.max", "memory.current", 512 * MIB),
                                          ("memory.swap.max", "memory.swap.current", 256 * MIB)]:
                if (pai / limite).exists():
                    teto = ler(pai / limite).strip()
                    if teto != "max" and int(teto) - int(ler(pai / atual)) < margem:
                        raise RuntimeError(f"Margem insuficiente no ancestral {pai}/{limite}")
        fases = {fase: coleta.executar_fase(fase) for fase in LIMITES}
        resumir(coleta, fases)
        (coleta.pasta / "conclusao_execucao.txt").write_text("Duas fases encerradas normalmente, sem OOM. Veja resumo e limitacoes.\n", encoding="utf-8")
        return 0
    except Exception as erro:
        mensagem = f"LIMITACAO: {type(erro).__name__}: {erro}\n"
        (coleta.pasta / "limitacao.txt").write_text(mensagem, encoding="utf-8")
        print(mensagem, flush=True)
        return 1
    finally:
        coleta.fechar()


if __name__ == "__main__":
    if platform.system() != "Linux":
        raise SystemExit("Somente GNU/Linux remoto; nenhum recurso sera instalado no Windows.")
    if len(sys.argv) == 4 and sys.argv[1] == "--carga" and sys.argv[2] in LIMITES:
        carga(sys.argv[2], Path(sys.argv[3]))
    elif len(sys.argv) != 1:
        raise SystemExit("Argumentos invalidos")
    else:
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
        raise SystemExit(main())
