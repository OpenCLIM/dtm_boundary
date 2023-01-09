# dtm_boundary
Creates a DTM of the chosen area of interest based on bounday input.

## Description
This model takes the boundary of a city/ area of interest, ascertains which of the OS British National Grid cells lie within the specified bounday, and performs a merge of all DTM data that falls within the boundary. 5m DTM data for the UK is available at the 5km cell level and so the code is based on this data. Should the 2m DTM data become available with a greater geographical coverage, the user can chose

## Input Files (data slots)
* Rasters
  * Description: Currently the best dataset available with greatest coverage within the UK is the 5m DTM. Should a higher resolution, comprehensive dataset become available, this can be used provided the name of the zip file containing all 5km DTMs within each 100km grid cell is names accordingly.
  * Location: /data/rasters
* Boundary
  * Description: A .gpkg of the geographical area of interest. 
  * Location: /data/boundary
* Grids
  * Description: A .gpkg of the OS British National Grid cells.
  * Location: /data/grids

## Outputs
The model should output only one file - a .asc file of the chosen area containing the 5m DTM.
