import sys
import glob
import json
import pandas as pd
import re
import os

# module to get column names of each dataset from schemas file
def get_column_names(schemas, ds_name, sorting_key='column_position'):
    column_details = schemas[ds_name]
    sorted_columns = sorted(column_details, key=lambda col : col[sorting_key])
    column_names = list(map(lambda column : column['column_name'], sorted_columns))
    return column_names

# module to read csv files of datasets using column names from schemas
def read_csv(file, schemas):
    file_path_list = re.split('[/\\\]', file)
    ds_name = file_path_list[-2]
    file_name = file_path_list[-1]
    columns = get_column_names(schemas, ds_name)
    df = pd.read_csv(file, names=columns, header=None)
    return df

# module to convert csv into json file under dataset folders accordingly
def to_json(df, tgt_base_dir, ds_name, file_name):
    json_file_path = f'{tgt_base_dir}/{ds_name}/{file_name}'
    os.makedirs(f'{tgt_base_dir}/{ds_name}', exist_ok=True)
    df.to_json(
        json_file_path,
        orient='records',
        lines=True
    )

# module of file converter to convert CSV into JSON
def file_converter(src_base_dir, tgt_base_dir, ds_name):
    schemas = json.load(open(f'{src_base_dir}/schemas.json'))
    files = glob.glob(f'{src_base_dir}/{ds_name}/part-*')
    if len(files) == 0:
        raise NameError(f'No file found for {ds_name}')

    for file in files:
        df = read_csv(file, schemas)
        file_name = re.split('[/\\\]', file)[-1]
        to_json(df, tgt_base_dir, ds_name, file_name)

# module to process files based on dataset names passed as arguments
def process_files(ds_names=None):
    src_base_dir = os.environ.get('SRC_BASE_DIR')
    tgt_base_dir = os.environ.get('TGT_BASE_DIR')
    schemas = json.load(open(f'{src_base_dir}/schemas.json'))

    if not ds_names:
        ds_names = schemas.keys()
    
    for ds_name in ds_names:
        try:
            print(f'Processing {ds_name} file')
            file_converter(src_base_dir, tgt_base_dir, ds_name)
        except NameError as ne:
            print(ne)
            print(f'Error processing {ds_name} file')
            pass
        

# init invoke functions
if __name__ == '__main__':
    if len(sys.argv) == 2:
        ds_names = json.loads(sys.argv[1])
        process_files(ds_names)
    else:
        process_files()
