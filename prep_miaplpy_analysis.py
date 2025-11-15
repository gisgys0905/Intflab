######################################################
# ISCE+miaplpy to do Phase_linking and timeseriesAnalysis
# prep_miaplpy.py prepare directory for Miaplpy
# execute the following steps : 
# <1> mkdir Miaplpy for Miaplpy Timeseries Analysis in the PROCESS directory
# <2> Copy the baseline directory and metadata directory, geom_reference_datasets to the Miaplpy directory
# <3> Copy the correspondent datasets based on the date range
# <4> find the roi yx and save roi.txt 
# <5> write miaplpy template for miaplpy analysis.
######################################################

# Junlian test lalo 27.96, 28.06, 104.57, 104.66

from lab_utils import *
import os, sys, shutil, glob
import numpy as np 
import argparse


def copy_baselinesdataset2Miaplpy(process_dir, Miaplpy_dir):
    baselines_dir = os.path.join(process_dir, "baselines")
    dst = os.path.join(Miaplpy_dir, "baselines")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(baselines_dir, dst)


def copy_referenceMetadataset2Miaplpy(process_dir, Miaplpy_dir):
    ref_dir = os.path.join(process_dir, "reference")
    dst = os.path.join(Miaplpy_dir, "reference")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(ref_dir, dst)


def copy_geomreferencedataset2Miaplpy(process_dir, Miaplpy_dir):
    geom_reference_dir =os.path.join(process_dir, "merged", "geom_reference")
    print("geom_reference_dir is :", geom_reference_dir)
    dst = os.path.join(Miaplpy_dir, "geom_reference")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(geom_reference_dir, dst)
    
    
def get_date_range(process_dir):
    rslc_dir = os.path.join(process_dir,"merged", "SLC")
    date_list = os.listdir(rslc_dir)
    date_list = np.array(date_list, dtype = 'int')
    return date_list, np.min(date_list), np.max(date_list)
    
    
def get_Miaplpy_directory(process_dir,date1=None, date2=None,):
    date_list, start_date, end_date = get_date_range(process_dir)
    if date1 is None and date2 is None:
        Miaplpy_dir = os.path.join(process_dir, f"Miaplpy_{start_date}_{end_date}")
    elif date1 is None and date2 is not None:
        if int(date2) in date_list:
            Miaplpy_dir = os.path.join(process_dir, f"Miaplpy_{start_date}_{date2}")
        else:
            print(f"{date2} is not in date_list")
            sys.exit(1)
    elif date2 is None and date1 is not None:
        if int(date1) in date_list:
            Miaplpy_dir = os.path.join(process_dir, f"Miaplpy_{date1}_{end_date}")
        else:
            print(f"{date1} is not in date_list")
            sys.exit(1)
    elif date1 is not None and date2 is not None:
        if int(date1) in date_list and int(date2) in date_list:
            Miaplpy_dir = os.path.join(process_dir, f"Miaplpy_{date1}_{date2}")
        else:
            print("check the date1 and date2")
            sys.exit(1)

    return Miaplpy_dir    
       
        
def get_final_date12(process_dir, date1=None, date2=None):
    date_list, start_date, end_date = get_date_range(process_dir)  
    date_list = list(date_list)
    if date1 is None and date2 is None:
        date_range = date_list
    elif date1 is None and date2 is not None:
        date2 = int(date2)
        date1_index = 0
        date2_index = date_list.index(date2)
        date_range = date_list[date1_index:date2_index+1]
    elif date2 is None and date1 is not None:
        date1 = int(date1)
        date1_index = date_list.index(date1)
        date_range = date_list[date1_index:]
    else: 
        date1, date2 = int(date1), int(date2)
        date1_index = date_list.index(date1)
        date2_index = date_list.index(date2)
        date_range = date_list[date1_index:date2_index+1]
    return date_range


