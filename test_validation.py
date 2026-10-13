
from invoice_validator import validate_invoice

invoice = {
    "vendor": "Demo Supplies",
    "invoice_date": "2026-10-10",
    "subtotal": "$85.00",
    "tax": "$8.50",
    "total": "$95.50"
}

result = validate_invoice(invoice)
print(result)
