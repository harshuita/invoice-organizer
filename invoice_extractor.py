
import ollama
import json

def extract_invoice_fields(invoice_text):
    response = ollama.chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "system",
                "content": """
You extract information from invoice text.
Return only the requested invoice fields.
Do not guess missing information.
Use null for missing values.
"""
            },
            {
                "role": "user",
                "content": f"""
Extract these fields from the invoice:
- vendor
- invoice_date
- subtotal
- tax
- total

Return a JSON object with exactly these fields.
Preserve monetary values as strings.

Invoice text:
{invoice_text}
"""
            }
        ],
        format={
            "type": "object",
            "properties": {
                "vendor": {"type": ["string", "null"]},
                "invoice_date": {"type": ["string", "null"]},
                "subtotal": {"type": ["string", "null"]},
                "tax": {"type": ["string", "null"]},
                "total": {"type": ["string", "null"]}
            },
            "required": [
                "vendor",
                "invoice_date",
                "subtotal",
                "tax",
                "total"
            ]
        },
        options={"temperature": 0}
    )

    return json.loads(response.message.content)
