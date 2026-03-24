#!/usr/bin/env python3
"""Seed the database with 50 CUAD contracts (2 per type) and run analysis on each."""

import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import Settings
from app.core.models import AnalysisResult, AnalysisStatus, ContractDocument
from app.services.cuad_loader import filter_by_type, get_contract_text, get_contract_types
from app.services.database import ensure_database, get_contract, save_analysis, save_contract
from app.agents.pipeline import run_analysis_pipeline

CONTRACTS_PER_TYPE = 2


async def seed() -> None:
    settings = Settings()
    await ensure_database(settings)

    contract_types = get_contract_types(settings.cuad_data_path)
    print(f"Found {len(contract_types)} contract types. Seeding {CONTRACTS_PER_TYPE} per type ({len(contract_types) * CONTRACTS_PER_TYPE} total).\n")

    seeded = 0
    failed = 0

    for contract_type in contract_types:
        filenames = filter_by_type(contract_type, settings.cuad_data_path)[:CONTRACTS_PER_TYPE]
        for filename in filenames:
            contract_id = uuid.uuid5(uuid.NAMESPACE_DNS, filename).hex

            existing = await get_contract(contract_id, settings)
            if existing and existing.status == AnalysisStatus.COMPLETED:
                print(f"  [skip] {filename}")
                continue

            contract = ContractDocument(
                id=contract_id,
                filename=filename,
                upload_date=datetime.utcnow(),
                file_path=str(Path(settings.cuad_data_path) / "full_contract_txt" / filename),
                contract_type=contract_type,
                status=AnalysisStatus.IN_PROGRESS,
            )
            await save_contract(contract, settings)

            analysis_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"analysis-{filename}").hex
            pending = AnalysisResult(
                id=analysis_id,
                contract_id=contract_id,
                status=AnalysisStatus.IN_PROGRESS,
            )
            await save_analysis(pending, settings)

            print(f"  Analyzing {filename} ({contract_type}) ...", end=" ", flush=True)
            try:
                contract_text = get_contract_text(filename, settings.cuad_data_path)
                analysis = await run_analysis_pipeline(contract_text, settings)
                analysis.id = analysis_id
                analysis.contract_id = contract_id
                analysis.status = AnalysisStatus.COMPLETED
                analysis.completed_at = datetime.utcnow()
                await save_analysis(analysis, settings)

                contract.status = AnalysisStatus.COMPLETED
                await save_contract(contract, settings)

                print(f"OK ({len(analysis.risk_flags)} risks, {len(analysis.obligations)} obligations)")
                seeded += 1
            except Exception as exc:
                print(f"FAILED: {exc}")
                pending.status = AnalysisStatus.FAILED
                pending.error_message = str(exc)
                await save_analysis(pending, settings)
                contract.status = AnalysisStatus.FAILED
                await save_contract(contract, settings)
                failed += 1

    print(f"\nDone. {seeded} contracts seeded, {failed} failed.")


if __name__ == "__main__":
    asyncio.run(seed())
