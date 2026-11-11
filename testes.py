"""Testes com resultados calculados à mão; executar com python testes.py."""

import ast
import argparse
from contextlib import contextmanager
import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

from algoritmos import ALGORITMOS, fifo, lru, nru, segunda_chance
from graficos import salvar_csv, salvar_graficos
from main import MOLDURAS_PADRAO, OPERACOES_PADRAO, PAGINAS_PADRAO, executar_simulacoes


def conferir(resultado, faltas, gravacoes):
    obtido = (resultado["page_faults"], resultado["swap_outs"])
    assert obtido == (faltas, gravacoes), f"{resultado}: esperado {(faltas, gravacoes)}"


def teste_conferencia_manual_por_acesso():
    # Contadores acumulados da tabela manual do relatório, com três molduras.
    esperados = {
        fifo: ([1, 2, 3, 4, 5, 6, 7, 7, 7, 8, 9, 9], [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 3, 3]),
        lru: ([1, 2, 3, 4, 5, 6, 7, 7, 7, 8, 9, 10], [0, 0, 0, 1, 1, 2, 2, 2, 2, 3, 3, 4]),
        segunda_chance: ([1, 2, 3, 4, 5, 6, 7, 7, 7, 8, 9, 9], [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 3, 3]),
        nru: ([1, 2, 3, 4, 4, 5, 6, 6, 6, 7, 8, 9], [0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 3, 3]),
    }
    for algoritmo, (faltas, gravacoes) in esperados.items():
        for tamanho in range(1, len(PAGINAS_PADRAO) + 1):
            resultado = algoritmo(3, PAGINAS_PADRAO[:tamanho], OPERACOES_PADRAO[:tamanho])
            conferir(resultado, faltas[tamanho - 1], gravacoes[tamanho - 1])


def teste_sequencia_conhecida_so_leituras():
    paginas = [1, 2, 1, 3, 1, 2]
    for algoritmo, faltas in ((fifo, 5), (lru, 4), (segunda_chance, 5), (nru, 4)):
        conferir(algoritmo(2, paginas, ["L"] * len(paginas)), faltas, 0)


def teste_fifo_nao_reordena_acerto():
    conferir(fifo(2, [1, 2, 1, 3, 1], ["L"] * 5), 4, 0)


def teste_lru_atualiza_ultimo_acesso():
    conferir(lru(2, [1, 2, 1, 3, 1], ["L"] * 5), 3, 0)


def teste_clock_renova_referencia_e_avanca_ponteiro():
    conferir(segunda_chance(3, [1, 2, 3, 4, 2, 5, 2], ["L"] * 7), 5, 0)


def teste_nru_classe_zero_e_desempate():
    conferir(nru(2, [1, 2, 1, 2, 3, 2], ["L"] * 6), 3, 0)


def teste_nru_classe_um_antes_da_dois():
    # A limpeza antes do quinto acesso ocorre mesmo quando há apenas acertos.
    conferir(nru(2, [1, 2, 2, 2, 2, 3, 1], ["E", "L", "L", "L", "L", "L", "L"]), 4, 1)


def teste_nru_classe_dois_antes_da_tres():
    conferir(nru(2, [1, 2, 3, 1], ["E", "L", "L", "L"]), 3, 0)


def teste_nru_classe_tres_e_desempate():
    conferir(nru(2, [1, 2, 3, 2], ["E"] * 4), 3, 1)


def teste_nru_preserva_indice_da_moldura():
    conferir(nru(2, [1, 2, 3, 4, 3], ["L"] * 5), 5, 0)


def teste_primeira_carga_nao_grava_em_disco():
    for algoritmo in ALGORITMOS:
        conferir(algoritmo(3, [1, 2, 3], ["E"] * 3), 3, 0)


def teste_leitura_preserva_dirty_e_escritas_nao_duplicam_swap():
    for algoritmo in ALGORITMOS:
        conferir(algoritmo(1, [1, 1, 1, 2], ["E", "E", "L", "L"]), 2, 1)


def teste_escrita_em_pagina_residente():
    for algoritmo in ALGORITMOS:
        conferir(algoritmo(1, [1, 1, 2], ["L", "E", "L"]), 2, 1)


