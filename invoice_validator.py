
import re
from decimal import Decimal, InvalidOperation


REQUIRED_FIELDS = [
    "vendor",
    "invoice_date",
    "subtotal",
    "tax",
    "total",
]


def parse_amount(value):
    if value is None:
        return None

    # Remove currency symbols, currency codes and commas.
    cleaned = re.sub(r"[^0-9.\-]", "", str(value))

    if not cleaned:
        raise ValueError(f"Invalid monetary amount: {value}")

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Invalid monetary amount: {value}")


def validate_invoice(data):
    errors = []
    warnings = []
    amounts = {}

    # Check required fields.
    for field in REQUIRED_FIELDS:
        value = data.get(field)

        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            warnings.append(f"Missing field: {field}")

    # Parse the monetary values.
    for field in ["subtotal", "tax", "total"]:
        value = data.get(field)

        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            continue

        try:
            amounts[field] = parse_amount(value)
        except ValueError as error:
            errors.append(str(error))

    # Check arithmetic only when all amounts are available.
    if all(
        field in amounts
        for field in ["subtotal", "tax", "total"]
    ):
        expected_total = amounts["subtotal"] + amounts["tax"]

        if abs(expected_total - amounts["total"]) > Decimal("0.01"):
            warnings.append(
                "Possible arithmetic mismatch: "
                f"subtotal + tax = {expected_total}, "
                f"but total = {amounts['total']}."
            )

    return {
        "errors": errors,
        "warnings": warnings,
        "needs_review": bool(errors or warnings),
    }
