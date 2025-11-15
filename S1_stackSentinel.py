#############################
# copyRight Author : Yisen Gao (AIRCAS-RADI AISAR) 30/08/2025 to present 
# written in       : Beijing China 
# brief introduce  : make bashfile step by step
#############################

import os
import sys
import argparse
import glob
import subprocess
from cores.validation import S1ParameterValidator
from lab_utils import logo as show_logo
from reset import reset_process_dir


def stack_sentinel(lat_min, lat_max, lon_min, lon_max, 
                   dem_dir, aux_dir, slc_dir, orbits_dir,
                   nalks, nrlks, process_dir):
    # Generate runfiles using stackSentinel.py
    # <1~4> lat_min, lat_max, lon_min, lon_max (float): bounding box coordinates
    # <5>  dem_dir (str): directory containing DEM files
    # <6>  aux_dir (str): directory containing AUX files
    # <7>  slc_dir (str): directory containing Sentinel-1 SLC files
    # <8>  orbits_dir (str): directory containing orbit files
    # <9>  nalks (int): number of azimuth looks
    # <10> nrlks (int): number of range looks
    # <11> process_dir (str): directory where runfiles will be generated

    # change to process directory
    
    process_path = process_dir
    if not os.path.exists(process_path):
        os.mkdir(process_path)
    ## get the dem file path 
    dem_path = dem_dir
    if not os.path.exists(dem_path):
        raise FileNotFoundError(f"DEM directory does not exist: {dem_dir}")
    # Look for files ending with 'wgs84'
    dem_pattern = os.path.join(dem_path, '*wgs84')
    dem_files = list(glob.glob(dem_pattern))
    if not dem_files:
        raise FileNotFoundError(f"No DEM file ending with 'wgs84' found in {dem_dir}")
    if len(dem_files) > 1:
        print(f"Warning: Multiple DEM files found, using: {dem_files[0].name}")
    dem_file = str(dem_files[0])
    
    # Construct bounding box string
    bbox = f'{lat_min} {lat_max} {lon_min} {lon_max}'
    
    # Build command
    cmd = [
        'stackSentinel.py',
        '-b', bbox,
        '-d', dem_file,
        '-a', aux_dir,
        '-s', slc_dir,
        '-o', orbits_dir,
        '-z', str(nalks),
        '-r', str(nrlks),
        '-f', '0.8',
        '-c', '5'
    ]
    
    print(f"Stack Sentinel parameters:")
    print(f"  Bounding box: [{lat_min}, {lat_max}] x [{lon_min}, {lon_max}]")
    print(f"  DEM file: {dem_file}")
    print(f"  AUX directory: {aux_dir}")
    print(f"  SLC directory: {slc_dir}")
    print(f"  Orbits directory: {orbits_dir}")
    print(f"  Azimuth looks: {nalks}")
    print(f"  Range looks: {nrlks}")
    print(f"  Process directory: {process_dir}")
    print(f"Running command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=process_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        print("Stack Sentinel completed successfully!")
        if result.stdout:
            print("Output:")
            print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"ERROR: stackSentinel.py failed with return code {e.returncode}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: stackSentinel.py not found. Please ensure ISCE2 is installed and in PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}")
        sys.exit(1)


def create_parser():
    """create argument parser"""
    parser = argparse.ArgumentParser(
        description='generate ISCE2 stack processing runfiles using stackSentinel.py'
    )
    
    # coordinate arguments
    parser.add_argument('--lat-min', type=float, required=True,
                       help='minimum latitude of the study area')
    parser.add_argument('--lat-max', type=float, required=True,
                       help='maximum latitude of the study area')
    parser.add_argument('--lon-min', type=float, required=True,
                       help='minimum longitude of the study area')
    parser.add_argument('--lon-max', type=float, required=True,
                       help='maximum longitude of the study area')
    
    # directory arguments
    parser.add_argument('--dem-dir', type=str, required=True,
                       help='directory containing DEM files')
    parser.add_argument('--aux-dir', type=str, required=True,
                       help='directory containing AUX files')
    parser.add_argument('--slc-dir', type=str, required=True,
                       help='directory containing Sentinel-1 SLC files')
    parser.add_argument('--orbits-dir', type=str, required=True,
                       help='directory containing orbit files')
    
    # processing parameters
    parser.add_argument('--nalks', type=int, required=True,
                       help='number of azimuth looks')
    parser.add_argument('--nrlks', type=int, required=True,
                       help='number of range looks')
    parser.add_argument('--process-dir', type=str, required=True,
                       help='directory where runfiles will be generated')
    parser.add_argument('--logo', action='store_true', default=False,
                        help='show the logo of IntfLab (default : False)')
    parser.add_argument('--reset', action='store_true', default=False,
                        help='whether reset the process directory (default : False)')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    vad = S1ParameterValidator()
    # receive parameters 
    lat_min = args.lat_min
    lat_max = args.lat_max
    lon_min = args.lon_min
    lon_max = args.lon_max
    dem_dir = args.dem_dir
    aux_dir = args.aux_dir 
    slc_dir = args.slc_dir 
    process_dir = args.process_dir
    orbits_dir = args.orbits_dir
    nalks, nrlks = args.nalks, args.nrlks
    logo, reset = args.logo, args.reset 
    # logo
    if logo:
        show_logo()
    # reset
    if reset:
        print(f"reset mode is :{reset}")
        reset_process_dir(process_dir=process_dir)
    
    # validate inputs
    if not vad.validate_coordinates(lat_min, lat_max, lon_min, lon_max):
        sys.exit(1)
    if not vad.validate_processing_parameters(nrlks, nalks):
        sys.exit(1)
    
    stack_sentinel( 
        lat_min, lat_max, lon_min, lon_max,
        dem_dir, aux_dir, slc_dir, orbits_dir,
        nalks, nrlks, process_dir
    )