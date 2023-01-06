import geopandas as gpd
import pandas as pd
import os
import shutil
from zipfile import ZipFile
from rasterio.plot import show
from rasterio.merge import merge
import rasterio as rio
from pathlib import Path
from glob import glob
from os.path import isfile, join, isdir
import fiona
import rasterio
import rasterio.mask

# Define Data Paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path,'inputs')
grids_path = os.path.join(inputs_path,'grids')
boundary_path = os.path.join(inputs_path,'boundary')
outputs_path = os.path.join(data_path, 'outputs')
outputs_path_ = data_path + '/' + 'outputs'
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path_)
raster_path = os.path.join(inputs_path, 'rasters')
raster_output = os.path.join(outputs_path, 'boundary.asc')
raster_output_clip = os.path.join(outputs_path,'boundary_clipped.asc')

# Identify input polygons and shapes (boundary of city, and OS grid cell references)
boundary = glob(boundary_path + "/*.*", recursive = True)
boundary = gpd.read_file(boundary[0])
grid = glob(grids_path + "/*_5km.gpkg", recursive = True)
grid = gpd.read_file(grid[0])

# Ensure all of the polygons are defined by the same crs
boundary.set_crs(epsg=27700, inplace=True)
grid.set_crs(epsg=27700, inplace=True)

# Identify which of the 5km OS grid cells fall within the chosen city boundary
cells_needed = gpd.overlay(boundary,grid, how='intersection')
list = cells_needed['tile_name']

# Identify which of the 100km OS grid cells fall within the chosen city boundary 
# This will determine which folders are needed to retrieve the DTM for the area

check=[]
check=pd.DataFrame(check)
check['cell_code']=['AAAAAA' for n in range(len(list)-1)]
a_length = len(list[2])
cell='A'

# Look at each 5km cell that falls in the area and examine the first two digits
for i in range(0,len(list)-1):
    cell=list[i]
    check.cell_code[i] = cell[a_length - 6:a_length - 4]

# Remove any duplicates, reset the index - dataframe for the 100km cells
grid_100 = check.drop_duplicates()
grid_100.reset_index(inplace=True, drop=True)

# Create a dataframe for the 5km cells
grid_5=cells_needed['tile_name']
grid_5=pd.DataFrame(grid_5)

# Establish which zip files need to be unzipped
files_to_unzip=[]
files_to_unzip=pd.DataFrame(files_to_unzip)
files_to_unzip=['XX' for n in range(len(grid_100))]
for i in range(0,len(grid_100)):
    name=grid_100.cell_code[i]
    name_path = os.path.join(raster_path, name + '.zip')
    files_to_unzip[i] = name_path

# Unzip the required files
for i in range (0,len(files_to_unzip)):
    if os.path.exists(files_to_unzip[i]) :
        with ZipFile(files_to_unzip[i],'r') as zip:
            # extract the files into the inputs directory
            zip.extractall(raster_path)

# Create a list of the file paths to each asc that falls within the shapefile
grid_5['file_name'] = grid_5['tile_name']+'.asc'
archive=[]
archive=pd.DataFrame(archive)
archive=['XX' for n in range(len(grid_5))]

for i in range(0,len(grid_5)):
    name = grid_5.file_name[i]
    path = glob(raster_path + '/**/' + name, recursive=True)
    archive[i] = path

# Merge the asc files to create one raster file for the chosen area
raster_to_mosiac = []
for p in archive:
    raster = rio.open(p[0])
    raster_to_mosiac.append(raster)

raster_to_mosiac
mosaic, output = merge(raster_to_mosiac)

output_meta = raster.meta.copy()
output_meta.update(
    {"driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": output,
        "crs": "epsg:27700"
    }
)

# Write to file
with rio.open(raster_output, 'w', **output_meta) as m:
    m.write(mosaic)

# This should then be read into the clip tool to adjust it back to the desired area
# If not this code can be used but it needs some work to sort out the edges
boundary = glob(boundary_path + "/*.*", recursive = True)

# Read Shape file
# with fiona.open(boundary[0], "r") as shapefile:
#     shapes = [feature["geometry"] for feature in shapefile]

# # read imagery file
# with rasterio.open(raster_output) as src:
#     out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
#     out_meta = src.meta

# # Save clipped imagery
# out_meta.update({"driver": "GTiff",
#                  "height": out_image.shape[1],
#                  "width": out_image.shape[2],
#                  "transform": out_transform})

# raster_output_clip = os.path.join(outputs_path,'boundary_clipped.asc')

# with rasterio.open(raster_output_clip, "w", **out_meta) as dest:
#     dest.write(out_image)