# Spatial Rainfall
This model takes spatial rainfall polygons supplied by the user, clips the data to the domain and ensures the data is in the correct projection.
The polygon must have a "Value" parameter with the parameters associated with this value given in Rainfall_polygons.txt

## Description
The CityCAT model can use rainfall polygons to have different rainfall in different parts of the domain (the default is to have the same rainfall data throughout the domain). This model accepts spatial rainfall data in .gpkg format, clips the data to the selected area, and ensures all data is in the same projection. If the file sizes are too large, multiple .gpkgs can be added directly, or zipped. The total rainfall in each part of the domain is specfied in Rainfall_polygons.txt and within CityCAT this is distributed depending on the unit profile of a storm event and its duration (see storm-event-curve)

## Input Parameters

## Input Files (data slots)
* rainfall_polygons
  * Description: A .gpkg file of the spatial rainfall polygons. The polygon must have a "Value" parameter with the parameters associated with this value given in Rainfall_depth.txt
  * Location: /data/inputs/rainfall_polygons
* Boundary
  * Description: A .gpkg of the geographical area of interest. 
  * Location: /data/inputs/boundary
* Parameters
  * Description: location and projection
  * Location: /data/inputs/parameters

## Outputs
* The model should output should have a single .gpkg file of the chosen area containing the rainfall polygon of interest with a rainfall_depth.txt is coped from the input data
  * Location: /data/outputs/rainfall_polygon
