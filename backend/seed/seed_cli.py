"""
CLI Tool to seed the database with realistic demonstration products:
- Product A: Compliant (Biscuits)
- Product B: Missing declaration (Fruit Preserve)
- Product C: Unit issue (Basmati Rice: '0.5 kg' / 'gms')
- Product D: Quantity qualifier (Wheat Flour: 'Approx. 1 kg')
- Product E1: Pan Masala (No Rule 26 exemption)
- Product E2: Medical Device (Confirmation Gate Fix 2)

Usage:
    cd backend
    python -m seed.seed_cli
"""

import sys
from pathlib import Path

# Ensure backend directory is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal, init_db
from app.services.inspection_service import inspection_service
from seed.demo_data import DEMO_PRODUCTS

def seed():
    print("=" * 70)
    print("SIH26034 — Seeding Database with Demo Inspections")
    print("=" * 70)

    init_db()
    db = SessionLocal()

    try:
        created_count = 0
        for i, item in enumerate(DEMO_PRODUCTS, start=1):
            insp_create = item["inspection"]
            extraction_payload = item["extraction"]

            # 1. Create inspection
            insp = inspection_service.create_inspection(db, insp_create)
            print(f"[{i}] Created Inspection: {insp.id}")
            print(f"    Product: {insp.product_name} ({insp.commodity_category})")

            # 2. Save extraction
            extraction_record = inspection_service.save_extraction(db, insp.id, extraction_payload)
            print(f"    Extraction stored: {extraction_record.id}")

            # 3. Trigger compliance analysis
            result = inspection_service.run_compliance_analysis(db, insp.id)
            print(f"    Compliance Status: {result.overall_status}")
            print(f"    Summary: {result.summary_counts}")
            print("-" * 70)
            created_count += 1

        print(f"\nSuccessfully seeded {created_count} inspections with extractions and compliance results!")
        summary = inspection_service.get_dashboard_summary(db)
        print(f"Dashboard Stats:")
        print(f"  Total: {summary.total_inspections}")
        print(f"  Compliant: {summary.compliant_inspections}")
        print(f"  Potential Violations: {summary.potential_violations}")
        print(f"  Needs Manual Review: {summary.needs_manual_review}")
        print(f"  Not Applicable: {summary.not_applicable}")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    seed()
