######################################################
# ISCE+mintpy to do Phase_linking and timeseriesAnalysis
# prep_mintpy_analysis.py prepare directory for Mintpy
# execute the following steps : 
# <1> mkdir Mintpy_startDate_endDate for Mintpy Timeseries Analysis in the PROCESS directory
# <2> Copy the baseline directory and metadata directory, geom_reference_datasets to the Mintpy directory
# <3> Copy the correspondent datasets based on the date range
# <4> find the roi yx and save roi.txt 
# <5> write Mintpy template for Mintpy analysis.
######################################################

from lab_utils import *
import os, sys, shutil, glob
import numpy as np 
import argparse


def copy_baselinesdataset2Mintpy(process_dir, Mintpy_dir):
    baselines_dir = os.path.join(process_dir, "baselines")
    dst = os.path.join(Mintpy_dir, "baselines")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(baselines_dir, dst)
    
    
def copy_referenceMetadataset2Mintpy(process_dir, Mintpy_dir):
    ref_dir = os.path.join(process_dir, "reference")
    dst = os.path.join(Mintpy_dir, "reference")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(ref_dir, dst)

def copy_geomreferencedataset2Mintpy(process_dir, Mintpy_dir):
    ref_dir = os.path.join(process_dir, "merged", "geom_reference")
    dst = os.path.join(Mintpy_dir, "geom_reference")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(ref_dir, dst)
    
def copy_ifgramStackdatasets2Mintpy(process_dir, Mintpy_dir, date1, date2):
    intf_dir = os.path.join(process_dir, "merged", "interferograms")
    date_list, start_date, end_date = get_date_range(process_dir)
    inf_date12_list = os.listdir(intf_dir)
    selected_path_list = list()
    if date1 is None and date2 is None:
        date1, date2 = start_date, end_date
    elif date1 is None and date2 is not None:
        date1 = start_date
    elif date1 is not None and date2 is None:
        date2 = end_date
    elif date1 is not None and date2 is not None :
        pass
    
    selected_date_pair = choose_correspond_date12_list(process_dir, date_list, inf_date12_list, date1, date2)    
    print(selected_date_pair)
    for path in selected_date_pair:
        base_name = os.path.basename(path)
        intf_path = os.path.join(Mintpy_dir, "interferograms")
        if not os.path.exists(intf_path):os.mkdir(intf_path)
        date_pair_path = os.path.join(intf_path, base_name)
        if not os.path.exists(date_pair_path):os.mkdir(date_pair_path)
        ref, dst = path, date_pair_path
        if os.path.exists(dst):
            shutil.rmtree(dst)
        print(f"copy ifgram datesets : {base_name}")
        shutil.copytree(ref, dst)
        
def choose_correspond_date12_list(process_dir, date_list, date12_list, date1, date2):
    """
    Args:
        date_list (list/np.array): [date1, date2 ... , date M] 
        date12_list (list/np.array): [date1_date2, date1_date3 ... dateK_dateM]
        date1 (str/int): the date wanna to start from
        date2 (str/int): the date wanna to end with
    """
    selected_date_pair = list()
    for date12 in date12_list:
        intf_date1, intf_date2 = int(date12.split("_")[0]), int(date12.split("_")[1])
        if intf_date1 >= date1 and intf_date2 <= date2:
            selected_path = os.path.join(process_dir, 'merged', "interferograms", f"{intf_date1}_{intf_date2}")
            selected_date_pair.append(selected_path)
    return selected_date_pair

def get_date_range(process_dir):
    rslc_dir = os.path.join(process_dir,"merged", "SLC")
    date_list = os.listdir(rslc_dir)
    date_list = np.array(date_list, dtype = 'int')
    return date_list, np.min(date_list), np.max(date_list)


def get_Mintpy_directory(process_dir,date1=None, date2=None):
    date_list, start_date, end_date = get_date_range(process_dir)
    if date1 is None and date2 is None:
        Mintpy_dir = os.path.join(process_dir, f"Mintpy_{start_date}_{end_date}")
    elif date1 is None and date2 is not None:
        if int(date2) in date_list:
            Mintpy_dir = os.path.join(process_dir, f"Mintpy_{start_date}_{date2}")
        else:
            print(f"{date2} is not in date_list")
            sys.exit(1)
    elif date2 is None and date1 is not None:
        if int(date1) in date_list:
            Mintpy_dir = os.path.join(process_dir, f"Mintpy_{date1}_{end_date}")
        else:
            print(f"{date1} is not in date_list")
            sys.exit(1)
    elif date1 is not None and date2 is not None:
        if int(date1) in date_list and int(date2) in date_list:
            Mintpy_dir = os.path.join(process_dir, f"Mintpy_{date1}_{date2}")
        else:
            print("check the date1 and date2 in the date range")
            sys.exit(1)
    return Mintpy_dir

def prepare_SAR_yx(Mintpy_dir, lat_min, lat_max, lon_min, lon_max):  
    lat_file = os.path.join(Miaplpy_dir, "geom_reference", "lat.rdr")
    lon_file = os.path.join(Miaplpy_dir, "geom_reference", "lon.rdr")

    lat_data = read_isce_file(lat_file)
    lon_data = read_isce_file(lon_file)

    y0, y1, x0, x1 = bbox2SAR(lat_min, lat_max, lon_min, lon_max,lat_data, lon_data)
    y0, y1, x0, x1 = int(y0), int(y1), int(x0), int(x1)
    roi_par = os.path.join(Mi, "roi.txt")
    print(f"save infomation of region of interesting in the file {roi_par}")
    write_roi_par(y0, y1, x0, x1, roi_par)
    

