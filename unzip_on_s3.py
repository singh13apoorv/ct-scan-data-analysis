import io
import os
import zipfile

import boto3

# Get the bucket name from environment
S3_BUCKET = os.environ.get("S3_BUCKET")

# Error Handling:
if not S3_BUCKET:
    raise ValueError("Bucket name is not set in environment.")

# Initialize S3 client
s3_client = boto3.client("s3")

# Define the S3 bucket and the key for the zipped file
bucket_name = S3_BUCKET
zip_key = "LIDCSmallDataset.zip"
extracted_folder_key = ""

# Download the zipped file from S3

try:
    response = s3_client.get_object(Bucket=bucket_name, Key=zip_key)
    zip_file_content = response["Body"].read()

    # Create a zip file object from the downloaded content
    with zipfile.ZipFile(io.BytesIO(zip_file_content)) as zip_ref:
        # Extract all the files in the zip
        for file_info in zip_ref.infolist():
            # Read each file in the zip
            extracted_file_content = zip_ref.read(file_info.filename)

            # Define the S3 key for the extracted file (same folder structure)
            extracted_file_key = extracted_folder_key + file_info.filename

            # Upload the extracted file back to S3
            s3_client.put_object(
                Bucket=bucket_name, Key=extracted_file_key, Body=extracted_file_content
            )

    print(f"Files extracted and uploaded to {bucket_name}/{extracted_folder_key}")
except ValueError as ve:
    print(f"ValueError: {str(ve)}")
except Exception as e:
    print(f"Unknow Error: {str(e)}")