def teste_pagina_limpa_nao_gera_swap_out():
    for algoritmo in ALGORITMOS:
        conferir(algoritmo(1, [1, 2, 3], ["L"] * 3), 3, 0)


def teste_pagina_recarregada_nao_herda_dirty_antigo():
    for algoritmo in ALGORITMOS:
        conferir(algoritmo(1, [1, 2, 1, 3], ["E", "L", "L", "L"]), 4, 1)


def teste_uma_moldura_e_escritas():
    for algoritmo in ALGORITMOS:
        conferir(algoritmo(1, [0, 1, 2, 3], ["E"] * 4), 4, 3)


def teste_pagina_repetida():
    for algoritmo in ALGORITMOS:
        conferir(algoritmo(3, [0] * 10, ["E"] * 10), 1, 0)


def teste_comparacao_3_4_8_16_molduras():
    esperados = {
        3: [(9, 3), (10, 4), (9, 3), (9, 3)],
        4: [(10, 4), (8, 3), (10, 4), (6, 1)],
        8: [(5, 0)] * 4,
        16: [(5, 0)] * 4,
    }
    resultados = executar_simulacoes(PAGINAS_PADRAO, OPERACOES_PADRAO, MOLDURAS_PADRAO)
    assert len(resultados) == 16
    for quantidade in MOLDURAS_PADRAO:
        linhas = [linha for linha in resultados if linha["molduras"] == quantidade]
        for linha, (faltas, gravacoes) in zip(linhas, esperados[quantidade]):
            assert linha["acessos"] == 12
            conferir(linha, faltas, gravacoes)


def teste_estados_independentes_e_entradas_preservadas():
    paginas = PAGINAS_PADRAO.copy()
    operacoes = OPERACOES_PADRAO.copy()
    primeira = executar_simulacoes(paginas, operacoes, [3, 4])
    for algoritmo in reversed(ALGORITMOS):
        algoritmo(1, [9, 8, 7], ["E"] * 3)
    segunda = executar_simulacoes(paginas, operacoes, [4, 3])
    assert primeira == segunda
    assert paginas == PAGINAS_PADRAO
    assert operacoes == OPERACOES_PADRAO


def teste_entradas_invalidas():
    casos = [
        (0, [1], ["L"]), (-1, [1], ["L"]), (1.5, [1], ["L"]),
        (True, [1], ["L"]), ("3", [1], ["L"]), (3, [], []),
        (3, [1, 2], ["L"]), (3, [1], ["L", "E"]), (3, [-1], ["L"]),
        (3, [1.5], ["L"]), (3, [True], ["L"]), (3, ["1"], ["L"]),
        (3, [1], ["X"]), (3, [1], [""]),
    ]
    for algoritmo in ALGORITMOS:
        for molduras, paginas, operacoes in casos:
            try:
                algoritmo(molduras, paginas, operacoes)
            except ValueError:
                continue
            raise AssertionError(f"{algoritmo.__name__} aceitou entrada inválida: {molduras, paginas, operacoes}")


def teste_csv_contem_os_16_resultados():
    resultados = executar_simulacoes(PAGINAS_PADRAO, OPERACOES_PADRAO, MOLDURAS_PADRAO)
    with tempfile.TemporaryDirectory(prefix="teste_csv_") as pasta:
        caminho = salvar_csv(resultados, pasta)
        with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        assert len(linhas) == 16
        for salvo, esperado in zip(linhas, resultados):
            assert salvo == {chave: str(valor) for chave, valor in esperado.items()}


def teste_pngs_validos_sem_janela():
    from PIL import Image
    import matplotlib

    resultados = executar_simulacoes(PAGINAS_PADRAO, OPERACOES_PADRAO, MOLDURAS_PADRAO)
    with tempfile.TemporaryDirectory(prefix="teste_png_") as pasta:
        caminhos = salvar_graficos(resultados, pasta)
        assert {caminho.name for caminho in caminhos} == {"page_faults.png", "swap_outs.png"}
        assert matplotlib.get_backend().lower() == "agg"
        for caminho in caminhos:
            with Image.open(caminho) as imagem:
                assert imagem.format == "PNG"
                assert imagem.width >= 800 and imagem.height >= 400
                imagem.verify()


