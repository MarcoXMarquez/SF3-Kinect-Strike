"""
Generador del artículo científico en formato IEEE para Microsoft Word (.docx).
Proyecto: KINECT STRIKE (Street Fighter III: 3rd Strike en Unity + Azure Kinect).
Temas centrales:
  1. Patrullaje autónomo por puntos de ruta y FSM reactiva de sigilo.
  2. Física predictiva balística con integración de Euler semi-implícita y derivación de deriva discreta.
  3. Control corporal somatosensorial con Azure Kinect DK, descriptores geométricos estáticos y bosque aleatorio ONNX.

Cumplimiento estricto de las directivas IEEE:
  - Sin página de portada separada; inicio directo con título TNR 24 pt centrado.
  - Firma de autores con filiación, país, correos y ORCID en TNR 10 pt según estándar IEEE Access / Conferences.
  - Resumen en TNR 9 pt <= 200 palabras, sin acrónimos indefinidos ni citas.
  - Términos del índice en orden alfabético del Tesauro IEEE en TNR 9 pt.
  - Cuerpo a dos columnas (3.5 in columna, 0.25 in espaciado).
  - Jerarquía completa de encabezados IEEE: Nivel 1 (Romano, centrado, small caps), Nivel 2 (Letra, cursiva, izquierda),
    Nivel 3 (Árabe + paréntesis, sangrado, negrita cursiva), Nivel 4 (Minúscula + paréntesis, sangrado profundo, cursiva),
    Componentes (Centrado, small caps, sin numerar).
  - Figuras y tablas ubicadas en parte superior o inferior de columna/página, numeración consecutiva global independiente.
  - Ecuaciones centradas con numeración entre paréntesis alineada a la derecha; citas directas "(n)" o "La ecuación (n)...".
  - Citas ordenadas por primera aparición en texto [1], [2], [3], con sintaxis de autores "Primer Autor et al. [n]" (>3 autores)
    o "Autor A y Autor B [m]" (2 autores), sin rangos con guion ("[1], [2], [3]").
  - 18 referencias IEEE en TNR 8 pt con iniciales, sin comas alrededor de Jr./Sr., DOI con punto final, URLs sin punto final.
"""

import os
import re
import shutil

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CAPT_DIR = os.path.join(ROOT_DIR, "Docs", "Capturas_Informe")
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
OUT_NAME = "Articulo_IEEE_KinectStrike_Waypoints_FisicaPredictiva_Kinect.docx"

FONT = "Times New Roman"
COL_W_IN = 3.5          # ancho columna IEEE (pulgadas)
COL_W_DXA = 5040        # 3.5 in en twips (dxa)
FULL_W_DXA = 10440      # 7.25 in (dos columnas + 0.25 in separación)

FIG_ORDER = ["wp", "phys", "kin", "duel"]
TAB_ORDER = ["fsm", "feat", "res", "lat"]
EQ_ORDER = [
    "loop", "ping", "move", "detect", "euler_v", "euler_p",
    "inverse", "drift", "segment", "residual", "hext", "asym", "angle"
]

# -----------------------------------------------------------------------------
# REFERENCIAS BIBLIOGRÁFICAS (IEEE Standards, 8 pt)
# -----------------------------------------------------------------------------
REFERENCES = {
    "zhang": 'Z. Zhang, "Microsoft Kinect sensor and its effect," *IEEE MultiMedia*, vol. 19, no. 2, pp. 4–10, Feb. 2012, doi: 10.1109/MMUL.2012.24.',
    "tolgyessy": 'M. Tölgyessy, M. Dekan, Ľ. Chovanec, and P. Hubinský, "Evaluation of the Azure Kinect and its comparison to Kinect V1 and Kinect V2," *Sensors*, vol. 21, no. 2, Art. no. 413, Jan. 2021, doi: 10.3390/s21020413.',
    "shotton": 'J. Shotton et al., "Real-time human pose recognition in parts from single depth images," in *Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)*, Colorado Springs, CO, USA, 2011, pp. 1297–1304, doi: 10.1109/CVPR.2011.5995316.',
    "reynolds": 'C. W. Reynolds, "Steering behaviors for autonomous characters," in *Proc. Game Developers Conf.*, San Jose, CA, USA, 1999, pp. 763–782.',
    "millington": 'I. Millington, *AI for Games*, 3rd ed. Boca Raton, FL, USA: CRC Press, 2019.',
    "eberly": 'D. H. Eberly, *Game Physics*, 2nd ed. Burlington, MA, USA: Morgan Kaufmann, 2010.',
    "hairer": 'E. Hairer, C. Lubich, and G. Wanner, *Geometric Numerical Integration: Structure-Preserving Algorithms for Ordinary Differential Equations*, 2nd ed. Berlin, Germany: Springer, 2006, doi: 10.1007/3-540-30666-8.',
    "unity": 'Unity Technologies, *Unity Engine*, ver. 6000.3.23f1. (2026). [Online]. Available: https://unity.com',
    "box2d": 'E. Catto, *Box2D: A 2D Physics Engine for Games*. Accessed: Oct. 20, 2026. [Online]. Available: https://box2d.org',
    "k4abt": 'Microsoft Corp., *Azure Kinect Body Tracking SDK*, ver. 1.1.2. (2022). [Online]. Available: https://learn.microsoft.com/azure/kinect-dk/body-sdk-download',
    "pykinect": 'I. Gorordo, *pyKinectAzure*. Accessed: Oct. 20, 2026. [Online]. Available: https://github.com/ibaiGorordo/pyKinectAzure',
    "opencv": 'G. Bradski, "The OpenCV library," *Dr. Dobb\'s J. Softw. Tools*, vol. 25, no. 11, pp. 120–125, Nov. 2000.',
    "xia": 'L. Xia, C.-C. Chen, and J. K. Aggarwal, "View invariant human action recognition using histograms of 3D joints," in *Proc. IEEE Comput. Soc. Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW)*, Providence, RI, USA, 2012, pp. 20–27, doi: 10.1109/CVPRW.2012.6239233.',
    "casiez": 'G. Casiez, N. Roussel, and D. Vogel, "1€ filter: A simple speed-based low-pass filter for noisy input in interactive systems," in *Proc. SIGCHI Conf. Human Factors Comput. Syst. (CHI)*, Austin, TX, USA, 2012, pp. 2527–2530, doi: 10.1145/2207676.2208639.',
    "breiman": 'L. Breiman, "Random forests," *Mach. Learn.*, vol. 45, no. 1, pp. 5–32, Oct. 2001, doi: 10.1023/A:1010933404324.',
    "sklearn": 'F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011.',
    "skl2onnx": 'ONNX Contributors, *sklearn-onnx: Convert Scikit-Learn Models to ONNX*. Accessed: Oct. 20, 2026. [Online]. Available: https://github.com/onnx/sklearn-onnx',
    "onnxrt": 'ONNX Runtime Developers, *ONNX Runtime*. (2021). [Online]. Available: https://onnxruntime.ai',
}

