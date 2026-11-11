"""Janela Tkinter/ttk. Os cálculos continuam em algoritmos.py."""

from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import filedialog, font, messagebox, ttk

from algoritmos import ALGORITMOS, validar_entradas
from graficos import salvar_csv, salvar_graficos
from main import MOLDURAS_PADRAO, OPERACOES_PADRAO, PAGINAS_PADRAO, executar_simulacoes

NOMES = ("FIFO", "LRU", "Segunda Chance (Clock)", "NRU")


def interpretar_entradas(texto_molduras, texto_paginas, texto_operacoes):
    try:
        molduras = int(texto_molduras)
    except ValueError:
        raise ValueError("Informe um número inteiro de molduras maior que zero.") from None
    try:
        paginas = [int(valor) for valor in texto_paginas.replace(",", " ").split()]
    except ValueError:
        raise ValueError("As páginas devem ser números inteiros não negativos.") from None
    operacoes = texto_operacoes.upper().replace(",", " ").split()
    validar_entradas(molduras, paginas, operacoes)
    return molduras, paginas, operacoes


def descrever_memoria(memoria):
    return "[" + ", ".join("-" if item is None else str(item["pagina"]) for item in memoria) + "]"


def criar_tabela(pai, colunas, larguras, altura=8):
    quadro = ttk.Frame(pai)
    quadro.columnconfigure(0, weight=1)
    quadro.rowconfigure(0, weight=1)
    tabela = ttk.Treeview(quadro, columns=colunas, show="headings", height=altura, selectmode="browse")
    for coluna, largura in zip(colunas, larguras):
        tabela.heading(coluna, text=coluna)
        tabela.column(coluna, width=largura, minwidth=largura, anchor="center")
    vertical = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
    horizontal = ttk.Scrollbar(quadro, orient="horizontal", command=tabela.xview)
    tabela.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    tabela.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    return quadro, tabela


