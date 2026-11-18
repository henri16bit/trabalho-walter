"""Gera o Word editável a partir do relatório e das imagens originais.

Dependências para esta ferramenta editorial: python-docx e Pillow.
Não é necessário executá-la para usar o simulador.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import re
from pathlib import Path
from urllib.parse import quote

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REF = "891c6b05621afc2c57655ceeba0819d3cb4c4067"
INLINE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|`([^`]+)`|\*([^*]+)\*")


def url_for(path: str, ref: str) -> str:
    if re.match(r"https?://", path):
        return path
    target = (ROOT / path).resolve()
    target.relative_to(ROOT)
    branch = "main" if path in ("README.md", "evidencias/REQUISITOS.md") else ref
    kind = "tree" if target.is_dir() else "blob"
    return f"https://github.com/henri16bit/trabalho-walter/{kind}/{branch}/{quote(path, safe='/')}"


def hyperlink(paragraph, label, target):
    relationship = paragraph.part.relate_to(
        target,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), relationship)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1F4E79")
    props.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    props.append(underline)
    run.append(props)
    text = OxmlElement("w:t")
    text.text = label.replace("`", "")
    run.append(text)
    link.append(run)
    paragraph._p.append(link)


def inline(paragraph, text, ref):
    start = 0
    for match in INLINE.finditer(text):
        if match.start() > start:
            paragraph.add_run(text[start:match.start()])
        label, target, bold, code, italic = match.groups()
        if label is not None:
            hyperlink(paragraph, label, url_for(target, ref))
        else:
            run = paragraph.add_run(bold or code or italic)
            if bold is not None:
                run.bold = True
            elif code is not None:
                run.font.name = "Courier New"
                run.font.size = Pt(9)
            else:
                run.italic = True
        start = match.end()
    if start < len(text):
        paragraph.add_run(text[start:])


def page_setup(section, landscape=False, appendix=False):
    section.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    section.page_width = Cm(29.7 if landscape else 21)
    section.page_height = Cm(21 if landscape else 29.7)
    section.top_margin = Cm(2 if appendix else 3)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2 if appendix else 3)
    section.right_margin = Cm(2)
    section.header_distance = Cm(1)
    section.footer_distance = Cm(1)


def clean_heading(text):
    text = text.replace("GNU/Linux", "GNU Linux")
    text = re.sub(r"[.,:;—–/()]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def set_styles(document):
    styles = document.styles
    for name in ("Normal", "Title", "Subtitle", "Heading 1", "Heading 2", "Heading 3", "Caption"):
        styles[name].font.name = "Times New Roman"
        styles[name].font.color.rgb = RGBColor(0, 0, 0)
    normal = styles["Normal"]
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.widow_control = True
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for name, size in (("Title", 20), ("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 12)):
        style = styles[name]
        style.font.size = Pt(size)
        style.font.bold = True
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(16)
        style.paragraph_format.space_after = Pt(10)
        style.paragraph_format.line_spacing = 1.15
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    styles["Caption"].font.size = Pt(10)
    styles["Caption"].font.italic = False
    styles["Caption"].paragraph_format.line_spacing = 1.15
    styles["Caption"].paragraph_format.space_after = Pt(8)
    styles["Caption"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    defaults = styles.element.find(qn("w:docDefaults"))
    if defaults is not None:
        for lang in defaults.iter(qn("w:lang")):
            lang.set(qn("w:val"), "pt-BR")


def make_table(document, lines, ref):
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows.pop(1)
    count = len(rows[0])
    table = document.add_table(rows=1, cols=count)
    table.autofit = False
    widths = {
        2: [3.3, 12.7], 3: [3.3, 2.4, 10.3], 4: [1.5, 1.0, 1.0, 12.5],
        5: [4.0, 3.0, 3.0, 3.0, 3.0], 6: [2.2, 2.7, 2.4, 3.2, 2.1, 3.4],
        7: [1.5, 1.5, 2.0, 2.75, 2.75, 2.75, 2.75],
    }[count]
    if rows[0][0] == "Informação da coleta":
        widths = [4.2, 11.8]
    if rows[0][0] == "Região":
        widths = [2.5, 5.6, 7.9]
    if rows[0][0] == "Medida":
        widths = [6.6, 4.3, 5.1]
    for column, width in zip(table.columns, widths):
        column.width = Cm(width)
    props = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement("w:" + edge)
        for key, value in (("val", "single"), ("sz", "4"), ("color", "D9D9D9")):
            border.set(qn("w:" + key), value)
        borders.append(border)
    props.append(borders)
    margins = OxmlElement("w:tblCellMar")
    for edge in ("top", "bottom", "left", "right"):
        margin = OxmlElement("w:" + edge)
        margin.set(qn("w:w"), "85" if edge in ("top", "bottom") else "100")
        margin.set(qn("w:type"), "dxa")
        margins.append(margin)
    props.append(margins)
    for index, row_values in enumerate(rows):
        row = table.rows[0] if index == 0 else table.add_row()
        trpr = row._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
        if index == 0:
            trpr.append(OxmlElement("w:tblHeader"))
        for j, (cell, text) in enumerate(zip(row.cells, row_values)):
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if count >= 4 and j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            if count == 4 and j == 3:
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            inline(p, text, ref)
            for run in p.runs:
                run.font.size = Pt(10)
                if index == 0:
                    run.bold = True
            if index == 0:
                fill = OxmlElement("w:shd")
                fill.set(qn("w:fill"), "E7E6E6")
                cell._tc.get_or_add_tcPr().append(fill)
    after = document.add_paragraph()
    after.paragraph_format.space_after = Pt(3)
    after.paragraph_format.line_spacing = 0.2
    after.add_run().font.size = Pt(2)


def cover(document):
    section = document.sections[0]
    section.different_first_page_header_footer = True
    for text in ("CENTRO UNIVERSITÁRIO DE RIO PRETO", "UNIRP", "Análise e Desenvolvimento de Sistemas", "Sistemas Operacionais"):
        p = document.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(3)
    p = document.add_paragraph("Henrique Caliari Fuzeto — RA 20252889\nMurillo Alves Augusto — RA 20251873")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(56)
    p.paragraph_format.space_after = Pt(58)
    p = document.add_paragraph("Gerência de memória virtual\npaginação e monitoramento\nno GNU Linux", "Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(50)
    p = document.add_paragraph("Trabalho semestral apresentado à disciplina de Sistemas Operacionais do curso de Análise e Desenvolvimento de Sistemas.\n\nProfessor Walter Gomes Pedroso Junior")
    p.paragraph_format.left_indent = Cm(7)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(42)
    p = document.add_paragraph("São José do Rio Preto\n18 de novembro de 2026")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def headers(document):
    section = document.sections[0]
    p = section.header.paragraphs[0]
    p.text = "UNIRP    |    Sistemas Operacionais    |    GNU/Linux"
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(0)
    for run in p.runs:
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0, 0, 0)
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    p._p.append(field)


def build(output: Path, ref: str):
    lines = (ROOT / "relatorio.md").read_text(encoding="utf-8").splitlines()
    document = Document()
    set_styles(document)
    page_setup(document.sections[0])
    headers(document)
    cover(document)
    document.add_page_break()
    document.add_heading("Apresentação", level=1)
    for line in lines:
        if line.startswith("**Ambiente de referência:") or line.startswith("**Síntese:"):
            inline(document.add_paragraph(), line, ref)
    inline(document.add_paragraph(), "**Divisão de responsabilidades:** Murillo Alves Augusto — Parte I, simulador; Henrique Caliari Fuzeto — Parte II, laboratório GNU/Linux. Análise dos resultados e conclusões compartilhadas pela dupla.", ref)
    inline(document.add_paragraph(), "**Material complementar:** [código, instruções e arquivos de evidência no repositório público](https://github.com/henri16bit/trabalho-walter). As figuras estão reunidas no apêndice de evidências visuais, com links para os PNG originais. Os links dos dados e do código apontam para uma versão preservada do repositório.", ref)
    document.add_heading("Organização da leitura", level=2)
    for item in ("2 Fundamentação teórica", "3 Metodologia e modelagem do simulador", "4 Resultados da simulação", "5 Laboratório GNU Linux", "6 Conclusões e lições aprendidas", "7 Referências bibliográficas", "Apêndice de evidências visuais"):
        p = document.add_paragraph(item)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
    start = next(i for i, line in enumerate(lines) if line.startswith("## 2."))
    i = start
    figures = []
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        heading = re.match(r"(#{2,4}) (.+)", line)
        if heading:
            level = len(heading[1]) - 1
            p = document.add_heading(clean_heading(heading[2]), level=level)
            if level == 1:
                p.paragraph_format.page_break_before = True
            i += 1
        elif line.startswith("!["):
            match = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line)
            if not match:
                raise ValueError(line)
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            caption = lines[i].strip().strip("*")
            number = int(re.search(r"Figura (\d+)", caption)[1])
            figures.append((number, match[1], match[2], caption))
            p = document.add_paragraph(f"Ver Figura {number} no apêndice de evidências visuais.")
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(7)
            p.runs[0].font.size = Pt(10)
            p.runs[0].italic = True
            i += 1
        elif line.startswith("|"):
            group = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                group.append(lines[i])
                i += 1
            make_table(document, group, ref)
        elif line.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            p = document.add_paragraph("\n".join(code))
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.keep_together = True
            p.paragraph_format.left_indent = Cm(0.3)
            for run in p.runs:
                run.font.name = "Courier New"
                run.font.size = Pt(10)
            i += 1
        else:
            paragraph_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||```|!\[|\d+\. [A-Z])", lines[i]):
                paragraph_lines.append(lines[i].strip())
                i += 1
            p = document.add_paragraph()
            inline(p, " ".join(paragraph_lines), ref)
            if line.startswith("**Tabela"):
                p.paragraph_format.keep_with_next = True
                p.paragraph_format.line_spacing = 1.15
            if re.match(r"\d+\. [A-Z]", line):
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(12)
                p.paragraph_format.keep_together = True
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for number, alt, path, caption in figures:
        image_path = ROOT / path
        with Image.open(image_path) as source:
            width, height = source.size
        landscape = width / height > 1.5
        section = document.add_section(WD_SECTION_START.NEW_PAGE)
        page_setup(section, landscape=landscape, appendix=True)
        section.different_first_page_header_footer = False
        p = document.add_heading("Apêndice de evidências visuais" if number == 1 else f"Evidência visual {number}", level=1)
        p.paragraph_format.space_before = Pt(0)
        inline(document.add_paragraph(style="Caption"), caption, ref)
        max_width = 25.7 if landscape else 17.0
        max_height = 12.7 if landscape else 20.5
        picture_width = min(max_width, max_height * width / height)
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        shape = p.add_run().add_picture(str(image_path), width=Cm(picture_width))
        shape._inline.docPr.set("descr", alt)
        p = document.add_paragraph(style="Caption")
        hyperlink(p, "Abrir a imagem original em resolução integral", url_for(path, ref))
        p.add_run(". Conteúdo preservado; amplie a página ou o PNG para conferir os detalhes.")
    assert len(figures) == 14
    document.core_properties.title = "Gerência de memória virtual paginação e monitoramento no GNU Linux"
    document.core_properties.subject = "Trabalho semestral de Sistemas Operacionais — UNIRP"
    document.core_properties.author = "Henrique Caliari Fuzeto; Murillo Alves Augusto"
    document.core_properties.keywords = "GNU/Linux, Ubuntu, paginação, FIFO, LRU, Clock, NRU, swap"
    document.core_properties.comments = ""
    document.core_properties.created = datetime.now(timezone.utc)
    document.core_properties.modified = datetime.now(timezone.utc)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)
    print(f"Word gerado: {output}; {len(figures)} imagens originais incorporadas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=ROOT / "output/docx/Relatorio_Sistemas_Operacionais_UNIRP.docx")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Commit que preserva os arquivos de evidência e código citados")
    args = parser.parse_args()
    build(args.saida, args.ref)