cite_order = []
eq_counter = [0]
h_state = {"l1": 0, "l2": 0, "l3": 0, "l4": 0}


def roman(n: int) -> str:
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def resolve(text: str) -> str:
    def repl(m):
        kind, keys = m.group(1), m.group(2)
        if kind == "cite":
            parts = []
            for k in keys.split(","):
                k = k.strip()
                if k not in REFERENCES:
                    raise KeyError(f"Referencia desconocida: {k}")
                if k not in cite_order:
                    cite_order.append(k)
                parts.append(f"[{cite_order.index(k) + 1}]")
            return ", ".join(parts)
        if kind == "fig":
            return f"Fig. {FIG_ORDER.index(keys) + 1}"
        if kind == "tab":
            return f"Tabla {roman(TAB_ORDER.index(keys) + 1)}"
        if kind == "eq":
            return f"({EQ_ORDER.index(keys) + 1})"
        return m.group(0)
    return re.sub(r"\{(cite|fig|tab|eq):([A-Za-z0-9_, ]+)\}", repl, text)


# -----------------------------------------------------------------------------
# ESTILOS Y FORMATO DE TEXTO
# -----------------------------------------------------------------------------
def set_run_font(run, size, name=FONT):
    run.font.name = name
    run.font.size = Pt(size)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def add_rich(p, text, size=10, italic=False, bold=False, small_caps=False):
    text = resolve(text)
    state = {"italic": italic, "bold": bold, "mono": False, "mode": None}
    buf = []

    def flush():
        if not buf:
            return
        r = p.add_run("".join(buf))
        if state["mono"]:
            set_run_font(r, size - 1, "Courier New")
        else:
            set_run_font(r, size)
        r.italic = state["italic"]
        r.bold = state["bold"]
        r.font.small_caps = small_caps
        if state["mode"] == "sub":
            r.font.subscript = True
        elif state["mode"] == "sup":
            r.font.superscript = True
        buf.clear()

    i = 0
    while i < len(text):
        c = text[i]
        if c == "*":
            flush(); state["italic"] = not state["italic"]; i += 1; continue
        if c == "#":
            flush(); state["bold"] = not state["bold"]; i += 1; continue
        if c == "`":
            flush(); state["mono"] = not state["mono"]; i += 1; continue
        if c in "_^" and i + 1 < len(text) and text[i + 1] == "{":
            flush(); state["mode"] = "sub" if c == "_" else "sup"; i += 2; continue
        if c == "}" and state["mode"]:
            flush(); state["mode"] = None; i += 1; continue
        buf.append(c)
        i += 1
    flush()


def fmt(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, first=0.14, left=0.0, before=0, after=0):
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Inches(first) if first else Inches(0)
    pf.left_indent = Inches(left) if left else Inches(0)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.0
    return p


def para(doc, text, first=0.14):
    p = fmt(doc.add_paragraph(), first=first)
    add_rich(p, text, 10)
    return p


def h1(doc, title, page_break=False):
    h_state["l1"] += 1
    h_state["l2"] = h_state["l3"] = h_state["l4"] = 0
    p = fmt(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER, first=0, before=8, after=4)
    p.paragraph_format.keep_with_next = True
    if page_break:
        p.paragraph_format.page_break_before = True
    add_rich(p, f"{roman(h_state['l1'])}. {title}", 10, small_caps=True)


def h2(doc, title):
    h_state["l2"] += 1
    h_state["l3"] = h_state["l4"] = 0
    p = fmt(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.LEFT, first=0, before=5, after=3)
    p.paragraph_format.keep_with_next = True
    add_rich(p, f"{chr(64 + h_state['l2'])}. {title}", 10, italic=True)


def h3(doc, title, text):
    h_state["l3"] += 1
    h_state["l4"] = 0
    p = fmt(doc.add_paragraph(), first=0.14)
    add_rich(p, f"{h_state['l3']}) {title}: ", 10, italic=True, bold=True)
    add_rich(p, text, 10)
    return p


def h4(doc, title, text):
    h_state["l4"] += 1
    p = fmt(doc.add_paragraph(), first=0.28)
    add_rich(p, f"{chr(96 + h_state['l4'])}) {title}: ", 10, italic=True)
    add_rich(p, text, 10)
    return p


def component_heading(doc, title):
    p = fmt(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER, first=0, before=8, after=4)
    p.paragraph_format.keep_with_next = True
    add_rich(p, title, 10, small_caps=True)


def equation(doc, name, markup):
    idx = EQ_ORDER.index(name) + 1
    eq_counter[0] += 1
    assert idx == eq_counter[0], f"Ecuación {name} fuera de orden: esperado {eq_counter[0]}, obtenido {idx}"
    p = fmt(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.LEFT, first=0, before=3, after=3)
    ts = p.paragraph_format.tab_stops
    ts.add_tab_stop(Inches(COL_W_IN / 2), WD_TAB_ALIGNMENT.CENTER)
    ts.add_tab_stop(Inches(COL_W_IN), WD_TAB_ALIGNMENT.RIGHT)
    add_rich(p, "\t" + markup, 10)
    r = p.add_run(f"\t({idx})")
    set_run_font(r, 10)


# -----------------------------------------------------------------------------
# TABLAS FLOTANTES (FIGURAS Y TABLAS EN PARTE SUPERIOR/INFERIOR)
# -----------------------------------------------------------------------------
def _border(tag, val="single", sz="4"):
    el = OxmlElement(f"w:{tag}")
    el.set(qn("w:val"), val)
    el.set(qn("w:sz"), sz)
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "000000")
    return el


def configure_table(table, width_dxa, col_widths, ypos="top", span=False):
    tbl = table._tbl
    tblPr = tbl.tblPr

    tblpPr = OxmlElement("w:tblpPr")
    attrs = {
        "w:leftFromText": "0", "w:rightFromText": "0",
        "w:topFromText": "0" if ypos == "top" else "180",
        "w:bottomFromText": "180" if ypos == "top" else "0",
        "w:vertAnchor": "margin",
        "w:horzAnchor": "margin" if span else "text",
        "w:tblpXSpec": "center", "w:tblpYSpec": ypos,
    }
    for k, v in attrs.items():
        tblpPr.set(qn(k), v)
    overlap = OxmlElement("w:tblOverlap")
    overlap.set(qn("w:val"), "never")
    style = tblPr.find(qn("w:tblStyle"))
    pos = list(tblPr).index(style) + 1 if style is not None else 0
    tblPr.insert(pos, tblpPr)
    tblPr.insert(pos + 1, overlap)

    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.insert(pos + 2, tblW)
    tblW.set(qn("w:w"), str(width_dxa))
    tblW.set(qn("w:type"), "dxa")
    after = list(tblPr).index(tblW) + 1

    borders = OxmlElement("w:tblBorders")
    for tag in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(_border(tag, "nil", "0"))
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    mar = OxmlElement("w:tblCellMar")
    for tag, w in (("top", "15"), ("left", "40"), ("bottom", "15"), ("right", "40")):
        e = OxmlElement(f"w:{tag}")
        e.set(qn("w:w"), w)
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    for el in (borders, layout, mar):
        tblPr.insert(after, el)
        after += 1

    for i, w in enumerate(col_widths):
        table.columns[i].width = w * 635  # dxa a EMU
        for cell in table.columns[i].cells:
            cell.width = w * 635


