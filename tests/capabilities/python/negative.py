"""Deliberately capability-free Python: local-only logic, no network,
persistence, auth, subprocess, cloud, or mail. Used by
scripts/test-registration-conformance.py to confirm the capability rules
produce zero false positives on ordinary application code (precision).
"""
import json
import math
from dataclasses import dataclass


@dataclass
class Invoice:
    amount: float
    tax_rate: float

    def total(self) -> float:
        return round(self.amount * (1 + self.tax_rate), 2)


def parse_invoices(raw: str) -> list[Invoice]:
    data = json.loads(raw)
    return [Invoice(item["amount"], item["tax_rate"]) for item in data]


def summarize(invoices: list[Invoice]) -> dict:
    total = sum(inv.total() for inv in invoices)
    return {"count": len(invoices), "total": round(total, 2), "average": round(total / max(len(invoices), 1), 2)}


def standard_deviation(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)