def write_mintpy_config(process_dir, Mintpy_dir):
    project_name = os.path.basename(process_dir.rstrip('/'))
    mintpy_config = os.path.join(Mintpy_dir, f"{project_name}.txt")
    
    print(f"Writing Mintpy config to {mintpy_config}")
    
    with open(mintpy_config, "w") as example:
        example.write("mintpy.load.processor        = isce \n")
        example.write("mintpy.load.updateMode       = yes \n")
        example.write("##---------for ISCE only: \n")
        example.write(f"mintpy.load.metaFile        = {os.path.join(Mintpy_dir, 'reference')}  #[path of common metadata file for the stack]\n")
        example.write(f"mintpy.load.baselineDir     = {os.path.join(Mintpy_dir, 'baselines', 'IW*.xml')}\n")
        example.write("##---------interferogram stack: \n")
        example.write(f"mintpy.load.unwFile         = {os.path.join(Mintpy_dir, 'interferograms', '*', 'filt_fine.unw')}\n")
        example.write(f"mintpy.load.corFile         = {os.path.join(Mintpy_dir, 'interferograms', '*', 'filt_fine.cor')}\n")
        example.write(f"mintpy.load.connCompFile    = {os.path.join(Mintpy_dir, 'interferograms', '*', 'filt_fine.unw.conncomp')}\n")
        example.write("##---------geometry:\n")
        example.write(f"mintpy.load.demFile         = {os.path.join(Mintpy_dir, 'geom_reference', 'hgt.rdr')}\n")
        example.write(f"mintpy.load.lookupYFile     = {os.path.join(Mintpy_dir, 'geom_reference', 'lon.rdr')}\n")
        example.write(f"mintpy.load.lookupXFile     = {os.path.join(Mintpy_dir, 'geom_reference', 'lat.rdr')}\n")
        example.write(f"mintpy.load.incAngleFile    = {os.path.join(Mintpy_dir, 'geom_reference', 'los.rdr')}\n")
        example.write(f"mintpy.load.azAngleFile     = {os.path.join(Mintpy_dir, 'geom_reference', 'los.rdr')}\n")
        example.write(f"mintpy.load.shadowMaskFile  = {os.path.join(Mintpy_dir, 'geom_reference', 'shadowMask.rdr')}\n")
        example.write("##---------subset (optional): \n")
        example.write("mintpy.subset.yx            = auto\n")
        example.write("mintpy.subset.lalo          = auto\n")
        example.write("mintpy.network.coherenceBased = yes\n")
        example.write("mintpy.network.minCoherence = 0.4\n")
        example.write("mintpy.networkInversion.minTempCoh = 0.5\n")
        example.write("mintpy.troposphericDelay.method = pyaps\n")
        example.write("mintpy.deramp = linear\n")

    print(f" Mintpy config file created at: {mintpy_config}")





def prep_mintpy(process_dir, date1, date2, lat_min, lat_max, lon_min, lon_max):
    print("prepare mintpy datasets beginning...")
    ## step1 : make Mintpy Analysis directory based on the date1/date2
    Mintpy_dir = get_Mintpy_directory(process_dir, date1, date2)
    print(f"create the mintpy directory named {os.path.basename(Mintpy_dir)}")
    if not os.path.exists(Mintpy_dir):os.mkdir(Mintpy_dir)
    ## step2 : copy some relevant datasets like baselines and Metadata to Mintpy directory
    print("copy baselines directory to Mintpy directory...")
    copy_baselinesdataset2Mintpy(process_dir, Mintpy_dir)
    print("copy reference directory to Mintpy directory...")
    copy_referenceMetadataset2Mintpy(process_dir, Mintpy_dir)
    print("copy geomReference directory to Mintpy directory...")
    copy_geomreferencedataset2Mintpy(process_dir, Mintpy_dir)
    ## step3 : copy ifgrams according to the given date1 and date2. 
    print("copy relevant ifgrams according to the given date1 and date2")
    copy_ifgramStackdatasets2Mintpy(process_dir, Mintpy_dir, date1=date1, date2=date2)
    ## step4 : write mintpy config 
    print("write mintpy config ... ")
    write_mintpy_config(process_dir, Mintpy_dir)
    print("normal processing of prep_mintpy_analysis.py finish !")

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='prepare files that Mintpy timeseriesAnalysis needed'
    )
    
    # process directory parameters
    parser.add_argument('--process-dir', type=str, required=True, 
                       help='process directory in ISCE2 analysis in the PyIntfLab software')
    
    # date range parameters 
    parser.add_argument('--date1', type=str, default=None, 
                       help='datasets from a start date YYmmdd')
    parser.add_argument('--date2', type=str, default=None, 
                       help='datasets ended with a stop date YYmmdd')
    
    # region of Interesting parameters
    parser.add_argument('--lat-min', type = float, required=True,
                        help='minimize latitude of the region of interest')
    
    parser.add_argument('--lat-max', type = float, required=True,
                        help='maxmium latitude of the region of interest')
    
    parser.add_argument('--lon-min', type = float, required=True,
                        help='minimize longitude of the region of interest')
    
    parser.add_argument('--lon-max', type = float, required=True,
                        help='maxmium longitude of the region of interest')
    return parser

    
if __name__ == '__main__':
    logo()
    parser = create_parser()
    args = parser.parse_args()
    
    # process directory
    process_dir = args.process_dir 
    
    # date12 arguments
    date1, date2 = args.date1, args.date2 
    
    lat_min, lat_max, lon_min, lon_max = args.lat_min, args.lat_max, args.lon_min, args.lon_max
    
    # run prep_miaplpy
    prep_mintpy(process_dir, date1=date1, date2=date2, 
                 lat_min=lat_min, lat_max = lat_max, lon_min=lon_min, lon_max=lon_max)
    