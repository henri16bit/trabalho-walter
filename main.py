"""Entrada pelo terminal: sequência pronta ou referências informadas pelo usuário."""

import argparse
from pathlib import Path

from algoritmos import ALGORITMOS
from graficos import salvar_csv, salvar_graficos

PAGINAS_PADRAO = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
OPERACOES_PADRAO = ["E", "L", "E", "L", "L", "E", "E", "L", "L", "E", "L", "L"]
MOLDURAS_PADRAO = [3, 4, 8, 16]


def ler_sequencia():
    texto = input("Páginas (inteiros separados por espaços ou vírgulas): ")
    try:
        paginas = [int(valor) for valor in texto.replace(",", " ").split()]
    except ValueError:
        raise ValueError("As páginas devem ser números inteiros não negativos.") from None
    texto = input("Operações (uma L ou E por página, separadas por espaços ou vírgulas): ")
    operacoes = texto.upper().replace(",", " ").split()
    return paginas, operacoes


def executar_simulacoes(paginas, operacoes, molduras):
    resultados = []
    for quantidade in sorted(set(molduras)):
        for algoritmo in ALGORITMOS:
            resultados.append(algoritmo(quantidade, paginas, operacoes))
    return resultados


def exibir_tabela(resultados):
    print(f"{'Algoritmo':<17} {'Molduras':>8} {'Acessos':>8} {'Page faults':>12} {'Swap outs':>10}")
    print("-" * 60)
    for linha in resultados:
        print(
            f"{linha['algoritmo']:<17} {linha['molduras']:>8} "
            f"{linha['acessos']:>8} {linha['page_faults']:>12} {linha['swap_outs']:>10}"
        )


def main():
    parser = argparse.ArgumentParser(description="Simulador de substituição de páginas — UNIRP")
    parser.add_argument("--manual", action="store_true", help="informar páginas e operações pelo terminal")
    parser.add_argument(
        "--molduras", type=int, nargs="+", default=MOLDURAS_PADRAO,
        help="quantidades de molduras a comparar (padrão: 3 4 8 16)",
    )
    parser.add_argument(
        "--saida", type=Path, default=Path(__file__).resolve().parent / "resultados",
        help="pasta para CSV e PNG (padrão: resultados ao lado de main.py)",
    )
    argumentos = parser.parse_args()
    try:
        if argumentos.manual:
            paginas, operacoes = ler_sequencia()
        else:
            paginas, operacoes = PAGINAS_PADRAO, OPERACOES_PADRAO
        resultados = executar_simulacoes(paginas, operacoes, argumentos.molduras)
    except ValueError as erro:
        parser.error(str(erro))
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada interrompida. Nenhuma simulação foi salva.")
        return 1

    print("L = leitura; E = escrita")
    print("Páginas:  ", " ".join(map(str, paginas)))
    print("Operações:", " ".join(operacoes))
    print()
    exibir_tabela(resultados)
    try:
        caminho_csv = salvar_csv(resultados, argumentos.saida)
        print(f"\nCSV salvo em: {caminho_csv}")
        for caminho in salvar_graficos(resultados, argumentos.saida):
            print(f"Gráfico salvo em: {caminho}")
    except ModuleNotFoundError as erro:
        print(f"Não foi possível gerar os gráficos: dependência ausente ({erro.name}).")
        print("Instale as dependências com: python -m pip install -r requirements.txt")
        return 1
    except OSError as erro:
        print(f"Não foi possível salvar os resultados: {erro}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
