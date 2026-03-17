from pathlib import Path

import pandas as pd

from app.core.config import Settings


def _master_csv_path(data_path: str) -> Path:
    return Path(data_path) / "master_clauses.csv"


def _txt_dir(data_path: str) -> Path:
    return Path(data_path) / "full_contract_txt"


def load_master_csv(data_path: str) -> pd.DataFrame:
    """Load the CUAD master clauses CSV into a DataFrame."""
    csv_path = _master_csv_path(data_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Master CSV not found at {csv_path}. Download the CUAD dataset first."
        )
    return pd.read_csv(csv_path)


def list_contracts(data_path: str) -> list[str]:
    """Return filenames of all .txt contracts in the CUAD dataset."""
    txt_dir = _txt_dir(data_path)
    if not txt_dir.exists():
        raise FileNotFoundError(
            f"Contract text directory not found at {txt_dir}. Download the CUAD dataset first."
        )
    return sorted(f.name for f in txt_dir.iterdir() if f.suffix == ".txt")


def get_contract_text(filename: str, data_path: str) -> str:
    """Read the full text of a single CUAD contract by filename."""
    file_path = _txt_dir(data_path) / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Contract not found: {file_path}")
    return file_path.read_text(encoding="utf-8", errors="replace")


def get_ground_truth(filename: str, data_path: str) -> dict[str, list[str]]:
    """Get the 41 clause annotations for a specific contract.

    Returns a dict mapping clause category name to list of extracted answer spans.
    Empty list means the clause is not present in the contract.
    """
    df = load_master_csv(data_path)

    # Master CSV has filenames in the first column; match by contract name
    # The filename in the CSV may include a path prefix, so match on the basename
    mask = df.iloc[:, 0].apply(lambda x: Path(str(x)).stem) == Path(filename).stem
    rows = df[mask]

    if rows.empty:
        raise ValueError(f"Contract '{filename}' not found in master CSV.")

    row = rows.iloc[0]
    ground_truth: dict[str, list[str]] = {}

    # Clause categories start from column index 1 onward
    for col in df.columns[1:]:
        val = row[col]
        if pd.isna(val) or str(val).strip() == "":
            ground_truth[col] = []
        else:
            # Multiple annotations are separated by semicolons in the CSV
            ground_truth[col] = [s.strip() for s in str(val).split(";") if s.strip()]

    return ground_truth


def get_contract_types(data_path: str) -> list[str]:
    """Return the list of unique contract types in the CUAD dataset."""
    df = load_master_csv(data_path)
    # Contract type is typically derived from the filename prefix or a dedicated column
    # CUAD filenames follow pattern: "TypeName_CompanyName_date.txt"
    filenames = df.iloc[:, 0].apply(lambda x: str(x))
    types = set()
    for name in filenames:
        # Extract type from filename: everything before the first underscore-separated company name
        # CUAD uses directory structure: full_contract_txt/TypeName/filename.txt
        parts = Path(name).parts
        if len(parts) >= 2:
            types.add(parts[-2])
        else:
            # Fallback: extract from filename pattern
            stem = Path(name).stem
            # Split on underscore, take first part as type hint
            type_part = stem.split("_")[0] if "_" in stem else stem
            types.add(type_part)
    return sorted(types)


def filter_by_type(contract_type: str, data_path: str) -> list[str]:
    """Return filenames of contracts matching a given contract type."""
    df = load_master_csv(data_path)
    filenames = df.iloc[:, 0].apply(lambda x: str(x))

    matching = []
    for name in filenames:
        parts = Path(name).parts
        if len(parts) >= 2 and parts[-2].lower() == contract_type.lower():
            matching.append(Path(name).name)
        elif contract_type.lower() in Path(name).stem.lower():
            matching.append(Path(name).name)

    return sorted(set(matching))
