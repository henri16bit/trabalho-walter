"""Exportação dos contadores para CSV e gráficos PNG, sem abrir janelas."""

import csv
from pathlib import Path


def salvar_csv(resultados, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "comparacao.csv"
    colunas = ["algoritmo", "molduras", "acessos", "page_faults", "swap_outs"]
    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(resultados)
    return caminho


def salvar_graficos(resultados, pasta):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    nomes = list(dict.fromkeys(linha["algoritmo"] for linha in resultados))
    estilos = [("o", "-"), ("s", "--"), ("^", "-."), ("D", ":")]
    caminhos = []
    for metrica, titulo in (("page_faults", "Page faults"), ("swap_outs", "Swap outs")):
        figura, eixo = plt.subplots(figsize=(8, 4.8))
        for indice, nome in enumerate(nomes):
            linhas = sorted(
                (linha for linha in resultados if linha["algoritmo"] == nome),
                key=lambda linha: linha["molduras"],
            )
            marcador, estilo = estilos[indice]
            eixo.plot(
                [linha["molduras"] for linha in linhas],
                [linha[metrica] for linha in linhas],
                label=nome, marker=marcador, linestyle=estilo,
                markersize=10 - indice, markerfacecolor="none", linewidth=1.6,
            )
        eixo.set_title(f"{titulo} por quantidade de molduras")
        eixo.set_xlabel("Quantidade de molduras")
        eixo.set_ylabel(f"Quantidade de {titulo.lower()}")
        eixo.set_xticks(sorted({linha["molduras"] for linha in resultados}))
        eixo.set_ylim(0, max(linha[metrica] for linha in resultados) + 1)
        eixo.yaxis.set_major_locator(MaxNLocator(integer=True))
        eixo.grid(True, alpha=0.25)
        eixo.legend()
        figura.text(0.5, 0.02, "Linhas coincidentes indicam resultados iguais.", ha="center", fontsize=9)
        figura.tight_layout(rect=(0, 0.05, 1, 1))
        caminho = pasta / f"{metrica}.png"
        figura.savefig(caminho, dpi=160)
        plt.close(figura)
        caminhos.append(caminho)
    return caminhos
