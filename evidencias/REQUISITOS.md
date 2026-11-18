# Requisitos e evidências

Conferência do enunciado do professor Walter, datado de 26/10/2026, páginas 1–3. Atualizada em **18/11/2026**, com validação Ubuntu do simulador, laboratório de 13/11 e **complemento real de swap de 17/11 sob pressão isolada em cgroup**. O [relatório](../relatorio.md) contém os nomes e RAs informados pela dupla e as evidências de cada etapa. Algoritmos e interface foram preservados.

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
| Atividade 3: carga elevada para observar início de swap e impacto de E/S | [Execução real de 17/11](https://github.com/henri16bit/trabalho-walter/actions/runs/44182556307), [CSV](swap_linux_20261117T214237Z_3360/comparacao.csv), [amostras](swap_linux_20261117T214237Z_3360/pressao_amostras.jsonl), [print resumo](swap_linux_20261117T214237Z_3360/capturas/swap_resumo.png), [RAM/swap](swap_linux_20261117T214237Z_3360/capturas/swap_ram.png), [análise](swap_observacoes.md) | **Demonstrado sob limite de RAM no cgroup:** mesma carga de 128 MiB, controle com 256 MiB de RAM e pressão com 64 MiB. Swap até 127,996 MiB; 12.832 major faults nas releituras e E/S de bloco registrada. Sem OOM ou esgotamento global. Tempos não são benchmark universal |
| Evidências reais, comandos e ambiente | [execução remota](https://github.com/henri16bit/trabalho-walter/actions/runs/43505223640), [comandos.tsv](linux_20261113T205043Z_3277/comandos.tsv), [sistema](linux_20261113T205043Z_3277/sistema.txt), [SHA256SUMS](linux_20261113T205043Z_3277/SHA256SUMS) | 35 comandos com código 0; 49 arquivos cobertos pelo manifesto e oito capturas reais de reexibição |
| Evidências do complemento de swap | [60 comandos](swap_linux_20261117T214237Z_3360/comandos.tsv), [origem](swap_linux_20261117T214237Z_3360/origem.json), [SHA256SUMS](swap_linux_20261117T214237Z_3360/SHA256SUMS), [proveniência](swap_linux_20261117T214237Z_3360/proveniencia.json) | 60 comandos com saída 0; dois processos encerrados normalmente; 75 arquivos conferidos, incluindo três capturas reais de reexibição |
| Clareza do código e instruções (rubrica) | [README](../README.md), [roteiro](../laboratorio_linux.sh), [workflow](../.github/workflows/laboratorio-linux.yml) | Instalação Linux, interface, CLI, testes, repetição remota e limites documentados |

## Sete seções acadêmicas

O [relatorio.md](../relatorio.md) foi atualizado para o estado efetivamente observado, com **Henrique Caliari Fuzeto — RA 20252889** e **Murillo Alves Augusto — RA 20251873**. O enunciado exige a versão final em **PDF ou Google Docs**; o Markdown ainda precisa ser revisado pela dupla e exportado. Não foram inventadas experiências pessoais ou divisão de atividades.

| Seção exigida | Evidência incorporada ao relatório | Pendência |
|---|---|---|
| 1. Capa e identificação | Nomes e RAs fornecidos pela dupla, ambiente Ubuntu e revisão de 18/11/2026 | Data efetiva de entrega |
| 2. Fundamentação teórica | Contém memória virtual, MMU, tabela, faults e estados | Revisão acadêmica final pela dupla |
| 3. Metodologia/modelagem | Tkinter, CLI, histórico, funções responsáveis, 33+9 testes e captura Ubuntu com procedência | Revisão final da dupla; testes de widgets estão identificados como automatizados |
| 4. Resultados e comparação | Tabelas e gráficos ligados ao CSV e ao terminal da execução Ubuntu de 17/11 | Revisão final da dupla |
| 5. Análise GNU/Linux | Três atividades, oito capturas iniciais e três capturas do complemento de swap, com interpretação | Revisão acadêmica; limites de cgroup, medição, estados e permissões explícitos |
| 6. Conclusões e lições da dupla | Conclusões técnicas baseadas nas medições reais e nos limites do experimento | Acrescentar/revisar lições e divisão real das atividades pela dupla |
| 7. Referências | Fontes de SO, manuais, Python, GitHub e links das execuções utilizadas | Revisão da apresentação acadêmica final |

**Ainda pendente:** divisão real de papéis e lições da dupla, revisão conjunta, data efetiva de entrega, exportação PDF/Google Docs e entrega ao professor. Swap e E/S foram observados sob pressão de memória localizada no cgroup; as limitações do experimento devem acompanhar a apresentação. A portabilidade do simulador para Windows não invalida as evidências de sua execução no Ubuntu; o laboratório apresentado foi realizado em GNU/Linux.
