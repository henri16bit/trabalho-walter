#!/usr/bin/env bash
# Executar em GNU/Linux: bash laboratorio_linux.sh
set -u
set -o pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
    printf 'Este laboratório deve ser executado exclusivamente em GNU/Linux.\n' >&2
    exit 1
fi

base="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
destino="$base/evidencias/linux_$(date -u +%Y%m%dT%H%M%SZ)_$$"
mkdir -p -- "$destino" || exit 1
exec > >(tee "$destino/execucao.txt") 2>&1
pid_processo=""
pid_carga=""

encerrar_filhos() {
    for filho in "$pid_processo" "$pid_carga"; do
        if [[ -n "$filho" ]]; then
            kill "$filho" 2>/dev/null || true
            wait "$filho" 2>/dev/null || true
        fi
    done
}
trap encerrar_filhos EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

registrar() {
    local arquivo="$1"
    shift
    printf '\nComando: '
    printf '%q ' "$@"
    printf '\n'
    if ! command -v "$1" >/dev/null 2>&1; then
        printf 'NÃO EXECUTADO: comando %s não instalado. Consulte as dependências no README.\n' "$1" > "$destino/$arquivo"
    else
        "$@" > "$destino/$arquivo" 2>&1
        local codigo=$?
        printf 'Código de saída: %s\n' "$codigo"
        if (( codigo != 0 )); then
            printf 'LIMITAÇÃO: o comando falhou. A mensagem real foi preservada.\n'
        fi
    fi
    cat -- "$destino/$arquivo"
}

printf 'Coleta real do laboratório GNU/Linux\nPasta: %s\n' "$destino"
registrar data.txt date -Is
registrar sistema.txt uname -a
registrar distribuicao.txt cat /etc/os-release
printf '\nDependências Ubuntu/Debian: python3, procps (pmap, ps, top, free), strace, memstat.\n'
printf 'O script não instala pacotes nem configura swap.\n'

if command -v python3 >/dev/null 2>&1; then
    printf '\nATIVIDADE 1 — Mapa de memória\n'
    python3 -u -c 'import os, time; dados = bytearray(1024 * 1024); print("PID observado:", os.getpid(), flush=True); time.sleep(120)' > "$destino/processo.txt" 2>&1 &
    pid_processo=$!
    sleep 1
    cat -- "$destino/processo.txt"
    if kill -0 "$pid_processo" 2>/dev/null; then
        registrar pmap.txt pmap -x "$pid_processo"
        registrar maps.txt cat "/proc/$pid_processo/maps"

        printf '\nATIVIDADE 2 — Processos e chamadas de sistema\n'
        registrar ps_aux.txt ps aux
        registrar ps_processo.txt ps -p "$pid_processo" -o pid,ppid,stat,pcpu,pmem,rss,vsz,comm
        registrar top.txt top -b -n 2 -d 1 -p "$pid_processo"
        kill "$pid_processo" 2>/dev/null || true
        wait "$pid_processo" 2>/dev/null || true
        pid_processo=""
    else
        printf 'LIMITAÇÃO: o processo de demonstração não iniciou; veja processo.txt.\n'
    fi
    registrar strace.txt strace -c python3 -c 'from pathlib import Path; print("Bytes lidos:", len(Path("/proc/meminfo").read_bytes()))'
else
    printf 'NÃO EXECUTADO: demonstração com PID e strace dependem de python3.\n'
    registrar ps_aux.txt ps aux
    registrar top.txt top -b -n 2 -d 1
fi

printf '\nATIVIDADE 3 — RAM e swap\n'
registrar free_antes.txt free -h
registrar memstat.txt memstat
registrar swaps_antes.txt cat /proc/swaps
registrar contadores_swap_antes.txt awk '/^(pswpin|pswpout) /' /proc/vmstat
if [[ -r /proc/swaps ]] && [[ "$(wc -l < /proc/swaps)" -le 1 ]]; then
    printf 'LIMITAÇÃO: /proc/swaps não lista áreas de swap; não é possível observar seu uso neste ambiente.\n'
fi

if command -v python3 >/dev/null 2>&1; then
    # Carga curta; recusa ambientes cujo limite de memória não possa ser conferido.
    python3 -u - <<'PY_CARGA' > "$destino/carga.txt" 2>&1 &
