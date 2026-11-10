"""Deterministic construction estimate engine. Monetary calculations use Decimal."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from pathlib import Path

CENT = Decimal('0.01')


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def number(value: object, field: str, *, maximum: str = '100000000') -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f'{field} must be a number') from None
    if not result.is_finite() or result < 0 or result > Decimal(maximum):
        raise ValueError(f'{field} must be between 0 and {maximum}')
    return result


def percentage(value: object, field: str) -> Decimal:
    return number(value, field, maximum='100') / Decimal('100')


def load_catalog(path: str | Path) -> dict[str, dict]:
    with open(path, newline='', encoding='utf-8-sig') as file:
        rows = list(csv.DictReader(file))
    catalog = {}
    for row in rows:
        code = (row.get('code') or '').strip()
        if not code or code in catalog:
            raise ValueError('Catalog needs unique nonempty item codes')
        catalog[code] = {
            'code': code,
            'description': (row.get('description') or '').strip(),
            'unit': (row.get('unit') or '').strip(),
            'material_unit_cost': number(row.get('material_unit_cost'), f'{code} material cost'),
            'labor_hours_per_unit': number(row.get('labor_hours_per_unit'), f'{code} labor hours'),
        }
    return catalog


def estimate(payload: dict, catalog: dict[str, dict]) -> dict:
    """Return an itemized, reproducible estimate based on explicit input assumptions."""
    if not isinstance(payload, dict):
        raise ValueError('Request must be an object')
    items = payload.get('items')
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError('Provide between 1 and 100 line items')
    labor_rate = number(payload.get('labor_rate', 55), 'labor_rate')
    waste = percentage(payload.get('waste_percent', 10), 'waste_percent')
    overhead = percentage(payload.get('overhead_percent', 12), 'overhead_percent')
    profit = percentage(payload.get('profit_markup_percent', 15), 'profit_markup_percent')
    sales_tax = percentage(payload.get('material_tax_percent', 0), 'material_tax_percent')
    details = []
    material_total = Decimal('0')
    labor_total = Decimal('0')
    for i, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f'Line {i} must be an object')
        code = str(item.get('code', '')).strip()
        if code not in catalog:
            raise ValueError(f'Line {i}: unknown catalog code {code!r}')
        qty = number(item.get('quantity'), f'Line {i} quantity', maximum='1000000')
        if qty == 0:
            raise ValueError(f'Line {i} quantity must be greater than zero')
        entry = catalog[code]
        mat = money(qty * entry['material_unit_cost'] * (1 + waste))
        hours = qty * entry['labor_hours_per_unit']
        labor = money(hours * labor_rate)
        material_total += mat
        labor_total += labor
        details.append({
            'code': code, 'description': entry['description'], 'unit': entry['unit'],
            'quantity': str(qty), 'material_cost': str(mat),
            'labor_hours': str(hours.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'labor_cost': str(labor), 'line_direct_cost': str(mat + labor),
        })
    material_tax = money(material_total * sales_tax)
    direct = material_total + labor_total + material_tax
    overhead_amount = money(direct * overhead)
    profit_amount = money((direct + overhead_amount) * profit)
    price = direct + overhead_amount + profit_amount
    return {
        'project_name': str(payload.get('project_name') or 'Untitled Project')[:120],
        'currency': 'USD', 'items': details,
        'totals': {
            'materials_including_waste': str(material_total), 'labor': str(labor_total),
            'material_tax': str(material_tax), 'direct_cost': str(direct),
            'overhead': str(overhead_amount), 'profit_markup': str(profit_amount),
            'estimated_price': str(price),
        },
        'assumptions': {
            'labor_rate_per_hour': str(labor_rate),
            'material_waste_percent': str(waste * 100),
            'overhead_percent': str(overhead * 100),
            'profit_markup_percent': str(profit * 100),
            'material_tax_percent': str(sales_tax * 100),
            'pricing_method': 'markup (not gross margin)',
            'disclaimer': 'Illustrative catalog prices only. Verify actual bids, taxes, permits, scope and local labor costs.'
        }
    }
