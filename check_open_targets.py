"""
Live check of the Open Targets integration for every disease in the app.
Run from the project folder (virtual environment active):
    python check_open_targets.py
"""

import app

for disease in app.DISEASES:

    records = app.query_open_targets(disease)

    print("=" * 64)

    if not records:
        print(disease, "-> NO DATA (read the [Open Targets] lines above)")
        continue

    pinned = "pinned" if disease in app.OT_PINNED_IDS else "searched"

    print(
        f"{disease} -> {records[0]['disease_label']} "
        f"[{records[0]['disease_id']}] ({pinned})"
    )

    for r in records:
        print(f"   {r['name']:<10} score={r['score']}  {r['approved_name']}")
