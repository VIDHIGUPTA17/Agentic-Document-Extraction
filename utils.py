import re
from decimal import Decimal
from typing import List, Dict, Any

_AMOUNT_RE = re.compile(r"\b(?:Rs\.?|INR|USD|EUR|GBP)?\s*([0-9,]+(?:\.[0-9]{1,2})?)\b", re.IGNORECASE)
_DATE_RE = re.compile(r"\b(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}|\d{4}[\-/]\d{1,2}[\-/]\d{1,2})\b")


def parse_amount(s: str):
    if not s: return None
    m = _AMOUNT_RE.search(s)
    if not m: return None
    val = m.group(1)
    val = val.replace(',', '')
    try:
        return float(val)
    except:
        return None

def parse_date(s: str):
    if not s: return None
    m = _DATE_RE.search(s)
    return m.group(0) if m else None

def compute_overall_confidence(fields):
    # simple weighted average
    if not fields: return 0.0
    total = sum(f.get('confidence',0) for f in fields)
    return float(total / len(fields))

def totals_match(line_items: List[Dict[str,Any]], total_val: float, tol: float = 1.0):
    s = 0.0
    for it in line_items:
        v = parse_amount(it.get('amount') or it.get('value') or '0') or 0.0
        s += v
    return abs(s - (total_val or 0.0)) <= tol, s
