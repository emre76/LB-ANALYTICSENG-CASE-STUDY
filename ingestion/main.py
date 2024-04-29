# import storage_adapter
import pandas as pd
from tempfile import NamedTemporaryFile
import logging
import os
from time import sleep
import click
from pathlib import Path
import json
from google.cloud import storage
import os
from operator import attrgetter


def get_file_name(local_input_path,month, table_name):
    tmp_filenname = None
    for filename in os.listdir(local_input_path):
        if month in filename and table_name in filename:
            tmp_filenname = filename
    return tmp_filenname 

def upload_csv_to_gcp(bucket_name, csv_file, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(csv_file)

def csv_to_parquet(csv_file, parquet_file):
    df = pd.read_csv(csv_file)
    df.to_parquet(parquet_file)

def print_schema(df):
    mapping_dict:dict = {"str": "STRING", "object": "STRING", "float64": "FLOAT64", "bool": "BOOLEAN", "int64": "INTEGER"}
    dtype_getter = attrgetter('name')
    dt = df.dtypes.map(dtype_getter).to_dict()

    for key,value in dt.items():
        print(f"- name: {key}")
        print(f"  data_type: {mapping_dict[value]}")


def cast_datatypes(df:pd.DataFrame, cast_to_datatypes) -> None:
    for key, value in cast_to_datatypes.items():
        if df.get(key) is None:
            df[key] = pd.NA
    
        df[key] = df[key].astype(value)
        logging.info(f'trying to cast column "{key}" to Pandas data type "{value}" ...')

def upload_parquet_to_gcp(file_path, bucket_name, parquet_path_gcp, destination_blob_name, cast_to_datatypes, entity_path_gcp):
    df = pd.read_csv(file_path,sep = ';')

    #print_schema(df)

    cast_datatypes(df, cast_to_datatypes)

    
    #print("\n")
    #print_schema(df)

    df.to_parquet(destination_blob_name)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=entity_path_gcp)
    for blob in blobs:
        blob.delete()

    blob = bucket.blob(parquet_path_gcp+"/"+destination_blob_name)
    blob.upload_from_filename(destination_blob_name)

@click.command()
@click.option(
    "--runtime",
    type=click.Choice(
        [
            "local-dev",
            "development",
            "test",
            "production",
        ],
        case_sensitive=False,
    ),
    default="local-dev",
)
@click.option("--month", type=str, required=True, help="the month in yyyymm format we are looking for")
@click.option("--table-name", type=str, required=True, help=" table name to be uploaded")
@click.option("--bucket-name", type=str, required=False, help="cloud bucket name, default value in conf file")
@click.option("--target-path-csv", type=str, required=False, help="target path for csv at the cloud bucket")
@click.option("--target-path-parquet", type=str, required=False, help="target path for parquet at the cloud bucket")
def run(runtime, month, table_name, bucket_name, target_path_csv, target_path_parquet):
    logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)-8s %(name)-20s %(message)s')
    logging.info(f"runtime: {runtime}")
    logging.info(f"month: {month}")
    logging.info(f"table-name: {table_name}")
    logging.info(f"bucket-name: {bucket_name}") 
    logging.info(f"target-path-csv: {target_path_csv}")
    logging.info(f"target-path-parquet: {target_path_parquet}")

    with open(os.path.join(Path(__file__).parents[1], 'config', 'config.json'), 'r', encoding="utf8") as f_read:
        _config = json.load(f_read)

    #print(_config)
    
    with open(os.path.join(Path(__file__).parents[1], 'config', 'source_columns.json'), 'r', encoding="utf8") as f_read:
        _config_cols = json.load(f_read)

    #print(_config_cols)
    
    _bucket = bucket_name if bucket_name else _config["gcp-adapter"]["bucket"]

    _local_input_path = _config["gcp-adapter"]["local_input_path"]
    _target_path_csv = _config["gcp-adapter"]["target_path_csv"]
    _target_path_parquet = _config["gcp-adapter"]["target_path_parquet"]

    cast_to_datatypes=_config_cols.get(table_name, {}).get("cast_to_datatypes")

    #print(_bucket)

    file_name = get_file_name(_local_input_path, month, table_name)
    file_path = os.path.join(_local_input_path,file_name)
    print(file_path)
    parquet_path_gcp = os.path.join(_target_path_parquet , file_name[file_name.find('_')+1 : file_name.find('.')] ,  f"part_month={file_name[:6]}",  f"part_day={file_name[:8]}",  f"part_datetime={file_name[:14]}")
    entity_path_gcp = os.path.join(_target_path_parquet , file_name[file_name.find('_')+1 : file_name.find('.')])

    upload_csv_to_gcp(_bucket, file_path, os.path.join(_target_path_csv,file_name))

    
    # Parquet file path
    parquet_file_path = "ingestion/output_data/output.parquet"

    # Destination blob name in GCP storage
    destination_blob_name = f"{file_name.split('_')[0]}.parquet"
    #print(destination_blob_name)

    # Convert CSV to Parquet
    csv_to_parquet(file_path, parquet_file_path)

    # Upload Parquet file to GCP Cloud Storage
    upload_parquet_to_gcp(file_path, _bucket, parquet_path_gcp,destination_blob_name,cast_to_datatypes, entity_path_gcp)






if __name__ == "__main__":
    run()