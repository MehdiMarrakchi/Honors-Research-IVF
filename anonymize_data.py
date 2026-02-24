#!/usr/bin/env python3
"""
Script to anonymize sensitive fields in generated data files.
Hashes PatientIDx, PatientID, TreatmentName, FirstName, and LastName fields
and stores the mapping in a separate file.
"""

import os
import json
import hashlib
import glob
from pathlib import Path
from typing import Dict, Any, Set
from tqdm import tqdm


# Fields to anonymize
FIELDS_TO_ANONYMIZE = ['PatientIDx', 'PatientID', 'TreatmentName', 'FirstName', 'LastName']


def hash_value(value: str) -> str:
    """Hash a value using SHA256 and return hex digest."""
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest() if value is not None else None


def anonymize_dict(data: Dict[str, Any], mapping: Dict[str, str], fields: Set[str]) -> Dict[str, Any]:
    """
    Recursively anonymize fields in a dictionary.
    
    Args:
        data: Dictionary to anonymize
        mapping: Dictionary to store hash-to-original mappings
        fields: Set of field names to anonymize
    
    Returns:
        Anonymized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    anonymized = {}
    for key, value in data.items():
        if key in fields and value is not None:
            # Hash the value
            hashed_value = hash_value(value)
            # Store mapping (only store once per unique value)
            if hashed_value not in mapping:
                mapping[hashed_value] = value
            anonymized[key] = hashed_value
        elif isinstance(value, dict):
            # Recursively process nested dictionaries
            anonymized[key] = anonymize_dict(value, mapping, fields)
        elif isinstance(value, list):
            # Recursively process lists
            anonymized[key] = [
                anonymize_dict(item, mapping, fields) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            anonymized[key] = value
    
    return anonymized


def process_jsonl_file(file_path: str, mapping: Dict[str, str], fields: Set[str]) -> int:
    """
    Process a JSONL file and anonymize it in place.
    
    Returns:
        Number of records processed
    """
    temp_file = file_path + '.tmp'
    count = 0
    
    with open(file_path, 'r', encoding='utf-8') as infile, \
         open(temp_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            if line.strip():
                data = json.loads(line)
                anonymized_data = anonymize_dict(data, mapping, fields)
                outfile.write(json.dumps(anonymized_data) + '\n')
                count += 1
    
    # Replace original file with anonymized version
    os.replace(temp_file, file_path)
    return count


def process_json_file(file_path: str, mapping: Dict[str, str], fields: Set[str]) -> bool:
    """
    Process a JSON file and anonymize it in place.
    
    Returns:
        True if file was processed successfully
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if it's a list or dict
    if isinstance(data, list):
        anonymized_data = [
            anonymize_dict(item, mapping, fields) if isinstance(item, dict) else item
            for item in data
        ]
    elif isinstance(data, dict):
        anonymized_data = anonymize_dict(data, mapping, fields)
    else:
        # Skip non-dict/list JSON files (like systeminfo)
        return False
    
    temp_file = file_path + '.tmp'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(anonymized_data, f, indent=2, ensure_ascii=False)
    
    # Replace original file with anonymized version
    os.replace(temp_file, file_path)
    return True


def save_mapping(mapping: Dict[str, str], output_file: str):
    """Save the hash-to-original mapping to a file."""
    # Create reverse mapping for easier lookup (original -> hash)
    reverse_mapping = {original: hash_val for hash_val, original in mapping.items()}
    
    mapping_data = {
        'hash_to_original': mapping,
        'original_to_hash': reverse_mapping,
        'total_mappings': len(mapping)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, indent=2, ensure_ascii=False)


def main():
    """Main function to crawl and anonymize generated files."""
    fields_to_anonymize = set(FIELDS_TO_ANONYMIZE)
    mapping: Dict[str, str] = {}
    
    # Find all generated files
    data_files = glob.glob('data_*.jsonl')
    failed_treatment_files = glob.glob('failed_treatments_*.json')
    failed_patient_files = glob.glob('failed_patients_*.json')
    
    all_files = data_files + failed_treatment_files + failed_patient_files
    
    if not all_files:
        print("No generated files found to anonymize.")
        print("Looking for: data_*.jsonl, failed_treatments_*.json, failed_patients_*.json")
        return
    
    print(f"Found {len(all_files)} file(s) to process:")
    for f in all_files:
        print(f"  - {f}")
    
    # Process each file
    total_records = 0
    for file_path in tqdm(all_files, desc="Processing files"):
        file_ext = Path(file_path).suffix
        
        if file_ext == '.jsonl':
            count = process_jsonl_file(file_path, mapping, fields_to_anonymize)
            total_records += count
            print(f"  Processed {count} records from {file_path}")
        elif file_ext == '.json':
            # Skip systeminfo files
            if 'systeminfo' in file_path:
                print(f"  Skipping {file_path} (system info file)")
                continue
            
            if process_json_file(file_path, mapping, fields_to_anonymize):
                print(f"  Processed {file_path}")
            else:
                print(f"  Skipped {file_path} (unexpected format)")
    
    # Save mapping to file
    if mapping:
        mapping_file = 'anonymization_mapping.json'
        save_mapping(mapping, mapping_file)
        print(f"\nAnonymization complete!")
        print(f"  Total unique values hashed: {len(mapping)}")
        print(f"  Total records processed: {total_records}")
        print(f"  Mapping saved to: {mapping_file}")
    else:
        print("\nNo fields were anonymized (no matching fields found in files).")


if __name__ == "__main__":
    main()

