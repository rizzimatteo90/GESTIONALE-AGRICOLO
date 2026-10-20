from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def _pdf(title, rows):
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=1.5*cm,leftMargin=1.5*cm,topMargin=1.5*cm,bottomMargin=1.5*cm)
    styles=getSampleStyleSheet(); story=[Paragraph('NICOLI RIZZI S.R.L.',styles['Title']),Paragraph(title,styles['Heading2']),Spacer(1,12)]
    data=[[str(x) for x in row] for row in rows]
    if data:
        t=Table(data,repeatRows=1,hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2f6b4f')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#d6ded8')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f6f3')]),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)])); story.append(t)
    doc.build(story); return buf.getvalue()
def genera_pdf_rapportino(data,utente,cliente,ore,note,df_det):
    rows=[['Data',str(data)],['Operatore',str(utente)],['Cliente',str(cliente)],['Ore totali',str(ore)],['Note',str(note or '')]]
    rows += [['Ora inizio','Ora fine','Mezzo','Attività']]
    for _,r in df_det.iterrows(): rows.append([r.iloc[0],r.iloc[1],r.iloc[2],r.iloc[3]])
    return _pdf('Rapportino giornaliero',rows)
def genera_pdf_report_mensile(titolo,df):
    rows=[list(df.columns)] + [[str(v) if v is not None else '' for v in row] for row in df.fillna('').itertuples(index=False,name=None)]
    return _pdf(titolo,rows)
