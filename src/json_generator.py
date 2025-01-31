import csv
import json


def load_json_file(filename):
    """Load JSON data from a file."""
    with open(filename, mode='r') as file:
        return json.load(file)


def read_csv_file(filename):
    """Read data from a CSV file into a list."""
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        return [row for row in reader]


def process_data(csv_data, json_data):
    """Process the CSV data and enrich it with JSON lookup data."""
    diagnosis_conditions = {
        entry['Code']: entry for entry in json_data['DiagnosisConditions']
    }
    anatomical_areas = {
        entry['Code']: entry['Name'] for entry in json_data['AnatomicalAreas']
    }

    enriched_rows = []
    json_output = {}

    # Initialize output JSON structure
    json_output["DiagnosisConditions"] = {}

    for source_code, diagnosis_code, subanalysis_code, anatomical_code in csv_data:  # noqa: E501
        source_code = source_code.strip()
        diagnosis_code = diagnosis_code.strip()
        subanalysis_code = subanalysis_code.strip() if subanalysis_code else None  # noqa: E501
        anatomical_code = anatomical_code.strip() if anatomical_code else None

        # Look up the diagnosis condition
        diagnosis_entry = diagnosis_conditions.get(diagnosis_code)
        if not diagnosis_entry:
            continue

        # Look up the anatomical area (if given)
        anatomical_name = anatomical_areas.get(anatomical_code, None)

        # Enrich the data for the CSV
        subanalysis_entry = None
        combined_diagnosis = diagnosis_entry[
            'Alias'
        ] if 'Alias' in diagnosis_entry else diagnosis_entry['Condition']

        if subanalysis_code:
            # Find the matching subanalysis in JSON lookup
            subanalysis_entry = next(
                (
                    sub for sub in diagnosis_entry.get(
                        "SubAnalysis", []
                    ) if sub["SubCode"] == subanalysis_code
                ),
                None
            )
            if subanalysis_entry:
                combined_diagnosis = subanalysis_entry[
                    'SubCondition'
                ] if subanalysis_entry['SubCondition'] else combined_diagnosis

        if anatomical_name:
            combined_diagnosis = f"{combined_diagnosis} of {anatomical_name}"

        enriched_rows.append({
            'SourceCode': source_code,
            'DiagnosisCondition': diagnosis_code,
            'SubAnalysis': subanalysis_code if subanalysis_code else '',
            'AnatomicalArea': anatomical_code if anatomical_code else '',
            'CombinedDiagnosis': combined_diagnosis,
            'ParentConcept': diagnosis_entry.get('ParentConcept', ''),
            'SubConcept': subanalysis_entry['SubConcept'] if subanalysis_entry and 'SubConcept' in subanalysis_entry else ''  # noqa: E501
        })

        # Build hierarchical JSON structure
        if diagnosis_code not in json_output["DiagnosisConditions"]:
            json_output["DiagnosisConditions"][diagnosis_code] = {
                "Condition": diagnosis_entry['Condition'],
                "Code": diagnosis_entry['Code'],
                "Alias": diagnosis_entry.get('Alias', None),
                "ParentConcept": diagnosis_entry.get('ParentConcept', None),
                "SubAnalysis": []
            }

        condition_object = json_output["DiagnosisConditions"][diagnosis_code]
        if subanalysis_code:
            subanalysis_object = next(
                (
                    sub for sub in condition_object[
                        "SubAnalysis"
                    ] if sub["SubCode"] == subanalysis_code
                ),
                None
            )
            if not subanalysis_object:
                subanalysis_object = {
                    "SubCondition": subanalysis_entry["SubCondition"] if subanalysis_entry else None,  # noqa: E501
                    "SubCode": subanalysis_code,
                    "SubConcept": subanalysis_entry["SubConcept"] if subanalysis_entry else None,  # noqa: E501
                    "AnatomicalAreas": []
                }
                condition_object["SubAnalysis"].append(subanalysis_object)

            if anatomical_code and anatomical_name:
                anatomical_area_object = {
                    "Name": anatomical_name,
                    "Code": anatomical_code
                }
                if anatomical_area_object not in subanalysis_object["AnatomicalAreas"]:  # noqa: E501
                    subanalysis_object["AnatomicalAreas"].append(anatomical_area_object)  # noqa: E501
        else:
            # If no subanalysis, ensure a placeholder exists
            placeholder = next(
                (
                    sub for sub in condition_object[
                        "SubAnalysis"
                    ] if sub["SubCode"] is None
                ),
                None
            )
            if not placeholder:
                placeholder = {
                    "SubCondition": None,
                    "SubCode": None,
                    "SubConcept": None,
                    "AnatomicalAreas": []
                }
                condition_object["SubAnalysis"].append(placeholder)

            if anatomical_code and anatomical_name:
                anatomical_area_object = {
                    "Name": anatomical_name,
                    "Code": anatomical_code
                }
                if anatomical_area_object not in placeholder["AnatomicalAreas"]:  # noqa: E501
                    placeholder["AnatomicalAreas"].append(anatomical_area_object)  # noqa: E501

    json_output["DiagnosisConditions"] = list(
        json_output["DiagnosisConditions"].values()
    )
    return enriched_rows, json_output


def write_json_file(data, filename):
    """Write JSON data to a file."""
    with open(filename, mode='w') as json_file:
        json.dump(data, json_file, indent=4)


def write_csv_file(rows, filename):
    """Write output rows to a CSV file."""
    with open(filename, mode='w', newline='') as csvfile:
        fieldnames = [
            'SourceCode',
            'DiagnosisCondition',
            'SubAnalysis',
            'AnatomicalArea',
            'CombinedDiagnosis',
            'ParentConcept',
            'SubConcept'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Transformation complete. Output saved to {filename}.")
    print(50*"-")


def main():
    # File paths
    lookup_json_file = 'data/config/diagnosis_config.json'
    input_csv_file = 'data/processed/input.csv'
    output_json_file = 'data/processed/output.json'
    output_csv_file = 'data/processed/output.csv'

    # Load input data
    json_data = load_json_file(lookup_json_file)
    csv_data = read_csv_file(input_csv_file)

    # Process the data
    enriched_rows, json_output = process_data(csv_data, json_data)

    # Write the outputs
    write_json_file(json_output, output_json_file)
    write_csv_file(enriched_rows, output_csv_file)


if __name__ == "__main__":
    main()
