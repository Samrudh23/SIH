"""
Realistic Seed / Demo Data Generator for SIH26034 Prototype.
Conforms strictly to the finalized Extraction and Compliance Schemas.
"""

from typing import List, Dict, Any
from app.schemas.common import BoundingBox, ImageCoverage
from app.schemas.extraction import (
    ExtractionPayload,
    ExtractedField,
    NetQuantityExtraction,
    MRPExtraction,
    DateExtraction,
    AddressExtraction,
    ConsumerCareExtraction,
)
from app.schemas.inspection import InspectionCreate

DEMO_PRODUCTS = [
    # -------------------------------------------------------------------------
    # Product A — COMPLIANT
    # -------------------------------------------------------------------------
    {
        "inspection": InspectionCreate(
            product_name="Parle-G Gold Glucose Biscuits",
            brand_name="Parle",
            commodity_category="Biscuits",
            inspector_id="insp_delhi_01",
            image_coverage=ImageCoverage(front=True, back=True, side=True, top=True),
            metadata={"source": "Supermarket Shelf Audit", "batch": "BATCH-2026-A1"},
        ),
        "extraction": ExtractionPayload(
            product_name=ExtractedField(
                value="Glucose Biscuits",
                raw_text="Parle-G Gold Glucose Biscuits",
                confidence=0.98,
                bounding_box=BoundingBox(x=50, y=20, w=300, h=40),
                location="front",
            ),
            commodity_category=ExtractedField(
                value="Biscuits",
                raw_text="Biscuits",
                confidence=0.99,
                location="front",
            ),
            manufacturer=AddressExtraction(
                premises="North Level Factory Unit 4",
                street="V.S. Khandekar Marg, Vile Parle East",
                city="Mumbai",
                state="Maharashtra",
                pin_code="400057",
                raw_text="Manufactured by: Parle Products Pvt. Ltd., North Level Factory Unit 4, V.S. Khandekar Marg, Vile Parle East, Mumbai, Maharashtra - 400057",
                confidence=0.96,
                bounding_box=BoundingBox(x=40, y=300, w=420, h=80),
                location="back",
            ),
            country_of_origin=ExtractedField(
                value="India",
                raw_text="Country of Origin: India",
                confidence=0.99,
                location="back",
            ),
            net_quantity=NetQuantityExtraction(
                value=100.0,
                unit="g",
                raw_text="Net Weight: 100 g",
                confidence=0.97,
                bounding_box=BoundingBox(x=380, y=180, w=120, h=35),
                qualifiers=None,
                quiet_zone_clear=True,
                location="front",
            ),
            mrp=MRPExtraction(
                value=30.00,
                currency="₹",
                tax_inclusivity=True,
                raw_text="MRP ₹ 30.00 incl. of all taxes",
                confidence=0.96,
                bounding_box=BoundingBox(x=380, y=230, w=150, h=35),
                is_sticker=False,
                location="back",
            ),
            date_of_manufacture=DateExtraction(
                month="08",
                year="2026",
                raw_text="Mfg Date: 08/2026",
                confidence=0.95,
                bounding_box=BoundingBox(x=380, y=275, w=130, h=30),
                is_rubber_stamped=False,
                has_overwriting=False,
                location="back",
            ),
            consumer_care=ConsumerCareExtraction(
                name_or_office="Consumer Care Executive, Parle Products",
                address="V.S. Khandekar Marg, Vile Parle East, Mumbai 400057",
                phone="1800227788",
                email="customercare@parle.biz",
                raw_text="For consumer complaints: Contact Consumer Care Executive, Parle Products, Toll Free: 1800227788, Email: customercare@parle.biz",
                confidence=0.94,
                bounding_box=BoundingBox(x=40, y=390, w=400, h=60),
                location="back",
            ),
            image_coverage=ImageCoverage(front=True, back=True, side=True, top=True),
        ),
    },

    # -------------------------------------------------------------------------
    # Product B — MISSING DECLARATION (Potential Violation)
    # -------------------------------------------------------------------------
    {
        "inspection": InspectionCreate(
            product_name="Himalayan Berry Preserve",
            brand_name="Orchard Fresh",
            commodity_category="Preserved Fruit",
            inspector_id="insp_mumbai_04",
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
            metadata={"source": "Retail Kirana Shop", "batch": "BATCH-B-MISSING"},
        ),
        "extraction": ExtractionPayload(
            product_name=ExtractedField(
                value="Berry Preserve",
                raw_text="Orchard Fresh Himalayan Berry Jam",
                confidence=0.92,
                location="front",
            ),
            commodity_category=ExtractedField(
                value="Preserved Fruit",
                raw_text="Fruit Preserve",
                confidence=0.90,
                location="front",
            ),
            manufacturer=AddressExtraction(
                premises="Shed 12",
                street="Old Shimla Highway",
                city="Solan",
                state="Himachal Pradesh",
                pin_code="173212",
                raw_text="Packed by: Orchard Foods, Shed 12, Old Shimla Highway, Solan, HP - 173212",
                confidence=0.91,
                location="back",
            ),
            country_of_origin=ExtractedField(
                value="India",
                raw_text="Made in India",
                confidence=0.95,
                location="back",
            ),
            net_quantity=NetQuantityExtraction(
                value=500.0,
                unit="g",
                raw_text="Net Weight: 500 g",
                confidence=0.94,
                location="front",
            ),
            mrp=MRPExtraction(
                value=195.00,
                currency="₹",
                tax_inclusivity=True,
                raw_text="MRP ₹ 195.00 inclusive of all taxes",
                confidence=0.90,
                location="back",
            ),
            # Missing date_of_manufacture intentionally!
            date_of_manufacture=None,
            # Missing consumer_care contact details intentionally!
            consumer_care=None,
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
        ),
    },

    # -------------------------------------------------------------------------
    # Product C — UNIT ISSUE (Prohibited unit 'gms' & Scaling violation '0.5 kg')
    # -------------------------------------------------------------------------
    {
        "inspection": InspectionCreate(
            product_name="Royal Heritage Basmati Rice",
            brand_name="Royal Heritage",
            commodity_category="Rice / Grains",
            inspector_id="insp_chandigarh_02",
            image_coverage=ImageCoverage(front=True, back=True, side=True, top=False),
            metadata={"source": "Hypermarket Inspection", "batch": "BATCH-C-UNITS"},
        ),
        "extraction": ExtractionPayload(
            product_name=ExtractedField(
                value="Basmati Rice",
                raw_text="Royal Heritage Aged Basmati Rice",
                confidence=0.95,
                location="front",
            ),
            commodity_category=ExtractedField(
                value="Rice",
                raw_text="Rice",
                confidence=0.95,
                location="front",
            ),
            manufacturer=AddressExtraction(
                premises="Grain Complex 5",
                street="GT Road",
                city="Karnal",
                state="Haryana",
                pin_code="132001",
                raw_text="Packed by: Rice Heritage Ltd, GT Road, Karnal, Haryana - 132001",
                confidence=0.93,
                location="back",
            ),
            country_of_origin=ExtractedField(
                value="India",
                raw_text="Product of India",
                confidence=0.98,
                location="back",
            ),
            # Declared as '0.5 kg' and uses prohibited 'gms' in text
            net_quantity=NetQuantityExtraction(
                value=0.5,
                unit="kg",
                raw_text="Net Wt: 0.5 kg (500 gms)",
                confidence=0.93,
                bounding_box=BoundingBox(x=200, y=320, w=180, h=40),
                location="front",
            ),
            mrp=MRPExtraction(
                value=90.00,
                currency="₹",
                tax_inclusivity=True,
                raw_text="MRP Rs. 90.00 incl. of all taxes",
                confidence=0.91,
                location="back",
            ),
            date_of_manufacture=DateExtraction(
                month="07",
                year="2026",
                raw_text="Packed: 07/2026",
                confidence=0.90,
                location="back",
            ),
            consumer_care=ConsumerCareExtraction(
                phone="01123456789",
                email="grievance@royalheritage.in",
                raw_text="Helpline: 01123456789, Email: grievance@royalheritage.in",
                confidence=0.89,
                location="back",
            ),
            image_coverage=ImageCoverage(front=True, back=True, side=True, top=False),
        ),
    },

    # -------------------------------------------------------------------------
    # Product D — PROHIBITED QUANTITY QUALIFIER ("Approx. 1 kg")
    # -------------------------------------------------------------------------
    {
        "inspection": InspectionCreate(
            product_name="Golden Harvest Chakki Fresh Atta",
            brand_name="Golden Harvest",
            commodity_category="Flour",
            inspector_id="insp_jaipur_01",
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
            metadata={"source": "Wholesale Mandi", "batch": "BATCH-D-QUALIFIER"},
        ),
        "extraction": ExtractionPayload(
            product_name=ExtractedField(
                value="Whole Wheat Atta",
                raw_text="Chakki Fresh Whole Wheat Atta",
                confidence=0.96,
                location="front",
            ),
            commodity_category=ExtractedField(
                value="Flour",
                raw_text="Atta",
                confidence=0.95,
                location="front",
            ),
            manufacturer=AddressExtraction(
                premises="Plot 44 RIICO Industrial Area",
                street="Tonk Road",
                city="Jaipur",
                state="Rajasthan",
                pin_code="302022",
                raw_text="Golden Harvest Mills, Plot 44 RIICO Industrial Area, Tonk Road, Jaipur, Rajasthan 302022",
                confidence=0.94,
                location="back",
            ),
            country_of_origin=ExtractedField(
                value="India",
                raw_text="Made in India",
                confidence=0.99,
                location="back",
            ),
            # Prohibited qualifier: "Approx. 1 kg" violates Rule 12(6)
            net_quantity=NetQuantityExtraction(
                value=1.0,
                unit="kg",
                raw_text="Net Quantity: Approx. 1 kg",
                confidence=0.95,
                bounding_box=BoundingBox(x=150, y=400, w=220, h=40),
                qualifiers=["approx"],
                location="front",
            ),
            mrp=MRPExtraction(
                value=55.00,
                currency="₹",
                tax_inclusivity=True,
                raw_text="MRP ₹ 55.00 incl. of all taxes",
                confidence=0.94,
                location="back",
            ),
            date_of_manufacture=DateExtraction(
                month="08",
                year="2026",
                raw_text="Mfg Date: 08/2026",
                confidence=0.93,
                location="back",
            ),
            consumer_care=ConsumerCareExtraction(
                phone="1800119988",
                email="care@goldenharvest.in",
                raw_text="Customer Care: 1800119988, care@goldenharvest.in",
                confidence=0.92,
                location="back",
            ),
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
        ),
    },

    # -------------------------------------------------------------------------
    # Product E1 — SPECIAL ROUTER: PAN MASALA (Disables under-10g exemption)
    # -------------------------------------------------------------------------
    {
        "inspection": InspectionCreate(
            product_name="Rajeshwar Pan Masala Sachet",
            brand_name="Rajeshwar",
            commodity_category="Pan Masala",
            inspector_id="insp_kanpur_03",
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
            metadata={"source": "Kiosk Inspection", "batch": "PAN-MASALA-2026"},
        ),
        "extraction": ExtractionPayload(
            product_name=ExtractedField(
                value="Pan Masala",
                raw_text="Rajeshwar Premium Pan Masala",
                confidence=0.97,
                location="front",
            ),
            commodity_category=ExtractedField(
                value="Pan Masala",
                raw_text="Pan Masala",
                confidence=0.99,
                location="front",
            ),
            manufacturer=AddressExtraction(
                premises="Plot 10 Industrial Estate",
                street="Fazalganj",
                city="Kanpur",
                state="Uttar Pradesh",
                pin_code="208012",
                raw_text="Mfg by: Rajeshwar Products, Plot 10 Fazalganj, Kanpur, UP 208012",
                confidence=0.95,
                location="back",
            ),
            country_of_origin=ExtractedField(
                value="India",
                raw_text="Origin: India",
                confidence=0.99,
                location="back",
            ),
            # Weight is 4g. Under Rule 26 normal packages <=10g are exempt, but G.S.R. 881(E) excludes Pan Masala!
            net_quantity=NetQuantityExtraction(
                value=4.0,
                unit="g",
                raw_text="Net Wt: 4 g",
                confidence=0.96,
                location="front",
            ),
            mrp=MRPExtraction(
                value=5.00,
                currency="₹",
                tax_inclusivity=True,
                raw_text="MRP ₹ 5.00 inclusive of all taxes",
                confidence=0.95,
                location="back",
            ),
            date_of_manufacture=DateExtraction(
                month="09",
                year="2026",
                raw_text="Packed: 09/2026",
                confidence=0.94,
                location="back",
            ),
            consumer_care=ConsumerCareExtraction(
                phone="0512223344",
                email="support@rajeshwarpm.com",
                raw_text="Helpline: 0512223344, support@rajeshwarpm.com",
                confidence=0.91,
                location="back",
            ),
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
        ),
    },

    # -------------------------------------------------------------------------
    # Product E2 — SPECIAL ROUTER: MEDICAL DEVICE (Confirmation Gate Fix 2)
    # -------------------------------------------------------------------------
    {
        "inspection": InspectionCreate(
            product_name="MediClean Sterile Gauze Swab",
            brand_name="MediClean",
            commodity_category="Medical Device",
            inspector_id="insp_ahmedabad_01",
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
            metadata={"source": "Hospital Pharmacy Audit", "batch": "MED-DEV-992"},
        ),
        "extraction": ExtractionPayload(
            product_name=ExtractedField(
                value="Sterile Gauze Swab",
                raw_text="MediClean Sterile Gauze Swab 10cm x 10cm",
                confidence=0.96,
                location="front",
            ),
            commodity_category=ExtractedField(
                value="Medical Device",
                raw_text="Medical Device",
                confidence=0.98,
                location="front",
            ),
            medical_device_markers=ExtractedField(
                value="MD-1402",
                raw_text="Mfg. Lic. No. MD-1402 (CDSCO Reg. MDR-2017)",
                confidence=0.96,
                location="back",
            ),
            manufacturer=AddressExtraction(
                premises="Plot 88 GIDC Estate",
                street="Vatva",
                city="Ahmedabad",
                state="Gujarat",
                pin_code="382445",
                raw_text="Manufactured by: MediClean Surgical Ltd, Plot 88 GIDC Vatva, Ahmedabad, Gujarat 382445",
                confidence=0.94,
                location="back",
            ),
            country_of_origin=ExtractedField(
                value="India",
                raw_text="Made in India",
                confidence=0.99,
                location="back",
            ),
            net_quantity=NetQuantityExtraction(
                value=10.0,
                unit="N",
                raw_text="Quantity: 10 N",
                confidence=0.95,
                location="front",
            ),
            mrp=MRPExtraction(
                value=150.00,
                currency="₹",
                tax_inclusivity=True,
                raw_text="MRP ₹ 150.00 incl. of all taxes",
                confidence=0.93,
                location="back",
            ),
            date_of_manufacture=DateExtraction(
                month="06",
                year="2026",
                raw_text="Mfg: 06/2026",
                confidence=0.92,
                location="back",
            ),
            consumer_care=ConsumerCareExtraction(
                phone="0792589000",
                email="grievance@mediclean.co.in",
                raw_text="Contact: 0792589000, grievance@mediclean.co.in",
                confidence=0.90,
                location="back",
            ),
            image_coverage=ImageCoverage(front=True, back=True, side=False, top=False),
        ),
    },
]
