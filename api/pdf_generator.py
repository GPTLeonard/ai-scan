from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, KeepInFrame, NextPageTemplate, FrameBreak
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
import re
from html import escape as html_escape

# Symbis Colors
COLOR_DARK = colors.HexColor("#243305")
COLOR_ACCENT = colors.HexColor("#94A807")
COLOR_BG = colors.HexColor("#F5F7F0")
COLOR_WHITE = colors.white
COLOR_TEXT = colors.HexColor("#333333")
COLOR_GREY_LIGHT = colors.HexColor("#E5E7EB")

# Robust Path Handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'assets')

# -----------------------------
# 1) Font & Style Configuration
# -----------------------------
FONT_BODY = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

def get_styles():
    return {
        'H1': PS(name='H1', fontName=FONT_BOLD, fontSize=26, leading=30, textColor=COLOR_DARK, spaceAfter=20, splitLongWords=1, wordWrap='LTR'),
        'H2': PS(name='H2', fontName=FONT_BOLD, fontSize=14, textColor=COLOR_ACCENT, leading=18, spaceBefore=15, spaceAfter=5, splitLongWords=1, wordWrap='LTR'),
        'Body': PS(name='Body', fontName=FONT_BODY, fontSize=10, leading=14, textColor=COLOR_TEXT, spaceAfter=10, splitLongWords=1, wordWrap='LTR'),
        'CardTitle': PS(name='CardTitle', fontName=FONT_BOLD, fontSize=11, leading=13, textColor=COLOR_DARK, alignment=TA_CENTER, splitLongWords=1, wordWrap='LTR'),
        'CardSub': PS(name='CardSub', fontName=FONT_BOLD, fontSize=9, leading=11, textColor=COLOR_ACCENT, alignment=TA_CENTER, splitLongWords=1, wordWrap='LTR'),
        'CardBody': PS(name='CardBody', fontName=FONT_BODY, fontSize=9, leading=12, textColor=COLOR_TEXT, splitLongWords=1, wordWrap='LTR')
    }

# -----------------------------
# 2) Text Cleaning
# -----------------------------
def md_to_reportlab_markup(text: str) -> str:
    if text is None: return ""
    t = str(text).strip()
    t = html_escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    t = t.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")
    return t

# -----------------------------
# 3) Logo & Header Logic
# -----------------------------
def draw_logo_fit(c, logo_path, x, y_top, max_w, max_h):
    """Draws logo strictly within bounding box."""
    try:
        ir = ImageReader(logo_path)
        iw, ih = ir.getSize()
        if iw <= 0 or ih <= 0: return

        # Calculate scale to fit within box
        scale = min(max_w / iw, max_h / ih)
        w = iw * scale
        h = ih * scale

        # y_top is top edge, reportlab draws from bottom-left
        y = y_top - h 
        c.drawImage(ir, x, y, width=w, height=h, mask="auto", preserveAspectRatio=True)
    except Exception:
        pass

def draw_header(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize 
    
    # Top Line Accent
    canvas.setFillColor(COLOR_ACCENT)
    canvas.rect(0, height - 0.2*cm, width, 0.2*cm, fill=1, stroke=0)
    
    # Logo Logic
    logo_path = os.path.join(ASSETS_DIR, 'symbis_logo_full.png')
    if os.path.exists(logo_path):
        # Define logo box
        x = 1.5 * cm
        y_top = height - 0.8 * cm # Some padding from top line
        max_w = 6.0 * cm
        max_h = 1.6 * cm
        draw_logo_fit(canvas, logo_path, x, y_top, max_w, max_h)
            
    # Right Header Text
    canvas.setFont(FONT_BOLD, 10)
    canvas.setFillColor(COLOR_DARK)
    canvas.drawRightString(width - 1.5*cm, height - 2*cm, "AI & AUTOMATISERING SCAN")
    
    canvas.restoreState()

# -----------------------------
# 4) Page Numbers
# -----------------------------
class SymbisCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        w, h = self._pagesize
        self.setLineWidth(0.5)
        self.setStrokeColor(COLOR_GREY_LIGHT)
        self.line(1.5*cm, 1.5*cm, w - 1.5*cm, 1.5*cm)
        self.setFont(FONT_BODY, 8)
        self.setFillColor(colors.grey)
        self.drawString(1.5*cm, 0.8*cm, "Symbis B.V. | www.symbis.nl")
        self.drawRightString(w - 1.5*cm, 0.8*cm, f"Pagina {self._pageNumber} / {page_count}")
        self.restoreState()

# -----------------------------
# 5) Components
# -----------------------------
def get_roadmap_visual(roadmap, col_width, styles):
    steps = [("VANDAAG", roadmap.get('vandaag', '...')), ("DEZE WEEK", roadmap.get('deze_week', '...')), ("DEZE MAAND", roadmap.get('deze_maand', '...'))]
    rows = []
    bullet_w = 1.5*cm
    text_w = col_width - bullet_w - 0.5*cm
    
    for idx, (time, text) in enumerate(steps):
        num = str(idx + 1)
        p_num = Paragraph(f"<font color='white'><b>{num}</b></font>", PS('StepNum', fontName=FONT_BOLD, alignment=TA_CENTER, fontSize=12, leading=14))
        content = [
            Paragraph(md_to_reportlab_markup(time), PS('StepTitle', fontName=FONT_BOLD, fontSize=10, textColor=COLOR_DARK)),
            Paragraph(md_to_reportlab_markup(text), PS('StepDesc', fontName=FONT_BODY, fontSize=9, textColor=COLOR_TEXT))
        ]
        rows.append([p_num, content])
        
    t = Table(rows, colWidths=[bullet_w, text_w])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Bullet centered vertically
        ('VALIGN', (1,0), (1,-1), 'TOP'),     # Text top aligned
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,0), (0,0), COLOR_ACCENT), ('BACKGROUND', (0,1), (0,1), COLOR_ACCENT), ('BACKGROUND', (0,2), (0,2), COLOR_ACCENT),
        ('LEFTPADDING', (0,0), (0,-1), 0), ('RIGHTPADDING', (0,0), (0,-1), 0), # No padding in bullet cells
        ('LEFTPADDING', (1,0), (1,-1), 10), # Padding for text
        ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10) # Row padding
    ]))
    return t

