#!/usr/bin/env bash
# Captura real de um xterm reexibindo resultados; nao realiza nova medicao.
set -euo pipefail
export LC_ALL=C.UTF-8
coleta="$(realpath -- "$1")"
script="$(realpath -- "${BASH_SOURCE[0]}")"

if [[ "${2:-}" == "--mostrar" ]]; then
    nome="$3"
    shift 3
    printf 'LABORATORIO GNU/LINUX - SWAP REAL EM CGROUP ISOLADO\n'
    printf 'Reexibicao de registros reais; nao e uma nova medicao ao vivo.\n'
    cat "$coleta/sistema.txt"
    printf 'Fonte completa: origem.json, comandos.tsv, amostras.jsonl e SHA256SUMS\n'
    for arquivo in "$@"; do
        printf '\n--- %s ---\n' "$arquivo"
        if [[ -f "$coleta/$arquivo" ]]; then
            cat "$coleta/$arquivo"
        else
            printf 'Nao gerado. Verifique limitacao.txt e logs do job.\n'
        fi
    done
    touch "$coleta/.pronto_$nome"
    sleep 15
    exit 0
fi

mkdir -p "$coleta/capturas"
capturar() {
    local nome="$1"
    shift
    rm -f -- "$coleta/.pronto_$nome"
    xterm -geometry 155x62+0+0 -fa 'DejaVu Sans Mono' -fs 11 \
        -bg '#101418' -fg '#e8edf2' -title "Swap GNU/Linux: $nome" \
        -e bash "$script" "$coleta" --mostrar "$nome" "$@" &
    local pid_terminal=$!
    for tentativa in {1..40}; do
        [[ -f "$coleta/.pronto_$nome" ]] && break
        sleep 0.25
    done
    if [[ ! -f "$coleta/.pronto_$nome" ]]; then
        kill "$pid_terminal" 2>/dev/null || true
        wait "$pid_terminal" 2>/dev/null || true
        printf 'Captura indisponivel: %s\n' "$nome" >&2
        return 1
    fi
    sleep 0.5
    scrot "$coleta/capturas/$nome.png"
    kill "$pid_terminal" 2>/dev/null || true
    wait "$pid_terminal" 2>/dev/null || true
}
if [[ -f "$coleta/resumo.txt" ]]; then
    capturar swap_resumo resumo.txt
    capturar swap_ram free_pressao_antes.txt swaps_pressao_antes.txt free_pressao_alocada.txt swaps_pressao_alocada.txt free_pressao_depois.txt swaps_pressao_depois.txt
    capturar swap_carga controle_carga.txt pressao_carga.txt
else
    capturar swap_limitacao limitacao.txt
fi
