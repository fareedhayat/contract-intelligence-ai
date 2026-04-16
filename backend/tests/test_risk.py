"""
Risk detection accuracy tests against CUAD ground truth.

CUAD provides Yes/No labels for 33 clause categories that map to risk types.
We measure precision and recall of our risk flagging against these labels.

Run with: pytest tests/test_risk.py -v -s
"""

import pytest

from app.core.config import Settings
from app.core.models import RiskFlag
from app.services.cuad_loader import (
    list_contracts,
    get_contract_text,
    get_ground_truth,
)
from app.agents.pipeline import run_analysis_pipeline


SAMPLE_SIZE = 10

PRECISION_TARGET = 0.80
RECALL_TARGET = 0.75

# Map our RiskCategory values to CUAD clause columns
RISK_TO_CUAD = {
    "termination": [
        "Termination For Convenience",
        "Post-Termination Services",
        "Right Of First Refusal, Offer Or Negotiation (ROFR/ROFO/ROFN)",
    ],
    "liability": [
        "Uncapped Liability",
        "Cap On Liability",
        "Liquidated Damages",
    ],
    "intellectual_property": [
        "IP Ownership Assignment",
        "Joint IP Ownership",
        "License Grant",
        "Non-Transferable License",
        "Affiliate IP License-Licensor",
        "Affiliate IP License-Licensee",
        "Unlimited/All-You-Can-Eat-License",
        "Irrevocable Or Perpetual License",
        "Source Code Escrow",
    ],
    "confidentiality": [
        "Non-Disparagement",
    ],
    "indemnification": [
        "Covenant Not To Sue",
        "Third Party Beneficiary",
    ],
    "change_of_control": [
        "Change Of Control",
        "Anti-Assignment",
    ],
    "exclusivity": [
        "Exclusivity",
    ],
    "competition": [
        "Non-Compete",
        "No-Solicit Of Customers",
        "No-Solicit Of Employees",
        "Competitive Restriction Exception",
    ],
    "insurance": [
        "Insurance",
    ],
    "audit": [
        "Audit Rights",
    ],
}


def _cuad_has_risk(ground_truth: dict[str, list[str]], cuad_columns: list[str]) -> bool:
    """Check if any of the CUAD columns have a non-empty annotation."""
    for col in cuad_columns:
        annotations = ground_truth.get(col, [])
        if annotations:
            return True
    return False


@pytest.fixture
def cuad_sample(settings):
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
async def test_risk_detection_accuracy(cuad_sample, settings):
    """Test risk detection precision and recall against CUAD labels."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for filename in cuad_sample:
        text = get_contract_text(filename, settings.cuad_data_path)
        gt = get_ground_truth(filename, settings.cuad_data_path)

        result = await run_analysis_pipeline(text, f"test-risk-{filename}", f"analysis-risk-{filename}", settings)

        # Categories flagged by our system
        flagged_categories = set(rf.category.value for rf in result.risk_flags)

        # Check each risk category
        for category, cuad_cols in RISK_TO_CUAD.items():
            cuad_positive = _cuad_has_risk(gt, cuad_cols)
            ai_flagged = category in flagged_categories

            if ai_flagged and cuad_positive:
                true_positives += 1
            elif ai_flagged and not cuad_positive:
                false_positives += 1
            elif not ai_flagged and cuad_positive:
                false_negatives += 1

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print("\n" + "=" * 60)
    print("RISK DETECTION ACCURACY RESULTS")
    print("=" * 60)
    print(f"  True Positives:  {true_positives}")
    print(f"  False Positives: {false_positives}")
    print(f"  False Negatives: {false_negatives}")
    print(f"  Precision:       {precision:.1%}  (target: {PRECISION_TARGET:.0%})  [{'PASS' if precision >= PRECISION_TARGET else 'FAIL'}]")
    print(f"  Recall:          {recall:.1%}  (target: {RECALL_TARGET:.0%})  [{'PASS' if recall >= RECALL_TARGET else 'FAIL'}]")
    print(f"  F1 Score:        {f1:.1%}")
    print("=" * 60)

    assert precision >= PRECISION_TARGET, (
        f"Risk detection precision {precision:.1%} below target {PRECISION_TARGET:.0%}"
    )
    assert recall >= RECALL_TARGET, (
        f"Risk detection recall {recall:.1%} below target {RECALL_TARGET:.0%}"
    )
