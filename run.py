import geopandas as gpd
import pandas as pd
import os
import subprocess
from zipfile import ZipFile
from rasterio.merge import merge
import rasterio as rio
from glob import glob
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
dem_path = os.path.join(outputs_path, 'dem')
dem_path_ = outputs_path + '/' + 'dem'
if not os.path.exists(dem_path):
    os.mkdir(dem_path_)
raster_path = os.path.join(inputs_path, 'rasters')

# Identify input polygons and shapes (boundary of city, and OS grid cell references)
boundary_1 = glob(boundary_path + "/*.*", recursive = True)
print('boundary_1:',boundary_1)
boundary = gpd.read_file(boundary_1[0])

# Identify the name of the boundary file for the city name
file_path = os.path.splitext(boundary_1[0])
print('file_path:',file_path)
filename=file_path[0].split("/")
print('filename:',filename)
location = filename[-1]
print('Location:',location)

raster_output = os.path.join(dem_path, location +'.asc')
print('raster_output:',raster_output)
raster_output_clip = os.path.join(dem_path,location +'.tif')
print('raster_output_clip:',raster_output_clip)
raster_output_image = os.path.join(dem_path,location +'.asc')
print('raster_output_image:',raster_output_image)

grid = glob(grids_path + "/*_5km.gpkg", recursive = True)
print('grid:', grid)
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
    print('Raster created')

# Make a note of the directories
print('Clip_file:',boundary_1[0])
print('Input_file:',raster_output)
print('Output_file:', raster_output_clip)

# Crop the raster to the polygon shapefile
command_output = subprocess.run(["gdalwarp", "-cutline", boundary_1[0], "-crop_to_cutline", raster_output,
                     raster_output_clip, '-dstnodata', '-9999'])

# Convert tif to an asc (for CityCat input)
subprocess.run(['gdal_translate', '-of', 'GTiff', raster_output_clip, raster_output_image])

# Remove unclipped file
# os.remove(raster_output)
os.remove(raster_output_clip)
print('Pre-clipped file removed')
