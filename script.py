import geopandas as gpd
import pandas as pd
import numpy as np
import os
import shutil
from zipfile import ZipFile
from glob import glob
import subprocess
import csv

# Define Data Paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path,'inputs')


# Define Input Paths
boundary_path = os.path.join(inputs_path,'boundary')
vector_path = os.path.join(inputs_path, 'rainfall_polygons')
parameters_path = os.path.join(inputs_path, 'parameters')

# Define and Create Output Paths
outputs_path = os.path.join(data_path, 'outputs')
outputs_path_ = data_path + '/' + 'outputs'
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path_)
rainfallpolygons_path = os.path.join(outputs_path, 'rainfall_polygons')
rainfallpolygons_path_ = outputs_path + '/' + 'rainfall_polygons'
if not os.path.exists(rainfallpolygons_path):
    os.mkdir(rainfallpolygons_path_)
# parameter_outputs_path = os.path.join(outputs_path, 'parameters')
# parameter_outputs_path_ = outputs_path + '/' + 'parameters'
# if not os.path.exists(parameter_outputs_path):
#     os.mkdir(parameter_outputs_path_)

# Look to see if a parameter file has been added
parameter_file = glob(parameters_path + "/*.csv", recursive = True)
print('parameter_file:', parameter_file)

# Identify the EPSG projection code
if len(parameter_file) == 1 :
    parameters = pd.read_csv(parameter_file[0])
    with open(parameter_file[0]) as file_obj:
        reader_obj = csv.reader(file_obj)
        for row in reader_obj:
            try:
                if row[0] == 'PROJECTION':
                    projection = row[1]
            except:
                continue
else:
    projection = os.getenv('PROJECTION')

print('projection:',projection)

# Identify input polygons and shapes (boundary of city, and OS grid cell references)
boundary_1 = glob(boundary_path + "/*.*", recursive = True)
print('Boundary File:',boundary_1)

# Read in the boundary
boundary = gpd.read_file(boundary_1[0])

# Check boundary crs matches the projection
if boundary.crs != projection:
    boundary.to_crs(epsg=projection, inplace=True)

print('boundary_crs:', boundary.crs)

# Identify the name of the boundary file for the city name
file_path = os.path.splitext(boundary_1[0])
print('File_path:',file_path)
print(os.name)
#code for file names is messy and needs to be done better
if os.name=='nt':
    filename=file_path[0].split("\\")
else:
    filename=file_path[0].split("/")
print('filename:',filename)
location = filename[-1]
print('Location:',location)

# Identify if the green-areas are saved in a zip file
rainfall_polygons_zip = glob(vector_path + "/*.zip", recursive = True)
print(rainfall_polygons_zip)

# If yes, unzip the file (if the user has formatted the data correctly, this should reveal a .gpkg)
if len(rainfall_polygons_zip) != 0:
    for i in range (0,len(rainfall_polygons_zip)):
        print('zip file found')
        with ZipFile(rainfall_polygons_zip[i],'r') as zip:
            zip.extractall(vector_path)

# Identify geopackages containing the polygons of the green-areas
rainfall_polygons = glob(vector_path + "/*.gpkg", recursive = True)

if len(rainfall_polygons) != 0:
    # Create a list of all of the gpkgs to be merged
    to_merge=[]
    to_merge=['XX' for n in range(len(rainfall_polygons))]
    for i in range (0,len(rainfall_polygons)):
        file_path = os.path.splitext(rainfall_polygons[i])
        if os.name=='nt':
            filename=file_path[0].split("\\")
        else:
            filename=file_path[0].split("/")
        #to_merge[i]=filename[4]+'.gpkg'
        to_merge[i]=filename[-1]+'.gpkg'

    print('to_merge:',to_merge)

    # Create a geodatabase and merge the data from each gpkg together
    all_rainfall_polygons = []
    all_rainfall_polygons=gpd.GeoDataFrame(all_rainfall_polygons)
    for cell in to_merge:
        #gdf = gpd.read_file('/data/inputs/vectors/%s' %cell)
        gdf = gpd.read_file(vector_path +'/' + cell)
        all_rainfall_polygons = pd.concat([gdf, all_rainfall_polygons],ignore_index=True)

    all_rainfall_polygons.to_crs(epsg=projection, inplace=True)

    clipped = gpd.clip(all_rainfall_polygons,boundary)

    permeable_areas = 'polygons'

    all_rainfall_polygons = clipped.to_file(os.path.join(outputs_path,'all_rainfall_polygons.shp'))
    all_rainfall_polygons = gpd.read_file(os.path.join(outputs_path,'all_rainfall_polygons.shp'))
    all_rainfall_polygons = all_rainfall_polygons.explode()
    all_rainfall_polygons.reset_index(inplace=True, drop=True)
    all_rainfall_polygons1 = all_rainfall_polygons.to_file(os.path.join(rainfallpolygons_path, location + '.gpkg'),driver='GPKG',index=False)
    
    os.remove(os.path.join(outputs_path,'all_rainfall_polygons.shp'))
    os.remove(os.path.join(outputs_path,'all_rainfall_polygons.cpg'))
    os.remove(os.path.join(outputs_path,'all_rainfall_polygons.dbf'))
    os.remove(os.path.join(outputs_path,'all_rainfall_polygons.prj'))
    os.remove(os.path.join(outputs_path,'all_rainfall_polygons.shx'))
    

# Identify CSV files containing the rainfall depth for rainfall polygons
rainfallpolygons_depth = glob(vector_path + "/*.csv") + glob(vector_path + "/*.txt")
if not rainfallpolygons_depth:
    print("rainfall depths associated with rainfall polygons do not exist")
else:
    file_path = os.path.splitext(rainfallpolygons_depth[0])
    if os.name=='nt':
        filename=file_path[0].split("\\")
    else:
        filename=file_path[0].split("/")
    rainfallpolygons_depth1 = os.path.join(rainfallpolygons_path, filename[-1] + '.csv')
    shutil.copy(rainfallpolygons_depth[0], rainfallpolygons_depth1)    


# Print all of the input parameters to an excel sheet to be read in later
# with open(os.path.join(parameter_outputs_path,'greenareas-parameters.csv'), 'w') as f:
#     f.write('PARAMETER,VALUE\n')
#     f.write('PERMEABLE_AREAS,%s\n' %permeable_areas)

# # Move the amended parameter file to the outputs folder
# if len(parameter_file) == 1 :
    
#     file_path = os.path.splitext(parameter_file[0])
#     print('Filepath:',file_path)
#     filename=file_path[0].split("/")
#     print('Filename:',filename[-1])

#     src = parameter_file[0]
#     print('src:',src)
#     dst = os.path.join(parameter_outputs_path,filename[-1] + '.csv')
#     print('dst,dst')
#     shutil.copy(src,dst)

#     # Print all of the input parameters to an excel sheet to be read in later
#     with open(os.path.join(dst), 'a') as f:
#         f.write('PERMEABLE_AREAS,%s\n' %permeable_areas)
