from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from src.shared.logger import log_info
from src.shared.normalize_text import normalize_compare_key


@dataclass
class ComparisonResult:
    missing_supplies: List[Dict[str, str]]
    veloe_total: int
    monday_initial_total: int
    new_ids_found: int


def compare_veloe_with_monday(
    veloe_supplies: List[Dict[str, str]],
    monday_item_names: List[str],
) -> ComparisonResult:
    """Compara IDs técnicos da Veloe com names dos itens no Monday."""
    monday_keys = {normalize_compare_key(name) for name in monday_item_names if name}

    missing: List[Dict[str, str]] = []
    for supply in veloe_supplies:
        veloe_key = normalize_compare_key(supply.get("id", ""))
        if veloe_key and veloe_key not in monday_keys:
            missing.append(supply)

    log_info(f"Veloe total: {len(veloe_supplies)}")
    log_info(f"Monday inicial: {len(monday_item_names)}")
    log_info(f"Novos IDs para criar: {len(missing)}")

    return ComparisonResult(
        missing_supplies=missing,
        veloe_total=len({
            normalize_compare_key(supply.get("id", ""))
            for supply in veloe_supplies
            if normalize_compare_key(supply.get("id", ""))
        }),
        monday_initial_total=len(monday_item_names),
        new_ids_found=len(missing),
    )



# PARA APAGAR
if __name__ == "__main__":
    from collections import Counter

    from src.veloe.api_client import create_veloe_session
    from src.veloe.login import login_veloe
    from src.veloe.fetch_vehicles import fetch_all_vehicles
    from src.veloe.date_periods import get_current_semester_period
    from src.veloe.fetch_supplies import fetch_supplies
    from src.monday.fetch_item_names import fetch_existing_item_names

    # Buscar dados
    session = create_veloe_session()
    token = login_veloe(session)
    vehicles = fetch_all_vehicles(session, token)
    period = get_current_semester_period()

    veloe_supplies = fetch_supplies(session, token, vehicles, period)
    monday_item_names = fetch_existing_item_names()

    # Normalizar IDs
    veloe_ids = [
        normalize_compare_key(supply.get("id", ""))
        for supply in veloe_supplies
    ]

    monday_ids = [
        normalize_compare_key(name)
        for name in monday_item_names
    ]

    veloe_keys = set(filter(None, veloe_ids))
    monday_keys = set(filter(None, monday_ids))

    # Diagnóstico
    missing = veloe_keys - monday_keys
    extra = monday_keys - veloe_keys

    veloe_duplicates = {
        key: count
        for key, count in Counter(veloe_ids).items()
        if key and count > 1
    }

    monday_duplicates = {
        key: count
        for key, count in Counter(monday_ids).items()
        if key and count > 1
    }

    print("\n========== DIAGNÓSTICO VELOE x MONDAY ==========")
    print(f"Veloe total: {len(veloe_ids)}")
    print(f"Veloe IDs únicos: {len(veloe_keys)}")
    print(f"Monday total: {len(monday_ids)}")
    print(f"Monday IDs únicos: {len(monday_keys)}")

    print(f"\nIDs ausentes no Monday ({len(missing)}):")
    print(sorted(missing))

    print(f"\nIDs extras no Monday ({len(extra)}):")
    print(sorted(extra))

    print(f"\nDuplicados Veloe: {veloe_duplicates}")
    print(f"Duplicados Monday: {monday_duplicates}")

    print("\n========== FIM DO DIAGNÓSTICO ==========")