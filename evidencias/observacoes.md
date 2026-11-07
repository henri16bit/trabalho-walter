# Evidências do laboratório GNU/Linux

**Estado em 07/11/2026: execução pendente.** Esta pasta ainda não contém capturas ou saídas dos exercícios Linux. O arquivo `resultados/validacao_windows.txt` registra somente a validação do simulador e da sintaxe do roteiro no Windows.

Preencha os campos depois da execução real. O script `laboratorio_linux.sh` criará uma subpasta datada para cada coleta, preservando as anteriores.

## Ambiente

- Data, horário e fuso da execução: [preencher]
- Responsáveis: [preencher]
- Ambiente remoto/distribuição: [preencher]
- Versão do kernel: [preencher a partir de `uname -a`]
- Pasta da coleta: [preencher]
- Comandos ausentes, falhas de permissão ou outras restrições: [preencher]

## Atividade 1 — pmap e maps

- Comando de criação do processo e PID real: [preencher]
- Arquivos `pmap.txt` e `maps.txt`: [informar caminhos]
- Capturas reais: [informar caminhos]
- Região de código, faixa de endereços e permissões: [preencher]
- Região de dados, faixa de endereços e permissões: [preencher; indicar se a identificação é aproximada]
- Heap e stack observados: [preencher]
- Biblioteca compartilhada identificada e permissões: [preencher]
- Diferença entre memória virtual e residente observada: [preencher]

## Atividade 2 — processos e chamadas de sistema

- Arquivos e capturas reais: [informar caminhos]
- PID analisado, estado, CPU, RSS e VSZ: [preencher com valores e unidades]
- Relação do estado observado com Running, Ready ou Blocked: [explicar]
- Chamadas de sistema efetivamente listadas no strace e suas funções: [preencher]
- Restrições de strace/ptrace ou visibilidade de processos: [preencher, se houver]

## Atividade 3 — RAM e swap

- Arquivos e capturas reais: [informar caminhos]
- Carga executada ou dispensada? Motivo e saída de `carga.txt`: [preencher]
- Tamanho efetivamente alocado e duração: [preencher somente se a carga ocorreu]

| Momento | RAM total | RAM usada | RAM disponível | Swap total/usado | pswpin/pswpout |
|---|---|---|---|---|---|
| Antes | [preencher] | [preencher] | [preencher] | [preencher] | [preencher] |
| Durante, se houve carga | [preencher] | [preencher] | [preencher] | [preencher] | [preencher] |
| Depois | [preencher] | [preencher] | [preencher] | [preencher] | [preencher] |

- Interpretação do `memstat` como memória virtual: [preencher]
- `/proc/swaps` lista alguma área? [preencher]
- Houve movimentação de swap durante a observação? [preencher com evidências; considerar outros processos]
- Limitações do contêiner e diferenças entre memória visível e limite do cgroup: [preencher]

## Conferência antes da entrega

- [ ] As três atividades possuem saídas reais ou limitações explicitamente registradas.
- [ ] Capturas mostram comandos, resultados e PIDs legíveis.
- [ ] Não há valores copiados de exemplos ou capturas fictícias.
- [ ] As interpretações foram acrescentadas à seção 5 do relatório.
- [ ] A conclusão corresponde ao que foi efetivamente executado.
