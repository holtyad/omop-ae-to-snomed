import pandas as pd


def remove_spaces(df):
    """
    Remove spaces from 'AccidentAndEmergencyDiagnosis'
    column and create a source column.
    """
    df['AccidentAndEmergencyDiagnosisSource'] = df['AccidentAndEmergencyDiagnosis']  # noqa E501
    df['AccidentAndEmergencyDiagnosis'] = df['AccidentAndEmergencyDiagnosis'].str.replace(' ', '')  # noqa E501
    return df


def extract_diagnosis_condition(df):
    """
    Extract the first two characters as the DiagnosisCondition.
    """
    df['DiagnosisCondition'] = df['AccidentAndEmergencyDiagnosis'].str[:2]
    return df


def determine_sub_analysis(df):
    """
    Determine the SubAnalysis based on the length of the cleaned code.
    """
    df['SubAnalysis'] = df['AccidentAndEmergencyDiagnosis'].apply(
        lambda x: x[2:3] if len(x) == 5 else (x[-1:] if len(x) == 3 else None)
    )
    return df


def determine_anatomical_area(df):
    """
    Determine the AnatomicalArea based on the length of the cleaned code.
    """
    df['AnatomicalArea'] = df['AccidentAndEmergencyDiagnosis'].apply(
        lambda x: x[-2:] if len(x) in [5, 4] else None
    )
    return df


def transform_diagnosis(df):
    """
    Perform all transformation operations on the DataFrame.
    """
    df = remove_spaces(df)
    df = extract_diagnosis_condition(df)
    df = determine_sub_analysis(df)
    df = determine_anatomical_area(df)

    return df[
        [
            'AccidentAndEmergencyDiagnosisSource',
            'DiagnosisCondition',
            'SubAnalysis',
            'AnatomicalArea'
        ]
    ]


def read_csv(input_file):
    """
    Read input CSV file into a DataFrame.
    """
    return pd.read_csv(input_file)


def save_csv(df, output_file):
    """
    Save the DataFrame to a CSV file.
    """
    df.to_csv(output_file, index=False)
    print(f"Preprocessing complete. Output saved to {output_file}.")
    print(50*"-")


def main():
    """
    Main function to perform data transformation.
    """
    # Input and output file paths
    input_file = 'data/raw_codes/example_raw_codes.csv'
    output_file = 'data/processed/input.csv'

    # Read the CSV
    df = read_csv(input_file)

    # Apply the transformation
    transformed_df = transform_diagnosis(df)

    # Save the output to a new CSV file
    save_csv(transformed_df, output_file)


if __name__ == "__main__":
    main()
