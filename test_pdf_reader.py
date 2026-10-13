
from pdf_reader import extract_text
from invoice_extractor import extract_invoice_fields
from invoice_validator import validate_invoice

pdf_text = extract_text("samples/sample_invoice2.pdf")

if not pdf_text.strip():
    raise ValueError("No extractable text found in the PDF.")

invoice = extract_invoice_fields(pdf_text)
validation = validate_invoice(invoice)

print("\nExtracted invoice:")
print(invoice)

print("\nValidation:")
print(validation)

if validation["needs_review"]:
    print("\nPlease review this invoice before accepting it.")
else:
    print("\nBasic validation passed. Human review is still recommended.")