def chamar_programa(argumentos, entrada=None):
    ambiente = os.environ.copy()
    ambiente["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(Path(__file__).with_name("main.py")), *argumentos],
        input=entrada, capture_output=True, text=True, encoding="utf-8",
        env=ambiente, timeout=60,
    )


def teste_terminal_manual_e_pasta_com_espacos():
    with tempfile.TemporaryDirectory(prefix="teste terminal ") as pasta:
        resposta = chamar_programa(
            ["--manual", "--molduras", "1", "--saida", pasta],
            "1, 1, 2\nl, e, l\n",
        )
        assert resposta.returncode == 0, resposta.stdout + resposta.stderr
        with (Path(pasta) / "comparacao.csv").open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        assert len(linhas) == 4
        assert all(linha["page_faults"] == "2" and linha["swap_outs"] == "1" for linha in linhas)
        assert (Path(pasta) / "page_faults.png").is_file()
        assert (Path(pasta) / "swap_outs.png").is_file()


def teste_terminal_rejeita_erros_sem_gerar_arquivos():
    casos = [
        (["--molduras", "0"], None, "maior que zero"),
        (["--manual"], "1 2\nL\n", "uma operação"),
        (["--manual"], "1\nX\n", "Use L"),
        (["--manual"], "-1\nL\n", "não negativos"),
        (["--manual"], "abc\n", "números inteiros"),
        (["--manual"], "\n\n", "pelo menos uma página"),
    ]
    with tempfile.TemporaryDirectory(prefix="teste_erro_") as pasta:
        for argumentos, entrada, mensagem in casos:
            resposta = chamar_programa([*argumentos, "--saida", pasta], entrada)
            assert resposta.returncode == 2, resposta.stdout + resposta.stderr
            assert mensagem in resposta.stderr
            assert "Traceback" not in resposta.stderr
        assert not list(Path(pasta).iterdir())


def teste_sintaxe_python_da_carga_linux():
    texto = Path(__file__).with_name("laboratorio_linux.sh").read_text(encoding="utf-8")
    codigo = texto.split("<<'PY_CARGA'", 1)[1].split("\n", 1)[1].split("\nPY_CARGA", 1)[0]
    ast.parse(codigo)  # Somente análise de sintaxe; não executa o experimento Linux.


def teste_historico_preserva_totais_e_formato_anterior():
    for algoritmo in ALGORITMOS:
        for molduras in (1, 3, 4, 8, 16):
            anterior = algoritmo(molduras, PAGINAS_PADRAO, OPERACOES_PADRAO)
            detalhado = algoritmo(molduras, PAGINAS_PADRAO, OPERACOES_PADRAO, registrar_historico=True)
            historico = detalhado.pop("historico")
            assert detalhado == anterior
            assert len(historico) == 12
            assert sum(passo["page_fault"] for passo in historico) == anterior["page_faults"]
            assert sum(passo["swap_out"] for passo in historico) == anterior["swap_outs"]
            assert historico[-1]["page_faults"] == anterior["page_faults"]
            assert historico[-1]["swap_outs"] == anterior["swap_outs"]


def teste_historico_respeita_transicoes_e_dirty():
    import random
    sorteio = random.Random(2026)
    paginas = [sorteio.randrange(7) for _ in range(100)]
    operacoes = [sorteio.choice(("L", "E")) for _ in paginas]
    for algoritmo in ALGORITMOS:
        for molduras in (1, 3, 4, 8, 16):
            anterior = [None] * molduras
            for numero, passo in enumerate(algoritmo(molduras, paginas, operacoes, True)["historico"], 1):
                antes = {item["pagina"]: item for item in anterior if item is not None}
                depois = {item["pagina"]: item for item in passo["memoria"] if item is not None}
                assert passo["acesso"] == numero and passo["pagina"] == paginas[numero - 1]
                assert passo["operacao"] == operacoes[numero - 1]
                assert len(passo["memoria"]) == molduras
                assert len(depois) == sum(item is not None for item in passo["memoria"])
                assert passo["page_fault"] == (passo["pagina"] not in antes)
                retiradas = set(antes) - set(depois)
                assert retiradas == (set() if passo["removida"] is None else {passo["removida"]})
                assert passo["swap_out"] == bool(retiradas and antes[passo["removida"]]["M"])
                assert passo["pagina"] in depois
                for indice, item in enumerate(anterior):
                    if item is not None and item["pagina"] in depois:
                        assert passo["memoria"][indice]["pagina"] == item["pagina"]
                        assert depois[item["pagina"]]["M"] >= item["M"]
                if passo["operacao"] == "E":
                    assert depois[passo["pagina"]]["M"] == 1
                anterior = passo["memoria"]


