######################################################
# S1stackApp.py : a main function of PyIntfLab to preprocess SLC using ISCE2
# copyRight Author : Yisen Gao (AIRCAS-RADI AISAR) 30/08/2025 to present 
# written in       : Beijing China 
## This application provides a comprehensive InSAR processing pipeline 
## for Sentinel-1 satellite data using the ISCE2 framework. It implements
## a modular architecture with intelligent workspace management and step-by-step
## processing capabilities. The pipeline handles the complete workflow from
## raw SLC data extraction through interferometric stack generation, including
## automatic DEM and orbit file acquisition. The system features robust error
## handling, parameter validation, and on-demand directory creation to optimize
## resource usage and maintain clean project organization throughout the
## complex multi-step InSAR processing chain based ISCE2.
#######################################################

import os
import sys
import argparse
import shutil
from cores.validation import S1ParameterValidator
from cores.workspace import S1WorkspaceManager
from lab_utils import *
from S1_burst2safe import S1_burst2safe
from S1_unzip import unzip_S1_SLC_list, get_S1_zip_files
from S1_dem import download_S1_SLC_dem 
from S1_orbit import download_S1_SLC_orbit_list, download_file
from S1_stackSentinel import stack_sentinel
from S1_runISCE2 import auto_insar_stacking_ISCE2
from lab_utils import S1_config
from lab_utils import logo as show_logo


def create_parser():
    EPILOG = S1_config['S1stackApp']
    parser = argparse.ArgumentParser(
        description='S1 InSAR preprocessing pipeline using ISCE2',
        epilog=EPILOG
    )
    ## directory parameters
    parser.add_argument('--data-dir', type=str, required=True,
                       help='base data directory containing project folder with zip files')
    parser.add_argument('--work-dir', type=str, required=True,
                       help='base working directory')
    parser.add_argument('--project', type=str, required=True,
                       help='project name')
    ## bbox parameters
    parser.add_argument('--lat-min', type=float, required=True,
                       help='minimum latitude of the study area')
    parser.add_argument('--lat-max', type=float, required=True,
                       help='maximum latitude of the study area')
    parser.add_argument('--lon-min', type=float, required=True,
                       help='minimum longitude of the study area')
    parser.add_argument('--lon-max', type=float, required=True,
                       help='maximum longitude of the study area')
    ## multilooks
    parser.add_argument('--nalks', type=int, required=True,
                       help='Number of azimuth looks')
    parser.add_argument('--nrlks', type=int, required=True,
                       help='Number of range looks')
    ## S1/S1_burst 
    parser.add_argument('--mode', type=str, default='S1', 
                        help = "Sentinel1 process mode: S1 or S1_burst (default=S1) ")
    ## logo reset and update
    parser.add_argument('--logo', action='store_true', default=True,
                        help='show the logo of IntfLab (default : True)')
    parser.add_argument('--reset', action='store_true', default=False,
                        help='whether reset the work directory (default : False)')
    parser.add_argument('--update', action='store_true', default=False,
                        help='whether delete the exist files and overwrite')
    # dostep
    parser.add_argument('--step', type=str, default='-',
                       help='Processing step: 1-5 or "all" (default: -)')
    return parser