def copy_ifgdataset2Miaplpy(process_dir, Miaplpy_dir, date1=None, date2=None):
    rslc_dir = os.path.join(process_dir, "merged", "SLC")
    date_range = get_final_date12(process_dir, date1, date2)
    print(f"corresponding date range is {date_range[0]} to {date_range[-1]}, totally {len(date_range)} num_dates")
    Miaplpy_rslc_dir = os.path.join(Miaplpy_dir, "SLC")
    if not os.path.exists(Miaplpy_rslc_dir):os.mkdir(Miaplpy_rslc_dir)
    rslc_dst_list = [os.path.join(Miaplpy_rslc_dir, str(date)) for date in date_range]
    for num, dst in enumerate(rslc_dst_list):
        date = os.path.basename(dst)
        ref_dir = os.path.join(rslc_dir, date)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(ref_dir, dst)    
        src_str = f"${{PROJECT}}/{'/'.join(ref_dir.rstrip('/').split('/')[-3:])}"
        dst_str = f"${{PROJECT}}/{'/'.join(dst.rstrip('/').split('/')[-3:])}"
        print(f"No.{num+1} rslc: {src_str} --> {dst_str}")


def prepare_SAR_yx(Miaplpy_dir, lat_min, lat_max, lon_min, lon_max):  
    lat_full_file = os.path.join(Miaplpy_dir, "geom_reference", "lat.rdr.full")
    lon_full_file = os.path.join(Miaplpy_dir, "geom_reference", "lon.rdr.full")

    lat_data = read_isce_file(lat_full_file)
    lon_data = read_isce_file(lon_full_file)

    y0, y1, x0, x1 = bbox2SAR(lat_min, lat_max, lon_min, lon_max,lat_data, lon_data)
    y0, y1, x0, x1 = int(y0), int(y1), int(x0), int(x1)
    roi_par = os.path.join(Miaplpy_dir, "roiSAR.txt")
    print(f"save infomation of region of interesting in the file {roi_par}")
    write_roi_par(y0, y1, x0, x1, roi_par)
    
    
def prepare_RSLC_full_files(Miaplpy_dir):
    rslc_dir = os.path.join(Miaplpy_dir, "SLC")
    ## prepare rslc.full 
    print("prepare RSLC.full file")
    for date in os.listdir(rslc_dir):
        rslc_vrt = os.path.join(rslc_dir, date, f"{date}.slc.full.vrt")
        rslc_full = os.path.join(rslc_dir,date, f"{date}.slc.full")
        log = os.path.join(rslc_dir,date,f"gdal_translate_{date}.log")
        cmd = f"gdal_translate -of ENVI {rslc_vrt} {rslc_full} > {log}"
        print(cmd)
        os.system(cmd)
        
def prepare_geomref_full_files(Miaplpy_dir):   
    geomref_dir = os.path.join(Miaplpy_dir, "geom_reference")
    ## prepare lon.rdr.full. lat.rdr.full los.rdr.full incidenceAngle.rdr.full shadowMask.rdr.full
    print("prepare geom_reference files full file") 
    geo_files_pattern = os.path.join(geomref_dir,"*.rdr.full.vrt")
    geom_vrt_files =  glob.glob(geo_files_pattern)
    print(geom_vrt_files)
    for geom_vrt_file in geom_vrt_files:
        basename = os.path.basename(geom_vrt_file)
        full_ext = ".".join(basename.split(".")[:-1])
        geom_full_file = os.path.join(geomref_dir, full_ext)
        log = os.path.join(geomref_dir, f"gdal_translate_{basename.split('.')[0]}.log")
        cmd = f"gdal_translate -of ENVI {geom_vrt_file} {geom_full_file} > {log}"
        print(cmd)
        os.system(cmd)

       
       
