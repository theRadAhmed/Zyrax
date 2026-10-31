"""
Lists the Open Targets disease candidates for every disease that has no
pinned ID yet, with how many associated targets each candidate has.
Use it to choose the correct ID, then add it to OT_PINNED_IDS in app.py.

Run from the project folder (virtual environment active):
    python find_disease_ids.py
"""

import app

for disease in app.DISEASES:

    if disease in app.OT_PINNED_IDS:
        continue

    term = app.OT_SEARCH_TERMS.get(disease, disease)

    print("=" * 76)
    print(f"{disease}   (search term: {term})")

    try:
        data = app._ot_post(app.OT_SEARCH_QUERY, {"queryString": term})
    except Exception as error:
        print("   search failed:", error)
        continue

    hits = [
        h for h in (data.get("search") or {}).get("hits") or []
        if h.get("entity") == "disease"
    ][:6]

    if not hits:
        print("   no disease candidates found")

    for h in hits:
        try:
            d = app._ot_post(
                app.OT_TARGETS_QUERY,
                {"efoId": h["id"], "size": 1}
            )
            n = (
                ((d.get("disease") or {}).get("associatedTargets") or {})
                .get("count")
            )
        except Exception:
            n = "?"
        print(f"   {h['id']:<16} {h['name']:<52} targets={n}")
