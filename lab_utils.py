#############################
# copyRight Author : Yisen Gao (AIRCAS-RADI AISAR) 30/08/2025 to present 
# time : 30/08/2025 Saturday
# brief introduce : utils of the system
#############################
    
from mintpy.utils.writefile import * 
from osgeo import gdal  
import os, sys
import numpy as np
import math
import geopandas as gpd
from shapely.geometry import Polygon

software = """
        ████─██─██─███─█──█─███─███─█───████─████─
        █──█──███───█──██─█──█──█───█───█──█─█──██
        ████───█────█──█─██──█──███─█───████─████─
        █──────█────█──█──█──█──█───█───█──█─█──██
        █──────█───███─█──█──█──█───███─█──█─████─
        
        version   : 2025-10-01 PyIntfLAB
        copyRight : Yisen Gao (UCAS) 30/08/2025 to present 
        An InSAR processing system based ISCE2 and etl
"""


# configDict for some satellite, only support sentinel1 now
S1_config = {
    "ORBIT_URL"  : "https://s1qc.asf.alaska.edu/aux_poeorb/",
    "wavelength" : 0.05546576, 
    "S1stackApp" : """
    Examples:
    # Run all steps
    python S1stackApp.py --data-dir /path/to/data --work-dir /path/to/work \\
                        --project myproject --lat-min 30.0 --lat-max 31.0 \\
                        --lon-min 120.0 --lon-max 121.0 --nalks 4 --nrlks 16 --step -
    
    # Run only step 1 (unzip)
    python S1stackApp.py --data-dir /path/to/data --work-dir /path/to/work \\
                        --project myproject --lat-min 30.0 --lat-max 31.0 \\
                        --lon-min 120.0 --lon-max 121.0 --nalks 4 --nrlks 16 --step 1
    """
}

def logo():
    print(software)
    
## transform the geobbox to SAR row/col numbers     
def generate_shp(lat_min, lat_max, lon_min, lon_max, output_path="roi.shp"): 
    # generate a shapefile for a bounding box.
    # <1> lat_min (float)   : minimum latitude
    # <2> lat_max (float)   : maximum latitude
    # <3> lon_min (float)   : minimum longitude
    # <4> lon_max (float)   : maximum longitude
    # <5> output_path (str) : output shapefile path, default 'roi.shp'
    # create geopandas polygon
    polygon = Polygon([
        (lon_min, lat_min),
        (lon_min, lat_max),
        (lon_max, lat_max),
        (lon_max, lat_min),
        (lon_min, lat_min)  
    ])
    # create geoDataFrame
    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[polygon], crs="EPSG:4326")
    # save as shapefile
    gdf.to_file(output_path, driver="ESRI Shapefile")
    # generate log_file 
    print(f"shapefile generated at: {output_path}")



## geobbox to SAR row/col in the azimuth&range direction 
def bbox2SAR(lat_min, lat_max, lon_min, lon_max, lat_data, lon_data):
    #  convert geographic bounding box to SAR ROI indicies. (azimuth and range)
    # <1> lat_min (float)     : minimum latitude
    # <2> lat_max (float)     : maximum latitude
    # <3> lon_min (float)     : minimum longitude
    # <4> lon_max (float)     : maximum longitude
    # <5> lat_data (np.array) : the latitude lookuptable lat.rdr  
    # <6> lon_data (np.array) : the lontitude lookuptable lon.rdr
    # <return> region_rec: return the SAR row col list 
    S, N, W, E = lat_min, lat_max, lon_min, lon_max
    geo_coord = [W, N, E, S]
    data_map =  (lon_data >= geo_coord[0])*(lon_data <= geo_coord[2])*(lat_data>=geo_coord[3])*(lat_data<=geo_coord[1])
    region_list = np.argwhere(data_map==1)
    region_rec = [10*math.floor(region_list[:,0].min()/10),10*math.ceil(region_list[:,0].max()/10),\
              10*math.floor(region_list[:,1].min()/10),10*math.ceil(region_list[:,1].max()/10)]
    return region_rec
    
## convert ISCE2 formatted file to npArray
def read_isce_file(file):
    # convert a GDAL_realiable file (usually ISCE2 file) to a numpy array 
    # <1> file(str): a string-path of input file 
    _, ext = os.path.splitext(file)
    ds = gdal.Open(file,gdal.GA_ReadOnly)
    print("input dataset BandsCount : ", ds.RasterCount)
    ## get the phase band for the unw data
    if ext != ".unw":band = ds.GetRasterBand(1)
    else:band = band = ds.GetRasterBand(2)
    data = np.expand_dims(band.ReadAsArray(), 2)
    W, L, N = data.shape
    loader = np.zeros([W, L, N], dtype=np.float32)
    loader[:,:,0] = data[:,:,0]
    return loader

## read roi.par file to the Python dictionary
def read_roi_par(file):
    roi_dict = {}
    with open(file, "r") as par:
        content = par.read().strip()
        import re
        pattern = r'(lat_min|lat_max|lon_min|lon_max)\s*:\s*([0-9.-]+)'
        matches = re.findall(pattern, content)
        for key, value in matches:
            roi_dict[key] = float(value)
    return roi_dict
        
## write roi.par file to the path
def write_roi_par(lat_min, lat_max, lon_min, lon_max, roipar):
    with open(roipar, "w") as par:
        par.write(f"lat_min : {lat_min}\n")
        par.write(f"lat_max : {lat_max}\n")
        par.write(f"lon_min : {lon_min}\n")
        par.write(f"lon_max : {lon_max}\n")
    print(f"roi.par saved in {roipar}")

## there may be some problems in the funtion @
## don`t use it 
def write_gdal_file(arr, output_filepath, data_type=gdal.GDT_Float32):
    if len(arr.shape) == 2:
        rows, cols = arr.shape
        bands = 1
        data_to_write = arr
    elif len(arr.shape) == 3:
        rows, cols, bands = arr.shape
        data_to_write = arr[:, :, 0] if bands == 1 else arr
    else:
        raise ValueError("Array must be 2D or 3D")
    driver = gdal.GetDriverByName('ENVI')    
    dataset = driver.Create(output_filepath, cols, rows, 1, data_type)
    if dataset is None:
        raise RuntimeError(f"Could not create file: {output_filepath}")
    if len(arr.shape) == 2:
        dataset.GetRasterBand(1).WriteArray(data_to_write)
    else:
        dataset.GetRasterBand(1).WriteArray(data_to_write[:, :])
    dataset.FlushCache()
    dataset = None
    print(f"GDAL write {output_filepath} finished")


## write np.array to the ISCE2 file according to the input array
def write_arr2file(arr, output_filepath):
    ## write np.array to the ISCE2 file according to the input array
    ## <1> arr(numpy.array) : the numpy array to convert
    ## <2> out_path (str)   : the output path of the arr2ISCEfile
    mirror_dic = {
        ".unw": "MOD_isce_unw", 
        ".cor": "isce_cor", 
        ".rdr": "isce_cor", 
        ".int": "isce_int",
        ".full": "envi"
    }
    _, ext = os.path.splitext(output_filepath)
    if ext == ".full":
        write_gdal_file(arr, output_filepath)
        return
    if ext not in mirror_dic:
        raise ValueError(f"Unsupported file extension: {ext}")
    file_type = mirror_dic[ext]
    write_isce_file(
        data = arr[:,:,0],
        out_file = output_filepath ,
        file_type = file_type
    )
    print(f"write {output_filepath} finished ")