def teste_historico_molduras_fixas_fifo_e_lru():
    for algoritmo, esperado in ((fifo, [3, 2]), (lru, [1, 3])):
        passos = algoritmo(2, [1, 2, 1, 3], ["L"] * 4, True)["historico"]
        assert [item["pagina"] for item in passos[-1]["memoria"]] == esperado
        assert passos[0]["memoria"][1] is None


def teste_historico_clock_bits_e_ponteiro():
    passos = segunda_chance(3, [1, 2, 3, 4, 2, 5, 2], ["L"] * 7, True)["historico"]
    assert [item["R"] for item in passos[3]["memoria"]] == [1, 0, 0]
    assert passos[3]["ponteiro"] == 1
    assert passos[4]["memoria"][1]["R"] == 1
    assert passos[5]["removida"] == 3
    assert passos[-1]["page_fault"] is False


def teste_historico_nru_limpeza_sem_apagar_modificacao():
    passos = nru(2, [1, 2, 2, 2, 2, 3], ["E", "L", "L", "L", "L", "L"], True)["historico"]
    assert passos[3]["memoria"][0] == {"pagina": 1, "R": 1, "M": 1}
    assert passos[4]["memoria"][0] == {"pagina": 1, "R": 0, "M": 1}
    assert passos[5]["removida"] == 1 and passos[5]["swap_out"] is True


def teste_historicos_sao_copias_independentes():
    for algoritmo in ALGORITMOS:
        passos = algoritmo(2, [0, 0, 1], ["L", "E", "L"], True)["historico"]
        assert passos[0]["memoria"][0]["M"] == 0
        assert passos[1]["memoria"][0]["M"] == 1
        passos[2]["memoria"][0]["pagina"] = 999
        assert passos[1]["memoria"][0]["pagina"] == 0
        novo = algoritmo(2, [0], ["L"], True)
        assert novo["historico"][0]["memoria"][0]["pagina"] == 0


def teste_importacao_interface_nao_abre_janela():
    resposta = subprocess.run([sys.executable, "-c", "import interface, tkinter; assert tkinter._default_root is None"],
                              cwd=Path(__file__).parent, capture_output=True, text=True, timeout=20)
    assert resposta.returncode == 0, resposta.stderr


def teste_conversao_entradas_interface():
    from interface import interpretar_entradas
    assert interpretar_entradas("3", "0, 2 1", "l,e L") == (3, [0, 2, 1], ["L", "E", "L"])
    for argumentos in (("", "1", "L"), ("0", "1", "L"), ("2", "", ""),
                       ("2", "abc", "L"), ("2", "-1", "L"), ("2", "1 2", "L"), ("2", "1", "X")):
        try:
            interpretar_entradas(*argumentos)
        except ValueError:
            continue
        raise AssertionError(f"Entrada inválida aceita: {argumentos}")


@contextmanager
def abrir_interface_teste():
    import tkinter as tk
    from interface import Interface
    raiz = tk.Tk()
    erros = []
    raiz.report_callback_exception = lambda tipo, erro, trace: erros.append(f"{tipo.__name__}: {erro}")
    try:
        aplicativo = Interface(raiz)
        raiz.update()
        yield raiz, aplicativo
        assert not erros, erros
    finally:
        raiz.destroy()


def linhas_tabela(tabela):
    return [tuple(str(valor) for valor in tabela.item(item, "values")) for item in tabela.get_children()]


