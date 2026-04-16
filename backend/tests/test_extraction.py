"""
Extraction accuracy tests against CUAD ground truth.

These tests require:
1. CUAD dataset downloaded to backend/data/
2. Azure OpenAI credentials configured

Run with: pytest tests/test_extraction.py -v -s
Results print accuracy metrics per field.
"""

import pytest

from app.core.config import Settings
from app.core.models import ExtractedData
from app.services.cuad_loader import (
    list_contracts,
    get_contract_text,
    get_ground_truth,
)
from app.agents.orchestrator import run_analysis_pipeline


# Number of contracts to test (subset for speed)
SAMPLE_SIZE = 10

# Target accuracy thresholds
EXTRACTION_TARGET = 0.85
DATE_TARGET = 0.90


def _normalize(text: str) -> str:
    """Normalize text for comparison."""
    return " ".join(text.lower().strip().split())


def _parties_match(extracted: list[str], ground_truth: list[str]) -> float:
    """Fuzzy match score for party names."""
    if not ground_truth:
        return 1.0 if not extracted else 0.0
    if not extracted:
        return 0.0

    gt_normalized = [_normalize(g) for g in ground_truth]
    matches = 0
    for party in extracted:
        party_norm = _normalize(party)
        if any(party_norm in gt or gt in party_norm for gt in gt_normalized):
            matches += 1

    precision = matches / len(extracted) if extracted else 0
    recall = min(matches, len(ground_truth)) / len(ground_truth) if ground_truth else 0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)  # F1


def _date_match(extracted: str | None, ground_truth: list[str]) -> float:
    """Check if extracted date matches any ground truth annotation."""
    if not ground_truth:
        return 1.0 if not extracted else 0.5
    if not extracted:
        return 0.0

    extracted_norm = _normalize(extracted)
    return 1.0 if any(extracted_norm in _normalize(gt) or _normalize(gt) in extracted_norm for gt in ground_truth) else 0.0


def _text_match(extracted: str | None, ground_truth: list[str]) -> float:
    """Check if extracted text matches any ground truth annotation."""
    if not ground_truth:
        return 1.0 if not extracted else 0.5
    if not extracted:
        return 0.0

    extracted_norm = _normalize(extracted)
    return 1.0 if any(extracted_norm in _normalize(gt) or _normalize(gt) in extracted_norm for gt in ground_truth) else 0.0


@pytest.fixture
def cuad_sample(settings):
    """Get a sample of CUAD contracts for testing."""
    try:
        filenames = list_contracts(settings.cuad_data_path)
    except FileNotFoundError:
        pytest.skip("CUAD dataset not downloaded")
    return filenames[:SAMPLE_SIZE]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not Settings().azure_openai_endpoint,
    reason="Azure OpenAI not configured",
)
async def test_extraction_accuracy(cuad_sample, settings):
    """Test extraction accuracy against CUAD ground truth.

    Measures per-field accuracy across a sample of contracts.
    """
    scores = {
        "parties": [],
        "effective_date": [],
        "expiration_date": [],
        "governing_law": [],
    }

    for filename in cuad_sample:
        text = get_contract_text(filename, settings.cuad_data_path)
        gt = get_ground_truth(filename, settings.cuad_data_path)

        # Run the pipeline
        result = await run_analysis_pipeline(text, f"test-{filename}", f"analysis-test-{filename}", settings)
        ed = result.extracted_data

        if ed is None:
            for key in scores:
                scores[key].append(0.0)
            continue

        # Parties (CUAD column: "Parties")
        gt_parties = gt.get("Parties", [])
        scores["parties"].append(_parties_match(ed.parties, gt_parties))

        # Effective Date (CUAD column: "Effective Date")
        gt_effective = gt.get("Effective Date", [])
        scores["effective_date"].append(_date_match(ed.effective_date, gt_effective))

        # Expiration Date (CUAD column: "Expiration Date")
        gt_expiration = gt.get("Expiration Date", [])
        scores["expiration_date"].append(_date_match(ed.expiration_date, gt_expiration))

        # Governing Law (CUAD column: "Governing Law")
        gt_law = gt.get("Governing Law", [])
        scores["governing_law"].append(_text_match(ed.governing_law, gt_law))

    # Print results
    print("\n" + "=" * 60)
    print("EXTRACTION ACCURACY RESULTS")
    print("=" * 60)

    overall_scores = []
    for field, field_scores in scores.items():
        avg = sum(field_scores) / len(field_scores) if field_scores else 0
        overall_scores.append(avg)
        status = "PASS" if avg >= EXTRACTION_TARGET else "FAIL"
        print(f"  {field:20s}: {avg:.1%}  [{status}]")

    overall = sum(overall_scores) / len(overall_scores) if overall_scores else 0
    print(f"\n  {'OVERALL':20s}: {overall:.1%}  (target: {EXTRACTION_TARGET:.0%})")
    print("=" * 60)

    assert overall >= EXTRACTION_TARGET, (
        f"Overall extraction accuracy {overall:.1%} below target {EXTRACTION_TARGET:.0%}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(
    not Settings().azure_openai_endpoint,
    reason="Azure OpenAI not configured",
)
async def test_date_extraction_accuracy(cuad_sample, settings):
    """Specifically test date extraction accuracy (higher target: 90%)."""
    date_scores = []

    for filename in cuad_sample:
        text = get_contract_text(filename, settings.cuad_data_path)
        gt = get_ground_truth(filename, settings.cuad_data_path)

        result = await run_analysis_pipeline(text, f"test-date-{filename}", f"analysis-date-{filename}", settings)
        ed = result.extracted_data

        if ed is None:
            date_scores.append(0.0)
            continue

        # Check all date fields
        for field, col in [("effective_date", "Effective Date"), ("expiration_date", "Expiration Date")]:
            gt_dates = gt.get(col, [])
            extracted = getattr(ed, field)
            date_scores.append(_date_match(extracted, gt_dates))

    avg = sum(date_scores) / len(date_scores) if date_scores else 0

    print(f"\n  Date extraction accuracy: {avg:.1%}  (target: {DATE_TARGET:.0%})")

    assert avg >= DATE_TARGET, (
        f"Date extraction accuracy {avg:.1%} below target {DATE_TARGET:.0%}"
    )