class Interface:
    """Agrupa os widgets e o estado da janela, sem implementar políticas de memória."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.resultado = None
        self.comparacao = []
        self.passo = -1
        self.paginas = tk.StringVar(value=", ".join(map(str, PAGINAS_PADRAO)))
        self.operacoes = tk.StringVar(value=", ".join(OPERACOES_PADRAO))
        self.molduras = tk.StringVar(value="3")
        self.algoritmo = tk.StringVar(value=NOMES[0])
        self.resumo = [tk.StringVar(value="-") for _ in range(4)]
        self.etapa = tk.StringVar(value="Execute uma simulação para acompanhar os acessos.")
        self.aviso = tk.StringVar(value="Edite as entradas ou use a sequência pronta.")
        self.aviso_comparacao = tk.StringVar(value="A comparação usa as páginas e operações informadas acima.")

        raiz.title("Simulador de Gerenciamento de Memória Virtual")
        largura = min(1080, raiz.winfo_screenwidth() - 60)
        altura = min(740, raiz.winfo_screenheight() - 100)
        raiz.geometry(f"{largura}x{altura}")
        raiz.minsize(860, 620)
        font.nametofont("TkDefaultFont").configure(size=10)
        ttk.Style(raiz).configure("Treeview", rowheight=27)
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(1, weight=1)

        entradas = ttk.LabelFrame(raiz, text="Entradas compartilhadas pelas duas abas", padding=10)
        entradas.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 8))
        entradas.columnconfigure(1, weight=1)
        ttk.Label(entradas, text="Páginas:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.campo_paginas = ttk.Entry(entradas, textvariable=self.paginas)
        self.campo_paginas.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        ttk.Label(entradas, text="Operações:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.campo_operacoes = ttk.Entry(entradas, textvariable=self.operacoes)
        self.campo_operacoes.grid(row=1, column=1, sticky="ew")
        ttk.Label(entradas, text="L = leitura | E = escrita. Separe os valores por espaços ou vírgulas; uma operação por acesso.").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.abas = ttk.Notebook(raiz)
        self.abas.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self.aba_simulacao = ttk.Frame(self.abas, padding=10)
        self.aba_comparacao = ttk.Frame(self.abas, padding=10)
        self.abas.add(self.aba_simulacao, text="Simulação")
        self.abas.add(self.aba_comparacao, text="Comparação")
        self.montar_simulacao()
        self.montar_comparacao()
        ttk.Label(raiz, textvariable=self.aviso, wraplength=820).grid(
            row=2, column=0, sticky="w", padx=14, pady=(0, 8))

        for variavel in (self.paginas, self.operacoes):
            variavel.trace_add("write", self.entradas_alteradas)
        for variavel in (self.molduras, self.algoritmo):
            variavel.trace_add("write", self.limpar_simulacao)

    def montar_simulacao(self):
        aba = self.aba_simulacao
        aba.columnconfigure(0, weight=1)
        aba.rowconfigure(3, weight=1)
        controles = ttk.Frame(aba)
        controles.grid(row=0, column=0, sticky="ew")
        ttk.Label(controles, text="Algoritmo:").pack(side="left")
        self.seletor = ttk.Combobox(controles, textvariable=self.algoritmo, values=NOMES, state="readonly", width=23)
        self.seletor.pack(side="left", padx=(6, 18))
        ttk.Label(controles, text="Molduras:").pack(side="left")
        self.campo_molduras = ttk.Spinbox(controles, from_=1, to=9999, textvariable=self.molduras, width=6)
        self.campo_molduras.pack(side="left", padx=(6, 18))
        self.botao_executar = ttk.Button(controles, text="Executar simulação", command=self.executar)
        self.botao_executar.pack(side="left", padx=(0, 8))
        self.botao_reiniciar = ttk.Button(controles, text="Reiniciar", command=self.reiniciar)
        self.botao_reiniciar.pack(side="left")

        totais = ttk.LabelFrame(aba, text="Totais da simulação completa", padding=8)
        totais.grid(row=1, column=0, sticky="ew", pady=10)
        for indice, titulo in enumerate(("Acessos", "Page faults", "Swap outs", "Taxa de faltas")):
            totais.columnconfigure(indice, weight=1)
            quadro = ttk.Frame(totais)
            quadro.grid(row=0, column=indice, sticky="ew", padx=10)
            ttk.Label(quadro, text=titulo).pack(anchor="w")
            ttk.Label(quadro, textvariable=self.resumo[indice], font=("TkDefaultFont", 17, "bold")).pack(anchor="w")

        navegacao = ttk.Frame(aba)
        navegacao.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.botao_inicio = ttk.Button(navegacao, text="Estado inicial", command=lambda: self.selecionar_passo(-1), state="disabled")
        self.botao_anterior = ttk.Button(navegacao, text="Anterior", command=lambda: self.selecionar_passo(self.passo - 1), state="disabled")
        self.botao_proximo = ttk.Button(navegacao, text="Próximo", command=lambda: self.selecionar_passo(self.passo + 1), state="disabled")
        for botao in (self.botao_inicio, self.botao_anterior, self.botao_proximo):
            botao.pack(side="left", padx=(0, 6))
        ttk.Label(navegacao, text="Selecione uma linha ou use os botões para navegar.").pack(side="left", padx=8)

        tabelas = ttk.Frame(aba)
        tabelas.grid(row=3, column=0, sticky="nsew")
        tabelas.columnconfigure(1, weight=1)
        tabelas.rowconfigure(1, weight=1)
        ttk.Label(tabelas, text="RAM no passo selecionado").grid(row=0, column=0, sticky="w", pady=(0, 5))
        ttk.Label(tabelas, text="Histórico dos acessos").grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 5))
        quadro, self.ram = criar_tabela(tabelas, ("Moldura", "Página", "R", "M"), (70, 65, 35, 35))
        quadro.grid(row=1, column=0, sticky="nsew")
        quadro, self.historico = criar_tabela(
            tabelas, ("Acesso", "Página", "Operação", "Molduras", "Resultado", "Removida", "Swap out"),
            (55, 55, 70, 190, 95, 70, 70))
        quadro.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        self.historico.bind("<<TreeviewSelect>>", self.selecao_historico)
        ttk.Label(aba, textvariable=self.etapa, wraplength=820).grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Label(aba, text="R: referência (apenas Clock/NRU). M: modificação/Dirty. '-' indica ausência; leituras preservam M.").grid(
            row=5, column=0, sticky="w", pady=(4, 0))

    def montar_comparacao(self):
        aba = self.aba_comparacao
        aba.columnconfigure(0, weight=1)
        aba.rowconfigure(2, weight=1)
        ttk.Label(aba, text="Mesmas páginas e operações para todos; 3, 4, 8 e 16 molduras. O campo Molduras vale só para a simulação individual.",
                  wraplength=820).grid(row=0, column=0, sticky="w", pady=(0, 10))
        controles = ttk.Frame(aba)
        controles.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.botao_comparar = ttk.Button(controles, text="Comparar algoritmos", command=self.comparar)
        self.botao_salvar = ttk.Button(controles, text="Salvar CSV e PNG", command=self.salvar, state="disabled")
        self.botao_graficos = ttk.Button(controles, text="Visualizar gráficos", command=self.visualizar_graficos, state="disabled")
        for botao in (self.botao_comparar, self.botao_salvar, self.botao_graficos):
            botao.pack(side="left", padx=(0, 10))
        quadro, self.tabela_comparacao = criar_tabela(
            aba, ("Algoritmo", "Molduras", "Acessos", "Page faults", "Swap outs"), (220, 100, 100, 130, 130), altura=16)
        quadro.grid(row=2, column=0, sticky="nsew")
        ttk.Label(aba, textvariable=self.aviso_comparacao, wraplength=820).grid(row=3, column=0, sticky="w", pady=(8, 0))

    def limpar_simulacao(self, *_):
        self.resultado = None
        self.passo = -1
        self.historico.delete(*self.historico.get_children())
        self.ram.delete(*self.ram.get_children())
        for valor in self.resumo:
            valor.set("-")
        for botao in (self.botao_inicio, self.botao_anterior, self.botao_proximo):
            botao.configure(state="disabled")
        self.etapa.set("Execute uma simulação para acompanhar os acessos.")
        self.aviso.set("Configuração alterada. Execute novamente para atualizar os resultados.")

    def entradas_alteradas(self, *_):
        self.limpar_simulacao()
        self.comparacao = []
        self.tabela_comparacao.delete(*self.tabela_comparacao.get_children())
        self.botao_salvar.configure(state="disabled")
        self.botao_graficos.configure(state="disabled")
        self.aviso_comparacao.set("Entradas alteradas. Compare novamente antes de salvar ou visualizar.")

    def reiniciar(self):
        self.paginas.set(", ".join(map(str, PAGINAS_PADRAO)))
        self.operacoes.set(", ".join(OPERACOES_PADRAO))
        self.molduras.set("3")
        self.algoritmo.set(NOMES[0])
        self.aviso.set("Sequência padrão restaurada; resultados anteriores limpos.")
        self.campo_paginas.focus_set()

    def executar(self):
        try:
            molduras, paginas, operacoes = interpretar_entradas(self.molduras.get(), self.paginas.get(), self.operacoes.get())
            algoritmo = ALGORITMOS[NOMES.index(self.algoritmo.get())]
            resultado = algoritmo(molduras, paginas, operacoes, registrar_historico=True)
        except ValueError as erro:
            messagebox.showerror("Entrada inválida", str(erro), parent=self.raiz)
            return
        self.limpar_simulacao()
        self.resultado = resultado
        valores = (resultado["acessos"], resultado["page_faults"], resultado["swap_outs"],
                   f"{100 * resultado['page_faults'] / resultado['acessos']:.1f}%")
        for campo, valor in zip(self.resumo, valores):
            campo.set(str(valor))
        for indice, passo in enumerate(resultado["historico"]):
            self.historico.insert("", "end", iid=str(indice), values=(
                passo["acesso"], passo["pagina"], "Leitura" if passo["operacao"] == "L" else "Escrita",
                descrever_memoria(passo["memoria"]), "Page fault" if passo["page_fault"] else "Acerto",
                "-" if passo["removida"] is None else passo["removida"], "Sim" if passo["swap_out"] else "Não"))
        self.selecionar_passo(0)
        self.aviso.set(f"{resultado['algoritmo']} | {molduras} molduras | Os totais acima correspondem à execução completa.")

    def selecionar_passo(self, indice):
        if self.resultado is None:
            return
        passos = self.resultado["historico"]
        self.passo = max(-1, min(indice, len(passos) - 1))
        if self.passo < 0:
            self.historico.selection_remove(*self.historico.selection())
            memoria = [None] * self.resultado["molduras"]
            self.etapa.set("Estado inicial: memória vazia, nenhum acesso, nenhuma falta e nenhuma gravação.")
        else:
            passo = passos[self.passo]
            identificador = str(self.passo)
            if self.historico.selection() != (identificador,):
                self.historico.selection_set(identificador)
            self.historico.see(identificador)
            memoria = passo["memoria"]
            detalhe = "Page fault" if passo["page_fault"] else "Acerto"
            if passo["removida"] is not None:
                detalhe += f"; removida página {passo['removida']}"
            detalhe += "; swap out: " + ("sim" if passo["swap_out"] else "não")
            if passo["ponteiro"] is not None:
                detalhe += f"; próxima busca Clock: moldura {passo['ponteiro'] + 1}"
            self.etapa.set(f"Acesso {passo['acesso']}/{len(passos)}: {detalhe}. Acumulado: {passo['page_faults']} faltas, {passo['swap_outs']} gravações.")
        self.ram.delete(*self.ram.get_children())
        for indice, item in enumerate(memoria, 1):
            valores = (indice, "-", "-", "-") if item is None else (
                indice, item["pagina"], "-" if item["R"] is None else item["R"], item["M"])
            self.ram.insert("", "end", values=valores)
        self.botao_inicio.configure(state="normal")
        self.botao_anterior.configure(state="normal" if self.passo >= 0 else "disabled")
        self.botao_proximo.configure(state="normal" if self.passo < len(passos) - 1 else "disabled")

    def selecao_historico(self, _evento=None):
        selecao = self.historico.selection()
        if selecao and int(selecao[0]) != self.passo:
            self.selecionar_passo(int(selecao[0]))

    def comparar(self):
        try:
            _, paginas, operacoes = interpretar_entradas("1", self.paginas.get(), self.operacoes.get())
            resultados = executar_simulacoes(paginas, operacoes, MOLDURAS_PADRAO)
        except ValueError as erro:
            messagebox.showerror("Entrada inválida", str(erro), parent=self.raiz)
            return
        self.comparacao = resultados
        self.tabela_comparacao.delete(*self.tabela_comparacao.get_children())
        for linha in resultados:
            self.tabela_comparacao.insert("", "end", values=tuple(linha[chave] for chave in
                ("algoritmo", "molduras", "acessos", "page_faults", "swap_outs")))
        self.botao_salvar.configure(state="normal")
        self.botao_graficos.configure(state="normal")
        self.aviso_comparacao.set(f"16 resultados calculados com a mesma sequência de {len(paginas)} acessos. Escolha uma pasta para salvar CSV e PNG.")
        self.aviso.set("Comparação concluída. Nenhum arquivo foi substituído automaticamente.")

    def salvar(self):
        if not self.comparacao:
            return
        pasta = filedialog.askdirectory(parent=self.raiz, title="Pasta para salvar CSV e PNG", mustexist=False)
        if not pasta:
            return
        destino = Path(pasta)
        if any((destino / nome).exists() for nome in ("comparacao.csv", "page_faults.png", "swap_outs.png")):
            if not messagebox.askyesno("Substituir arquivos?", "Já existem resultados nesta pasta. Deseja substituir o CSV e os dois PNG?", parent=self.raiz):
                return
        try:
            salvar_csv(self.comparacao, destino)
            salvar_graficos(self.comparacao, destino)
        except (OSError, ImportError) as erro:
            messagebox.showerror("Falha ao salvar", str(erro), parent=self.raiz)
            return
        self.aviso_comparacao.set(f"CSV e dois PNG salvos em: {destino}")

    def visualizar_graficos(self):
        if not self.comparacao:
            return
        try:
            from PIL import Image, ImageTk
            imagens = []
            with tempfile.TemporaryDirectory(prefix="memoria_graficos_") as pasta:
                for caminho in salvar_graficos(self.comparacao, pasta):
                    with Image.open(caminho) as imagem:
                        imagem.thumbnail((min(960, self.raiz.winfo_screenwidth() - 80),
                                          min(570, self.raiz.winfo_screenheight() - 160)))
                        imagens.append(ImageTk.PhotoImage(imagem, master=self.raiz))
        except (OSError, ImportError) as erro:
            messagebox.showerror("Falha ao gerar gráficos", str(erro), parent=self.raiz)
            return
        janela = tk.Toplevel(self.raiz)
        janela.title("Gráficos da comparação")
        janela.imagens = imagens  # Mantém as imagens enquanto a janela estiver aberta.
        abas = ttk.Notebook(janela)
        abas.pack(fill="both", expand=True, padx=10, pady=10)
        for titulo, imagem in zip(("Page faults", "Swap outs"), imagens):
            painel = ttk.Frame(abas)
            ttk.Label(painel, image=imagem).pack()
            abas.add(painel, text=titulo)
        ttk.Label(janela, text="Use 'Salvar CSV e PNG' na aba Comparação para guardar os arquivos.").pack(pady=(0, 10))
        return janela


def main():
    try:
        raiz = tk.Tk()
    except tk.TclError as erro:
        print(f"Não foi possível abrir a janela: {erro}")
        print("Use uma sessão com ambiente gráfico; a versão de terminal continua disponível em main.py.")
        return 1
    Interface(raiz)
    raiz.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