def teste_gui_quatro_algoritmos_usam_entradas():
    from interface import NOMES
    with abrir_interface_teste() as (raiz, app):
        app.paginas.set("0, 0, 2")
        app.operacoes.set("L, E, L")
        app.molduras.set("1")
        for nome in NOMES:
            app.algoritmo.set(nome)
            app.botao_executar.invoke()
            raiz.update()
            assert [campo.get() for campo in app.resumo] == ["3", "2", "1", "66.7%"]
            assert len(app.historico.get_children()) == 3
            assert linhas_tabela(app.historico)[-1][-2:] == ("0", "Sim")


def teste_gui_navegacao_atualiza_ram_e_historico():
    with abrir_interface_teste() as (raiz, app):
        app.paginas.set("1 2 3 4")
        app.operacoes.set("E L L L")
        app.botao_executar.invoke()
        app.historico.selection_set("3")
        raiz.update()
        assert [linha[1] for linha in linhas_tabela(app.ram)] == ["4", "2", "3"]
        assert app.botao_proximo.instate(["disabled"])
        app.botao_anterior.invoke()
        raiz.update()
        assert [linha[1] for linha in linhas_tabela(app.ram)] == ["1", "2", "3"]
        app.botao_inicio.invoke()
        raiz.update()
        assert [linha[1] for linha in linhas_tabela(app.ram)] == ["-", "-", "-"]
        assert app.botao_anterior.instate(["disabled"])
        app.botao_proximo.invoke()
        raiz.update()
        assert linhas_tabela(app.ram)[0] == ("1", "1", "-", "1")


def teste_gui_entradas_invalidas_mostram_mensagem():
    with abrir_interface_teste() as (raiz, app):
        casos = [("0", "1", "L"), ("", "1", "L"), ("3", "", ""),
                 ("3", "1 2", "L"), ("3", "abc", "L"), ("3", "1", "X")]
        for molduras, paginas, operacoes in casos:
            app.molduras.set(molduras)
            app.paginas.set(paginas)
            app.operacoes.set(operacoes)
            with patch("interface.messagebox.showerror") as mensagem:
                app.botao_executar.invoke()
                raiz.update()
                assert mensagem.call_count == 1
                assert mensagem.call_args.args[0] == "Entrada inválida"
            assert app.resultado is None and not app.historico.get_children()
        app.paginas.set("")
        with patch("interface.messagebox.showerror") as mensagem:
            app.botao_comparar.invoke()
            assert mensagem.call_count == 1
        assert not app.comparacao


def teste_gui_repeticao_e_reinicio_sem_estado_antigo():
    with abrir_interface_teste() as (raiz, app):
        app.botao_executar.invoke()
        app.botao_comparar.invoke()
        app.paginas.set("7 7")
        assert app.resultado is None and not app.comparacao
        assert app.botao_salvar.instate(["disabled"]) and app.botao_graficos.instate(["disabled"])
        app.operacoes.set("E L")
        app.molduras.set("1")
        app.botao_executar.invoke()
        raiz.update()
        conferir(app.resultado, 1, 0)
        app.botao_reiniciar.invoke()
        raiz.update()
        assert app.molduras.get() == "3" and app.resultado is None
        assert not app.ram.get_children() and not app.historico.get_children()


def teste_gui_comparacao_mesmas_entradas_16_linhas():
    with abrir_interface_teste() as (raiz, app):
        app.paginas.set("0 1 2 3 0 1 4")
        app.operacoes.set("E L E L L E E")
        app.molduras.set("")  # Esse campo não define as capacidades da comparação.
        app.botao_comparar.invoke()
        raiz.update()
        esperado = executar_simulacoes([0, 1, 2, 3, 0, 1, 4], ["E", "L", "E", "L", "L", "E", "E"], MOLDURAS_PADRAO)
        assert app.comparacao == esperado
        assert len(linhas_tabela(app.tabela_comparacao)) == 16
        for exibido, calculado in zip(linhas_tabela(app.tabela_comparacao), esperado):
            assert exibido == tuple(str(valor) for valor in calculado.values())


