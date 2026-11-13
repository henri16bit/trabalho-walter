# Requisitos e evidências

Conferência do enunciado do professor Walter, datado de 26/10/2026, páginas 1–3. Atualizada após a coleta real de 13/11/2026. Este inventário técnico não é o relatório acadêmico. A pedido do usuário, algoritmos, interface e `relatorio.md` foram preservados.

## Código e laboratório

| Exigência do enunciado | Evidência verificável | Situação / limite |
|---|---|---|
| Entrada de molduras, sequência de páginas e leitura/escrita (§3.1) | [main.py](../main.py), [interface.py](../interface.py), [testes.py](../testes.py) | Implementado anteriormente; preservado |
| FIFO, LRU/Aging, Segunda Chance e NRU (objetivos e rubrica) | [algoritmos.py](../algoritmos.py) | Quatro algoritmos; a alternativa escolhida foi LRU |
| Page faults, swap outs por Dirty e tabela comparativa (§3.3) | [CSV](../resultados/comparacao.csv), [page faults](../resultados/page_faults.png), [swap outs](../resultados/swap_outs.png) | 16 combinações, com 3/4/8/16 molduras |
| Código funcional e verificável (rubrica) | [33 testes sem janela + 9 gráficos no Ubuntu](https://github.com/henri16bit/trabalho-walter/actions/runs/43100556246) | Validação do simulador; não substitui o laboratório |
| Atividade 1: `pmap -x`, segmentos e rwx | [pmap](linux_20261113T205043Z_3277/pmap.txt), [maps](linux_20261113T205043Z_3277/maps.txt), capturas [pmap](linux_20261113T205043Z_3277/capturas/atividade1_pmap.png) / [maps](linux_20261113T205043Z_3277/capturas/atividade1_maps.png) | Executada; interpretação em [observacoes.md](observacoes.md). Data/BSS sem separação exata por ELF |
| Atividade 2: `ps aux` e `top/htop`, estados | [ps aux](linux_20261113T205043Z_3277/ps_aux.txt), [estados](linux_20261113T205043Z_3277/estados.txt), [top](linux_20261113T205043Z_3277/top.txt) | Executada com `top`; transições reais R/S. Running/Ready não separados individualmente; D não observado |
| Atividade 2: `strace -c <comando>` | [strace.txt](linux_20261113T205043Z_3277/strace.txt), [captura](linux_20261113T205043Z_3277/capturas/atividade2_strace.png) | Executada: 769 syscalls; nenhuma restrição de ptrace observada |
| Atividade 3: `free -h`, `memstat`, `/proc/swaps` | [free antes](linux_20261113T205043Z_3277/free_antes.txt), [durante](linux_20261113T205043Z_3277/free_durante.txt), [depois](linux_20261113T205043Z_3277/free_depois.txt), [memstat](linux_20261113T205043Z_3277/memstat.txt), [swaps](linux_20261113T205043Z_3277/swaps_depois.txt) | Executada; `memstat` limitado aos processos acessíveis ao usuário runner |
| Atividade 3: carga real | [carga.txt](linux_20261113T205043Z_3277/carga.txt), [ps](linux_20261113T205043Z_3277/ps_carga.txt), [pmap](linux_20261113T205043Z_3277/pmap_carga.txt), [captura](linux_20261113T205043Z_3277/capturas/atividade3_carga.png) | Executada com limite seguro: 32 MiB, 20,002 s de espera medida, RSS antes/durante/depois |
| Atividade 3: carga elevada para observar início de swap e impacto de E/S | [contadores antes](linux_20261113T205043Z_3277/contadores_swap_antes.txt), [durante](linux_20261113T205043Z_3277/contadores_swap_durante.txt), [depois](linux_20261113T205043Z_3277/contadores_swap_depois.txt), [RAM/swap](linux_20261113T205043Z_3277/capturas/atividade3_ram.png) | **Não demonstrado:** aproximadamente 3 GiB de swap disponível, uso 0 e pswpin/pswpout 0. Sem carga perigosa; impactos discutidos apenas conceitualmente |
| Evidências reais, comandos e ambiente | [execução remota](https://github.com/henri16bit/trabalho-walter/actions/runs/43505223640), [comandos.tsv](linux_20261113T205043Z_3277/comandos.tsv), [sistema](linux_20261113T205043Z_3277/sistema.txt), [SHA256SUMS](linux_20261113T205043Z_3277/SHA256SUMS) | 35 comandos com código 0; 49 arquivos cobertos pelo manifesto e oito capturas reais de reexibição |
| Clareza do código e instruções (rubrica) | [README](../README.md), [roteiro](../laboratorio_linux.sh), [workflow](../.github/workflows/laboratorio-linux.yml) | Instalação Linux, interface, CLI, testes, repetição remota e limites documentados |

## Sete seções acadêmicas: conferência somente

O PDF exige entrega em PDF ou Google Docs. O usuário posteriormente pediu para não fazer o relatório; por isso o arquivo existente foi apenas conferido, sem edição ou exportação.

| Seção exigida | Estado do rascunho existente | Pendência |
|---|---|---|
| 1. Capa e identificação | Existe com campos em aberto | Nomes, identificação da dupla, data e definição dos responsáveis |
| 2. Fundamentação teórica | Contém memória virtual, MMU, tabela, faults e estados | Revisão acadêmica final pela dupla |
| 3. Metodologia/modelagem | Existe, mas descreve versão anterior de terminal e 25 testes | Atualizar para Tkinter, histórico e 33+9 testes quando o usuário autorizar o relatório |
| 4. Resultados e comparação | Possui tabelas e gráficos dos quatro algoritmos | Revisão final da dupla; os arquivos do simulador foram preservados |
| 5. Análise GNU/Linux | Ainda contém campos pendentes | Incorporar estas evidências reais e as limitações, quando autorizado |
| 6. Conclusões e lições da dupla | Ainda descreve laboratório pendente | Redação/revisão conjunta da dupla com base na coleta |
| 7. Referências | Já contém fontes de SO e manuais Linux | Revisão da formatação e das fontes efetivamente utilizadas |

**Fora da conclusão técnica atual:** produção do relatório final, exportação PDF/Google Docs, identificação e divisão de papéis da dupla, revisão conjunta e entrega ao professor. A coleta bem-sucedida não demonstra uso de swap nem conclui automaticamente essas exigências acadêmicas.
