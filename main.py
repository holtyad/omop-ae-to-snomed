
import typer
from pathlib import Path
from src.transform_codes import (
    transform_diagnosis,
    read_csv,
    save_csv,
)

from src.json_generator import (
    load_json_file,
    read_csv_file,
    process_data,
    write_json_file,
    write_csv_file,
)

from src.fuzzy_match import (
    fuzzy_merge,
    read_csv as read_fuzzy_csv,
    select_and_group_data,
    prepare_concept_code,
)

app = typer.Typer()


def process_codes(raw_file: str, output_file: str) -> None:
    """Transform raw codes CSV to transformed CSV."""
    df = read_csv(raw_file)
    transformed_df = transform_diagnosis(df)
    save_csv(transformed_df, output_file)


def generate_json(
    lookup_json: str,
    input_csv: str,
    output_json: str,
    output_csv: str,
) -> None:
    """Generate enriched JSON and CSV from processed input."""
    json_data = load_json_file(lookup_json)
    csv_data = read_csv_file(input_csv)
    enriched_rows, json_output = process_data(csv_data, json_data)
    write_json_file(json_output, output_json)
    write_csv_file(enriched_rows, output_csv)


def fuzzy_match(
    input_csv: str,
    concept_file: str,
    output_lookup: str,
) -> None:
    """Perform fuzzy matching and output lookup results."""
    input_df = read_fuzzy_csv(input_csv)
    concept_df = read_fuzzy_csv(concept_file, delimiter="|")

    merged = fuzzy_merge(
        input_df,
        concept_df,
        left_on="CombinedDiagnosis",
        right_on="concept_name",
        threshold=90,
    )
    merged["ConceptCode"] = prepare_concept_code(merged)
    filtered = select_and_group_data(merged)
    filtered.to_csv(output_lookup, index=False)


@app.command()
def main(
    raw_codes_path: Path = Path("data/raw_codes/example_raw_codes.csv")
) -> None:
    """Process raw codes and generate outputs."""
    processed_input = Path("data/processed/input.csv")
    lookup_json_file = Path("data/config/diagnosis_config.json")
    output_json_file = Path("data/processed/output.json")
    output_csv_file = Path("data/processed/output.csv")
    concept_file = Path("data/config/concepts.csv")
    lookup_output_file = Path("data/processed/output_lookup/lookup_output.csv")

    process_codes(
        raw_codes_path,
        processed_input
    )
    generate_json(
        lookup_json_file,
        processed_input,
        output_json_file,
        output_csv_file
    )
    fuzzy_match(
        output_csv_file,
        concept_file,
        lookup_output_file
    )

    print(50*"-")
    print(f"Concept matching complete. Output saved to {lookup_output_file}.")


if __name__ == "__main__":
    app()