def teste_gui_exportacao_e_cancelamento():
    with abrir_interface_teste() as (raiz, app), tempfile.TemporaryDirectory(prefix="exportacao_gui_") as pasta:
        app.botao_comparar.invoke()
        with patch("interface.filedialog.askdirectory", return_value=pasta), patch("interface.messagebox.showerror") as erro:
            app.botao_salvar.invoke()
            raiz.update()
            assert not erro.called
        with (Path(pasta) / "comparacao.csv").open(encoding="utf-8-sig", newline="") as arquivo:
            assert list(csv.DictReader(arquivo)) == [{chave: str(valor) for chave, valor in linha.items()} for linha in app.comparacao]
        from PIL import Image
        for nome in ("page_faults.png", "swap_outs.png"):
            with Image.open(Path(pasta) / nome) as imagem:
                imagem.verify()
        antes = {arquivo.name: arquivo.read_bytes() for arquivo in Path(pasta).iterdir()}
        with patch("interface.filedialog.askdirectory", return_value=pasta), patch("interface.messagebox.askyesno", return_value=False):
            app.botao_salvar.invoke()
        with patch("interface.filedialog.askdirectory", return_value=""):
            app.botao_salvar.invoke()
        assert antes == {arquivo.name: arquivo.read_bytes() for arquivo in Path(pasta).iterdir()}


def teste_gui_visualizacao_real_dos_png():
    with abrir_interface_teste() as (raiz, app):
        app.botao_comparar.invoke()
        janela = app.visualizar_graficos()
        raiz.update()
        assert janela.winfo_exists() and len(janela.imagens) == 2
        assert all(imagem.width() >= 500 for imagem in janela.imagens)
        janela.destroy()


def teste_gui_layout_minimo_sem_cortar_botoes():
    with abrir_interface_teste() as (raiz, app):
        raiz.geometry("860x620")
        for aba, controles in ((app.aba_simulacao, [app.botao_executar, app.botao_reiniciar, app.botao_proximo, app.ram, app.historico]),
                               (app.aba_comparacao, [app.botao_comparar, app.botao_salvar, app.botao_graficos, app.tabela_comparacao])):
            app.abas.select(aba)
            raiz.update()
            for widget in controles:
                assert widget.winfo_ismapped()
                assert widget.winfo_rootx() >= raiz.winfo_rootx()
                assert widget.winfo_rooty() >= raiz.winfo_rooty()
                assert widget.winfo_rootx() + widget.winfo_width() <= raiz.winfo_rootx() + raiz.winfo_width()
                assert widget.winfo_rooty() + widget.winfo_height() <= raiz.winfo_rooty() + raiz.winfo_height()


def teste_gui_estado_com_16_molduras_cabe_na_coluna():
    from tkinter import font
    from interface import descrever_memoria
    with abrir_interface_teste() as (raiz, app):
        app.molduras.set("16")
        app.botao_executar.invoke()
        app.selecionar_passo(11)
        raiz.update()
        assert len(app.ram.get_children()) == 16
        fonte = font.nametofont("TkDefaultFont")
        texto = descrever_memoria(app.resultado["historico"][-1]["memoria"])
        assert int(app.historico.column("Molduras", "width")) >= fonte.measure(texto) + 20
        assert linhas_tabela(app.historico)[-1][3] == texto


def main():
    if not __debug__:
        print("Execute os testes sem a opção -O, pois ela desativa as verificações assert.")
        return 1
    parser = argparse.ArgumentParser(description="Validação do simulador; testes gráficos separados.")
    parser.add_argument("--interface", action="store_true", help="executar somente os testes que abrem janelas Tk")
    argumentos = parser.parse_args()
    testes = [funcao for nome, funcao in globals().items()
              if nome.startswith("teste_") and nome.startswith("teste_gui_") == argumentos.interface]
    falhas = 0
    for teste in testes:
        try:
            teste()
            print(f"OK: {teste.__name__}")
        except Exception as erro:
            falhas += 1
            print(f"FALHOU: {teste.__name__}: {type(erro).__name__}: {erro}")
    print(f"\n{len(testes) - falhas}/{len(testes)} testes passaram.")
    return int(falhas > 0)


if __name__ == "__main__":
    raise SystemExit(main())