def cell_borders(cell, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcb = OxmlElement("w:tcBorders")
    if top:
        tcb.append(_border("top", "single", top))
    if bottom:
        tcb.append(_border("bottom", "single", bottom))
    anchor = None
    for tag in ("w:tcW", "w:gridSpan", "w:vMerge"):
        el = tcPr.find(qn(tag))
        if el is not None:
            anchor = el
    if anchor is not None:
        anchor.addnext(tcb)
    else:
        tcPr.insert(0, tcb)


def cell_text(cell, text, size=8, align=WD_ALIGN_PARAGRAPH.CENTER, small_caps=False, italic=False):
    p = cell.paragraphs[0]
    fmt(p, align=align, first=0)
    add_rich(p, text, size, small_caps=small_caps, italic=italic)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def figure(doc, key, image_path, caption, ypos="top", span=False):
    n = FIG_ORDER.index(key) + 1
    width_dxa = FULL_W_DXA if span else COL_W_DXA
    img_w = 6.85 if span else 3.40
    table = doc.add_table(rows=2, cols=1)
    configure_table(table, width_dxa, [width_dxa], ypos=ypos, span=span)
    p_img = fmt(table.cell(0, 0).paragraphs[0], align=WD_ALIGN_PARAGRAPH.CENTER, first=0)
    p_img.add_run().add_picture(image_path, width=Inches(img_w))
    p_cap = fmt(table.cell(1, 0).paragraphs[0], align=WD_ALIGN_PARAGRAPH.JUSTIFY, first=0, before=2)
    add_rich(p_cap, f"Fig. {n}. ", 8)
    add_rich(p_cap, caption, 8)


def data_table(doc, key, title, headers, rows, col_widths, ypos="top"):
    n = TAB_ORDER.index(key) + 1
    ncols = len(headers)
    table = doc.add_table(rows=3 + len(rows), cols=ncols)
    configure_table(table, sum(col_widths), col_widths, ypos=ypos)

    c0 = table.cell(0, 0).merge(table.cell(0, ncols - 1))
    cell_text(c0, f"Tabla {roman(n)}", 8, small_caps=True)
    c1 = table.cell(1, 0).merge(table.cell(1, ncols - 1))
    cell_text(c1, title, 8, small_caps=True)
    c1.paragraphs[0].paragraph_format.space_after = Pt(2)

    for j, h in enumerate(headers):
        c = table.cell(2, j)
        cell_text(c, h, 8)
        cell_borders(c, top="8", bottom="4")
    for i, row in enumerate(rows):
        last = i == len(rows) - 1
        for j, val in enumerate(row):
            c = table.cell(3 + i, j)
            cell_text(c, val, 8, align=WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER)
            if last:
                cell_borders(c, bottom="8")


# -----------------------------------------------------------------------------
# CONSTRUCCIÓN COMPLETA DEL ARTÍCULO IEEE
# -----------------------------------------------------------------------------
def build():
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.line_spacing = 1.0

    core = doc.core_properties
    core.title = "Patrullaje por Puntos de Ruta, Física Predictiva Balística y Control Corporal con Azure Kinect en un Videojuego de Lucha 2D"
    core.author = "Kevin Joel Callo Ccagiavilca; Marco Antonio Marquez Herrera; Alejandro Sebastian Alfonso Huacasi"

    # Página carta con márgenes estándar IEEE
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1.0)
    sec.left_margin = sec.right_margin = Inches(0.625)

    # ---------------- 1. TÍTULO DEL ARTÍCULO (TNR 24 pt, Centrado) ----------------
    p_title = fmt(doc.paragraphs[0] if doc.paragraphs else doc.add_paragraph(),
                  align=WD_ALIGN_PARAGRAPH.CENTER, first=0, after=0)
    add_rich(p_title, "Patrullaje por Puntos de Ruta, Física Predictiva Balística y Control Corporal con Azure Kinect en un Videojuego de Lucha 2D", 24)

    # Espacio antes del bloque de autores
    fmt(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER, first=0, before=0, after=4)

    # ---------------- 2. FIRMA DE AUTORES EN TRES COLUMNAS (Formato IEEE Conference) ----------------
    authors_info = [
        {
            "name": "Kevin Joel Callo Ccagiavilca",
            "dept": "Escuela Profesional de Ingeniería de Sistemas",
            "org": "Universidad Nacional de San Agustín de Arequipa",
            "loc": "Arequipa, Perú",
            "email": "kcalloc@unsa.edu.pe",
        },
        {
            "name": "Marco Antonio Marquez Herrera",
            "dept": "Escuela Profesional de Ingeniería de Sistemas",
            "org": "Universidad Nacional de San Agustín de Arequipa",
            "loc": "Arequipa, Perú",
            "email": "mmarquezhe@unsa.edu.pe",
        },
        {
            "name": "Alejandro Sebastian Alfonso Huacasi",
            "dept": "Escuela Profesional de Ingeniería de Sistemas",
            "org": "Universidad Nacional de San Agustín de Arequipa",
            "loc": "Arequipa, Perú",
            "email": "aalfonso@unsa.edu.pe",
        },
    ]

    tbl_auth = doc.add_table(rows=1, cols=3)
    tblPr = tbl_auth._tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), str(FULL_W_DXA))
    tblW.set(qn("w:type"), "dxa")

    borders = OxmlElement("w:tblBorders")
    for tag in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(_border(tag, "nil", "0"))
    tblPr.append(borders)

    col_w_dxa = FULL_W_DXA // 3
    for i, a in enumerate(authors_info):
        cell = tbl_auth.cell(0, i)
        cell.width = col_w_dxa * 635
        tcPr = cell._tc.get_or_add_tcPr()
        tcW = tcPr.find(qn("w:tcW"))
        if tcW is None:
            tcW = OxmlElement("w:tcW")
            tcPr.append(tcW)
        tcW.set(qn("w:w"), str(col_w_dxa))
        tcW.set(qn("w:type"), "dxa")

        p0 = cell.paragraphs[0]
        fmt(p0, align=WD_ALIGN_PARAGRAPH.CENTER, first=0, before=4, after=2)
        r0 = p0.add_run(a["name"])
        set_run_font(r0, 10)
        r0.bold = True

        for key, italic in (("dept", True), ("org", True), ("loc", False), ("email", False)):
            p_line = cell.add_paragraph()
            fmt(p_line, align=WD_ALIGN_PARAGRAPH.CENTER, first=0, before=0, after=1)
            r_line = p_line.add_run(a[key])
            set_run_font(r_line, 9.5)
            r_line.italic = italic

    p_post = doc.add_paragraph()
    fmt(p_post, align=WD_ALIGN_PARAGRAPH.CENTER, first=0, before=2, after=6)

    # ---------------- 3. SECCIÓN A DOS COLUMNAS (3.5 in, 0.25 in espaciado) ----------------
    body = doc.add_section(WD_SECTION.CONTINUOUS)
    cols = body._sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        body._sectPr.append(cols)
    cols.set(qn("w:num"), "2")
    cols.set(qn("w:space"), "360")  # 0.25 pulgada en dxa

    # ---------------- 4. RESUMEN Y TÉRMINOS DEL ÍNDICE (TNR 9 pt) ----------------
    abstract = (
        "Este artículo presenta el diseño e integración de tres subsistemas interactivos en un videojuego de lucha "
        "bidimensional inspirado en Street Fighter III: 3rd Strike y desarrollado en Unity. El primero es un sistema de "
        "patrullaje autónomo basado en puntos de ruta, que combina recorridos cíclicos y de ida y vuelta con una máquina "
        "de estados finitos que conmuta entre patrulla, espera, persecución y captura. El segundo es un motor de física "
        "predictiva para proyectiles que reproduce el integrador de Euler semi-implícito del motor físico, resuelve la "
        "velocidad inicial necesaria para impactar blancos móviles y evalúa su posición y la fase de sus escudos en el "
        "instante futuro de impacto. El tercero es un esquema de control corporal con el sensor de profundidad Azure "
        "Kinect, en el que un clasificador de bosques aleatorios reconoce siete posturas de combate a partir de cuarenta "
        "y cuatro descriptores geométricos estáticos, invariantes a la velocidad y normalizados por la antropometría del "
        "jugador. Con catorce sujetos y noventa y ocho muestras, el clasificador alcanzó una exactitud de 95.92 % en "
        "validación cruzada agrupada por sujeto, y un periodo de calibración de 1.5 s eliminó las activaciones espurias "
        "al iniciar el seguimiento corporal."
    )
    assert len(abstract.split()) <= 200, f"El resumen tiene {len(abstract.split())} palabras; excede el límite de 200."
    p_abs = fmt(doc.add_paragraph(), first=0.14)
    add_rich(p_abs, "Resumen—", 9, italic=True, bold=True)
    add_rich(p_abs, abstract, 9, bold=True)

    p_idx = fmt(doc.add_paragraph(), first=0.14, before=6, after=4)
    add_rich(p_idx, "Términos del índice—", 9, italic=True, bold=True)
    add_rich(p_idx, "Aprendizaje automático, bosques aleatorios, estimación de pose, juegos, modelos predictivos, navegación, trayectoria.", 9, bold=True)

    # ======================= I. INTRODUCCIÓN =======================
    h1(doc, "Introducción")
    para(doc, "Los sensores de profundidad de consumo transformaron la interacción humano-computadora al permitir el "
              "seguimiento del cuerpo completo sin marcadores de contacto {cite:zhang}. Investigaciones rigurosas conducidas "
              "por Tölgyessy et al. {cite:tolgyessy} demostraron que el sensor Azure Kinect ofrece mejoras notables en "
              "repetibilidad métrica y minimización de ruido volumétrico respecto a las generaciones previas. En este "
              "ámbito, los avances seminales de Shotton et al. {cite:shotton} establecieron la viabilidad de estimar "
              "articulaciones tridimensionales en tiempo real a partir de imágenes de profundidad mediante bosques aleatorios, "
              "abriendo el camino para videojuegos de ejercicio físico en los cuales la postura del usuario gobierna las "
              "acciones del personaje sin requerir mandos convencionales.")
    para(doc, "De forma simultánea, la experiencia inmersiva de juego exige que los personajes no jugadores exhiban "
              "patrones de navegación espacial verosímiles y consistentes con las restricciones cinemáticas del entorno virtual. "
              "Los principios de comportamientos de dirección formulados por Reynolds {cite:reynolds} y las estructuras de "
              "toma de decisiones sistematizadas por Millington {cite:millington} constituyen el fundamento algorítmico del "
              "desplazamiento autónomo. Asimismo, cuando la mecánica de combate involucra disparos balísticos, la simulación "
              "debe regirse por integradores numéricos estables y conservativos {cite:eberly}, {cite:hairer}, de modo que "
              "cualquier trayectoria predicha por la interfaz coincida rigurosamente con la dinámica calculada por el motor.")
    para(doc, "El presente trabajo documenta la integración formal, en un único proyecto desarrollado sobre Unity "
              "{cite:unity}, de tres subsistemas interactivos concebidos para un videojuego de lucha bidimensional inspirado "
              "en *Street Fighter III: 3rd Strike*. Las contribuciones principales son: 1) un sistema de navegación por puntos "
              "de ruta con máquina de estados finitos (FSM, por sus siglas en inglés) que implementa patrullaje perimetral y "
              "persecución reactiva de intercepción; 2) un motor de física predictiva discreta que modela la parábola bajo "
              "el integrador de Euler semi-implícito y resuelve la velocidad inicial para blancos móviles con escudos "
              "oscilantes; y 3) una arquitectura somatosensorial con Azure Kinect basada en descriptores puramente geométricos "
              "estáticos que detecta posturas sostenidas y suprime activaciones falsas al iniciar el seguimiento.")
    para(doc, "El manuscrito se estructura de la siguiente manera: la Sección II detalla la arquitectura global del sistema; "
              "las Secciones III, IV y V exponen el patrullaje por puntos de ruta, la física predictiva y el control corporal "
              "con Azure Kinect; la Sección VI analiza los resultados experimentales y la discusión técnica; y la Sección VII "
              "sintetiza las conclusiones y perspectivas de investigación futura.")

    # ======================= II. ARQUITECTURA DEL SISTEMA =======================
    h1(doc, "Arquitectura del Sistema")
    para(doc, "El proyecto se fundamenta en Unity 6 empleando animación manual por fotogramas a una cadencia estricta de "
              "14 fotogramas por segundo (FPS) y una resolución espacial de 100 píxeles por unidad (PPU), garantizando la "
              "estética fiel del clásico de Capcom. La interfaz organiza la experiencia mediante un menú principal jerárquico "
              "que conecta el modo historia cinemático, la arena de duelo local y un selector de minijuegos técnicos.")
    para(doc, "La capa de entrada de los luchadores se desacopló estructuralmente mediante la interfaz abstracta "
              "`IFighterInput`. Esta abstracción permite que el controlador `DuelFighter` procese indistintamente comandos "
              "originados en teclado tradicional o procedentes del adaptador somatosensorial `KinectFighterInput`. El proceso "
              "de percepción visual se ejecuta de manera asíncrona en un entorno Python independiente, el cual clasifica "
              "las articulaciones en vivo y transmite la postura resultante a Unity mediante paquetes UDP datagram a través "
              "del socket local 127.0.0.1:5005 con una frecuencia de refresco de 33 Hz.")

    # ======================= III. SISTEMA DE PATRULLAJE POR PUNTOS DE RUTA =======================
    h1(doc, "Sistema de Patrullaje por Puntos de Ruta")
    para(doc, "El minijuego de infiltración sitúa a Ryu en un dojo ceremonial de 14.8 m × 8.0 m poblado por tres obstáculos "
              "rocosos masivos. El objetivo consiste en recolectar cuatro orbes de energía mística evitando la intercepción "
              "de dos guardias autónomos, Ken y Sean, para luego activar el portal de extracción. La {fig:wp} ilustra la "
              "topología completa del dojo y los circuitos de navegación.")
    figure(doc, "wp", os.path.join(CAPT_DIR, "fig1_waypoints_scene.png"),
           "Topología del escenario de sigilo reconstruida desde los parámetros algorítmicos: circuito perimetral cíclico "
           "(Ken, nodos WP_A1 a WP_A6), circuito alternante de ida y vuelta (Sean, nodos WP_B1 a WP_B4), radios de detección "
           "y captura de guardias, obstáculos de roca procedurales, orbes coleccionables y portal de extracción.",
           ypos="top", span=True)

    h2(doc, "Topología y Modos de Recorrido")
    para(doc, "La clase `WaypointCircuit` administra una lista ligada de nodos de posición espacial #w#_{i} ∈ ℝ² y define "
              "tres estrategias de progresión. En el modo cíclico perimetral, asignado a Ken a través de seis nodos periféricos, "
              "el avance tras alcanzar el nodo *k* se resuelve mediante aritmética modular:")
    equation(doc, "loop", "*i*_{*k*+1} = (*i*_{*k*} + 1) mod *N*")
    para(doc, "Para Sean, cuyo recorrido rodea los pilares centrales mediante cuatro nodos colineales, se utiliza el modo de "
              "ida y vuelta gobernado por un indicador direccional *d*_{*k*} ∈ {−1, +1} que conmuta de signo al tocar los "
              "extremos del grafo:", first=0)
    equation(doc, "ping", "*i*_{*k*+1} = *i*_{*k*} + *d*_{*k*}")
    para(doc, "Cuando un guardia pierde de vista al jugador tras una persecución infructuosa, el método `GetClosestWaypointIndex` "
              "calcula la distancia euclidiana al cuadrado hacia la totalidad de nodos del circuito y reanuda el patrullaje "
              "en el vértice espacialmente más próximo, eliminando oscilaciones o teletransportes visuales.", first=0)

    h2(doc, "Máquina de Estados Finitos del Guardia")
    para(doc, "El comportamiento de cada agente, materializado en `WaypointPatrolNPC`, está coordinado por la FSM de cuatro "
              "estados especificada en la {tab:fsm}. Durante el estado de patrulla ordinaria, el desplazamiento se modela como "
              "movimiento rectilíneo hacia el nodo meta activo #w#:")
    data_table(doc, "fsm", "Estados de la Máquina de Estados Finitos del Guardia",
               ["Estado", "Condición de Entrada", "Comportamiento Cinematográfico"],
               [["Patrulla", "Arranque o fin de reposo", "Avance cinemático hacia nodo activo según {eq:move}"],
                ["Espera", "Distancia a nodo < 0.20 m", "Reposo visual e inspección local (0.8 s a 1.2 s)"],
                ["Persecución", "Jugador dentro de *R*_{d} por {eq:detect}", "Búsqueda reactiva acelerada (3.8 a 4.0 m/s)"],
                ["Captura", "Distancia al jugador ≤ 0.85 m", "Emisión de evento de captura y detención"]],
               [1000, 1900, 2140], ypos="top")
    equation(doc, "move", "#p#(*t* + Δ*t*) = #p#(*t*) + *v*_{p} Δ*t* (#w# − #p#(*t*)) / ‖#w# − #p#(*t*)‖")
    para(doc, "Al ingresar en el radio de tolerancia (0.20 m), el guardia entra en espera durante 0.8 s (Ken) o 1.2 s (Sean). "
              "La transición a persecución, inspirada en las reglas de aproximación de Reynolds {cite:reynolds}, se dispara en "
              "cuanto la distancia euclidiana al jugador satisface la condición:", first=0)
    equation(doc, "detect", "‖#p#_{J} − #p#_{G}‖ ≤ *R*_{d}")
    para(doc, "donde *R*_{d} equivale a 2.3 m para Ken y 2.2 m para Sean. En persecución, la rapidez escala de 2.8 m/s a 3.8 m/s "
              "para Ken y de 3.2 m/s a 4.0 m/s para Sean. Si la separación sobrepasa 1.5 *R*_{d}, el guardia retorna a su nodo; "
              "si desciende por debajo de 0.85 m, se declara captura inmediata y el gestor del minijuego detiene la sesión.", first=0)

    h2(doc, "Renderizado Procedural y Animación")
    para(doc, "Los obstáculos rocosos integran un sombreador procedural que perturba las coordenadas de textura mediante ruido "
              "de gradiente. El portal de extracción implementa un vórtice animado en tiempo real que transmuta su cromatismo de "
              "carmesí latente a azul cobalto luminiscente al recolectar los cuatro orbes. Las animaciones se ejecutan mediante "
              "el componente `SpriteFrameAnimator`, garantizando cadencia fija sin árboles de mezcla de Mecanim.")

    # ======================= IV. FÍSICA PREDICTIVA BALÍSTICA =======================
    h1(doc, "Física Predictiva Balística")
    para(doc, "El minijuego de asedio sitúa al combatiente en los tejados industriales de Hong Kong a lo largo de una campaña "
              "de cinco fases continuas. El desafío exige abatir blancos oscilantes mediante proyectiles energéticos superando "
              "barreras metálicas intermedias y, en asaltos avanzados, coordinando el disparo con los intervalos de apertura de "
              "escudos refractarios periódicos. La {fig:phys} ilustra la trayectoria trazada por el predictor.")
    figure(doc, "phys", os.path.join(CAPT_DIR, "fig2_predictive_physics_neonsiege.png"),
           "Trayectoria predicha mediante integración de Euler semi-implícita a Δ*t* = 0.02 s. El proyectil supera la barrera "
           "de blindaje y colisiona en las coordenadas futuras del blanco móvil cuando su escudo defensivo se encuentra inactivo.",
           ypos="top")

    h2(doc, "Integración Numérica y Derivación de la Deriva")
    para(doc, "El motor 2D de Unity utiliza internamente la biblioteca Box2D {cite:box2d}, la cual procesa la cinemática de "
              "cuerpos rígidos con un paso temporal discreto Δ*t* = 0.02 s (50 Hz). A fin de eliminar cualquier desfasaje entre "
              "la parábola predicha y el vuelo real, `SiegeBallistics.Step` emula la formulación simpléctica de Euler "
              "semi-implícito analizada por Hairer et al. {cite:hairer}:")
    equation(doc, "euler_v", "#v#^{*n*+1} = #v#^{*n*} + #g# Δ*t*")
    equation(doc, "euler_p", "#p#^{*n*+1} = #p#^{*n*} + #v#^{*n*+1} Δ*t*")
    para(doc, "asumiendo vector de aceleración gravitatoria #g# = (0, −9.81) m/s² y resistencia aerodinámica despreciable. "
              "Al desarrollar recursivamente {eq:euler_v} y {eq:euler_p} tras *N* iteraciones, la posición vertical satisface:", first=0)
    equation(doc, "inverse", "*v*_{0*y*} = (*D*_{*y*} − *O*_{*y*}) / *T* − ½ *g* Δ*t* (*N* + 1)")
    para(doc, "donde *T* = *N*Δ*t*. Contrastando esta expresión con la cinemática continua clásica descrita por Eberly "
              "{cite:eberly}, donde *y*(*T*) = *y*_{0} + *v*_{0*y*} *T* + ½ *g* *T*², se demuestra que la solución continua "
              "incurre en una deriva sistemática acumulada en el eje vertical dada por:", first=0)
    equation(doc, "drift", "*E*_{*y*}(*T*) = *p*_{*ny*} − *p*_{\\text{cont},*y*}(*T*) = ½ *g* Δ*t* *T*")
    para(doc, "Para un proyectil con tiempo de vuelo *T* = 3.0 s y Δ*t* = 0.02 s, la ecuación {eq:drift} produce un error de "
              "0.294 m, magnitud que supera holgadamente el radio de colisión del proyectil (*r* = 0.14 m) y provocaría fallos "
              "sistemáticos. La formulación discreta adoptada anula idénticamente este desvío.", first=0)

    h2(doc, "Predicción Espaciotemporal de Intercepción")
    para(doc, "Los objetivos enemigos oscilan armónicamente y accionan escudos periódicos. En consecuencia, el algoritmo "
              "`FindSolution` no apunta hacia las coordenadas instantáneas del blanco, sino a su configuración en el instante "
              "de arribo. Para tiempos candidatos *t*_{*i*} = *i*Δ*t* (*i* ∈ [24, 184], es decir, 0.48 s a 3.68 s), se descartan "
              "aquellos donde el escudo estará activo, se computa la posición futura #D#(*t*_{*i*}) y se valida la curva con "
              "`Forecast`. Si la trayectoria intersecta las barreras antes del blanco, se descarta.")
    para(doc, "Para la detección de colisión continua con esferas móviles, se transforma la trayectoria al sistema coordenado "
              "local del objetivo. Si #a# y #b# representan los extremos del segmento del paso temporal y #c# el centro del "
              "blanco, el parámetro de aproximación mínima se obtiene mediante:")
    equation(doc, "segment", "*u* = clamp( (#c# − #a#)·(#b# − #a#) / ‖#b# − #a#‖², 0, 1 )")
    para(doc, "confirmándose colisión efectiva cuando ‖#a# + *u*(#b# − #a#) − #c#‖ ≤ *r* + *r*_{b} − 0.07 m.", first=0)

    h2(doc, "Resolución de Raíces por Bisección")
    para(doc, "Cuando el usuario apunta manualmente mediante ratón fijando la rapidez nominal *v*, el método `AimAt` localiza "
              "las soluciones temporales que satisfacen la función residual de energía:")
    equation(doc, "residual", "*f*(*t*) = ‖#v#_{\\text{req}}(*t*)‖² − *v*²")
    para(doc, "El dominio temporal se subdivide en intervalos de 0.02 s y cada cambio de signo se refina mediante 14 "
              "iteraciones de bisección numérica, obteniendo los arcos balísticos bajo y alto para el tiro.", first=0)

    # ======================= V. CONTROL CORPORAL CON AZURE KINECT =======================
    h1(doc, "Control Corporal con Azure Kinect")
    para(doc, "En el modo historia, el jugador personifica a Ryu frente a Ken en el castillo Suzaku gobernando sus acciones "
              "mediante posturas corporales completas. Al sostener una postura en el espacio, la acción de combate se ejecuta "
              "cíclicamente mientras la pose permanezca inmóvil. La {fig:kin} exhibe el panel del estudio de postura.")
    figure(doc, "kin", os.path.join(CAPT_DIR, "fig3_kinect_posture_studio.png"),
           "Estudio de postura en tiempo real: proyección ortogonal frontal y sagital de las 32 articulaciones estimadas, "
           "distribución probabilística por clase y visualización de la barra temporal de pose sostenida completada.",
           ypos="top")

    h2(doc, "Adquisición y Canal de Comunicación")
    para(doc, "La cámara Azure Kinect se calibra en modo de profundidad NFOV (campo de visión estrecho) sin agrupamiento a 30 FPS. "
              "El SDK oficial de seguimiento de cuerpos {cite:k4abt}, enlazado en Python mediante pyKinectAzure {cite:pykinect}, "
              "entrega 32 articulaciones en coordenadas métricas cartesianas. La herramienta de supervisión con OpenCV "
              "{cite:opencv} proyecta el esqueleto y envía datagramas UDP cada 30 ms con el vector de estado hacia Unity.")

    h2(doc, "Compilación del Corpus de Entrenamiento")
    para(doc, "El conjunto experimental consta de 98 secuencias tridimensionales de 35 fotogramas capturadas sobre 14 sujetos "
              "heterogéneos, categorizadas en siete posturas canónicas: reposo (*idle*), puñetazo derecho, puñetazo izquierdo, "
              "patada derecha, patada izquierda, agachado y bloqueo. Se descartaron deliberadamente los registros de transiciones "
              "dinámicas intermedias a fin de concentrar el aprendizaje exclusivamente en la topología de poses estacionarias.")

    h2(doc, "Diagnóstico del Extractor Cinemático Previo")
    para(doc, "El extractor inicial utilizaba 44 variables fundamentadas en velocidades máximas de extremidades y diferencias "
              "de desplazamiento respecto al primer cuadro. Dado que en el corpus de entrenamiento solo el reposo exhibía "
              "velocidades cercanas a cero, el algoritmo asoció la inmovilidad con la clase reposo. En consecuencia, al mantener "
              "un golpe estático, la velocidad nula colapsaba la predicción hacia reposo; recíprocamente, al ingresar un usuario "
              "en el campo del sensor, la velocidad de traslación disparaba golpes accidentales. Este diagnóstico motivó la "
              "reformulación hacia descriptores puramente espaciales.")

    h2(doc, "Descriptores Geométricos Estáticos Invariantes")
    para(doc, "Siguiendo los paradigmas de invariancia posicional formulados por Xia et al. {cite:xia}, el extractor se "
              "rediseñó con 44 atributos calculados respecto a la pelvis, filtrados con el algoritmo One-Euro {cite:casiez} "
              "y normalizados por las magnitudes antropométricas del torso, brazo (*L*_{b}) y pierna (*L*_{p}) del jugador. "
              "La taxonomía se resume en la {tab:feat}.")
    data_table(doc, "feat", "Familias de Descriptores Geométricos Estáticos",
               ["Familia Funcional", "Dim.", "Capacidad Discriminante"],
               [["Extensión planar de brazos", "15", "Separación de puñetazos derecho e izquierdo"],
                ["Elevación relativa de manos", "11", "Diferenciación de guardia/bloqueo frente a reposo"],
                ["Profundidad y asimetría de piernas", "13", "Discriminación de patadas bilaterales y agachado"],
                ["Ángulos articulares espaciales", "5", "Refuerzo angular de codos, rodillas e inclinación"],
                ["Espacio Total de Características", "44", "Siete posturas corporales invariantes"]],
               [1900, 540, 2600], ypos="top")
    h3(doc, "Extensión horizontal de extremidades superiores",
       "evalúa la proyección del segmento muñeca-hombro en el plano transversal normalizado:")
    equation(doc, "hext", "*e*_{h} = ‖(*x*_{m} − *x*_{s}, *z*_{m} − *z*_{s})‖ / *L*_{b}")
    para(doc, "donde los subíndices *m* y *s* corresponden a muñeca y hombro. Esta magnitud no se ve afectada si los brazos "
              "cuelgan verticalmente relajados, evitando confusiones presentes en distancias tridimensionales ingenuas.", first=0)
    h3(doc, "Elevación torácica de manos",
       "mide la distancia vertical de muñecas respecto a la columna torácica y cráneo, discriminando el bloqueo.")
    h3(doc, "Asimetría podal relativa",
       "computa el diferencial de profundidad vertical de los tobillos respecto a la pelvis normalizado:")
    equation(doc, "asym", "*a*_{t} = *y*_{ti} / *L*_{pi} − *y*_{td} / *L*_{pd}")
    para(doc, "cuyo signo discrimina la patada derecha (>0) de la izquierda (<0), mientras que magnitudes convergentes bajas "
              "caracterizan la flexión de agachado.", first=0)
    h3(doc, "Ángulos articulares espaciales",
       "determinan la flexión tridimensional de codos y rodillas mediante el producto interior euclidiano:")
    equation(doc, "angle", "θ = arccos( (#BA#·#BC#) / (‖#BA#‖ ‖#BC#‖) )")

    h2(doc, "Clasificación mediante Bosques Aleatorios")
    para(doc, "A partir del vector de 44 atributos, se entrenó un ensamble de bosques aleatorios propuesto por Breiman "
              "{cite:breiman} compuesto por 200 árboles de decisión con profundidad acotada a 10 niveles usando scikit-learn "
              "{cite:sklearn}. El clasificador se exportó al formato estándar ONNX mediante la herramienta sklearn-onnx "
              "{cite:skl2onnx} para su inferencia optimizada con ONNX Runtime {cite:onnxrt}.")

    h2(doc, "Activación Temporal y Bucle de Ataque")
    h3(doc, "Periodo de estabilización y calibración",
       "durante los primeros 1.5 s tras adquirir el esqueleto, se fuerza artificialmente el estado de reposo, suprimiendo "
       "los transitorios observados al entrar en cámara. Asimismo, se fijó el umbral de confianza mínima en 0.48.")
    h3(doc, "Comprobación biomecánica",
       "las predicciones deben verificar filtros anatómicos: en puñetazos, la extensión calculada en {eq:hext} debe superar "
       "0.48 y exceder en 0.04 al brazo opuesto; en patadas, la asimetría {eq:asym} debe exceder ±0.06; y en bloqueo, la elevación "
       "media debe superar 0.35.")
    h3(doc, "Bucle de ataque sostenido",
       "cuando una postura válida se sostiene de manera ininterrumpida por 0.5 s, el controlador `KinectFighterInput` fija "
       "el ataque y lo reitera en bucle hasta que el usuario retorne a reposo o modifique la configuración corporal, como "
       "se aprecia en el combate de la {fig:duel}.")
    figure(doc, "duel", os.path.join(CAPT_DIR, "fig4_story_mode_kinect_duel.png"),
           "Enfrentamiento del modo historia en el castillo Suzaku: el jugador adopta una postura sostenida de puñetazo derecho, "
           "reconocida por el motor con confianza 0.94 y ejecutada de forma continua sobre Ken.",
           ypos="bottom")

    # ======================= VI. RESULTADOS Y DISCUSIÓN =======================
    h1(doc, "Resultados y Discusión")
    h2(doc, "Validación Numérica de la Física Predictiva")
    para(doc, "Se ejecutó una auditoría computacional automatizada comparando 85 pasos de la simulación predictiva frente a "
              "un cuerpo rígido dinámico de Box2D en una escena aislada de Unity. El error de posición medido fue estrictamente "
              "nulo (0.000 unidades en todas las coordenadas), validando que la solución inversa {eq:inverse} reproduce con "
              "exactitud el integrador discreto. En pruebas funcionales sobre los cinco asaltos de la campaña, el sistema "
              "alcanzó 26 impactos exitosos en 27 lanzamientos (96.3 % de efectividad), requiriendo en el tercer asalto el "
              "uso de parábolas altas a 75° con rapidez de 13.8 m/s para sortear los muros.")

    h2(doc, "Métricas del Clasificador Somatosensorial")
    para(doc, "La evaluación del clasificador se estructuró mediante validación cruzada estratificada por sujetos (*Leave-Two-Subjects-Out*, "
              "7 particiones), asegurando que los patrones evaluados provinieran de individuos no observados en el entrenamiento. "
              "El modelo obtuvo una exactitud media de 95.92 % ± 5.20 %, registrándose puntuaciones entre 85.7 % y 100.0 % en las "
              "distintas rondas. Los atributos con mayor peso de Gini correspondieron a las asimetrías de tobillos, pies y muñecas.")
    para(doc, "La {tab:res} presenta la comparación de robustez entre el extractor cinemático original y el modelo geométrico "
              "propuesto frente a posturas sostenidas artificiales con ruido gaussiano de 2 mm. El enfoque original colapsó al "
              "24.5 % de acierto al anularse la velocidad de extremidades, mientras que la formulación geométrica mantuvo un 100 % "
              "de discriminación en condiciones controladas.")
    data_table(doc, "res", "Aciertos sobre Poses Sostenidas por Clase Postural",
               ["Clase de Combate", "Extractor Cinemático", "Extractor Geométrico"],
               [["Reposo (*Idle*)", "14/14 (100 %)", "14/14 (100 %)"],
                ["Puñetazo derecho", "0/14 (0 %)", "14/14 (100 %)"],
                ["Puñetazo izquierdo", "0/14 (0 %)", "14/14 (100 %)"],
                ["Patada derecha", "0/14 (0 %)", "14/14 (100 %)"],
                ["Patada izquierda", "0/14 (0 %)", "14/14 (100 %)"],
                ["Agachado (*Crouch*)", "0/14 (0 %)", "14/14 (100 %)"],
                ["Bloqueo (*Guard*)", "10/14 (71.4 %)", "14/14 (100 %)"],
                ["Exactitud Global", "24/98 (24.5 %)", "98/98 (100.0 %)"]],
               [1640, 1700, 1700], ypos="top")

    h2(doc, "Presupuesto Temporal y Latencia de Interacción")
    para(doc, "Para validar la respuesta en tiempo real requerida por un videojuego de lucha a 30 FPS (presupuesto de 33.33 ms por "
              "cuadro), se instrumentó el pipeline completo de percepción y transmisión. La {tab:lat} detalla los tiempos medios "
              "cronometrados a lo largo de 5000 cuadros consecutivos.")
    data_table(doc, "lat", "Presupuesto Temporal del Pipeline de Percepción Corporal",
               ["Etapa del Proceso", "Tiempo Medio", "Desviación Estándar"],
               [["Captura y estimación esquelética (Azure Kinect)", "16.60 ms", "± 1.20 ms"],
                ["Filtrado One-Euro y extracción de 44 atributos", "0.82 ms", "± 0.08 ms"],
                ["Inferencia ONNX (Random Forest, 200 árboles)", "0.38 ms", "± 0.04 ms"],
                ["Serialización y transmisión UDP (puerto 5005)", "0.24 ms", "± 0.03 ms"],
                ["Recepción y buffer en Unity (`KinectFighterInput`)", "0.45 ms", "± 0.06 ms"],
                ["Latencia Total de Interacción", "18.49 ms", "± 1.41 ms"],
                ["Margen Temporal Disponible (Presupuesto 33.33 ms)", "+14.84 ms", "(44.5 % holgura)"]],
               [2600, 1200, 1240], ypos="bottom")
    para(doc, "El retardo acumulado de 18.49 ms se ubica holgadamente por debajo del umbral de 33.33 ms, garantizando una tasa de "
              "refresco sin caída de cuadros ni encolamiento en el socket de red local.")

    h2(doc, "Comportamiento del Sistema de Patrullaje")
    para(doc, "El sistema de puntos de ruta demostró determinismo completo y cero asignaciones de memoria en el recolector de "
              "basura (*garbage collector*) durante el recorrido ordinario. La rutina `GetClosestWaypointIndex` requirió una media "
              "de 0.012 ms en CPU para seleccionar el nodo tras una evasión, permitiendo que los guardias reasuman el patrullaje "
              "sin discontinuidades visuales.")

    h2(doc, "Limitaciones del Estudio")
    para(doc, "Entre las limitaciones se identifica un tamaño de muestra de 14 sujetos en interiores, la ausencia de una clase "
              "para saltos verticales debido a restricciones de altura en el campo de visión del sensor, y la necesidad de conducir "
              "estudios psicométricos de experiencia de usuario en torneos presenciales.")

    # ======================= VII. CONCLUSIONES =======================
    h1(doc, "Conclusiones", page_break=False)
    para(doc, "El desarrollo e integración de los tres subsistemas en *Kinect Strike* demuestra que es posible combinar técnicas "
              "avanzadas de visión por computador, física matemática discreta e inteligencia artificial en una arquitectura de "
              "videojuegos coherente y de alto rendimiento. En primer lugar, el sistema de navegación por puntos de ruta probó "
              "que la alternancia modular entre circuitos cíclicos y de vaivén acoplados a una FSM reactiva genera patrones de "
              "guardia predecibles pero desafiantes. En segundo lugar, se demostró analítica y experimentalmente que la física "
              "predictiva para motores de videojuegos debe emular el integrador discreto de Euler semi-implícito en lugar de las "
              "ecuaciones continuas analíticas, anulando una deriva teórica de 0.294 m y alcanzando un error de impacto de cero. "
              "Finalmente, la transición de descriptores cinemáticos basados en velocidad hacia descriptores geométricos estáticos "
              "normalizados permitió resolver el reconocimiento de posturas de combate sostenidas con 95.92 % de exactitud general, "
              "mientras que la calibración temporal de 1.5 s eliminó completamente las activaciones accidentales.")
    para(doc, "Como trabajos futuros se proyecta el entrenamiento de redes convolucionales sobre mapas de profundidad para la "
              "detección de saltos acrobáticos, la incorporación de un árbol de comportamiento jerárquico para los guardias del "
              "dojo, y la evaluación de transferibilidad del clasificador en entornos de juego multijugador en red.")

    # ======================= COMPONENTES SIN NUMERAR =======================
    component_heading(doc, "Agradecimientos")
    para(doc, "Los autores expresan su agradecimiento al Dr. José Sulla Torres y a la Mg. Roxana Limache por su rigurosa asesoría "
              "académica y valiosas observaciones durante el desarrollo de este proyecto en el curso de Laboratorio de Desarrollo de "
              "Software para Juegos de la Universidad Nacional de San Agustín de Arequipa.")

    component_heading(doc, "Referencias")
    unused = [k for k in REFERENCES if k not in cite_order]
    assert not unused, f"Referencias no citadas en el texto: {unused}"

    for n, key in enumerate(cite_order, 1):
        p_ref = doc.add_paragraph()
        pf = p_ref.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.left_indent = Inches(0.28)
        pf.first_line_indent = Inches(-0.28)
        pf.space_after = Pt(1.5)
        pf.tab_stops.add_tab_stop(Inches(0.28))
        r_num = p_ref.add_run(f"[{n}]\t")
        set_run_font(r_num, 8)
        add_rich(p_ref, REFERENCES[key], 8)

    # Guardar en Escritorio y en carpeta Docs
    out_desktop = os.path.join(DESKTOP, OUT_NAME)
    doc.save(out_desktop)
    out_docs = os.path.join(ROOT_DIR, "Docs", OUT_NAME)
    shutil.copyfile(out_desktop, out_docs)
    out_desktop_alt = os.path.join(DESKTOP, "Articulo_IEEE_KinectStrike_Autores_UNSA.docx")
    shutil.copyfile(out_desktop, out_desktop_alt)

    print(f"Resumen: {len(abstract.split())} palabras (Límite: <= 200).")
    print(f"Referencias citadas: {len(cite_order)} / {len(REFERENCES)}.")
    print(f"Ecuaciones registradas: {eq_counter[0]} / {len(EQ_ORDER)}.")
    print(f"Generado exitosamente en Escritorio: {out_desktop}")
    print(f"Copia sincronizada en Docs: {out_docs}")


if __name__ == "__main__":
    build()
