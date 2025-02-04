'''
read in .rds, .rds.gz, and .fst files and convert to pandas df
'''

# .RDS/.RDS.GZ
import os, gzip, tempfile
import pyreadr

def read_rds(file):
    df = pyreadr.read_r(file)[None]
    
    return df

def read_rdsgz(file):
    # Create a temporary file to store the decompressed RDS content
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        temp_rds_file_path = tmp_file.name

        # Open and decompress the .gz file
        with gzip.open(file, 'rb') as gz_file:
            # Write the decompressed content to the temporary file
            tmp_file.write(gz_file.read())

    # Read the decompressed RDS content from the temporary file
    df = read_rds(temp_rds_file_path)

    # Delete the temporary file
    os.remove(temp_rds_file_path)

    return df

# .FST
import rpy2.robjects as ro
from rpy2.robjects.packages import importr, isinstalled
from rpy2.robjects import pandas2ri

def read_fst(file):
    with (ro.default_converter + pandas2ri.converter).context():
        if not isinstalled('fst'):
            print("Installing 'fst' package to conda environment...")
            utils = importr('utils')
            utils.install_packages('fst')

        fst = importr('fst')
        r_df = fst.read_fst(file)
        df = ro.conversion.rpy2py(r_df)
    
    return df
