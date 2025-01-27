import logging
import os
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# AWS keys
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")

# configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Create a logger
logger = logging.getLogger("s3_downloader")
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels

# Create handlers for info and error logs
info_handler = logging.FileHandler(LOG_DIR / "info.log")
info_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler(LOG_DIR / "error.log")
error_handler.setLevel(logging.ERROR)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Add the formatter to handlers
info_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)


def download_dicom_files(
    bucket_name: str,
    prefix: str,
    local_dir: str,
    aws_access_key=None,
    aws_secret_key=None,
):
    """
    Downloads all files from a specified S3 bucket and prefix into a local directory.

    Args:
        bucket_name (str): Name of the S3 bucket.
        prefix (str): Path prefix inside the bucket to the DICOM files.
        local_dir (str): Local directory to save the downloaded files.
        aws_access_key (str): AWS access key (optional for public buckets).
        aws_secret_key (str): AWS secret access key (optional for public buckets).

    Returns:
        None
    """

    try:
        if aws_access_key and aws_secret_key:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
            )
        else:
            s3 = boto3.client("s3")

        # List objects in the S3 bucket with the given prefix
        logger.info(f"Fetching file list from bucket: {bucket_name}, prefix: {prefix}")
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # Ensure the local directory exists
        Path(local_dir).mkdir(parents=True, exist_ok=True)

        if "Contents" not in response:
            logger.warning("No files found in the specified S3 prefix.")
            return

        for obj in response["Contents"]:
            file_key = obj["Key"]
            file_name = os.path.basename(file_key)

            if not file_name or not file_name.endswith(".dcm"):
                # Skip directories
                continue

            sanitized_filename = file_key.replace("/", "_")
            sanitized_filename = sanitized_filename.replace(" ", "")
            local_file_path = os.path.join(local_dir, sanitized_filename)

            try:
                # Download the file
                logger.info(f"Downloading {file_key} to {local_file_path}")
                s3.download_file(bucket_name, file_key, local_file_path)
            except Exception as e:
                logger.error(f"Failed to download {file_key}: {str(e)}")

    except NoCredentialsError:
        logger.error("AWS credential not provided or missing.")
    except PartialCredentialsError:
        logger.error("Incomplete AWS credential provided.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    # configuration
    BUCKET_NAME = "ct-scan-proj-data"
    PREFIX = "lidc_small_dset/"
    LOCAL_DOWNLOAD_DIR = "./dicom_data/"

    download_dicom_files(
        bucket_name=BUCKET_NAME,
        prefix=PREFIX,
        local_dir=LOCAL_DOWNLOAD_DIR,
        aws_access_key=AWS_ACCESS_KEY,
        aws_secret_key=AWS_SECRET_KEY,
    )
