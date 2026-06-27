from pathlib import Path

import pandas as pd


DOCUMENT_TABLE_FILENAME = "document_table_v01.csv"
AI_ANALYSIS_TABLE_FILENAME = "ai_analysis_table_v01.csv"
JSON_LIKE_COLUMNS = [
    "issue_sub",
    "keywords",
    "people",
    "organizations",
    "locations",
]


def validate_data_files(data_dir="data"):
    data_path = Path(data_dir)
    document_table_path = data_path / DOCUMENT_TABLE_FILENAME
    ai_analysis_table_path = data_path / AI_ANALYSIS_TABLE_FILENAME

    missing_files = []

    if not document_table_path.exists():
        missing_files.append(str(document_table_path))

    if not ai_analysis_table_path.exists():
        missing_files.append(str(ai_analysis_table_path))

    return {
        "document_table_exists": document_table_path.exists(),
        "ai_analysis_table_exists": ai_analysis_table_path.exists(),
        "document_table_path": str(document_table_path),
        "ai_analysis_table_path": str(ai_analysis_table_path),
        "missing_files": missing_files,
    }


def load_source_tables(data_dir="data"):
    validation = validate_data_files(data_dir)

    if validation["missing_files"]:
        missing = ", ".join(validation["missing_files"])
        raise FileNotFoundError(f"Missing data file(s): {missing}")

    doc_df = pd.read_csv(validation["document_table_path"])
    ai_df = pd.read_csv(validation["ai_analysis_table_path"])

    return doc_df, ai_df


def build_master_df(doc_df, ai_df):
    if "doc_id" not in doc_df.columns:
        raise ValueError("document_table_v01.csv is missing required column: doc_id")

    if "doc_id" not in ai_df.columns:
        raise ValueError("ai_analysis_table_v01.csv is missing required column: doc_id")

    master_df = doc_df.merge(
        ai_df,
        on="doc_id",
        how="left",
        suffixes=("_doc", "_ai"),
    )

    if "date_doc" in master_df.columns:
        master_df["date_doc"] = pd.to_datetime(
            master_df["date_doc"],
            errors="coerce",
        )

    for col in JSON_LIKE_COLUMNS:
        if col in master_df.columns:
            master_df[col] = (
                master_df[col]
                .fillna("")
                .astype(str)
            )

    return master_df


def prepare_master_df(data_dir="data"):
    doc_df, ai_df = load_source_tables(data_dir)
    return build_master_df(doc_df, ai_df)


def get_data_summary(master_df):
    date_min = None
    date_max = None

    if "date_doc" in master_df.columns:
        dates = pd.to_datetime(master_df["date_doc"], errors="coerce")
        date_min_value = dates.min()
        date_max_value = dates.max()

        if pd.notna(date_min_value):
            date_min = str(date_min_value)

        if pd.notna(date_max_value):
            date_max = str(date_max_value)

    issue_main_count = 0

    if "issue_main" in master_df.columns:
        issue_main_count = int(master_df["issue_main"].dropna().nunique())

    return {
        "rows": int(len(master_df)),
        "columns": list(master_df.columns),
        "date_min": date_min,
        "date_max": date_max,
        "issue_main_count": issue_main_count,
    }
