import pytest # noqa E501
import json
import csv
import tempfile
from src.json_generator import (
    load_json_file,
    read_csv_file,
    process_data,
    write_json_file,
    write_csv_file
)


# Sample JSON lookup data
sample_json_data = {
    "DiagnosisConditions": [
        {
            "Condition": "Diabetes and other endocrinological conditions",
            "Code": "30",
            "Alias": "Diabetes",
            "ParentConcept": "309048008",
            "SubAnalysis": [
                {
                    "SubCondition": "Diabetic",
                    "SubCode": "1",
                    "SubConcept": "73211009"
                },
                {
                    "SubCondition": "Other non-diabetic",
                    "SubCode": "2",
                    "SubConcept": "309048008"
                }
            ]
        }
    ],
    "AnatomicalAreas": [
        {"Code": "01", "Name": "Brain"},
        {"Code": "02", "Name": "Head"}
    ]
}

# Sample input CSV data
sample_csv_data = [
    ["30", "30", "", ""],
    ["302", "30", "2", ""],
    ["301", "30", "1", ""]
]

# Expected outputs for processed data
expected_enriched_rows = [
    {
        "SourceCode": "30",
        "DiagnosisCondition": "30",
        "SubAnalysis": "",
        "AnatomicalArea": "",
        "CombinedDiagnosis": "Diabetes",
        "ParentConcept": "309048008",
        "SubConcept": ""
    },
    {
        "SourceCode": "302",
        "DiagnosisCondition": "30",
        "SubAnalysis": "2",
        "AnatomicalArea": "",
        "CombinedDiagnosis": "Other non-diabetic",
        "ParentConcept": "309048008",
        "SubConcept": "309048008"
    },
    {
        "SourceCode": "301",
        "DiagnosisCondition": "30",
        "SubAnalysis": "1",
        "AnatomicalArea": "",
        "CombinedDiagnosis": "Diabetic",
        "ParentConcept": "309048008",
        "SubConcept": "73211009"
    }
]

expected_json_output = {
    "DiagnosisConditions": [
        {
            "Condition": "Diabetes and other endocrinological conditions",
            "Code": "30",
            "Alias": "Diabetes",
            "ParentConcept": "309048008",
            "SubAnalysis": [
                {
                    "SubCondition": None,
                    "SubCode": None,
                    "SubConcept": None,
                    "AnatomicalAreas": []
                },
                {
                    "SubCondition": "Other non-diabetic",
                    "SubCode": "2",
                    "SubConcept": "309048008",
                    "AnatomicalAreas": []
                },
                {
                    "SubCondition": "Diabetic",
                    "SubCode": "1",
                    "SubConcept": "73211009",
                    "AnatomicalAreas": []
                }
            ]
        }
    ]
}


def test_load_json_file():
    with tempfile.NamedTemporaryFile(
        mode='w',
        delete=False
    ) as temp_file:

        json.dump(sample_json_data, temp_file)
        temp_file_name = temp_file.name

    loaded_data = load_json_file(temp_file_name)
    assert loaded_data == sample_json_data


def test_read_csv_file():
    with tempfile.NamedTemporaryFile(
        mode='w',
        newline='',
        delete=False
    ) as temp_file:

        writer = csv.writer(temp_file)
        writer.writerow(
            [
                "SourceCode",
                "DiagnosisCode",
                "SubAnalysisCode",
                "AnatomicalCode"
            ]
        )
        writer.writerows(sample_csv_data)
        temp_file_name = temp_file.name

    read_data = read_csv_file(temp_file_name)
    assert read_data == sample_csv_data


def test_process_data():
    enriched_rows, json_output = process_data(
        sample_csv_data,
        sample_json_data
    )
    assert enriched_rows == expected_enriched_rows
    assert json_output == expected_json_output


def test_write_json_file():
    with tempfile.NamedTemporaryFile(
        mode='w',
        delete=False
    ) as temp_file:

        write_json_file(expected_json_output, temp_file.name)
        temp_file_name = temp_file.name

    with open(temp_file_name, 'r') as file:
        data = json.load(file)
    assert data == expected_json_output


def test_write_csv_file():
    with tempfile.NamedTemporaryFile(
        mode='w',
        newline='',
        delete=False
    ) as temp_file:

        write_csv_file(expected_enriched_rows, temp_file.name)
        temp_file_name = temp_file.name

    with open(temp_file_name, 'r') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]

    # Convert all row values back into strings for comparison
    expected_rows_str = [
        {k: str(v) for k, v in row.items()} for row in expected_enriched_rows
    ]
    assert rows == expected_rows_str