def S1_auto_InSAR_stacking(data_dir, work_dir, project, 
                        lat_min, lat_max, lon_min, lon_max, 
                        nalks, nrlks, mode, update_mode, step):
    # Complete S1 InSAR preprocessing pipeline using ISCE2
    # <1>  data_dir    (str)    : Base data directory containing project folder with zip files
    # <2>  work_dir    (str)    : Base working directory 
    # <3>  project     (str)    : Project name
    # <4>  lat_min     (float)  : Bounding box coordinates lat_min
    # <5>  lat_max     (float)  : Bounding box coordinates lat_max
    # <6>  lon_min     (float)  : Bounding box coordinates lon_min
    # <7>  lon_max     (float)  : Bounding box coordinates lon_max
    # <8>  nalks       (int)    : number of looks in the azimuth direction 
    # <9>  nrlks       (int)    : number of looks in the range direction 
    # <10> mode        (str)    : use S1/S1_burst mode to process Sentinel1 datasets
    # <11> step        (str)    : dostep execute in the Timeseries InSAR processing
    # <12> update_mode (bool)   : whether cover exist files and overwrite thems  
    
    # init project directory
    workspace = S1WorkspaceManager(work_dir, project)
    zip_source_dir = os.path.join(workspace, data_dir)
    project_dir = workspace.get_project_path()
    slc_dir = workspace.slc_dir
    orbit_dir = workspace.orbit_dir
    dem_dir = workspace.dem_dir
    aux_dir = workspace.aux_dir
    orbit_dir = workspace.orbit_dir
    process_dir = workspace.process_dir
    print(f"go to project directory : {project_dir}")
    
    # step 1: unzip SLC files
    if step == 1 or step == '-':
        if mode == "S1":
            unzip_S1_SLC_list(zip_source_dir,slc_dir,update_mode=update_mode)
        elif mode == "S1_burst":
            S1_burst2safe(datadir, workdir)
    # step2 : download orbit files
    if step == 2 or step == '-':
        download_S1_SLC_orbit_list(slc_dir, orbit_dir, update_mode = update_mode)
    # step3 : download dem files
    if step == 3 or step == '-':
        download_S1_SLC_dem(lat_min, lat_max, lon_min, lon_max, str(dem_dir))
    # step 4: Generate stack processing runfiles
    if step == 4 or step == '-':
        stack_sentinel(
            lat_min, lat_max, lon_min, lon_max,
            str(dem_dir), str(aux_dir), str(slc_dir), str(orbit_dir),
            nalks, nrlks, str(process_dir)
        )
    # step 5 : batch run files ~
    elif step == 5 or step == '-':
        runfiles_dir = os.path.join(process_dir, "run_files")
        auto_insar_stacking_ISCE2(str(runfiles_dir), nounwrap=False)
    
    print('normal S1stackApp.py workflow finished ~')
    os.chdir(project_dir)    
    


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    
    # receive parameters 
    data_dir, work_dir = args.data_dir, args.work_dir
    project = args.project
    lat_min, lat_max = args.lat_min, args.lat_max
    lon_min, lon_max = args.lon_min, args.lon_max
    nalks, nrlks = args.nalks, args.nrlks
    mode, step = args.mode, args.step
    logo, reset = args.logo, args.reset 

    # logo 
    if logo: 
        show_logo()
    # reset 
    if reset:
        print(f"the reset mode is : {reset}")
        work_dir_exp = f"{work_dir}/*"
        cmd = f"rm -rf {work_dir_exp}"
        print(f"Running Command : {cmd}")
        os.system(cmd)
        
    # initialize validator
    validator = S1ParameterValidator()
    coord_valid, coord_error = validator.validate_coordinates(
    )
    if not coord_valid:
        print(f"ERROR: {coord_error}")
        sys.exit(1)
    # Validate number of range looks and azimuth looks
    param_valid, param_error = validator.validate_processing_parameters(
        args.nalks, args.nrlks
    )
    if not param_valid:
        print(f"ERROR: {param_error}")
        sys.exit(1)
    # Validate and convert step
    step, step_error = validator.validate_step(args.step)
    if step is None:
        print(f"ERROR: {step_error}")
        sys.exit(1)
    # Validate the data and work directory
    dir_valid, dir_error = validator.validate_directories(
        args.data_dir, args.work_dir
    )
    if not dir_valid:
        print(f"ERROR: {dir_error}")
        sys.exit(1)
             
    S1_auto_InSAR_stacking(data_dir, work_dir, project, 
                        lat_min, lat_max, lon_min, lon_max, 
                        nalks, nrlks, mode, update_mode, step)
    