def prepare_miaplpy_template(Miaplpy_dir):
    output_file = os.path.join(Miaplpy_dir, "miaplpy.txt")
    with open(output_file, "w") as example:
        example.write("##------------------------ miaplpyApp.cfg ------------------------##\n")
        example.write("########## 1. load data given the area of interest\n")
        example.write("miaplpy.load.processor      = isce  #[isce,snap,gamma,roipac], auto for isceTops\n")
        example.write("miaplpy.load.updateMode     = yes  #[yes / no], auto for yes, skip re-loading if HDF5 files are complete\n")
        example.write("miaplpy.load.compression    = auto  #[gzip / lzf / no], auto for no.\n")
        example.write("miaplpy.load.autoPath       = auto    # [yes, no] auto for no.\n")
        example.write("##---------Coregistered SLC images:\n")
        example.write(f"miaplpy.load.slcFile        = {os.path.join(Miaplpy_dir, 'SLC', '*', '*.slc.full')}  #[path2slc_file]\n")
        example.write("\n")
        example.write("##---------for ISCE only:\n")
        example.write(f"miaplpy.load.metaFile       = {os.path.join(Miaplpy_dir, 'reference', 'IW*.xml')}  #[path2metadata_file], i.e.: ./reference/IW1.xml, ./referenceShelve/data.dat \n")
        example.write(f"miaplpy.load.baselineDir    = {os.path.join(Miaplpy_dir, 'baselines')}  #[path2baseline_dir], i.e.: ./baselines\n")
        example.write("##---------geometry datasets:\n") 
        example.write(f"miaplpy.load.demFile        = {os.path.join(Miaplpy_dir, 'geom_reference', 'hgt.rdr.full')}\n")
        example.write(f"miaplpy.load.lookupYFile    = {os.path.join(Miaplpy_dir, 'geom_reference', 'lat.rdr.full')}\n")
        example.write(f"miaplpy.load.lookupXFile    = {os.path.join(Miaplpy_dir, 'geom_reference', 'lon.rdr.full')}\n")
        example.write(f"miaplpy.load.incAngleFile   = {os.path.join(Miaplpy_dir, 'geom_reference', 'los.rdr.full')}\n")
        example.write(f"miaplpy.load.azAngleFile    = {os.path.join(Miaplpy_dir, 'geom_reference', 'los.rdr.full')}\n")
        example.write(f"miaplpy.load.shadowMaskFile = {os.path.join(Miaplpy_dir, 'geom_reference', 'shadowMask.rdr.full')}\n")
        example.write(f"miaplpy.load.waterMaskFile  = auto  #[path2water_mask_file], optional\n")
        example.write(f"miaplpy.load.bperpFile      = auto  #[path2bperp_file], optional\n")
        example.write("##---------subset (optional):\n")
        example.write("## if both yx and lalo are specified, use lalo option unless a) no lookup file AND b) dataset is in radar coord\n")
        example.write("miaplpy.subset.yx           = [1800.0:2700.0, 4990.0:8180.0]    #[y0:y1,x0:x1 / no], auto for no\n")
        example.write("\n")

        example.write("########################## phase_linking ##########################################\n")
        example.write("miaplpy.inversion.patchSize                = auto \n")
        example.write("miaplpy.inversion.ministackSize            = auto  \n")
        example.write("miaplpy.inversion.rangeWindow              = 19   \n")
        example.write("miaplpy.inversion.azimuthWindow            = 9  \n")
        example.write("miaplpy.inversion.shpTest                  = auto \n")
        example.write("miaplpy.inversion.phaseLinkingMethod       = sequential_EMI \n")
        example.write("miaplpy.inversion.sbw_connNum              = auto  \n")
        example.write("miaplpy.inversion.PsNumShp                 = auto\n")
        example.write("miaplpy.inversion.mask                     = auto  \n")
        example.write("\n")

        example.write("########## 4. Select the network and generate interferograms\n")
        example.write("miaplpy.interferograms.networkType             = single_reference     # [mini_stacks, single_reference, sequential, delaunay] default: single_reference\n")
        example.write("miaplpy.interferograms.list                    = auto     # auto for None, list of interferograms to unwrap in a text file\n")
        example.write("miaplpy.interferograms.referenceDate           = 20250101     # auto for the middle image\n")
        example.write("miaplpy.interferograms.filterStrength          = auto     # [0-1], interferogram smoothing factor, auto for 0\n")
        example.write("miaplpy.interferograms.ministackRefMonth       = auto     # The month of the year that coherence is high to choose reference from, default: 6\n")
        example.write("miaplpy.interferograms.connNum                 = auto     # Number of connections in sequential interferograms, auto for 3\n")
        example.write("miaplpy.interferograms.delaunayBaselineRatio   = auto     # [1, 4, 9] Ratio between perpendiclar and temporal baselines, auto for 1\n")
        example.write("miaplpy.interferograms.delaunayTempThresh      = auto     # [days] temporal threshold for delaunay triangles, auto for 120\n")
        example.write("miaplpy.interferograms.delaunayPerpThresh      = auto     # [meters] Perp baseline threshold for delaunay triangles, auto for 200\n")
        example.write("miaplpy.interferograms.oneYear                 = auto     # [yes, no ] Add one year interferograms, auto for no\n")
        example.write("\n")

        example.write("#################################### phase unwrapping #########################################################\n")
        example.write("miaplpy.unwrap.two-stage                  = auto     # [yes, no], auto for yes, Do two stage unwrapping\n")
        example.write("miaplpy.unwrap.removeFilter               = auto     # [yes, no], auto for yes, remove filter after unwrap\n")
        example.write("miaplpy.unwrap.snaphu.maxDiscontinuity    = auto     # (snaphu parameter) max phase discontinuity in cycle, auto for 1.2\n")
        example.write("miaplpy.unwrap.snaphu.initMethod          = auto     # [MCF, MST] auto for MCF\n")
        example.write("miaplpy.unwrap.snaphu.tileNumPixels       = auto     # number of pixels in a tile, auto for 10000000\n")
        example.write("miaplpy.unwrap.mask                       = auto     # auto for None\n")
        example.write("\n")

        example.write("#################################### load_ifg ####################################################################\n")
        example.write(f"miaplpy.load.unwFile        = {os.path.join(Miaplpy_dir, 'miaplpy', 'inverted', 'interferograms_single_reference', '*', 'filt_*.unw')}  #[path2unw_file]\n")
        example.write(f"miaplpy.load.corFile        = {os.path.join(Miaplpy_dir, 'miaplpy', 'inverted', 'interferograms_single_reference', '*', 'filt_*.cor')}  #[path2cor_file]\n")
        example.write(f"miaplpy.load.connCompFile   = {os.path.join(Miaplpy_dir, 'miaplpy', 'inverted', 'interferograms_single_reference', '*', 'filt_*.unw.conncomp')}  #[path2conn_file], optional\n")
        example.write("miaplpy.load.intFile        = auto  #[path2int_file], optional\n")
        example.write("miaplpy.load.ionoFile       = auto  #[path2iono_file], optional\n")
        example.write("\n")

        example.write("#################################################### ifg_corrction_unwrapPhase ##################################################### \n")
        example.write("## mintpy.network.coherenceBased  = yes  #[yes / no], auto for no, exclude interferograms with coherence < minCoherence\n")
        example.write("## mintpy.network.minCoherence    = 0.35  #[0.0-1.0], auto for 0.7\n")
        example.write("\n")

        example.write("########## correct_unwrap_error (optional)\n")
        example.write("## connected components (mintpy.load.connCompFile) are required for this step.\n")
        example.write("## reference: Yunjun et al. (2019, section 3)\n")
        example.write("## supported methods:\n")
        example.write("## a. phase_closure          - suitable for highly redundant network\n")
        example.write("## b. bridging               - suitable for regions separated by narrow decorrelated features, e.g. rivers, narrow water bodies\n")
        example.write("## c. bridging+phase_closure - recommended when there is a small percentage of errors left after bridging\n")
        example.write("mintpy.unwrapError.method          = no  #[bridging / phase_closure / bridging+phase_closure / no], auto for no\n")
        example.write("mintpy.unwrapError.waterMaskFile   = auto  #[waterMask.h5 / no], auto for waterMask.h5 or no [if not found]\n")
        example.write("\n")
        example.write("## phase_closure options:\n")
        example.write("mintpy.unwrapError.numSample       = auto  #[int>1], auto for 100, number of samples to invert for common conn. comp.\n")
        example.write("\n")
        example.write("## briding options:\n")
        example.write("mintpy.unwrapError.ramp            = linear  #[linear / quadratic], auto for no; recommend linear for L-band data\n")
        example.write("mintpy.unwrapError.bridgePtsRadius = auto  #[1-inf], auto for 50, half size of the window around end points\n")
        example.write("\n")

        example.write("####################### 8. Invert network of interferograms to timeseries ####################################### \n")
        example.write("miaplpy.timeseries.tempCohType            = average     # [full, average], auto for full.\n")
        example.write("miaplpy.timeseries.minTempCoh             = 0.5     # auto for 0.5\n")
        example.write("miaplpy.timeseries.waterMask              = auto     # auto for None, path to water mask\n")
        example.write("miaplpy.timeseries.shadowMask             = auto     # [yes, no] auto for no, using shadow mask to mask final results\n")
        example.write("miaplpy.timeseries.residualNorm           = L2     # [L1, L2], auto for L2, norm minimization solution\n")
        example.write("miaplpy.timeseries.L1smoothingFactor      = auto     # [0-1] auto for 0.001\n")
        example.write("miaplpy.timeseries.L2weightFunc           = auto     # [var / fim / coh / no], auto for var\n")
        example.write("miaplpy.timeseries.minNormVelocity        = auto     # [yes / no], auto for yes, min-norm deformation velocity / phase\n")
        example.write("\n")

        example.write("########################## 9. timeseries_correction ###############################################################\n")
        example.write("mintpy.troposphericDelay.method = height_correlation  #[pyaps / height_correlation / gacos / no], auto for pyaps\n")
        example.write("\n")
        example.write("########## 9. deramp (optional)\n")
        example.write("## Estimate and remove a phase ramp for each acquisition based on the reliable pixels.\n")
        example.write("mintpy.deramp          = linear  #[no / linear / quadratic], auto for no - no ramp will be removed\n")
        example.write("mintpy.deramp.maskFile = auto  #[filename / no], auto for maskTempCoh.h5, mask file for ramp estimation\n")
        example.write("\n")
        example.write("##                     no  - use the mean   geometry [fast]\n")
        example.write("mintpy.topographicResidual                   = auto  #[yes / no], auto for yes\n")
        example.write("mintpy.topographicResidual.polyOrder         = auto  #[1-inf], auto for 2, poly order of temporal deformation model\n")
        example.write("mintpy.topographicResidual.phaseVelocity     = auto  #[yes / no], auto for no - use phase velocity for minimization\n")
        example.write("mintpy.topographicResidual.stepDate          = auto  #[20080529,20190704T1733 / no], auto for no, date of step jump\n")
        example.write("mintpy.topographicResidual.excludeDate       = auto  #[20070321 / txtFile / no], auto for exclude_date.txt\n")
        example.write("mintpy.topographicResidual.pixelwiseGeometry = auto  #[yes / no], auto for yes, use pixel-wise geometry info\n")
        example.write("\n")
        example.write("mintpy.reference.lalo     = auto\n")
        example.write("mintpy.networkInversion.minTempCoh  = 0.5 #[0.6 0.0-1.0], auto for 0.7, min temporal coherence for mask\n")
        example.write("mintpy.networkInversion.maskThreshold = 0.4 #[0-inf], auto for 0.4\n")
            
        
