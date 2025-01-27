# ct-scan-data-analysis

## Step 1: Create and activate conda environment:

- `conda create --name ct-scan-da python=3.11`
- `conda activate ct-scan-da`

## Step 2: Add environment variables to conda environment:

- `conda env config vars set AWS_ACCESS_KEY=(Enter your access key string)`
- `conda env config vars set AWS_SECRET_KEY=(Enter your secret key string)`
- `conda env config vars set S3_BUCKET=(Enter your bucket name string)`
- `conda env config vars set FOLDER_PREFIX=(Enter your folder prefix string)`

## Step 3: Install the requirements:

- `pip install -r requirements.txt`

## Step 4: Do this step only if you have the data as a zip file in S3 bucket:

- `python unzip_on_s3.py`

## step 5: Run the download script:

<p>
    This script downloads all the data in the s3 bucket in the given folder
    and stores it to a folder called ./dicom_data. This script also generates
    and saves info and error logs to info.log and error.log files in ./logs folder
    respectively.
</p>

- `python download_script.py`

## Step 6: Run the extract and transform script:

<p>
    This script extracts the metadata, creates a csv file called dicom_metadata.csv
    and use the metadata to reorganise the downloaded data to an new folder called
    ./reorganized_dicom_data.
    This script also generate a conflict.log file if there is a conflict between two
    files and saves it to ./logs/conflicts.log.txt
</p>

- `python extract_and_transform.py`

## Step 7: Run the iPython notebook for summary statistics and visualization:

### Open jupyter lab

- `jupyter lab`

### Open the file summarize_and_visualize_dicom.ipynb and run each cell

