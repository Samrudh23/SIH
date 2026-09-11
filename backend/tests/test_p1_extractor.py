import pytest
from app.services.p1_extractor import P1Extractor, normalize_surface
from app.schemas.common import ImageCoverage
from app.models.inspection import ImageEvidenceModel

@pytest.fixture
def extractor():
    return P1Extractor()

def test_normalize_surface():
    assert normalize_surface("front") == "front"
    assert normalize_surface("PDP") == "front"
    assert normalize_surface("front / pdp") == "front"
    assert normalize_surface("back") == "back"
    assert normalize_surface("REAR") == "back"
    assert normalize_surface("side") == "side"
    assert normalize_surface("top") == "top"
    assert normalize_surface("bottom") == "top"
    assert normalize_surface(None) == "front"

def test_parse_compliant_text(extractor):
    raw_text = """
    Parle-G Gold Glucose Biscuits
    Category: Biscuits
    Country of Origin: India
    Manufactured by: Parle Products Pvt Ltd, Plot 10, Industrial Area, Mumbai, Maharashtra - 400057
    Net Qty: 100 g
    MRP: Rs. 30.00 incl. of all taxes
    Mfg Date: 08/2026
    Consumer Care: Toll Free 1800227788, customercare@parle.biz
    """
    parsed = extractor.parse_text_declarations(raw_text, surface="front", image_id="img_001")

    assert parsed["product_name"].value is not None
    assert "Glucose Biscuits" in parsed["product_name"].raw_text
    assert parsed["commodity_category"].value == "Biscuits"
    assert parsed["country_of_origin"].value == "India"
    assert parsed["manufacturer"].pin_code == "400057"
    assert parsed["net_quantity"].value == 100.0
    assert parsed["net_quantity"].unit == "g"
    assert parsed["mrp"].value == 30.0
    assert parsed["mrp"].tax_inclusivity is True
    assert parsed["date_of_manufacture"].month == "08"
    assert parsed["date_of_manufacture"].year == "2026"
    assert parsed["consumer_care"].phone == "1800227788"
    assert parsed["consumer_care"].email == "customercare@parle.biz"

def test_parse_low_confidence_tax_phrase(extractor):
    raw_text = "Price: ₹ 99.00 incl of taxes"
    parsed = extractor.parse_text_declarations(raw_text, surface="front", base_confidence=0.71)

    assert parsed["mrp"].value == 99.0
    assert parsed["mrp"].tax_inclusivity is True
    assert parsed["mrp"].confidence == 0.71

def test_parse_prohibited_quantity_qualifiers(extractor):
    raw_text = "Net Qty: Approx. 500 g"
    parsed = extractor.parse_text_declarations(raw_text, surface="front")

    assert parsed["net_quantity"].value == 500.0
    assert parsed["net_quantity"].qualifiers == ["approx"]

def test_parse_pan_masala_classification(extractor):
    raw_text = """
    Premium Pan Masala
    Net Weight: 5 g
    MRP ₹ 10.00 incl of all taxes
    Mfg: 09/2026
    Mfg by: Pan Masala Co, Kanpur - 208001
    """
    parsed = extractor.parse_text_declarations(raw_text, surface="front")

    assert parsed["commodity_category"].value == "Pan Masala"
    assert parsed["net_quantity"].value == 5.0

def test_parse_medical_device_markers(extractor):
    raw_text = """
    Sterile Gauze Swab
    Mfg Lic No MD-1234
    CDSCO Registered
    MRP Rs. 50.00 incl. of all taxes
    """
    parsed = extractor.parse_text_declarations(raw_text, surface="back")

    assert parsed["commodity_category"].value == "Medical Device"
    assert parsed["medical_device_markers"] is not None
    assert "MD-1234" in parsed["medical_device_markers"].raw_text

def test_extract_from_inspection_images_aggregation(extractor):
    # Simulate two images: front has MRP 40, back has MRP 40 (no conflict)
    img1 = ImageEvidenceModel(
        id="img_front",
        inspection_id="insp_test",
        file_name="front.jpg",
        original_file_name="front.jpg",
        file_path="",
        file_size_bytes=1000,
        mime_type="image/jpeg",
        image_type="front",
        metadata_json={
            "sample_text": "GoodDay Butter Cookies\nNet Qty: 200 g\nMRP ₹ 40.00 incl of all taxes\nMfg by: Bakery, Pune - 411001"
        },
    )
    img2 = ImageEvidenceModel(
        id="img_back",
        inspection_id="insp_test",
        file_name="back.jpg",
        original_file_name="back.jpg",
        file_path="",
        file_size_bytes=1000,
        mime_type="image/jpeg",
        image_type="back",
        metadata_json={
            "sample_text": "MRP ₹ 40.00 incl of all taxes\nDate: 09/2026\nHelpline: 1800112233\nCountry of Origin: India"
        },
    )

    payload = extractor.extract_from_inspection_images([img1, img2])
    assert len(payload.mrp_observations) == 2
    assert payload.mrp_observations[0].surface_location == "front"
    assert payload.mrp_observations[1].surface_location == "back"
    assert payload.image_coverage.front is True
    assert payload.image_coverage.back is True
    assert payload.image_coverage.side is False
    assert payload.date_of_manufacture is not None

def test_extract_from_inspection_images_preserves_conflicts(extractor):
    # Front says 100, Back says 120
    img1 = ImageEvidenceModel(
        id="img_1",
        inspection_id="insp_conf",
        file_name="f.jpg",
        original_file_name="f.jpg",
        file_path="",
        file_size_bytes=100,
        mime_type="image/jpeg",
        image_type="front",
        metadata_json={"sample_text": "Tea Leaves\nMRP ₹ 100.00 incl of all taxes\nNet Weight: 500 g"},
    )
    img2 = ImageEvidenceModel(
        id="img_2",
        inspection_id="insp_conf",
        file_name="b.jpg",
        original_file_name="b.jpg",
        file_path="",
        file_size_bytes=100,
        mime_type="image/jpeg",
        image_type="back",
        metadata_json={"sample_text": "MRP ₹ 120.00 incl of all taxes\nNet Weight: 400 g"},
    )

    payload = extractor.extract_from_inspection_images([img1, img2])
    assert len(payload.mrp_observations) == 2
    assert payload.mrp_observations[0].value == 100.0
    assert payload.mrp_observations[1].value == 120.0
    assert len(payload.net_quantity_observations) == 2
    assert payload.net_quantity_observations[0].value == 500.0
    assert payload.net_quantity_observations[1].value == 400.0
