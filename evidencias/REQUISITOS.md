# Requisitos e evidências

Conferência do enunciado do professor Walter, datado de 26/10/2026, páginas 1–3. Atualizada em **17/11/2026**, com a nova validação Ubuntu do simulador e a coleta real do laboratório de 13/11/2026. O [relatório](../relatorio.md) foi revisado após autorização do usuário. Algoritmos e interface foram preservados; a automação de captura passou a mostrar a janela e a identificação do Ubuntu no mesmo display.

## Código e laboratório

| Exigência do enunciado | Evidência verificável | Situação / limite |
|---|---|---|
| Entrada de molduras, sequência de páginas e leitura/escrita (§3.1) | [main.py](../main.py), [interface.py](../interface.py), [testes.py](../testes.py) | Implementado anteriormente; preservado |
| FIFO, LRU/Aging, Segunda Chance e NRU (objetivos e rubrica) | [algoritmos.py](../algoritmos.py) | Quatro algoritmos; a alternativa escolhida foi LRU |
| Page faults, swap outs por Dirty e tabela comparativa (§3.3) | [CSV Ubuntu](simulador_linux_20261117_44179462467/comparacao.csv), [terminal](simulador_linux_20261117_44179462467/terminal.txt), [page faults](simulador_linux_20261117_44179462467/page_faults.png), [swap outs](simulador_linux_20261117_44179462467/swap_outs.png) | 16 combinações, com 3/4/8/16 molduras; arquivos gerados no Ubuntu e preservados |
| Código funcional e verificável (rubrica) | [Execução Ubuntu de 17/11](https://github.com/henri16bit/trabalho-walter/actions/runs/44179462467), [33 testes](simulador_linux_20261117_44179462467/testes_logica.txt), [9 testes gráficos](simulador_linux_20261117_44179462467/testes_interface.txt), [captura GUI + Ubuntu](simulador_linux_20261117_44179462467/comprovacao_ubuntu.png) | 42 testes aprovados; janelas reais em Xvfb, acionamento automatizado. Não comprova interação humana nem substitui o laboratório |
| Atividade 1: `pmap -x`, segmentos e rwx | [pmap](linux_20261113T205043Z_3277/pmap.txt), [maps](linux_20261113T205043Z_3277/maps.txt), capturas [pmap](linux_20261113T205043Z_3277/capturas/atividade1_pmap.png) / [maps](linux_20261113T205043Z_3277/capturas/atividade1_maps.png) | Executada; interpretação em [observacoes.md](observacoes.md). Data/BSS sem separação exata por ELF |
| Atividade 2: `ps aux` e `top/htop`, estados | [ps aux](linux_20261113T205043Z_3277/ps_aux.txt), [estados](linux_20261113T205043Z_3277/estados.txt), [top](linux_20261113T205043Z_3277/top.txt) | Executada com `top`; transições reais R/S. Running/Ready não separados individualmente; D não observado |
| Atividade 2: `strace -c <comando>` | [strace.txt](linux_20261113T205043Z_3277/strace.txt), [captura](linux_20261113T205043Z_3277/capturas/atividade2_strace.png) | Executada: 769 syscalls; nenhuma restrição de ptrace observada |
| Atividade 3: `free -h`, `memstat`, `/proc/swaps` | [free antes](linux_20261113T205043Z_3277/free_antes.txt), [durante](linux_20261113T205043Z_3277/free_durante.txt), [depois](linux_20261113T205043Z_3277/free_depois.txt), [memstat](linux_20261113T205043Z_3277/memstat.txt), [swaps](linux_20261113T205043Z_3277/swaps_depois.txt) | Executada; `memstat` limitado aos processos acessíveis ao usuário runner |
| Atividade 3: carga real | [carga.txt](linux_20261113T205043Z_3277/carga.txt), [ps](linux_20261113T205043Z_3277/ps_carga.txt), [pmap](linux_20261113T205043Z_3277/pmap_carga.txt), [captura](linux_20261113T205043Z_3277/capturas/atividade3_carga.png) | Executada com limite seguro: 32 MiB, 20,002 s de espera medida, RSS antes/durante/depois |
| Atividade 3: carga elevada para observar início de swap e impacto de E/S | [contadores antes](linux_20261113T205043Z_3277/contadores_swap_antes.txt), [durante](linux_20261113T205043Z_3277/contadores_swap_durante.txt), [depois](linux_20261113T205043Z_3277/contadores_swap_depois.txt), [RAM/swap](linux_20261113T205043Z_3277/capturas/atividade3_ram.png) | **Não demonstrado:** aproximadamente 3 GiB de swap disponível, uso 0 e pswpin/pswpout 0. Sem carga perigosa; impactos discutidos apenas conceitualmente |
| Evidências reais, comandos e ambiente | [execução remota](https://github.com/henri16bit/trabalho-walter/actions/runs/43505223640), [comandos.tsv](linux_20261113T205043Z_3277/comandos.tsv), [sistema](linux_20261113T205043Z_3277/sistema.txt), [SHA256SUMS](linux_20261113T205043Z_3277/SHA256SUMS) | 35 comandos com código 0; 49 arquivos cobertos pelo manifesto e oito capturas reais de reexibição |
| Clareza do código e instruções (rubrica) | [README](../README.md), [roteiro](../laboratorio_linux.sh), [workflow](../.github/workflows/laboratorio-linux.yml) | Instalação Linux, interface, CLI, testes, repetição remota e limites documentados |

## Sete seções acadêmicas

O [relatorio.md](../relatorio.md) foi atualizado para o estado efetivamente observado. O enunciado exige a versão final em **PDF ou Google Docs**; o Markdown ainda precisa ser revisado pela dupla e exportado. Não foram inventados nomes, RAs, experiências pessoais ou divisão de atividades.

| Seção exigida | Evidência incorporada ao relatório | Pendência |
|---|---|---|
| 1. Capa e identificação | Ambiente Ubuntu e situação atual explícitos; revisão datada de 17/11/2026 | Nomes, RAs e data de entrega |
| 2. Fundamentação teórica | Contém memória virtual, MMU, tabela, faults e estados | Revisão acadêmica final pela dupla |
| 3. Metodologia/modelagem | Tkinter, CLI, histórico, funções responsáveis, 33+9 testes e captura Ubuntu com procedência | Revisão final da dupla; testes de widgets estão identificados como automatizados |
| 4. Resultados e comparação | Tabelas e gráficos ligados ao CSV e ao terminal da execução Ubuntu de 17/11 | Revisão final da dupla |
| 5. Análise GNU/Linux | Dados reais das três atividades, oito capturas com legendas e interpretação dos resultados | Swap sob pressão/impacto de E/S não demonstrados; limites de estados e permissões explícitos |
| 6. Conclusões e lições da dupla | Conclusões técnicas baseadas nas medições reais e nos limites do experimento | Acrescentar/revisar lições e divisão real das atividades pela dupla |
| 7. Referências | Fontes de SO, manuais, Python, GitHub e links das execuções utilizadas | Revisão da apresentação acadêmica final |

**Ainda pendente:** comprovar swap sob pressão e seu impacto de E/S, identificação e divisão real de papéis da dupla, revisão conjunta, exportação PDF/Google Docs e entrega ao professor. Um workflow bem-sucedido não elimina essas pendências. A portabilidade do simulador para Windows não invalida as evidências de sua execução no Ubuntu; o laboratório apresentado foi realizado em GNU/Linux.
