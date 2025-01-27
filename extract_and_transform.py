import os
import shutil

import pandas as pd
import pydicom
from pydicom.errors import InvalidDicomError


# Function to extract metadata from a DICOM file
def extract_metadata(dicom_file):
    """Extracts metadata from a DICOM file."""
    try:
        ds = pydicom.dcmread(dicom_file)

        # Extract relevant fields
        metadata = {
            "PatientID": getattr(ds, "PatientID", None),
            "StudyInstanceUID": getattr(ds, "StudyInstanceUID", None),
            "SeriesInstanceUID": getattr(ds, "SeriesInstanceUID", None),
            "NumberOfSlices": getattr(ds, "InstanceNumber", None),
            "SliceThickness": getattr(ds, "SliceThickness", None),
            "PixelSpacing": getattr(ds, "PixelSpacing", None),
            "StudyDate": getattr(ds, "StudyDate", None),
            "AcquisitionDate": getattr(ds, "AcquisitionDate", None),
        }
        return metadata

    except InvalidDicomError:
        print(f"Invalid DICOM file: {dicom_file}")
        return None
    except Exception as e:
        print(f"Error reading {dicom_file}: {e}")
        return None


# Function to reorganize files based on metadata
def reorganize_files(dicom_file, metadata, destination_dir, file_conflict_log):
    """Reorganizes DICOM files into logical folders based on metadata."""
    patient_id = metadata.get("PatientID")
    study_instance_uid = metadata.get("StudyInstanceUID")

    if not patient_id or not study_instance_uid:
        print(f"Missing metadata for file: {dicom_file}, skipping.")
        return

    # Create the target directory path: <PatientID>/<StudyInstanceUID>/
    target_dir = os.path.join(destination_dir, patient_id, study_instance_uid)

    # Create directories if they don't exist
    os.makedirs(target_dir, exist_ok=True)

    # Determine the new file path and move the file there
    filename = os.path.basename(dicom_file)
    new_file_path = os.path.join(target_dir, filename)

    # Avoid overwriting existing files (handle duplicates)
    if os.path.exists(new_file_path):
        print(f"Duplicate file detected: {dicom_file}. Skipping.")
        # Log the conflict
        file_conflict_log.append(f"Duplicate file: {dicom_file}")
    else:
        shutil.move(dicom_file, new_file_path)
        print(f"Moved {dicom_file} to {new_file_path}")


# Function to extract metadata from all DICOM files in a directory
def extract_and_reorganize_metadata_from_directory(directory, destination_dir):
    """Extracts metadata and reorganizes DICOM files."""
    metadata_list = []
    file_conflict_log = []

    for root, _, files in os.walk(directory):
        for file in files:
            # Skip hidden/system files like .DS_Store
            if file.startswith("."):
                print(f"Skipping hidden/system file: {file}")
                continue

            dicom_path = os.path.join(root, file)
            metadata = extract_metadata(dicom_path)
            if metadata:
                metadata_list.append(metadata)
                reorganize_files(
                    dicom_path, metadata, destination_dir, file_conflict_log
                )

    # Convert metadata list to a DataFrame for further processing or saving
    metadata_df = pd.DataFrame(metadata_list)

    return metadata_df, file_conflict_log


if __name__ == "__main__":
    # Path to the directory containing downloaded DICOM files
    DICOM_DIR = "./dicom_data"

    # Path to the directory where reorganized files will be saved
    DESTINATION_DIR = "./reorganized_dicom_data"

    # Path to the logs directory
    LOGS_DIR = "./logs"

    # Ensure logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Extract metadata and reorganize files
    metadata_df, conflict_log = extract_and_reorganize_metadata_from_directory(
        DICOM_DIR, DESTINATION_DIR
    )

    # Save metadata to a CSV file for reference
    if not metadata_df.empty:
        metadata_csv_path = "./dicom_metadata.csv"
        metadata_df.to_csv(metadata_csv_path, index=False)
        print(f"Metadata extracted and saved to {metadata_csv_path}")
    else:
        print("No valid DICOM metadata found.")

    # If there were file conflicts, save the conflict log to a file in the logs folder
    if conflict_log:
        conflict_log_path = os.path.join(LOGS_DIR, "conflict_log.txt")
        with open(conflict_log_path, "w") as f:
            for entry in conflict_log:
                f.write(f"{entry}\n")
        print(f"File conflicts logged in {conflict_log_path}")
