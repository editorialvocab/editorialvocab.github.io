import json
import os
from fpdf import FPDF

def generate_monthly_pdf(json_path, output_filename, month_name):
    if not os.path.exists(json_path):
        print(f"Data not found for {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title Page
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 60, f"Vocabulary Mastery: {month_name}", ln=True, align='C')
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "Daily Editorials & Vocabulary Official Guide", ln=True, align='C')
    pdf.add_page()

    # Words
    for entry in data:
        word = entry.get('word', 'N/A').upper()
        meaning = entry.get('hindi_meaning', entry.get('bangla_meaning', ''))
        definition = entry.get('definition', '')
        example = entry.get('example', '')

        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(10, 15, 30) # Navy color from your style.css
        pdf.cell(0, 10, word, ln=True)
        
        pdf.set_font("Helvetica", "I", 12)
        pdf.set_text_color(201, 168, 76) # Gold color
        pdf.cell(0, 8, meaning, ln=True)
        
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Definition: {definition}")
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 6, f"Example: \"{example}\"")
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    pdf.output(output_filename)
    print(f"Ebook generated: {output_filename}")

if __name__ == "__main__":
    # Example usage for April 2026
    # Path structure based on your project_reference.md
    generate_monthly_pdf("../EdData/data/WordOfTheDayEnToHn/04-2026.json", "Vocab_India_April_2026.pdf", "April 2026")