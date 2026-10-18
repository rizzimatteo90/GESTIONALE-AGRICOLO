import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def genera_pdf_rapportino(r_data, r_ut, r_cli, r_ore, r_note, dettagli_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1A365D"), spaceAfter=12
    )
    
    story.append(Paragraph("NICOLI RIZZI S.R.L.", title_style))
    story.append(Paragraph("<b>Rapportino Giornaliero Attività</b>", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    info_data = [
        [Paragraph(f"<b>Data:</b> {r_data}", styles['Normal']), Paragraph(f"<b>Operatore:</b> {r_ut}", styles['Normal'])],
        [Paragraph(f"<b>Cliente:</b> {r_cli}", styles['Normal']), Paragraph(f"<b>Ore Totali:</b> {r_ore} h", styles['Normal'])],
    ]
    t_info = Table(info_data, colWidths=[250, 250])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))
    
    if r_note:
        story.append(Paragraph(f"<b>Note Generali:</b> {r_note}", styles['Normal']))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("<b>Dettaglio Lavorazioni</b>", styles['Heading3']))
    story.append(Spacer(1, 6))
    
    table_data = [["Ora Inizio", "Ora Fine", "Mezzo / Attrezzatura", "Descrizione Attività"]]
    for _, row in dettagli_df.iterrows():
        table_data.append([
            str(row.get('Ora Inizio', '')),
            str(row.get('Ora Fine', '')),
            str(row.get('Mezzo / Attrezzatura', '')),
            str(row.get('Descrizione Lavoro', ''))
        ])
        
    t_det = Table(table_data, colWidths=[65, 65, 150, 220])
    t_det.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_det)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_report_mensile(titolo, df_dati):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1A365D"), spaceAfter=12
    )
    
    story.append(Paragraph("NICOLI RIZZI S.R.L.", title_style))
    story.append(Paragraph(f"<b>{titolo}</b>", styles['Heading2']))
    story.append(Spacer(1, 15))
    
    if df_dati.empty:
        story.append(Paragraph("Nessun dato registrato per il periodo selezionato.", styles['Normal']))
    else:
        table_data = [[Paragraph(f"<b>{col}</b>", styles['Normal']) for col in df_dati.columns]]
        for _, row in df_dati.iterrows():
            table_data.append([Paragraph(str(val), styles['Normal']) for val in row])
            
        col_width = 500 / len(df_dati.columns)
        t_rep = Table(table_data, colWidths=[col_width] * len(df_dati.columns))
        t_rep.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_rep)
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()