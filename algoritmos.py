"""Simulação didática de substituição de páginas, sem acessar a RAM real."""

INTERVALO_LIMPEZA_R = 4


def validar_entradas(molduras, paginas, operacoes):
    if type(molduras) is not int or molduras < 1:
        raise ValueError("A quantidade de molduras deve ser um inteiro maior que zero.")
    if not paginas:
        raise ValueError("Informe pelo menos uma página.")
    if len(paginas) != len(operacoes):
        raise ValueError("Informe exatamente uma operação para cada página.")
    if any(type(pagina) is not int or pagina < 0 for pagina in paginas):
        raise ValueError("As páginas devem ser números inteiros não negativos.")
    if any(operacao not in ("L", "E") for operacao in operacoes):
        raise ValueError("Use L para leitura e E para escrita.")


def montar_resultado(nome, molduras, acessos, faltas, gravacoes):
    return {
        "algoritmo": nome,
        "molduras": molduras,
        "acessos": acessos,
        "page_faults": faltas,
        "swap_outs": gravacoes,
    }


def fifo(molduras, paginas, operacoes):
    validar_entradas(molduras, paginas, operacoes)
    memoria = []
    faltas = gravacoes = 0

    for pagina, operacao in zip(paginas, operacoes):
        residente = next((item for item in memoria if item["pagina"] == pagina), None)
        if residente is not None:
            if operacao == "E":
                residente["M"] = 1
            continue  # Um acerto não muda a ordem de entrada no FIFO.

        faltas += 1
        if len(memoria) == molduras:
            vitima = memoria.pop(0)
            gravacoes += vitima["M"]
        memoria.append({"pagina": pagina, "M": int(operacao == "E")})

    return montar_resultado("FIFO", molduras, len(paginas), faltas, gravacoes)


def lru(molduras, paginas, operacoes):
    validar_entradas(molduras, paginas, operacoes)
    memoria = []
    faltas = gravacoes = 0

    for instante, (pagina, operacao) in enumerate(zip(paginas, operacoes)):
        residente = next((item for item in memoria if item["pagina"] == pagina), None)
        if residente is not None:
            residente["ultimo_acesso"] = instante
            if operacao == "E":
                residente["M"] = 1
            continue

        faltas += 1
        if len(memoria) == molduras:
            vitima = min(memoria, key=lambda item: item["ultimo_acesso"])
            gravacoes += vitima["M"]
            memoria.remove(vitima)
        memoria.append({
            "pagina": pagina,
            "M": int(operacao == "E"),
            "ultimo_acesso": instante,
        })

    return montar_resultado("LRU", molduras, len(paginas), faltas, gravacoes)


def segunda_chance(molduras, paginas, operacoes):
    validar_entradas(molduras, paginas, operacoes)
    memoria = [None] * molduras
    ponteiro = 0
    faltas = gravacoes = 0

    for pagina, operacao in zip(paginas, operacoes):
        residente = next(
            (item for item in memoria if item is not None and item["pagina"] == pagina),
            None,
        )
        if residente is not None:
            residente["R"] = 1
            if operacao == "E":
                residente["M"] = 1
            continue

        faltas += 1
        while memoria[ponteiro] is not None and memoria[ponteiro]["R"] == 1:
            memoria[ponteiro]["R"] = 0
            ponteiro = (ponteiro + 1) % molduras

        if memoria[ponteiro] is not None:
            gravacoes += memoria[ponteiro]["M"]
        memoria[ponteiro] = {"pagina": pagina, "R": 1, "M": int(operacao == "E")}
        ponteiro = (ponteiro + 1) % molduras

    return montar_resultado("Segunda Chance", molduras, len(paginas), faltas, gravacoes)


def nru(molduras, paginas, operacoes):
    validar_entradas(molduras, paginas, operacoes)
    memoria = []
    faltas = gravacoes = 0

    for instante, (pagina, operacao) in enumerate(zip(paginas, operacoes)):
        # Limpa R antes dos acessos 5, 9, 13...; o acesso atual volta a marcar R.
        if instante > 0 and instante % INTERVALO_LIMPEZA_R == 0:
            for item in memoria:
                item["R"] = 0

        residente = next((item for item in memoria if item["pagina"] == pagina), None)
        if residente is not None:
            residente["R"] = 1
            if operacao == "E":
                residente["M"] = 1
            continue

        faltas += 1
        nova_pagina = {"pagina": pagina, "R": 1, "M": int(operacao == "E")}
        if len(memoria) < molduras:
            memoria.append(nova_pagina)
        else:
            # 2*R + M produz as classes 0, 1, 2 e 3. Empate: menor índice.
            indice = min(
                range(len(memoria)),
                key=lambda i: (2 * memoria[i]["R"] + memoria[i]["M"], i),
            )
            gravacoes += memoria[indice]["M"]
            memoria[indice] = nova_pagina

    return montar_resultado("NRU", molduras, len(paginas), faltas, gravacoes)


ALGORITMOS = (fifo, lru, segunda_chance, nru)
