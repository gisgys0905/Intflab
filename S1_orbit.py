#############################
# copyRight Author : Yisen Gao (AIRCAS-RADI AISAR) 30/08/2025 to present 
# written in       : Beijing China 
# brief introduce  : download the S1 orbit files by requesting the website
#############################

import os
import sys
import glob
import requests
import argparse
from datetime import datetime, timedelta
from multiprocessing import cpu_count
from joblib import Parallel, delayed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lab_utils import S1_config
from lab_utils import logo as show_logo
from reset import reset_orbit_dir


def download_file(session, task):
    ############################################################
    # download the orbit files 
    # <1> session (requests.session): the session between user and net
    # <2> task (list): the task of download files 
    ############################################################
    file_url, save_path = task
    try:
        with session.get(file_url, stream=True, timeout=666) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Downloaded: {os.path.basename(save_path)}")
    except Exception as e:
        print(f"Failed to download {file_url}: {e}")


def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,                
        backoff_factor=1,      
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session

def get_response(session):
    resp = session.get(ORBIT_URL, timeout=666).content
    lst = [str(i[:77])[2:-1] for i in resp.split(b'href="')]
    return lst


def download_S1_SLC_orbit_list(SLC_dir, orbits_dir, update_mode):
    ############################################################
    # download S1*.zip orbit files 
    # <1> SLC_dir (str)          :  the SLC_dir directory of the S1*.zip 
    # <2> orbits_dir (str)       :  the orbit files output directory 
    # <3> update_mode (str)      :  whether ignore the exist files , delete and update overwrite it
    ############################################################
    download_tasks = list()
    if not os.path.exists(orbits_dir):
        os.mkdir(orbits_dir)
    ## create data list 
    session = create_session()
    lst = get_response(session=session)
    ## S1_pattern directorys
    S1_dir = os.path.join(SLC_dir, "S1*.SAFE")
    for file in glob.glob(S1_dir):
        date_str = file.split('_')[-5][:8]
        y, m, d = int(date_str[:4]),  int(date_str[4:6]),  int(date_str[6:8])
        dt = datetime(y, m, d)
        prev_dt = dt - timedelta(days=1)
        next_dt = dt + timedelta(days=1)
        prev_dt_str = f'{prev_dt.year}{prev_dt.month:02d}{prev_dt.day:02d}'
        next_dt_str = f'{next_dt.year}{next_dt.month:02d}{next_dt.day:02d}'
        
        for filename in lst:
            orbit_path = os.path.join(orbits_dir, filename)
            if os.path.exists(orbit_path):
                if update_mode:
                    cmd = f"rm -rf {orbit_path}"
                    print(f"update_mode: {update_mode}, Running Command : {cmd}")
                    os.system(cmd)
                else:
                    print(f"update_mode: {update_mode}, pass it and continue")
                    continue
            if (filename[-35:-27] == prev_dt_str) and (filename[-19:-11] == next_dt_str):
                download_tasks.append((
                f"{ORBIT_URL}{filename}",
                        orbit_path
                        ))  
                        
    njobs = min(max(cpu_count() // 4, 2), 8)
    print(f"starting parallel download with {njobs} jobs...")
    Parallel(n_jobs=njobs)(
        delayed(download_file)(session, task) for task in download_tasks
    )
    print("all downloads finished.")


        
def create_parser():
    """create argument parser"""
    parser = argparse.ArgumentParser(
        description='download sentinel-1 SLC orbit files'
    )
    parser.add_argument('--SLC-dir', type=str, required=True,
                       help='directory containing Sentinel-1 SAFE files')
    parser.add_argument('--orbit-dir', type=str, required=True,
                       help='output directory for orbit files')
    parser.add_argument('--update', action='store_true', default=False,
                        help='whether delete and update the exist file')
    parser.add_argument('--reset', action='store_true', default=False,
                        help='whether reset the orbits directory (default : False)')
    parser.add_argument('--logo', action='store_true', default=False,
                        help='show the logo of IntfLab (default : False)')
    return parser


    
if __name__ == '__main__':
    # basic information 
    global ORBIT_URL
    ORBIT_URL = S1_config['ORBIT_URL']
    # create parser
    parser = create_parser()
    args = parser.parse_args()
    # receive the arguments
    SLC_dir, orbit_dir = args.SLC_dir, args.orbit_dir
    update_mode, reset, logo = args.update, args.reset, args.logo 
    if logo:
        show_logo()
    if reset:
        print(f"reset mode is :{reset}")
        reset_orbit_dir(orbit_dir=orbit_dir)
    # download orbit files
    download_S1_SLC_orbit_list(SLC_dir, orbit_dir, 
                               update_mode=update_mode
                               )
    