import os
from pathlib import Path
import resource
import time

MIB = 1024 * 1024


def executar_carga():
    informacoes = {}
    for linha in Path("/proc/meminfo").read_text().splitlines():
        chave, valor = linha.split(":", 1)
        informacoes[chave] = int(valor.split()[0]) * 1024
    disponivel = informacoes["MemAvailable"]

    raiz = Path("/sys/fs/cgroup")
    if not (raiz / "cgroup.controllers").is_file():
        print("NÃO EXECUTADO: carga automática requer cgroup v2 acessível; limite do ambiente não confirmado.")
        return
    caminhos = [raiz]
    for linha in Path("/proc/self/cgroup").read_text().splitlines():
        if linha.startswith("0::"):
            relativo = linha.split(":", 2)[2].lstrip("/")
            atual = (raiz / relativo).resolve()
            if atual.is_relative_to(raiz) and atual.is_dir():
                while atual != raiz:
                    caminhos.append(atual)
                    atual = atual.parent

    limites_lidos = 0
    for caminho in caminhos:
        limite = caminho / "memory.max"
        if limite.is_file():
            valor = limite.read_text().strip()
            usado = int((caminho / "memory.current").read_text())
            limites_lidos += 1
            if valor != "max":
                disponivel = min(disponivel, int(valor) - usado)
            limite_alto = caminho / "memory.high"
            if limite_alto.is_file():
                alto = limite_alto.read_text().strip()
                if alto != "max":
                    disponivel = min(disponivel, int(alto) - usado)

    if limites_lidos == 0:
        print("NÃO EXECUTADO: não foi possível verificar limites de memória do cgroup.")
        return
    print("Margem disponível considerada (MiB):", disponivel // MIB)
    if disponivel < 256 * MIB:
        print("NÃO EXECUTADO: margem inferior a 256 MiB; carga dispensada.")
        return

    quantidade = min(32, disponivel // (10 * MIB))
    limite_atual, limite_maximo = resource.getrlimit(resource.RLIMIT_AS)
    teto = 256 * MIB
    for limite in (limite_atual, limite_maximo):
        if limite != resource.RLIM_INFINITY:
            teto = min(teto, limite)
    resource.setrlimit(resource.RLIMIT_AS, (teto, limite_maximo))
    dados = bytearray(quantidade * MIB)
    for indice in range(0, len(dados), os.sysconf("SC_PAGE_SIZE")):
        dados[indice] = 1
    print(f"Carga ativa: PID={os.getpid()}, {quantidade} MiB, duração=20 segundos.", flush=True)
    time.sleep(20)
    del dados
    print("Carga liberada; processo encerrando.")


try:
    executar_carga()
except (OSError, ValueError, KeyError, MemoryError) as erro:
    print(f"CARGA INTERROMPIDA: {type(erro).__name__}: {erro}")
    raise SystemExit(1)
PY_CARGA
    pid_carga=$!
    sleep 2
    cat -- "$destino/carga.txt"
    if kill -0 "$pid_carga" 2>/dev/null; then
        registrar free_durante.txt free -h
        registrar pmap_carga.txt pmap -x "$pid_carga"
        registrar swaps_durante.txt cat /proc/swaps
        registrar contadores_swap_durante.txt awk '/^(pswpin|pswpout) /' /proc/vmstat
    fi
    wait "$pid_carga"
    printf 'Código de saída do processo de carga: %s\n' "$?"
    pid_carga=""
    cat -- "$destino/carga.txt"
else
    printf 'NÃO EXECUTADO: teste de carga depende de python3.\n'
fi

registrar free_depois.txt free -h
registrar swaps_depois.txt cat /proc/swaps
registrar contadores_swap_depois.txt awk '/^(pswpin|pswpout) /' /proc/vmstat
printf '\nColeta encerrada. Revise os códigos de saída e as limitações em execucao.txt.\n'
printf 'Capture as telas reais e preencha evidencias/observacoes.md e a seção 5 do relatório.\n'
printf 'Swap inalterado é um resultado possível; não aumente a carga para forçar swap.\n'
