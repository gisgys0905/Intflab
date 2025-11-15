#############################
# copyRight Author : Yisen Gao (AIRCAS-RADI AISAR) 05/11/2025 to present 
# written in       : Beijing China 
# brief introduce  : unzipping Sentinel1 SLC file S1*.zips
############################ 

import os
import sys
import zipfile
import glob
import argparse
from multiprocessing import cpu_count
from joblib import Parallel, delayed
from lab_utils import logo as show_logo
from reset import reset_zipped_dir


def unzip_S1_SLC(zip_file, safe_file, update_mode):
    ############################################################
    # unzip a single Sentinel-1 SLC zip file from ASF/NASA
    # <1> zip_file    : path to the S1 SLC zip file
    # <2> target_dir  : target directory to extract files
    # <3> update_mode : whether update exist file
    # <return>        : None
    ############################################################
    ## for the S1_mode 
    ##  zip_file   : ~/DATADIR/PROJECT_NAME/S1*.zip
    ##  target_dir : ~/WORKDIR/PROJECT_NAME/SLC/S1*.SAFE
    ## for the S1_burst mode :s
    ##  one single file to the single unzipped file
    ############################################################
    zip_file_basename = os.path.basename(zip_file)
    print(f"unzipping {zip_file_basename} ...")
    safe_file_basename = os.path.basename(safe_file)
    # skip if already extracted
    ## if update_mode == True  : then delete the exist file and unzip it again
    ## if update_mode == False : keep the exist file and skip unzip
    if os.path.exists(safe_file):
        if update_mode:
            print(f"remove {safe_file_basename} ...")
            cmd = f"rm -rf {safe_file}"
            print(f"running command : {cmd}")
            os.system(cmd)
        else:
            print(f"updateMode : {update_mode}. pass and return")
            return 
    # create log file
    target_dir = os.path.dirname(safe_file)
    log_file = os.path.join(target_dir, f"unzip_{safe_file_basename}.log")
    with open(log_file, 'w', encoding='utf-8') as log_f:
        log_f.write(f'unzip_{zip_file_basename}:\n')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            log_f.write(f'total files to extract: {total_files}\n')
            log_f.write('extracting files:\n')
            for i, file_name in enumerate(file_list, 1):
                log_f.write(f'\t[{i:4d}/{total_files}] {file_name}\n')
                zip_ref.extract(file_name, path=target_dir)
            log_f.write('extraction completed successfully.\n')
        print(f"unzip finished: {zip_file_basename}")


def unzip_S1_SLC_list(zipped_dir, slc_dir, update_mode):
    ############################################################
    # Unzip multiple Sentinel-1 SLC zip files in parallel
    # <1>       : zipped_dir    : zipped directory to storage zipped files
    # <2>       : slc_dir       : slc directory to extract files
    # <3>       : update_mode   : whether update exist file
    # <return>  : None
    ############################################################
    # get S1 zip files
    zip_files = get_S1_zip_files(zip_dir)
    if not zip_files:
        print(f"no sentinel-1 zip files found in {zip_dir}")
        print("expected file pattern: S1*.SAFE.zip")
        sys.exit(1)
        
    if not os.path.exists(slc_dir):
        os.mkdir(slc_dir)
    n_jobs = min(max(int(cpu_count() / 4), 2), 8)
    ## create safe_file_list to load safe file
    safe_file_list = []
    for zip_file in zip_files:
        zip_basename = os.path.basename(zip_file)
        safe_basename = zip_basename[:-4] + ".SAFE"
        safe_file = os.path.join(slc_dir, safe_basename)
        safe_file_list.append(safe_file)
    ## Parallel unzip files
    n_jobs = min(max(int(cpu_count() / 4), 2), 8) 
    Parallel(n_jobs=n_jobs)(
        delayed(unzip_S1_SLC)(zip_file, safe_file, update_mode) 
        for zip_file, safe_file in zip(zip_files, safe_file_list)
    )


def get_S1_zip_files(zipped_dir):
    # get all Sentinel-1 zip files from data directory
    # <1> zipped_dir: S1 zip files directory
    # <return> s1_zip_files: the entire path list of each zipfile 
    data_path = zipped_dir
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"data directory does not exist: {data_path}")
    # find all zip files
    zip_pattern = os.path.join(data_path, "*.zip")
    zip_files = glob.glob(zip_pattern)
    # filter for S1 files
    s1_zip_files = []
    for zip_file in zip_files:
        zip_name = os.path.basename(zip_file)
        if zip_name.startswith('S1') and zip_name.endswith(".zip"):
            s1_zip_files.append(zip_file)
    return sorted(s1_zip_files)


def create_parser():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="unzip S1*.zip files by parallel automatillay"
    )
    parser.add_argument('--zip-dir', type=str, required=True, 
                       help='sentinel-1 zip files directory')
    parser.add_argument('--slc-dir', type=str, required=True, 
                       help='target directory to unzip SLC files')
    parser.add_argument('--update', action='store_true', default=False,
                        help='whether update exist file (default : False)')
    parser.add_argument('--reset', action='store_true', default=False,
                        help='whether reset the zipfiles directory (default : False)')
    parser.add_argument('--logo', action='store_true', default=True,
                        help='show the logo of IntfLab')
    parser.add_argument('--mode', type=str, default="S1",
                        help='mode in processing Sentinel1 S1/S1_burst (default : S1)')
    return parser


if __name__ == "__main__":
    # create parser and args    
    parser = create_parser()
    args = parser.parse_args()
    # receive arguments
    zip_dir = args.zip_dir
    slc_dir = args.slc_dir
    update_mode = args.update
    reset, logo = args.reset, args.logo
    # reassure there is only zip files
    if reset:
        print(f"reset mode is :{reset}")
        reset_zipped_dir(zip_dir)
    if logo:
        show_logo()
    # run unzip_S1_SLC_list to unzip each file 
    unzip_S1_SLC_list(zip_dir, slc_dir, update_mode=update_mode)