def prep_miaplpy(process_dir, date1 = None, date2 = None, 
                 lat_min=None, lat_max=None, lon_min=None, lon_max=None):
    if not (lat_min and lat_max and lon_min and lon_max):
        print("lat and lon infomation is necessary. please check your lat/lon")
        sys.exit(1)
    Miaplpy_dir = get_Miaplpy_directory(process_dir, date1=date1)
    Miaplpy_basename = os.path.basename(Miaplpy_dir)
    print(f"date1 = {date1}, date2 = {date2}, create Miaplpy directory named {Miaplpy_basename}")
    if not os.path.exists(Miaplpy_dir):os.mkdir(Miaplpy_dir)
    print("copy baselines directory to Miaplpy directory...")
    copy_baselinesdataset2Miaplpy(process_dir, Miaplpy_dir)
    print("copy reference directory to Miaplpy directory...")
    copy_referenceMetadataset2Miaplpy(process_dir, Miaplpy_dir)
    print("copy geom_reference directory to Miaplpy directory...")
    copy_geomreferencedataset2Miaplpy(process_dir, Miaplpy_dir)
    print("copy correspond SLC files to Miaplpy directory...")
    # copy_ifgdataset2Miaplpy(process_dir, Miaplpy_dir, date1, date2)
    print("transform RSLC vrt files to full files...")
    # prepare_RSLC_full_files(Miaplpy_dir)
    print("transform geom_reference files to full files ...")
    # prepare_geomref_full_files(Miaplpy_dir)
    print("find the SAR yx based on the lookuptable and lat lon ...")
    # prepare_SAR_yx(Miaplpy_dir, lat_min, lat_max, lon_min, lon_max)
    print("prepare miaplpy template text file...")
    # prepare_miaplpy_template(Miaplpy_dir)
    
    
def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='prepare files that miaplpy timeseriesAnalysis needed'
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
    prep_miaplpy(process_dir, date1=date1, date2=date2, 
                 lat_min=lat_min, lat_max = lat_max, lon_min=lon_min, lon_max=lon_max)
    
    