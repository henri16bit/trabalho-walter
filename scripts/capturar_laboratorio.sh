#!/usr/bin/env bash
# Captura um terminal X real reexibindo as saídas brutas da coleta.
# Não desenha imagens nem apresenta esta reexibição como medição ao vivo.
set -euo pipefail
export LC_ALL=C.UTF-8
coleta="$(realpath -- "$1")"
base="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$coleta/capturas"

if [[ "${2:-}" == "--mostrar" ]]; then
    nome="$3"
    printf 'LABORATORIO GNU/LINUX - saídas reais reexibidas após a coleta\n'
    printf 'Não é uma nova medição ao vivo. Origem e comandos: origem.txt e comandos.tsv\n'
    cat "$coleta/data.txt" "$coleta/sistema.txt"
    shift 3
    for arquivo in "$@"; do
        printf '\n--- %s ---\n' "$arquivo"
        awk -F '\t' -v alvo="$arquivo" '$1 == alvo {print "Comando: " $4 " | saída=" $2}' "$coleta/comandos.tsv"
        if [[ "$arquivo" == "top.txt" ]]; then
            printf 'Trecho: últimas 16 linhas; arquivo completo preservado.\n'
            tail -n 16 "$coleta/$arquivo"
        elif [[ "$arquivo" == "memstat.txt" ]]; then
            printf 'Trecho: primeiras 32 linhas; arquivo completo preservado.\n'
            head -n 32 "$coleta/$arquivo"
        else
            cat "$coleta/$arquivo"
        fi
    done
    touch "$coleta/capturas/.pronto_$nome"
    sleep 15
    exit 0
fi

capturar() {
    local nome="$1"
    shift
    xterm -geometry 155x70+0+0 -fa 'DejaVu Sans Mono' -fs 12 \
        -bg '#101418' -fg '#e8edf2' -title "Laboratório: $nome" \
        -e bash "$base/scripts/capturar_laboratorio.sh" "$coleta" --mostrar "$nome" "$@" &
    local pid_terminal=$!
    for tentativa in {1..40}; do
        [[ -f "$coleta/capturas/.pronto_$nome" ]] && break
        sleep 0.25
    done
    if [[ ! -f "$coleta/capturas/.pronto_$nome" ]]; then
        kill "$pid_terminal" 2>/dev/null || true
        wait "$pid_terminal" 2>/dev/null || true
        printf 'Falha ao preparar captura %s\n' "$nome" >&2
        return 1
    fi
    sleep 0.5
    scrot "$coleta/capturas/$nome.png"
    kill "$pid_terminal" 2>/dev/null || true
    wait "$pid_terminal" 2>/dev/null || true
}

capturar atividade1_pmap pmap.txt
capturar atividade1_maps maps.txt
capturar atividade2_estados estados.txt
capturar atividade2_top ps_processo.txt top.txt
capturar atividade2_strace strace.txt
capturar atividade3_ram free_antes.txt free_durante.txt free_depois.txt swaps_depois.txt contadores_swap_antes.txt contadores_swap_depois.txt
capturar atividade3_carga carga.txt ps_carga.txt
capturar atividade3_memstat memstat.txt
