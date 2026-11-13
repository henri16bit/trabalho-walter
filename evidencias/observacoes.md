# Registro técnico do laboratório GNU/Linux

As três atividades foram executadas em um Ubuntu remoto, incluindo a carga real de memória. **Não houve movimentação de swap**: a exigência de observar E/S de swap sob pressão elevada não foi demonstrada. Este registro acompanha as evidências; o relatório acadêmico não foi editado, conforme a orientação mais recente.

## Origem e integridade

- Coleta principal: [linux_20261113T205043Z_3277](linux_20261113T205043Z_3277/), iniciada em **13/11/2026, 20:50:43 UTC (17:50:43 em São Paulo)**.
- [Execução 43505223640](https://github.com/henri16bit/trabalho-walter/actions/runs/43505223640), commit `0d9b57c6f068a195ba1c7160b805e49a7428b6bd`.
- [comandos.tsv](linux_20261113T205043Z_3277/comandos.tsv): 35 comandos, todos com saída 0; [carga_exit_code.txt](linux_20261113T205043Z_3277/carga_exit_code.txt): processo da carga também retornou 0.
- [execucao.txt](linux_20261113T205043Z_3277/execucao.txt) preserva a transcrição. [SHA256SUMS](linux_20261113T205043Z_3277/SHA256SUMS) cobre 49 arquivos brutos/capturas, conferidos após o download; não inclui a si próprio.
- Artefato GitHub `14075049632`; SHA-256 do ZIP: `7af70c745b8cb550815846fdf3fb4ced239787a4cec426b30ca1637f6881f93e`.
- A [primeira coleta](linux_20261113T204746Z_3148/) foi preservada: [execução 43504780085](https://github.com/henri16bit/trabalho-walter/actions/runs/43504780085). A segunda ampliou o terminal para manter os cabeçalhos nas capturas de mapas. Não misturar os PIDs e valores das duas execuções.

As oito capturas principais foram obtidas por `scrot` em um **xterm real sob Xvfb no Ubuntu**, reexibindo os arquivos coletados. Não são novas medições ao vivo, imagens de IA ou prova de interação manual. Os recortes textuais de `top` e `memstat` estão identificados na tela; as saídas completas permanecem nos TXT.

## Ambiente e revisão do roteiro

| Item | Observação / fonte |
|---|---|
| Distribuição | Ubuntu 24.04.5 LTS, [distribuicao.txt](linux_20261113T205043Z_3277/distribuicao.txt) |
| Kernel | `7.0.0-1017-azure`, x86_64, [sistema.txt](linux_20261113T205043Z_3277/sistema.txt) |
| Ambiente | Runner remoto, virtualização `microsoft`, [virtualizacao.txt](linux_20261113T205043Z_3277/virtualizacao.txt) |
| CPU | 4 CPUs lógicas visíveis, [cpu.txt](linux_20261113T205043Z_3277/cpu.txt) |
| Ferramentas | Python 3.12.3; procps 4.0.4; strace 6.8; memstat 1.1, [versoes.txt](linux_20261113T205043Z_3277/versoes.txt) |
| Página | 4096 bytes, [pagina_bytes.txt](linux_20261113T205043Z_3277/pagina_bytes.txt) |
| Cgroup | v2; `memory.max` e `memory.high` = `max` nos dois níveis consultados, [carga.txt](linux_20261113T205043Z_3277/carga.txt) |

O roteiro existente teve a sintaxe Bash e dos trechos Python conferida. Foram acrescentados identificação do ambiente, códigos de saída, amostras de estados, `free -b` e RSS antes/durante/depois. A demonstração alterna até cinco ciclos de 1 segundo de computação e 2 de espera, com `RLIMIT_CPU=8 s`; foi encerrada pela coleta após o quarto ciclo. O roteiro encerra somente seus próprios processos.

A carga permanece limitada a **32 MiB por 20 segundos**, também a 10% da margem verificada, com mínimo de 256 MiB disponíveis e `RLIMIT_AS=256 MiB`. Sem limites verificáveis de cgroup v2, a carga é dispensada. Não se configura swap nem se instalam recursos Linux no Windows. O workflow tem timeout.

## Atividade 1: segmentos e permissões

Foram executados `pmap -x 3311` e `cat /proc/3311/maps`: [pmap.txt](linux_20261113T205043Z_3277/pmap.txt) e [maps.txt](linux_20261113T205043Z_3277/maps.txt). Capturas: [pmap](linux_20261113T205043Z_3277/capturas/atividade1_pmap.png) e [maps](linux_20261113T205043Z_3277/capturas/atividade1_maps.png).

| Região | Intervalo virtual observado | Interpretação |
|---|---|---|
| Código | `00420000-00703000` | `r-xp`, código do interpretador `/usr/bin/python3.12` |
| Dados | `00a29000-00ba7000` | `rw-p`, região gravável associada ao executável |
| Heap | `083a4000-084a3000` | `rw-p`, identificado como `[heap]` |
| Stack | `7ffd29a34000-7ffd29a56000` | `rw-p`, pilha principal `[stack]` |
| Biblioteca libc | `7fba7f028000-7fba7f1b1000` | `r-xp`, região executável de `libc.so.6`; o mesmo arquivo tem outras regiões de leitura/dados |

`r`, `w` e `x` indicam leitura, escrita e execução; `p` indica mapeamento privado e `s`, compartilhado. Os endereços são virtuais e podem mudar em outra execução. A identificação de dados baseia-se no mapeamento gravável; não foram examinadas as seções ELF para separar `.data` e `.bss`. Regiões anônimas fora de `[heap]` também podem conter alocações dinâmicas. Referência: [proc_pid_maps(5)](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html).

O `pmap -x` totalizou **19.524 KiB virtuais, 11.444 KiB residentes e 4.888 KiB Dirty**. Nem todo espaço virtual estava residente. Dirty descreve páginas modificadas; não é contador de swap out e não comprova gravação em disco. Referência: [pmap(1)](https://man7.org/linux/man-pages/man1/pmap.1.html).

## Atividade 2: processos e chamadas de sistema

Saídas completas: [ps aux](linux_20261113T205043Z_3277/ps_aux.txt), [ps do processo](linux_20261113T205043Z_3277/ps_processo.txt), [12 amostras de estados](linux_20261113T205043Z_3277/estados.txt), [5 amostras de top](linux_20261113T205043Z_3277/top.txt), [strace](linux_20261113T205043Z_3277/strace.txt). Capturas: [estados](linux_20261113T205043Z_3277/capturas/atividade2_estados.png), [top](linux_20261113T205043Z_3277/capturas/atividade2_top.png) e [strace](linux_20261113T205043Z_3277/capturas/atividade2_strace.png).

O PID **3311** passou de `S` às 20:50:44.426 UTC para `R` às 20:50:46.459 e voltou a `S` às 20:50:47.476. Em espera, `WCHAN=hrtimer_nanosleep`, compatível com o temporizador do programa. `S` é espera interrompível; `R` abrange execução e prontidão. **Não foi possível separar Running de Ready por essas amostras, nem foi demonstrado estado `D` de espera não interrompível.** Referência: [ps(1)](https://man7.org/linux/man-pages/man1/ps.1.html).

A primeira amostra de `ps` apresentou RSS **11.444 KiB**, VSZ **19.520 KiB** e `%CPU=93,5`, mesmo estando em `S`: o percentual considera a vida do processo. No `top`, houve `R` com 64,0% no intervalo, depois `S` com 35,6% e 0,0%. Estado instantâneo e utilização no intervalo são medidas diferentes. Foi utilizado `top -b -n 5 -d 1`, não uma sessão humana interativa. Referência: [top(1)](https://man7.org/linux/man-pages/man1/top.1.html).

O `strace -c` iniciou e rastreou um Python que leu `/proc/meminfo`: **1.674 bytes**, **769 chamadas**, **90 retornos de erro de syscalls**, soma de tempos **0,003841 s**, código final do comando **0**. Não houve bloqueio de ptrace.

| Chamada | Quantidade | Função |
|---|---:|---|
| `newfstatat` | 211 | Consultar metadados |
| `read` | 72 | Ler descritores |
| `openat` | 59 | Abrir arquivos |
| `mmap` | 29 | Criar mapeamentos virtuais |
| `brk` | 15 | Ajustar o limite da área de dados |
| `close` | 53 | Fechar descritores |

O resumo inclui inicialização e importações do Python, não apenas a leitura final. Os 90 retornos de erro não significam 90 falhas do laboratório. Sem argumentos e errno de cada chamada, não se atribui causa específica a esses retornos. Os tempos não constituem benchmark. Referência: [strace(1)](https://man7.org/linux/man-pages/man1/strace.1.html).

## Atividade 3: RAM, carga e swap

Saídas: [carga](linux_20261113T205043Z_3277/carga.txt), [pmap da carga](linux_20261113T205043Z_3277/pmap_carga.txt), [ps da carga](linux_20261113T205043Z_3277/ps_carga.txt), [memstat antes](linux_20261113T205043Z_3277/memstat.txt), [memstat durante](linux_20261113T205043Z_3277/memstat_durante.txt), [memstat depois](linux_20261113T205043Z_3277/memstat_depois.txt). Capturas: [RAM/swap](linux_20261113T205043Z_3277/capturas/atividade3_ram.png), [carga](linux_20261113T205043Z_3277/capturas/atividade3_carga.png), [memstat](linux_20261113T205043Z_3277/capturas/atividade3_memstat.png).

A margem inicial considerada foi **15.045 MiB**. O PID **3398** alocou e tocou **32 MiB**, esperou **20,002 s** e liberou a alocação. Seu RSS foi **12.004 → 44.780 → 12.008 KiB**. O aumento de 32.776 KiB é compatível com 32.768 KiB alocados mais pequenas diferenças do próprio processo. Isso comprova a carga independentemente da oscilação global do sistema.

Valores abaixo convertidos de `free -b` por divisão por 1.048.576 e arredondados para três casas. Os arquivos `free_antes.txt`, `free_durante.txt` e `free_depois.txt` preservam também `free -h`; são chamadas consecutivas, não amostras simultâneas.

| Momento / fonte | RAM total (MiB) | Usada (MiB) | Disponível (MiB) | Swap usado | pswpin / pswpout |
|---|---:|---:|---:|---:|---|
| [Antes](linux_20261113T205043Z_3277/free_bytes_antes.txt) | 15.982,910 | 932,090 | 15.050,820 | 0 B | 0 / 0 |
| [Durante](linux_20261113T205043Z_3277/free_bytes_durante.txt) | 15.982,910 | 973,629 | 15.009,281 | 0 B | 0 / 0 |
| [Depois](linux_20261113T205043Z_3277/free_bytes_depois.txt) | 15.982,910 | 945,250 | 15.037,660 | 0 B | 0 / 0 |

O aumento global de aproximadamente **41,539 MiB** supera a carga de 32 MiB: outros processos e caches também variaram. Não atribuir toda a diferença à carga. `available` estima memória disponível para novas aplicações, enquanto `free` conta memória livre. Referência: [free(1)](https://man7.org/linux/man-pages/man1/free.1.html).

O `memstat` retornou 0, mas sua visão é limitada aos processos acessíveis ao usuário `runner`, pois não foi usado como root. O total antes da carga, **550.118.920k**, é memória **virtual**, não RAM ocupada. Durante a carga, indicou **37.988k** privados no PID 3398, separadamente dos objetos compartilhados; esse número não é diretamente equivalente ao RSS de 44.780 KiB. A ferramenta abrevia caminhos longos na saída padrão. Referência: [memstat(1)](https://manpages.debian.org/trixie/memstat/memstat.1.en.html).

[swaps_depois.txt](linux_20261113T205043Z_3277/swaps_depois.txt) lista `/swapfile`, tipo `file`, **3.145.724 KiB**, uso 0 e prioridade -1. `free -b` informa **3.221.221.376 bytes**, aproximadamente 3 GiB. A área já existia no runner. Os contadores [antes](linux_20261113T205043Z_3277/contadores_swap_antes.txt), [durante](linux_20261113T205043Z_3277/contadores_swap_durante.txt) e [depois](linux_20261113T205043Z_3277/contadores_swap_depois.txt) ficaram em zero.

**Limitação:** não houve início de uso de swap nem medição de impacto de E/S por paginação. A memória disponível permaneceu ampla. Transferências ao armazenamento podem acrescentar latência e disputar E/S, mas isso é discussão conceitual, não medição desta coleta. Os contadores são globais do kernel. Referências: [proc_swaps(5)](https://man7.org/linux/man-pages/man5/proc_swaps.5.html) e [proc_vmstat(5)](https://man7.org/linux/man-pages/man5/proc_vmstat.5.html).

## Limitações e pendências

- Nenhuma ferramenta exigida esteve ausente ou retornou falha nesta coleta. A abrangência do `memstat` é limitada pelas permissões do usuário.
- Cgroup v2 estava acessível, sem teto numérico nos níveis lidos; a carga usou `MemAvailable` e seu próprio limite virtual. Isso não autoriza cargas maiores em outro ambiente. Referência: [documentação do kernel](https://docs.kernel.org/admin-guide/cgroup-v2.html).
- Running/Ready não foram distinguidos individualmente; as transições observadas foram `R`/`S`. Estado `D` não foi demonstrado.
- O requisito de observar swap sob carga elevada permanece não demonstrado. Não aumentar a carga automaticamente para preencher essa lacuna.
- O relatório acadêmico e sua exportação não foram alterados. A [matriz de requisitos](REQUISITOS.md) separa essas pendências das evidências técnicas.
