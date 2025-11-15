#############################
# copyRight Author : CAS-aircas Yisen 
# time : 30/08/2025 Saturday
# written in : Beijing China 
# brief introduce : using dem.py to download Digital Elevation model, exp is .wgs84
# sunny day in Beijing at 01/09/2025

## MudCreep : 35.83 35.90 -121.50 -121.38
#############################


import os
import sys
import argparse
import subprocess
from cores.validation import S1ParameterValidator
from lab_utils import logo as show_logo 
from reset import reset_dem_dir

def download_S1_SLC_dem(lat_min, lat_max, lon_min, lon_max, dem_dir):
    # download Digital Elevation Model using dem.py
    # <1> lat_min (float): minimum latitude (south)
    # <2> lat_max (float): maximum latitude (north)  
    # <3> lon_min (float): minimum longitude (west)
    # <4> lon_max (float): maximum longitude (east)
    # <5> dem_dir (str): output directory for DEM files
    ## create dem directory
    if not os.path.exists(dem_dir):
        os.mkdir(dem_dir)
    os.chdir(dem_dir)
    ## make lat/lon buffer
    lat_min_dem = int(float(lat_min)) - 1
    lat_max_dem = int(float(lat_max)) + 1
    lon_min_dem = int(float(lon_min)) - 1
    lon_max_dem = int(float(lon_max)) + 1
        
    ## command
    log_file = os.path.join(dem_dir, "dem_download.log")
    cmd = f"dem.py -b {str(lat_min_dem)} {str(lat_max_dem)} {str(lon_min_dem)} {str(lon_max_dem)} -r -s 1 -u http://step.esa.int/auxdata/dem/SRTMGL1/ -c > {log_file}"
    print(f"Running command {cmd}")
    os.system(cmd)
    

def create_parser():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='download Digital Elevation Model using dem.py'
    )
    
    parser.add_argument('--lat-min', type=float, required=True,
                       help='minimum latitude (south boundary)')
    parser.add_argument('--lat-max', type=float, required=True,
                       help='maximum latitude (north boundary)')
    parser.add_argument('--lon-min', type=float, required=True,
                       help='minimum longitude (west boundary)')
    parser.add_argument('--lon-max', type=float, required=True,
                       help='maximum longitude (east boundary)')
    parser.add_argument('--dem-dir', type=str, required=True,
                       help='output directory for DEM files')
    parser.add_argument('--logo', action='store_true', default=False,
                        help='show the logo of IntfLab (default : False)')
    parser.add_argument('--reset', action='store_true', default=False,
                        help='whether reset the DEM directory (default : False)')
    return parser


    
if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    vld = S1ParameterValidator()
    # receive parameters 
    lat_min, lat_max = args.lat_min, args.lat_max
    lon_min, lon_max = args.lon_min, args.lon_max
    dem_dir = args.dem_dir
    logo, reset = args.logo, args.reset
    # logo
    if logo:
        show_logo()
    # validate coordinates
    if not vld.validate_coordinates(lat_min, lat_max, lon_min, lon_max):
        sys.exit(1)
    if reset:
        print(f"reset mode is :{reset}")
        reset_dem_dir(dem_dir)
        
    download_S1_SLC_dem(lat_min, lat_max, lon_min, lon_max, dem_dir)