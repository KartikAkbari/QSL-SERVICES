from flask import Flask, request, send_file
from fpdf import FPDF
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

class InvoicePDF(FPDF):
    def header(self):
        # Draw a simple black border around the page content
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.6)
        self.rect(8, 8, 194, 281)  # A4: 210x297, so 8 units margin
        # Header image (right-aligned, top)
        self.image("static/Header.jpg", x=100, y=10, w=100)
        self.set_font("Arial", "", 11)
        left_lines = [
            "cube one GmbH",
            "Hauptstraße 23",
            "55270 Klein-Winternheim",
            "Deutschland"
        ]
        right_labels = [
            "Rechnungs-Nr.",
            "Rechnungsdatum",
            "Referenz",
            "Leistungszeitraum",
            "Ihre Kundennummer",
            "Ihr Ansprechpartner"
        ]
        right_values = [
            getattr(self, "invoice_number", ""),
            getattr(self, "invoice_date", ""),
            getattr(self, "reference", ""),
            getattr(self, "period", ""),
            getattr(self, "customer_number", ""),
            getattr(self, "contact_person", "")
        ]
        y_start = 35
        for i in range(max(len(left_lines), len(right_labels))):
            self.set_xy(10, y_start + i * 7)
            self.set_font("Arial", "", 11)
            self.cell(90, 7, left_lines[i] if i < len(left_lines) else "", 0, 0, "L")
            self.set_font("Arial", "", 10)
            if i < len(right_labels):
                self.set_xy(110, y_start + i * 7)
                self.cell(40, 7, right_labels[i], 0, 0, "L")
                self.set_font("Arial", "B", 10)
                self.cell(40, 7, right_values[i], 0, 0, "L")
        # Store the y position after the last header row for use in the body
        self._after_header_y = y_start + max(len(left_lines), len(right_labels)) * 7 + 5

    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", "", 8)
        col1 = "Hiren Lakhani\nSeeweg 119\n89160 Dornstadt\nDeutschland"
        col2 = "Tel.: +49-17641576497\nE-Mail: qualificationservices@gmail.com"
        col3 = "USt.-ID: DE344672403\nSteuer-Nr.: 151/243/10064\nInhaber/-in: Hiren Lakhani"
        col4 = "Deutsche Kreditbank AG\nIBAN: DE17120300001201022496\nBIC: BYLADEM1001"
        self.set_x(10)
        self.multi_cell(45, 4, col1, align="L")
        self.set_xy(55, self.get_y() - 12)
        self.multi_cell(45, 4, col2, align="L")
        self.set_xy(100, self.get_y() - 12)
        self.multi_cell(45, 4, col3, align="L")
        self.set_xy(145, self.get_y() - 12)
        self.multi_cell(55, 4, col4, align="L")
        self.set_y(-10)
        self.cell(0, 10, f"Seite {self.page_no()} von {{nb}}", 0, 0, "R")

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    data = request.get_json()
    os.makedirs("invoices", exist_ok=True)

    pdf = InvoicePDF()
    pdf.alias_nb_pages()
    pdf.invoice_number = data.get('invoiceNumber', 'RE-XXXX')
    pdf.invoice_date = data.get('date', '25.06.2025')
    pdf.reference = data.get('reference', 'Projekt BI-Belgien')
    pdf.period = data.get('period', '01.06.2025 - 22.06.2025')
    pdf.customer_number = data.get('customerNumber', '1021')
    pdf.contact_person = data.get('contactPerson', 'Hiren Lakhani')
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    # Title (start below the header rows)
    pdf.set_xy(10, pdf._after_header_y)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Rechnung Nr. {pdf.invoice_number}", ln=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihren Auftrag und das damit verbundene Vertrauen!\nHiermit stelle ich Ihnen die folgenden Leistungen in Rechnung:")
    pdf.ln(2)

    # Table header
    pdf.set_fill_color(225, 225, 225)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(15, 10, "Pos.", 1, 0, "C", True)
    pdf.cell(80, 10, "Beschreibung", 1, 0, "C", True)
    pdf.cell(30, 10, "Menge", 1, 0, "C", True)
    pdf.cell(35, 10, "Einzelpreis", 1, 0, "C", True)
    pdf.cell(30, 10, "Gesamtpreis", 1, 1, "C", True)

    # Table rows for each service
    pdf.set_font("Arial", "", 12)
    services = data.get('services', [])
    net_total = 0
    for idx, service in enumerate(services):
        desc = service.get('description', '')
        qty = float(service.get('quantity', 0))
        price = float(service.get('price', 0))
        total = qty * price
        net_total += total
        pdf.cell(15, 10, f"{idx+1}.", 1, 0, "C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, desc, 1, 0, "L")
        pdf.set_font("Arial", "", 12)
        pdf.cell(30, 10, f"{qty:.2f} Stk", 1, 0, "C")
        pdf.cell(35, 10, f"{price:,.2f} EUR", 1, 0, "R")
        pdf.cell(30, 10, f"{total:,.2f} EUR", 1, 1, "R")
    y_totals = pdf.get_y()

    # Totals section (labels left, values right-aligned with Gesamtpreis)
    tax_name = data.get('taxName', 'Umsatzsteuer 19%')
    tax_rate = float(data.get('taxRate', 19))
    tax_amount = net_total * (tax_rate / 100)
    gross = net_total + tax_amount

    label_x = 10
    value_x = 170  # Start of Gesamtpreis column
    label_width = 160  # Spans all columns except the last
    value_width = 30   # Same as Gesamtpreis column

    pdf.set_font("Arial", "", 12)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.4)

    pdf.set_xy(label_x, y_totals)
    pdf.cell(label_width, 10, "Gesamtbetrag netto", 1, 0, "L", True)
    pdf.cell(value_width, 10, f"{net_total:,.2f} EUR", 1, 1, "R", True)
    pdf.set_xy(label_x, pdf.get_y())
    pdf.cell(label_width, 10, f"zzgl. {tax_name}", 1, 0, "L", True)
    pdf.cell(value_width, 10, f"{tax_amount:,.2f} EUR", 1, 1, "R", True)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.set_fill_color(235, 235, 235)
    pdf.set_xy(label_x, pdf.get_y())
    pdf.cell(label_width, 10, "Gesamtbetrag brutto", 1, 0, "L", True)
    pdf.cell(value_width, 10, f"{gross:,.2f} EUR", 1, 1, "R", True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)

    # Payment instructions
    pdf.multi_cell(0, 8, "Bitte überweisen Sie den Rechnungsbetrag unter Angabe der Rechnungsnummer auf das unten angegebene Konto.\n\nMit freundlichen Grüßen\nHiren Lakhani")

    filename = f"Invoice_{data['clientName'].replace(' ', '_')}.pdf"
    filepath = os.path.join("invoices", filename)
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)