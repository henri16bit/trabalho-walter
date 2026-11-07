# Gerência de memória virtual — UNIRP

Trabalho de Sistemas Operacionais do curso de Análise e Desenvolvimento de Sistemas, professor Walter Gomes Pedroso Junior. Simulador de terminal em Python, com FIFO, LRU, Segunda Chance (Clock) e NRU.

Repositório público: [henri16bit/trabalho-walter](https://github.com/henri16bit/trabalho-walter).

## Comece por aqui — instalação para a dupla

Este projeto é executado pelo terminal. Você precisa baixar os arquivos, ter Python instalado e preparar as dependências no seu próprio computador. A pasta `.venv` da máquina em que o projeto foi desenvolvido **não acompanha o repositório**.

### 1. Instalar ou conferir o Python

Requer **Python 3.11 ou superior**. A versão efetivamente testada foi Python **3.12.14**, com matplotlib **3.11.2**; Python 3.12 é uma escolha para reproduzir esse ambiente. Outras versões compatíveis não foram testadas nesta entrega.

No Windows, obtenha o Python no [site oficial](https://www.python.org/downloads/windows/). Se usar o instalador tradicional e a opção aparecer, marque **Add python.exe to PATH**. Depois da instalação, feche e abra o PowerShell e confira:

```powershell
python --version
```

Se `python` não for encontrado ou abrir a Microsoft Store, teste `py -3 --version`. Se esse comando funcionar, use `py -3 -m venv .venv` no lugar de `python -m venv .venv` na etapa 3. Se nenhum funcionar, conclua a instalação do Python antes de continuar. Não baixe apenas o pacote embutível (*embeddable package*), pois esse não é o caminho de instalação deste roteiro.

### 2. Baixar o projeto e abrir a pasta certa

**Sem instalar Git:** abra o [repositório](https://github.com/henri16bit/trabalho-walter), clique em **Code → Download ZIP** e extraia o ZIP. Abra a pasta extraída que contém `main.py`, `README.md` e `requirements.txt`. Na barra de endereço do Explorador de Arquivos, digite `powershell` e pressione Enter para abrir o terminal nessa pasta. Não execute os arquivos de dentro do ZIP. Consulte também o [guia oficial de download do GitHub](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).

**Se já tiver Git instalado:** abra o PowerShell na pasta em que deseja guardar o projeto e execute:

```powershell
git clone https://github.com/henri16bit/trabalho-walter.git
cd trabalho-walter
```

Escolha uma das duas formas de download. Antes de continuar, execute `Get-ChildItem` e confira se `main.py` e `requirements.txt` aparecem na listagem.

### 3. Preparar as dependências no Windows

Na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

A instalação das dependências precisa de internet. A `.venv` é uma pasta com o ambiente Python do projeto; ela deve ser criada em cada computador. Não é necessário ativá-la com `Activate.ps1`, pois os comandos usam diretamente seu executável. Veja a [documentação oficial de venv](https://docs.python.org/3/library/venv.html).

### 4. Executar e conferir

```powershell
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe testes.py
```

O primeiro comando executa a sequência pronta com 3, 4, 8 e 16 molduras, mostra uma tabela e grava `resultados/comparacao.csv`, `resultados/page_faults.png` e `resultados/swap_outs.png`. Nenhuma janela gráfica é aberta; os PNG podem ser abertos normalmente no visualizador de imagens. O segundo comando executa os testes. A versão entregue obteve **25/25 testes passaram** no Windows; confira a saída real no seu computador.

Depois da primeira instalação, basta abrir a pasta e repetir os dois comandos acima. Não é necessário reinstalar as dependências a cada execução.

## Informar outra sequência

Para escolher as molduras ou informar uma sequência diferente:

```powershell
.\.venv\Scripts\python.exe main.py --molduras 3 4 --saida resultados/comparacao_3_4
.\.venv\Scripts\python.exe main.py --manual --molduras 3 4 8 16 --saida resultados/manual
```

No modo manual, digite, por exemplo:

```text
Páginas:   1, 2, 1, 3, 1, 2
Operações: E, L, L, E, L, L
```

Digite somente os valores, sem os rótulos `Páginas:` e `Operações:`. Espaços e vírgulas são aceitos como separadores; letras minúsculas também são aceitas. Cada página deve ser um inteiro não negativo. Deve haver exatamente uma operação por acesso: **L = leitura; E = escrita**. Molduras devem ser inteiros maiores que zero.

Cada execução substitui os três arquivos na pasta de saída escolhida. As tabelas do relatório correspondem à sequência pronta com **3, 4, 8 e 16** molduras. Para preservar as figuras dessa comparação, use `--saida resultados/manual` nos demais experimentos. Para restaurá-las, execute `main.py` sem argumentos.

## Executar o simulador em Linux

O simulador usa bibliotecas disponíveis no Windows e no Linux; sua execução em Linux ainda está pendente. Em um Linux remoto, com os arquivos já baixados e o terminal na pasta do projeto, confira `python3 --version` (deve ser 3.11 ou superior) e execute:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
.venv/bin/python testes.py
```

No Ubuntu/Debian, a criação de ambientes Python pode exigir o pacote `python3-venv`. O laboratório abaixo usa apenas Python padrão e comandos Linux, sem matplotlib.

## Se aparecer um erro

| Situação | O que conferir ou executar |
|---|---|
| `python` não é reconhecido ou abre a Microsoft Store | Confira a instalação e teste `py -3 --version`, conforme a etapa 1. |
| `.venv\Scripts\python.exe` não existe | Entre na pasta que contém `main.py` e crie o ambiente com `python -m venv .venv` ou `py -3 -m venv .venv`. |
| `main.py` ou `requirements.txt` não foi encontrado | O terminal está na pasta errada. Use `Get-ChildItem` e entre na pasta extraída que contém esses arquivos. |
| `No module named matplotlib` | Execute `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` e rode o programa com esse mesmo Python. |
| Não há versão compatível de matplotlib ou a instalação falha | Confira `.\.venv\Scripts\python.exe --version`, internet e a mensagem completa do pip. O projeto exige Python 3.11 ou superior. |
| O PowerShell bloqueia `Activate.ps1` | Use os comandos deste README com `.\.venv\Scripts\python.exe`; a ativação não é necessária. |
| Um comando Linux não funciona no Windows | Execute o laboratório no Linux remoto, seguindo a seção específica abaixo. |

Se precisar de ajuda, envie o comando executado, a mensagem completa de erro, o sistema operacional e a versão do Python. Não altere a versão de uma dependência ou os algoritmos antes de identificar a causa do erro.

## Texto pronto para pedir ajuda a uma IA

Abra a pasta do projeto na ferramenta de IA, ou forneça os arquivos solicitados por ela. Copie o texto abaixo e preencha os campos. Se a IA não puder acessar o repositório, envie pelo menos `README.md`, `requirements.txt`, `main.py`, `algoritmos.py`, `graficos.py` e `testes.py`; para o laboratório e o relatório, envie também `laboratorio_linux.sh` e `relatorio.md`.

```text
Estou trabalhando em dupla no projeto acadêmico de Sistemas Operacionais da
UNIRP, professor Walter Gomes Pedroso Junior.
Repositório: https://github.com/henri16bit/trabalho-walter

Meu sistema operacional: [preencher]
Versão do Python, se já estiver instalado: [preencher]
Meu objetivo agora: [instalar / executar / entender o código / resolver um erro /
realizar o laboratório GNU/Linux / preencher o relatório]
Comando executado e erro completo, se houver: [preencher]

Leia primeiro o README e os arquivos relacionados ao objetivo. Ajude-me com
passos curtos e comandos adequados ao meu terminal. No Windows, crie uma .venv
local e use .\.venv\Scripts\python.exe; instale requirements.txt, execute main.py
e testes.py. A versão entregue passou em 25 testes no Windows. Confira a saída
real antes de dizer que algo funcionou; se não puder executar, diga isso.

Mantenha o escopo acadêmico simples: Python pelo terminal, sem interface gráfica,
web, banco de dados ou funcionalidades extras. Os quatro algoritmos são FIFO,
LRU, Segunda Chance/Clock e NRU. No NRU, limpe R antes dos acessos 5, 9, 13...
e desempate pelo menor índice de moldura. Leitura não apaga Dirty; só a retirada
de uma página modificada conta como swap out. Preserve a independência dos estados.

Use --saida resultados/manual em experiências diferentes para preservar os
gráficos do relatório. Se mudar código ou entradas, explique a mudança e valide
os resultados; não atualize tabelas sem executar a simulação correspondente.

Os experimentos GNU/Linux ainda estão pendentes nesta entrega. Faça-os somente
em um Linux remoto disponível, seguindo laboratorio_linux.sh e o README.
Não instale WSL, Docker, máquina virtual ou distribuição Linux no meu Windows.
Não aumente a carga para forçar swap. Registre ferramentas ausentes, permissões
negadas ou ausência de swap como limitações. Nunca invente capturas, saídas,
resultados ou testes executados. As evidências reais vão para evidencias/.

Ajude-me a compreender os algoritmos e os resultados para apresentar o trabalho.
Antes de concluir, informe o que realmente executou e o que continua pendente.
```

## Regras do simulador

A sequência pronta possui 12 acessos:

```text
Páginas:   1 2 3 4 1 2 5 1 2 3 4 5
Operações: E L E L L E E L L E L L
```

Cada algoritmo começa com memória vazia e estado próprio. Uma página ausente gera um page fault; escrita marca M/Dirty e leitura preserva esse bit. Somente a retirada de uma página modificada conta como swap out. Não há gravação extra ao terminar a simulação.

No NRU, a classe é `2*R + M`. Os bits R são zerados antes dos acessos **5, 9, 13...**, incluindo acertos na contagem do intervalo. O acesso atual marca R novamente. M nunca é apagado pela limpeza. Empates são resolvidos pelo **menor índice de moldura**, começando em zero. A Segunda Chance usa seu próprio ponteiro circular e limpa R durante a busca por uma vítima.

Esses contadores representam um modelo didático. O programa não modifica a memória virtual nem o swap do sistema operacional.

## Arquivos

| Arquivo/pasta | Finalidade |
|---|---|
| `main.py` | Entrada, execução dos algoritmos e tabela no terminal |
| `algoritmos.py` | Quatro algoritmos e validação das entradas |
| `graficos.py` | CSV e dois gráficos PNG |
| `testes.py` | 25 testes funcionais e de validação |
| `requirements.txt` | Dependência matplotlib |
| `laboratorio_linux.sh` | Coleta dos três exercícios em GNU/Linux |
| `relatorio.md` | Relatório técnico com resultados reais do simulador |
| `resultados/` | CSV, gráficos e registro da validação no Windows |
| `evidencias/observacoes.md` | Campos para organizar as futuras evidências Linux |
| `.gitignore` | Exclui ambiente Python e caches do controle de versão |
| `.gitattributes` | Mantém quebras de linha LF, inclusive no script Bash, ao clonar o projeto |

Para entregar o projeto, inclua os fontes, documentos, resultados e evidências; exclua `.venv` e `__pycache__`.

## Laboratório em Linux remoto

**Situação atual:** os três exercícios Linux não foram executados. A sessão de desenvolvimento estava no Windows, sem terminal Linux remoto acessível. Não foram instalados WSL, Docker, máquina virtual ou distribuição Linux. A validação `bash -n` no Git Bash verifica somente a sintaxe; ela não equivale à realização do laboratório.

### 1. Abrir o ambiente

Use um Codespace disponível na sua conta ou um servidor Linux da instituição. No GitHub, envie os arquivos do projeto para um repositório, preferencialmente privado, sem `.venv` nem caches. Abra **Code → Codespaces** e crie ou abra o ambiente autorizado para esse repositório. Confira a franquia da conta antes de criar recursos. O terminal aberto no navegador executa no Linux remoto. Consulte a [documentação oficial do GitHub Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository).

No terminal remoto, dentro da pasta do projeto:

```bash
uname -s
python3 --version
command -v pmap ps top strace free memstat
```

`uname -s` deve identificar Linux. Se faltarem dependências, em Ubuntu/Debian e com permissão administrativa **no ambiente remoto**:

```bash
sudo apt-get update
sudo apt-get install -y python3 procps strace memstat
```

`pmap`, `ps`, `top` e `free` pertencem ao pacote `procps`; `strace` e `memstat` são pacotes separados. Se não houver `sudo`, se um pacote não estiver nos repositórios disponíveis ou se uma ferramenta for bloqueada, registre a mensagem e solicite o recurso ao responsável pelo ambiente. `htop` é opcional; este roteiro usa `top`.

### 2. Fazer a coleta automática

```bash
bash laboratorio_linux.sh
```

O script cria uma pasta nova `evidencias/linux_DATA_PID/`, com data UTC no nome, e salva as saídas reais, erros e códigos de saída. Ele cria seus próprios processos e os encerra ao sair. Não instala pacotes nem habilita swap. Ao final, consulte `execucao.txt`; uma ferramenta ausente não significa que sua atividade foi realizada.

O teste de carga usa **no máximo 32 MiB durante 20 segundos**, limitado também a 10% da margem observada. Ele consulta `MemAvailable` e os limites visíveis de cgroup v2, exige margem mínima de 256 MiB e limita o espaço de endereçamento do processo. Se não conseguir verificar os limites, estiver em cgroup v1 ou houver pouca margem, registra a limitação e dispensa a carga. O objetivo é observar uma alocação pequena; a medição é momentânea e o restante do ambiente pode continuar consumindo memória.

Não aumente a carga para provocar swap. A ausência de swap ou a ausência de movimentação durante uma carga pequena deve ser relatada como resultado/limitação. `free` pode refletir uma visão mais ampla que o limite do contêiner; por isso o script também consulta o cgroup. A descrição de `memory.current`, `memory.max` e `memory.high` está na [documentação do kernel](https://docs.kernel.org/admin-guide/cgroup-v2.html).

### 3. Comandos para observar e capturar as telas

O script já faz a coleta em texto. Para obter capturas reais interativas, execute também os comandos a seguir, no mesmo terminal Linux. Mantenha visíveis o comando, seu resultado e o PID. O processo de demonstração dura 180 segundos; se ele terminar, inicie outro e use o novo PID.

**Atividade 1 — mapa de memória:**

```bash
python3 -u -c 'import os, time; dados = bytearray(1024 * 1024); print("PID:", os.getpid()); time.sleep(180)' &
pid_teste=$!
echo "$pid_teste"
pmap -x "$pid_teste"
cat "/proc/$pid_teste/maps"
```

Relacione código, dados, heap, stack e bibliotecas aos endereços e permissões. A seção 5.1 do relatório orienta a interpretação; não classifique toda região anônima como heap.

**Atividade 2 — processos e chamadas de sistema:**

```bash
ps aux
ps -p "$pid_teste" -o pid,ppid,stat,pcpu,pmem,rss,vsz,comm
top -p "$pid_teste"
```

No `top`, pressione `q` para sair. Depois:

```bash
strace -c python3 -c 'from pathlib import Path; print("Bytes lidos:", len(Path("/proc/meminfo").read_bytes()))'
kill "$pid_teste"
wait "$pid_teste" 2>/dev/null
```

O `kill` encerra apenas o processo de demonstração cujo PID foi guardado. Interprete os estados, CPU, RSS e VSZ com a seção 5.2 do relatório. Se `strace` retornar erro de `ptrace` ou permissão, salve o erro como limitação; não substitua por uma saída esperada.

**Atividade 3 — RAM e swap:**

```bash
free -h
memstat
cat /proc/swaps
```

Use os arquivos `free_antes.txt`, `free_durante.txt` e `free_depois.txt` gerados pelo script para comparar a carga controlada; o arquivo intermediário só existe se o processo de carga permanecer ativo. Confira em `carga.txt` se a alocação realmente ocorreu. O script também registra `pswpin` e `pswpout` de `/proc/vmstat`, contadores cumulativos de movimentação de páginas; alterações podem envolver outros processos. `memstat` informa memória **virtual**, conforme seu [manual](https://manpages.debian.org/trixie/memstat/memstat.1.en.html).

### 4. Concluir as evidências

1. Salve capturas reais em `evidencias/` com nomes como `atividade1_pmap.png`, `atividade1_maps.png`, `atividade2_ps_top.png`, `atividade2_strace.png` e `atividade3_memoria.png`.
2. Preencha [evidencias/observacoes.md](evidencias/observacoes.md) e a seção 5 de [relatorio.md](relatorio.md), citando os arquivos efetivamente obtidos.
3. Se `/proc/swaps` apresentar apenas o cabeçalho, registre ausência de swap. Se houver swap mas os contadores não mudarem, registre ausência de movimentação observada. Não afirme que toda alocação necessariamente utiliza swap.
4. Baixe a pasta de evidências para juntar à entrega. Encerre o Codespace após o uso, pela área de gerenciamento do GitHub.

## Validação e entrega do relatório

Foram executados **25/25 testes com sucesso** no Windows, inclusive contadores por acesso, classes NRU, referência do Clock, Dirty, independência de estado, entradas inválidas, leitura do CSV e decodificação dos PNG. Veja [resultados/validacao_windows.txt](resultados/validacao_windows.txt). As duas imagens também foram inspecionadas visualmente. A sintaxe do Bash passou e a proteção contra execução fora do Linux foi verificada. **Não há evidências de execução dos experimentos Linux nem de execução do simulador nesse sistema.**

O relatório está em Markdown, com tabelas e links relativos para as figuras. Preencha os nomes da dupla e conclua o laboratório antes da entrega final. Para transferir ao Google Docs, copie o texto e as tabelas e insira os dois PNG em suas posições; revise a paginação e exporte o documento em PDF. Alternativamente, use um editor que exporte Markdown com imagens para PDF. O PDF ainda não foi gerado ou revisado.
