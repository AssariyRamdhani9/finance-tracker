# backend/app/routers/export.py

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from app.core.security import verify_token
from app.core.config import settings
from supabase import create_client
import pandas as pd
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

router = APIRouter(prefix="/export", tags=["Export"])
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def get_transactions_data(user_id: str, month: str = None):
    """Ambil data transaksi untuk export"""
    
    query = supabase.table("transactions")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("transaction_date", desc=True)
    
    if month:

        year, month_num = month.split('-')
        start_date = f"{year}-{month_num}-01"
        
        next_month = int(month_num) + 1
        next_year = int(year)
        if next_month > 12:
            next_month = 1
            next_year += 1
        end_date = f"{next_year:04d}-{next_month:02d}-01"
        
        query = query.gte("transaction_date", start_date).lt("transaction_date", end_date)
    
    response = query.execute()
    return response.data

@router.get("/csv")
async def export_csv(
    month: str = None,
    current_user: dict = Depends(verify_token)
):
    """Export transaksi ke CSV"""
    
    data = get_transactions_data(current_user["user_id"], month)
    
    if not data:
        raise HTTPException(404, "No transactions found")
    

    df = pd.DataFrame(data)
    

    columns = ['transaction_date', 'description', 'category', 'merchant', 'amount']
    df = df[columns]
    

    df.columns = ['Tanggal', 'Deskripsi', 'Kategori', 'Toko', 'Jumlah (Rp)']
    

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, sep=';')
    csv_buffer.seek(0)
    

    filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=csv_buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/excel")
async def export_excel(
    month: str = None,
    current_user: dict = Depends(verify_token)
):
    """Export transaksi ke Excel"""
    
    data = get_transactions_data(current_user["user_id"], month)
    
    if not data:
        raise HTTPException(404, "No transactions found")
    

    df = pd.DataFrame(data)
    

    columns = ['transaction_date', 'description', 'category', 'merchant', 'amount']
    df = df[columns]
    df.columns = ['Tanggal', 'Deskripsi', 'Kategori', 'Toko', 'Jumlah (Rp)']
    

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Transaksi', index=False)
        

        worksheet = writer.sheets['Transaksi']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    excel_buffer.seek(0)
    
    filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return Response(
        content=excel_buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/pdf")
async def export_pdf(
    month: str = None,
    current_user: dict = Depends(verify_token)
):
    """Export transaksi ke PDF"""
    
    data = get_transactions_data(current_user["user_id"], month)
    
    if not data:
        raise HTTPException(404, "No transactions found")
    

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    

    title = Paragraph("Laporan Transaksi Keuangan", title_style)
    

    if month:
        subtitle = Paragraph(f"Periode: {month}", styles['Normal'])
    else:
        subtitle = Paragraph("Semua Transaksi", styles['Normal'])
    

    table_data = [
        ['No', 'Tanggal', 'Deskripsi', 'Kategori', 'Toko', 'Jumlah (Rp)']
    ]
    
    total = 0
    for i, t in enumerate(data, 1):
        amount = float(t.get('amount', 0))
        total += amount
        table_data.append([
            str(i),
            t.get('transaction_date', '-'),
            t.get('description', '-')[:40],
            t.get('category', '-'),
            t.get('merchant', '-') or '-',
            f"Rp {amount:,.0f}"
        ])
    
    table_data.append(['', '', '', '', 'TOTAL', f"Rp {total:,.0f}"])
    
    # Create table
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 4),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    
  
    elements = [title, subtitle, Spacer(1, 0.2*inch), table]
    doc.build(elements)
    
    pdf_buffer.seek(0)
    
    filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/summary")
async def export_summary(
    month: str = None,
    current_user: dict = Depends(verify_token)
):
    """Export summary ke Excel"""
    
    data = get_transactions_data(current_user["user_id"], month)
    
    if not data:
        raise HTTPException(404, "No transactions found")
    
    df = pd.DataFrame(data)
    
    summary = df.groupby('category')['amount'].sum().reset_index()
    summary.columns = ['Kategori', 'Total']
    summary['Total'] = summary['Total'].apply(lambda x: f"Rp {x:,.0f}")
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_detail = df[['transaction_date', 'description', 'category', 'merchant', 'amount']]
        df_detail.columns = ['Tanggal', 'Deskripsi', 'Kategori', 'Toko', 'Jumlah']
        df_detail.to_excel(writer, sheet_name='Detail Transaksi', index=False)
        

        summary.to_excel(writer, sheet_name='Ringkasan', index=False)
        

        stats = pd.DataFrame({
            'Statistik': [
                'Total Transaksi',
                'Total Pengeluaran',
                'Rata-rata per Transaksi',
                'Transaksi Tertinggi',
                'Transaksi Terendah',
                'Kategori Terbanyak'
            ],
            'Nilai': [
                len(df),
                f"Rp {df['amount'].sum():,.0f}",
                f"Rp {df['amount'].mean():,.0f}",
                f"Rp {df['amount'].max():,.0f}",
                f"Rp {df['amount'].min():,.0f}",
                df['category'].mode().iloc[0] if not df.empty else '-'
            ]
        })
        stats.to_excel(writer, sheet_name='Statistik', index=False)
    
    excel_buffer.seek(0)
    
    filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return Response(
        content=excel_buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )