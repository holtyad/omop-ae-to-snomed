import pandas as pd
from thefuzz import fuzz, process


def read_csv(file_path, delimiter=','):
    """
    Reads a CSV file into a pandas DataFrame with all columns as strings.

    Parameters:
    - file_path: Path to the CSV file.
    - delimiter: Delimiter for the CSV file (default is ',').

    Returns:
    - DataFrame with the CSV data.
    """
    return pd.read_csv(file_path, dtype=str, index_col=False, sep=delimiter)


def fuzzy_merge(df_left, df_right, left_on, right_on, threshold=90):
    """
    Perform a fuzzy left join on two DataFrames based on specified columns.

    Parameters:
    - df_left: Left DataFrame.
    - df_right: Right DataFrame.
    - left_on: Column name in the left DataFrame to match.
    - right_on: Column name in the right DataFrame to match.
    - threshold: Minimum score for a match to be considered (default is 90).

    Returns:
    - A DataFrame with a left join based on fuzzy matching.
    """
    df_left[left_on] = df_left[left_on].astype(str)
    df_right[right_on] = df_right[right_on].astype(str)

    matched_rows = []

    for idx, row in df_left.iterrows():
        left_value = row[left_on]
        best_matches = process.extract(
            left_value,
            df_right[right_on],
            scorer=fuzz.ratio,
            limit=1
        )
        best_match = best_matches[0] if best_matches else None

        if best_match and best_match[1] >= threshold:
            matched_row = df_right[df_right[right_on] == best_match[0]].iloc[0]
            merged_row = pd.concat([row, matched_row])
            matched_rows.append(merged_row)
            print(f"{50*'-'} \n{merged_row}\nthreshold: {best_match[1]}")
            print(f"row: {idx}")
        else:
            matched_rows.append(row)

    return pd.DataFrame(matched_rows)


def prepare_concept_code(df):
    """
    Prepares the Concept Code by backfilling columns and selecting the
    first non-null value.

    Parameters:
    - df: DataFrame containing at least 'concept_code', 'SubConcept',
    and 'ParentConcept' columns.

    Returns:
    - Series containing the resolved Concept Code.
    """
    return df[[
        'concept_code',
        'SubConcept',
        'ParentConcept'
        ]].bfill(axis=1).iloc[:, 0]


def select_and_group_data(df):
    """
    Selects specific columns and groups data by 'SourceCode'.

    Parameters:
    - df: DataFrame containing the necessary columns.

    Returns:
    - Grouped DataFrame.
    """
    df = df[['SourceCode', 'CombinedDiagnosis', 'ConceptCode']]
    return df.groupby(
        'SourceCode',
        as_index=False
    ).agg({'CombinedDiagnosis': 'max', 'ConceptCode': 'max'})


def main():
    """
    Main function to orchestrate reading, processing,
    and writing CSV data.
    """
    input_df = read_csv('data/processed/output.csv')
    concept_df = read_csv('data/config/concepts.csv', delimiter='|')

    merged = fuzzy_merge(
        input_df,
        concept_df,
        left_on='CombinedDiagnosis',
        right_on='concept_name',
        threshold=90  # Adjust threshold as needed, higher = more strict.
    )
    merged['ConceptCode'] = prepare_concept_code(merged)

    filtered = select_and_group_data(merged)
    filtered.to_csv(
        'data/processed/output_lookup/lookup_output.csv',
        index=False
    )


if __name__ == "__main__":
    main()
