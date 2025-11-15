#############################
# copyRight Author : Yisen Gao (AIRCAS-RADI AISAR) 05/11/2025 to present 
# written in       : Beijing China 
# brief introduce  : S1 burst2safe
#############################

from lab_utils import logo as show_logo
from reset import reset_burstS1_data_dir
import os
import re
import argparse
import subprocess
import shutil
import sys

def extract_date(filename):
    # extract date from sentinel1 filename
    match = re.search(r'_(\d{8})T', filename)
    if match:
        return match.group(1)
    return None


def extract_safe_date_list(safe_dir):
    safe_pattern = re.compile(r'^S1[AB]_.*?_(\d{8})T.*\.SAFE$')
    safe_date_list = [
        safe_pattern.search(safe_file).group(1)
        for safe_file in os.listdir(safe_dir)
        if safe_pattern.match(safe_file)
    ]
    return safe_date_list


def S1_burst2safe(datadir, workdir, update_mode):
    # create SLC directory in workdir 
    safe_dir = os.path.join(workdir, 'SLC')
    if not os.path.exists(safe_dir):
        os.makedirs(safe_dir)

    tiff_files = [f for f in os.listdir(datadir) if f.endswith('.tiff')]
    for tiff_file in tiff_files:
        src_path = os.path.join(datadir, tiff_file)
        dst_path = os.path.join(safe_dir, tiff_file)
        shutil.copy2(src_path, dst_path)

    os.chdir(safe_dir)
    tiff_files = [f for f in os.listdir('.') if f.endswith('.tiff')]
    tiff_files.sort(key=extract_date)
    date_groups = {}
    for file in tiff_files:
        date = extract_date(file)
        if date:
            burst_name = file.split('-BURST')[0] + '-BURST'
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(burst_name)
            
    for date, bursts in date_groups.items():
        safe_date_list = extract_safe_date_list(safe_dir)
        if date in safe_date_list:
            # if safe_date_list contain date corresponding SAFE file:
            ## if the update_mode is True, then delete the file and run burst2safe
            ## if the update_mode is False, just pass it 
            if update_mode:
               print("update mode is : on, delete the exists file and update")
               safe_file = [os.path.join(safe_dir, safe_file) for safe_file in os.listdir(safe_dir) if date in safe_file][0]
               cmd = f"rm -rf {safe_file}"    
               print(f"Running command : {cmd}")                         
               os.system(cmd)
            else:
                pass
        if len(bursts) > 1:
            command = ['burst2safe'] + bursts
            try:
                print(f"Running command: {' '.join(command)}")
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running command: {e}")
        else:
            print(f"Skipping {date} as there is only one burst file.")
    print(f"burst2safe is done.\n go back to directory {workdir}")
    os.chdir(workdir)
    

def create_parser():
    ## create argument parser
    parser = argparse.ArgumentParser(
        description='download sentinel-1 SLC orbit files'
    )
    
    parser.add_argument('--data-dir', type=str, required=True,
                       help='directory containing sentinel-1 GTiff and xml files')
    parser.add_argument('--work-dir', type=str, required=True,
                       help='directory as workspace')
    parser.add_argument('--update', action='store_true', default=False,
                        help='whether delete and update the exist file')
    parser.add_argument('--reset', action='store_true', default=False,
                        help='whether reset the SLC directory (default : False)')
    parser.add_argument('--logo', action='store_true', default=False,
                        help='show the logo of IntfLab (default : False)')
    return parser



if __name__ == "__main__":
    # create parser and args    
    parser = create_parser()
    args = parser.parse_args()
    # receive arguments
    data_dir = args.data_dir
    work_dir = args.work_dir
    update_mode = args.update
    reset, logo = args.reset, args.logo 
    if logo:     
        show_logo()
    if reset:
        reset_burstS1_data_dir(data_dir)
        
    S1_burst2safe(datadir=data_dir, workdir=work_dir, update_mode = update_mode)