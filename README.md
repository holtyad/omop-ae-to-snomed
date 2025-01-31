# OMOP AE to SNOMED

## Overview

Welcome to the **OMOP AE to SNOMED** repository, a Python-based project designed to dynamically convert NHS Accident and Emergency (A&E) Clinical Codes into OMOP Standard Concept Codes using SNOMED CT. This repository bridges the gap between raw clinical data and standardized terminologies, facilitating seamless integration into OMOP ETL pipelines. Contributions and suggestions for improvement from the community are warmly welcomed.

## Key Features

- **Converts A&E Clinical Codes**: Transforms A&E clinical codes into standardized SNOMED CT codes.
- **Utilizes Fuzzy Matching**: Integrates anatomical site data with diagnosis and sub-analysis for accurate SNOMED CT mapping.
- **Rich Data Outputs**: Provides JSON and CSV outputs for OMOP ETL integration.
- **Customizable Output**: Flexibility to choose input and output file locations.

## Installation and Usage

### Installation

Ensure you have Python 3 installed, then run the following command to install the necessary dependencies:

```bash
python3 -m pip install -r requirements.txt
```

### Usage

Run the main script with your raw codes CSV file as follows:

```bash
python3 main.py --raw_codes_path="data/raw_codes/example_raw_codes.csv"
```

- The script defaults to using `data/raw_codes/example_raw_codes.csv` if no path is specified.
- You can specify output locations for your CSV and JSON files.

The script processes your input CSV to output a machine-readable JSON lookup. This is particularly useful if you intend to integrate the outputs into your own OMOP ETL pipeline.

## Raw Input Format

To ensure the correct processing of your data, your input file should consist of A&E diagnostic codes formatted as follows:

```csv
AccidentAndEmergencyDiagnosis
03 27
25222
07 31
07 34
05234
12 26
```

Each line should represent a unique code that combines a primary diagnosis and optional sub-diagnosis and anatomical site identifiers. For further examples, please refer to the `data/` folder which includes sample input files demonstrating the required format.

## How It Works

### Input: Accident and Emergency Diagnosis Codes

The input consists of diagnostic codes derived from NHS A&E Clinical Codes, including:

1. **Diagnosis Condition**: Type of diagnosis using a structured code.
2. **Sub-analysis**: Specifics about the diagnosis, investigation, or treatment.
3. **Anatomical Site**: The specific area of the body affected.

### Workflow and Data Transformation

1. **Data Preprocessing**:
   - Reads and parses raw clinical codes from a CSV file.
   - Transforms these codes into a more structured format.

2. **Mapping to SNOMED CT**:
   - Each diagnostic condition is manually mapped to a parent SNOMED CT concept code.
   - Sub-analysis and anatomical area data are used for finer granularity and combined diagnosis descriptions.
   - Utilizes `fuzzy_match.py` to integrate anatomical site data for accurate SNOMED CT code assignment.

3. **Data Enrichment**:
   - Enriches data using mappings from a JSON lookup to correlate diagnosis conditions and sub-analyses with appropriate SNOMED codes.

4. **Output Generation**:
   - Produces an enriched CSV and a JSON file containing hierarchical structures suitable for OMOP integration.

### Outputs

1. **CSV Output**:
   - Example structure of processed data with mapped SNOMED CT codes.

   ```csv
   SourceCode,CombinedDiagnosis,ConceptCode
   02 06,Contusion of Nose,60897004
   07 31,Tendon injury of Knee,312847008
   ```

2. **JSON Output**:
   - Organized structure with detailed conditions, sub-analyses, and corresponding SNOMED codes.

   ```json
   {
       "DiagnosisConditions": [
        {
            "Condition": "Respiratory conditions",
            "Code": "25",
            "Alias": "Asthma",
            "ParentConcept": "50043002",
            "SubAnalysis": [
                {
                    "SubCondition": "Other non-asthma",
                    "SubCode": "2",
                    "SubConcept": "50043002",
                    "AnatomicalAreas": [
                        {
                            "Name": "Chest",
                            "Code": "22"
                        }
                    ]
                }
            ]
        }
        ...
       ]
   }
   ```

3. **Final Lookup**:
   - Outputs a machine-readable format for direct use within your OMOP pipeline.
   - If a fuzzy match is not feasible, parent or sub-concept codes are prioritized.

For examples of both input and output files, explore the `data/` folder in the repository, which showcases various stages of file transformations from raw to final outputs.

## Contribution and Support

If you find this repository useful or have any suggestions, queries, or improvement proposals, feel free to reach out.

Or raise an issue within the repo, I will monitor when I can.

Contact: [tomholt887@gmail.com](mailto:tomholt887@gmail.com)

We look forward to your enhancements and ideas to make this project even more robust and applicable in the field of healthcare data integration.
