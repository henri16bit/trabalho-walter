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


def montar_resultado(nome, molduras, acessos, faltas, gravacoes, historico=None):
    resultado = {
        "algoritmo": nome,
        "molduras": molduras,
        "acessos": acessos,
        "page_faults": faltas,
        "swap_outs": gravacoes,
    }
    if historico is not None:
        resultado["historico"] = historico
    return resultado


def registrar_etapa(historico, pagina, operacao, memoria, molduras,
                    falta, vitima, faltas, gravacoes, ponteiro=None):
    if historico is None:
        return
    # Copia cada moldura: acessos futuros não podem alterar etapas já registradas.
    estado = [None] * molduras
    for indice, item in enumerate(memoria):
        if item is not None:
            estado[item.get("moldura", indice)] = {
                "pagina": item["pagina"], "R": item.get("R"), "M": item["M"],
            }
    historico.append({
        "acesso": len(historico) + 1, "pagina": pagina, "operacao": operacao,
        "memoria": estado, "page_fault": falta,
        "removida": vitima["pagina"] if vitima is not None else None,
        "swap_out": bool(vitima is not None and vitima["M"]),
        "page_faults": faltas, "swap_outs": gravacoes, "ponteiro": ponteiro,
    })


def fifo(molduras, paginas, operacoes, registrar_historico=False):
    validar_entradas(molduras, paginas, operacoes)
    memoria = []
    faltas = gravacoes = 0
    historico = [] if registrar_historico else None

    for pagina, operacao in zip(paginas, operacoes):
        residente = next((item for item in memoria if item["pagina"] == pagina), None)
        if residente is not None:
            if operacao == "E":
                residente["M"] = 1
            registrar_etapa(historico, pagina, operacao, memoria, molduras,
                            False, None, faltas, gravacoes)
            continue  # Um acerto não muda a ordem de entrada no FIFO.

        faltas += 1
        vitima = None
        indice = len(memoria)
        if len(memoria) == molduras:
            vitima = memoria.pop(0)
            gravacoes += vitima["M"]
            indice = vitima["moldura"]
        memoria.append({"pagina": pagina, "M": int(operacao == "E"), "moldura": indice})
        registrar_etapa(historico, pagina, operacao, memoria, molduras,
                        True, vitima, faltas, gravacoes)

    return montar_resultado("FIFO", molduras, len(paginas), faltas, gravacoes, historico)


def lru(molduras, paginas, operacoes, registrar_historico=False):
    validar_entradas(molduras, paginas, operacoes)
    memoria = []
    faltas = gravacoes = 0
    historico = [] if registrar_historico else None

    for instante, (pagina, operacao) in enumerate(zip(paginas, operacoes)):
        residente = next((item for item in memoria if item["pagina"] == pagina), None)
        if residente is not None:
            residente["ultimo_acesso"] = instante
            if operacao == "E":
                residente["M"] = 1
            registrar_etapa(historico, pagina, operacao, memoria, molduras,
                            False, None, faltas, gravacoes)
            continue

        faltas += 1
        vitima = None
        indice = len(memoria)
        if len(memoria) == molduras:
            vitima = min(memoria, key=lambda item: item["ultimo_acesso"])
            gravacoes += vitima["M"]
            memoria.remove(vitima)
            indice = vitima["moldura"]
        memoria.append({
            "pagina": pagina,
            "M": int(operacao == "E"),
            "ultimo_acesso": instante,
            "moldura": indice,
        })
        registrar_etapa(historico, pagina, operacao, memoria, molduras,
                        True, vitima, faltas, gravacoes)

    return montar_resultado("LRU", molduras, len(paginas), faltas, gravacoes, historico)


def segunda_chance(molduras, paginas, operacoes, registrar_historico=False):
    validar_entradas(molduras, paginas, operacoes)
    memoria = [None] * molduras
    ponteiro = 0
    faltas = gravacoes = 0
    historico = [] if registrar_historico else None

    for pagina, operacao in zip(paginas, operacoes):
        residente = next(
            (item for item in memoria if item is not None and item["pagina"] == pagina),
            None,
        )
        if residente is not None:
            residente["R"] = 1
            if operacao == "E":
                residente["M"] = 1
            registrar_etapa(historico, pagina, operacao, memoria, molduras,
                            False, None, faltas, gravacoes, ponteiro)
            continue

        faltas += 1
        while memoria[ponteiro] is not None and memoria[ponteiro]["R"] == 1:
            memoria[ponteiro]["R"] = 0
            ponteiro = (ponteiro + 1) % molduras

        vitima = memoria[ponteiro]
        if vitima is not None:
            gravacoes += vitima["M"]
        memoria[ponteiro] = {"pagina": pagina, "R": 1, "M": int(operacao == "E")}
        ponteiro = (ponteiro + 1) % molduras
        registrar_etapa(historico, pagina, operacao, memoria, molduras,
                        True, vitima, faltas, gravacoes, ponteiro)

    return montar_resultado("Segunda Chance", molduras, len(paginas), faltas, gravacoes, historico)


def nru(molduras, paginas, operacoes, registrar_historico=False):
    validar_entradas(molduras, paginas, operacoes)
    memoria = []
    faltas = gravacoes = 0
    historico = [] if registrar_historico else None

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
            registrar_etapa(historico, pagina, operacao, memoria, molduras,
                            False, None, faltas, gravacoes)
            continue

        faltas += 1
        vitima = None
        nova_pagina = {"pagina": pagina, "R": 1, "M": int(operacao == "E")}
        if len(memoria) < molduras:
            memoria.append(nova_pagina)
        else:
            # 2*R + M produz as classes 0, 1, 2 e 3. Empate: menor índice.
            indice = min(
                range(len(memoria)),
                key=lambda i: (2 * memoria[i]["R"] + memoria[i]["M"], i),
            )
            vitima = memoria[indice]
            gravacoes += vitima["M"]
            memoria[indice] = nova_pagina
        registrar_etapa(historico, pagina, operacao, memoria, molduras,
                        True, vitima, faltas, gravacoes)

    return montar_resultado("NRU", molduras, len(paginas), faltas, gravacoes, historico)


ALGORITMOS = (fifo, lru, segunda_chance, nru)