# -----------------------------
# 6) Main Generator
# -----------------------------
def generate_pdf(data: dict, company_name: str) -> bytes:
    buffer = BytesIO()
    page_w, page_h = landscape(A4)
    # Margins
    margin_top, margin_bottom = 2.8*cm, 2*cm
    margin_left, margin_right = 1.5*cm, 1.5*cm
    content_width = page_w - margin_left - margin_right
    content_height = page_h - margin_top - margin_bottom
    
    doc = BaseDocTemplate(buffer, pagesize=(page_w, page_h))
    
    # Frames
    col_gap = 1*cm
    w_col1 = (content_width - col_gap) * 0.65
    w_col2 = (content_width - col_gap) * 0.35
    
    frames_p1 = [
        Frame(margin_left, margin_bottom, w_col1, content_height, id='col1', showBoundary=0, topPadding=0, bottomPadding=0),
        Frame(margin_left + w_col1 + col_gap, margin_bottom, w_col2, content_height, id='col2', showBoundary=0, topPadding=0, bottomPadding=0)
    ]
    frames_p2 = [Frame(margin_left, margin_bottom, content_width, content_height, id='normal', showBoundary=0, topPadding=0, bottomPadding=0)]
    
    doc.addPageTemplates([
        PageTemplate(id='page1', frames=frames_p1, onPage=draw_header),
        PageTemplate(id='page2', frames=frames_p2, onPage=draw_header)
    ])
    
    styles = get_styles()
    story = []
    
    # --- PAGE 1 ---
    story.append(Paragraph(f"Adviesrapport: {company_name}", styles['H1']))
    story.append(Spacer(1, 0.5*cm))
    
    score = data.get("symbis_score", {})
    story.append(Paragraph("HUIDIGE FASE", styles['H2']))
    story.append(Paragraph(f"<font size=18 color='#243305'><b>{md_to_reportlab_markup(score.get('huidige_fase', 'Startpunt'))}</b></font>", styles['Body']))
    story.append(Paragraph(md_to_reportlab_markup(score.get('score_toelichting', '')), styles['Body']))
    
    analysis = data.get("bedrijfs_analyse", {})
    story.append(Paragraph("ANALYSE", styles['H2']))
    story.append(Paragraph(f"<b>Samenvatting:</b> {md_to_reportlab_markup(analysis.get('samenvatting', ''))}", styles['Body']))
    
    story.append(Paragraph("JOUW EERSTE STAPPEN", styles['H2']))
    story.append(Spacer(1, 0.2*cm))
    story.append(get_roadmap_visual(data.get("roadmap", {}), w_col1, styles))
    
    story.append(FrameBreak())
    
    hero_path = os.path.join(ASSETS_DIR, 'cover_hero.webp')
    if os.path.exists(hero_path):
        story.append(Image(hero_path, width=w_col2, height=4.0*cm, kind='proportional'))
    else: story.append(Spacer(1, 4.0*cm))
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("<b>Jouw Adviseur</b>", styles['H2']))
    story.append(Paragraph("Heb je vragen over dit rapport? Ik kijk graag met je mee.", styles['Body']))
    contact_path = os.path.join(ASSETS_DIR, 'contact_image.webp')
    if os.path.exists(contact_path):
        story.append(Spacer(1, 0.5*cm))
        story.append(Image(contact_path, width=w_col2, height=4.0*cm, kind='proportional'))
    story.append(Paragraph("<b>Symbis B.V.</b><br/>085 - 123 45 67<br/>info@symbis.nl", styles['Body']))
    
    # --- PAGE 2 ---
    story.append(NextPageTemplate('page2'))
    story.append(PageBreak())
    
    story.append(Paragraph("Aanbevolen Oplossingen", styles['H1']))
    story.append(Spacer(1, 0.5*cm))
    
    # DYNAMIC CARDS
    adviezen = data.get("advies_secties", [])
    # Limit to 3, but handle fewer
    adviezen = adviezen[:3]
    num_cards = len(adviezen)
    
    if num_cards > 0:
        gap_w = 0.7*cm
        # Calculate Card Width based on 3-card layout for consistency
        # Max width if 3 cards were present: (total - 2*gap) / 3
        std_card_w = (content_width - 2*gap_w) / 3.0
        card_h = 10*cm # Fixed height for uniformity
        
        row_data = []
        col_widths = []
        table_style = []
        
        # Helper to create card Content
        def make_card(adv):
            content = [
                Paragraph(md_to_reportlab_markup(adv.get('titel', 'Advies')), styles['CardTitle']),
                Spacer(1, 5),
                Paragraph(md_to_reportlab_markup(adv.get('tool', '').upper()), styles['CardSub']),
                Spacer(1, 10),
                Paragraph(md_to_reportlab_markup(adv.get('beschrijving', '')), styles['CardBody']),
                Spacer(1, 10),
                Paragraph(f"<b>Impact:</b><br/>{md_to_reportlab_markup(adv.get('impact',''))}", styles['CardBody'])
            ]
            # Wrap in KeepInFrame to enforce height limits / shrinking
            return KeepInFrame(std_card_w, card_h, content, mode='shrink')

        if num_cards == 3:
            # [C] [gap] [C] [gap] [C]
            col_widths = [std_card_w, gap_w, std_card_w, gap_w, std_card_w]
            row_data = [make_card(adviezen[0]), '', make_card(adviezen[1]), '', make_card(adviezen[2])]
            # Styles: cell 0, 2, 4 get boxes. cell 1, 3 are empty.
            active_cols = [0, 2, 4]

        elif num_cards == 2:
            # Center 2 cards: [gutter] [C] [gap] [C] [gutter]
            gutter = (content_width - (2*std_card_w + gap_w)) / 2.0
            col_widths = [gutter, std_card_w, gap_w, std_card_w, gutter]
            row_data = ['', make_card(adviezen[0]), '', make_card(adviezen[1]), '']
            active_cols = [1, 3]

        elif num_cards == 1:
            # Center 1 card: [gutter] [C] [gutter]
            gutter = (content_width - std_card_w) / 2.0
            col_widths = [gutter, std_card_w, gutter]
            row_data = ['', make_card(adviezen[0]), '']
            active_cols = [1]
            
        # Build Table Style
        t_style_cmds = [('VALIGN', (0,0), (-1,-1), 'TOP')]
        for col_idx in active_cols:
            t_style_cmds.append(('BACKGROUND', (col_idx,0), (col_idx,0), COLOR_BG))
            t_style_cmds.append(('BOX', (col_idx,0), (col_idx,0), 1, COLOR_ACCENT))
            t_style_cmds.append(('LEFTPADDING', (col_idx,0), (col_idx,0), 10))
            t_style_cmds.append(('RIGHTPADDING', (col_idx,0), (col_idx,0), 10))
            t_style_cmds.append(('TOPPADDING', (col_idx,0), (col_idx,0), 10))
            t_style_cmds.append(('BOTTOMPADDING', (col_idx,0), (col_idx,0), 10))

        t_cards = Table([row_data], colWidths=col_widths)
        t_cards.setStyle(TableStyle(t_style_cmds))
        story.append(t_cards)
    
    story.append(Spacer(1, 1.5*cm))

    # Reference Case
    case = data.get("relevant_case", {})
    if case:
        story.append(Paragraph("INSPIRATIE UIT DE PRAKTIJK", styles['H2']))
        case_txt = [
             Paragraph(md_to_reportlab_markup(case.get("titel", "")), PS('CT', parent=styles['H2'], fontSize=14, textColor=COLOR_WHITE)),
             Spacer(1, 5),
             Paragraph(md_to_reportlab_markup(case.get("beschrijving", "")), PS('CD', parent=styles['Body'], fontSize=10, textColor=COLOR_WHITE)),
             Spacer(1, 10),
             Paragraph(f"<b>Waarom relevant:</b> {md_to_reportlab_markup(case.get('waarom_relevant', ''))}", PS('CR', parent=styles['Body'], fontSize=10, textColor=COLOR_ACCENT))
        ]
        t_case = Table([[case_txt]], colWidths=[content_width])
        t_case.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), COLOR_DARK), ('LEFTPADDING', (0,0), (-1,-1), 20), ('RIGHTPADDING', (0,0), (-1,-1), 20), ('TOPPADDING', (0,0), (-1,-1), 20), ('BOTTOMPADDING', (0,0), (-1,-1), 20)]))
        story.append(t_case)

    doc.build(story, canvasmaker=SymbisCanvas)
    buffer.seek(0)
    return buffer.getvalue()
