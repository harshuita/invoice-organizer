
import json
import ollama
from invoice_validator import validate_invoice


invoice = {
    "vendor": "Demo Supplies",
    "invoice_date": "2026-10-10",
    "subtotal": "$85.00",
    "tax": "$8.50",
    "total": "$95.50",
}

invoice_text = """
Vendor: Demo Supplies
Invoice Date: 2026-10-10
Subtotal: $85.00
Tax: $8.50
Shipping Fee: $2.00
Total: $95.50
"""


def search_invoice_text(invoice_text, query):
    terms = query.lower().split()
    return [
        line.strip()
        for line in invoice_text.splitlines()
        if any(term in line.lower() for term in terms)
    ]


tools = [
    {
        "type": "function",
        "function": {
            "name": "validate_invoice",
            "description": "Check invoice fields and arithmetic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "properties": {
                            "vendor": {"type": ["string", "null"]},
                            "invoice_date": {"type": ["string", "null"]},
                            "subtotal": {"type": ["string", "null"]},
                            "tax": {"type": ["string", "null"]},
                            "total": {"type": ["string", "null"]},
                        },
                        "required": [
                            "vendor", "invoice_date", "subtotal",
                            "tax", "total"
                        ],
                    }
                },
                "required": ["data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_invoice_text",
            "description": (
                "Search invoice text for a keyword or amount "
                "to investigate a validation warning."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
]


messages = [
    {
        "role": "system",
        "content": (
            "Investigate invoices carefully. First validate the invoice. "
            "After seeing the validation result, search the original text "
            "if there is a mismatch. Do not assume a discrepancy is an error "
            "if additional charges may explain it. Never change invoice "
            "values automatically. Leave unresolved issues for human review."
        ),
    },
    {
        "role": "user",
        "content": (
            f"Invoice data:\n{json.dumps(invoice)}\n\n"
            f"Original invoice text:\n{invoice_text}"
        ),
    },
]


MAX_ROUNDS = 3
finished = False

for round_number in range(1, MAX_ROUNDS + 1):
    print(f"\n--- Agent round {round_number} ---")

    response = ollama.chat(
        model="qwen3:4b",
        messages=messages,
        tools=tools,
        options={"temperature": 0},
    )

    message = response.message
    messages.append(message)

    if not message.tool_calls:
        if message.content.strip():
            print("\nAgent's response:")
            print(message.content)
            finished = True
        break

    for tool_call in message.tool_calls:
        name = tool_call.function.name
        args = tool_call.function.arguments

        if name == "validate_invoice":
            result = validate_invoice(args["data"])

        elif name == "search_invoice_text":
            query = args["query"]
            result = {
                "query": query,
                "matches": search_invoice_text(invoice_text, query),
            }

        else:
            result = {"error": f"Unknown tool: {name}"}

        print(f"{name} result:", result)

        messages.append({
            "role": "tool",
            "tool_name": name,
            "content": json.dumps(result),
        })


if not finished:
    print(
        "\nAgent stopped at the round limit or did not return a final "
        "answer. Review the tool results above before accepting the invoice."
    )
