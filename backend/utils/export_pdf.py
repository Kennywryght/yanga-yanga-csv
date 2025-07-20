# utils/export_pdf.py

from fpdf import FPDF
import pandas as pd

def generate_pdf_report(df_summary, total_income, total_spent, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Yanga Yanga Monthly Spending Report", ln=True, align="C")

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Total Income: MWK {total_income:,.2f}", ln=True)
    pdf.cell(0, 10, f"Total Spending: MWK {total_spent:,.2f}", ln=True)
    pdf.ln(10)

    # Table header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 10, "Category", 1)
    pdf.cell(50, 10, "Amount (MWK)", 1)
    pdf.cell(50, 10, "Percentage (%)", 1)
    pdf.ln()

    # Table data
    pdf.set_font("Arial", '', 12)
    for row in df_summary:
        pdf.cell(80, 10, str(row['Category']), 1)
        pdf.cell(50, 10, f"{row['Amount (MWK)']:.2f}", 1)
        pdf.cell(50, 10, f"{row['Percentage']:.2f}", 1)
        pdf.ln()

    pdf.output(output_path)
