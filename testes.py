"""Testes com resultados calculados à mão; executar com python testes.py."""

import ast
import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile

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


def main():
    if not __debug__:
        print("Execute os testes sem a opção -O, pois ela desativa as verificações assert.")
        return 1
    testes = [funcao for nome, funcao in globals().items() if nome.startswith("teste_")]
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
