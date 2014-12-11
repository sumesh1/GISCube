import os, shutil
import numpy as np
import json
from netCDF4 import Dataset
from dajaxice.decorators import dajaxice_register
from giscube.config import MEDIA_ROOT, MEDIA_URL

from scripts.extract_shp_table import extract_shp_table
from scripts.metadata import get_nc_data
from scripts.conversion import nc_to_gtif, nc_to_geojson, shp_to_kml, convert_geotiff_to_kml
from scripts.clip_geotiff_by_shp import clip_geotiff_by_shp
from scripts.data_management import change_geotiff_resolution


@dajaxice_register(method='GET')
def remove_loaded_file(request, param):
    Uploaded_file = MEDIA_ROOT + MEDIA_URL + param
    os.remove(Uploaded_file)
    #and remove the associated folder for a file is exists
    try:
        shutil.rmtree('{0}'.format(Uploaded_file[:-4]))
    except:
        pass
    
    
@dajaxice_register(method='GET')
def reproject_shapefile(request, selected_shapefile, shapefile_re_project_epsg, projected_shapefile_name):
    if projected_shapefile_name.split(".")[-1] != "shp":
        projected_shapefile_name = "{0}.shp".format(projected_shapefile_name)
    s = 'ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:{2} {0} {1}'.format(MEDIA_ROOT+MEDIA_URL+projected_shapefile_name, MEDIA_ROOT+MEDIA_URL+selected_shapefile+'.shp', shapefile_re_project_epsg)
    os.system(s)


@dajaxice_register(method='GET')
def reproject_geotiff(request, selected_geotiff, geotif_re_project_epsg, projected_geotiff_name):
    if projected_geotiff_name.split(".")[-1] != "tif" or projected_geotiff_name.split(".")[-1] != "tiff":
        projected_geotiff_name = "{0}.tif".format(projected_geotiff_name)
    s = "gdalwarp -t_srs 'epsg:{2}' {0} {1}".format(MEDIA_ROOT+MEDIA_URL+selected_geotiff, MEDIA_ROOT+MEDIA_URL+projected_geotiff_name, geotif_re_project_epsg)
    os.system(s)


@dajaxice_register(method='GET')
def extract_shp_table_text(request, selected_vector, text_name):
    if text_name.split(".")[-1] != "txt":
        text_name = "{0}.txt".format(text_name)
    extract_shp_table(MEDIA_ROOT+MEDIA_URL+selected_vector+'.shp', MEDIA_ROOT+MEDIA_URL+text_name)


@dajaxice_register(method='GET')
def extract_netcdf_header(request, selected_netcdf, text_name):
    if text_name.split(".")[-1] != "txt":
        text_name = "{0}.txt".format(text_name)
    s = "ncdump -h {0} > {1}".format(MEDIA_ROOT+MEDIA_URL+selected_netcdf, MEDIA_ROOT+MEDIA_URL+text_name)
    os.system(s)


@dajaxice_register(method='GET')
def dump_netcdf_to_text(request, selected_netcdf, text_name):
    if text_name.split(".")[-1] != "txt":
        text_name = "{0}.txt".format(text_name)
    s = "ncdump {0} > {1}".format(MEDIA_ROOT+MEDIA_URL+selected_netcdf, MEDIA_ROOT+MEDIA_URL+text_name)
    os.system(s)


@dajaxice_register(method='GET')
def get_netcdf_times(request, nc_file, time_var):
    nc_dataset = Dataset(MEDIA_ROOT+MEDIA_URL+nc_file, mode='r')
    time_data = nc_dataset.variables[time_var][:]
    times = [float(t) for t in time_data]
    return json.dumps({'time_data': times})


@dajaxice_register(method='GET')
def netcdf_to_geotiff(request, nc_file, latitude_var, longitude_var, time_var, value_var, selected_time, geotiff_name):
    nc_dataset = Dataset(MEDIA_ROOT+MEDIA_URL+nc_file, mode='r')
    latitude_data = nc_dataset.variables[latitude_var][:]
    longitude_data = nc_dataset.variables[longitude_var][:]
    time_data = nc_dataset.variables[time_var][:]
    selected_time_index = np.where(time_data==float(selected_time))[0][0]
    value_data = get_nc_data(nc_file, latitude_var, longitude_var, time_var, value_var, selected_time_index)
    nc_to_gtif(latitude_data, longitude_data, value_data, geotiff_name)


@dajaxice_register(method='GET')
def netcdf_to_geojson(request, nc_file_nc_to_json, latitude_var_nc_to_json, longitude_var_nc_to_json, time_var_nc_to_json, value_var_nc_to_json, selected_time_nc_to_json, geojson_name):
    nc_dataset = Dataset(MEDIA_ROOT+MEDIA_URL+nc_file_nc_to_json, mode='r')
    latitude_data = nc_dataset.variables[latitude_var_nc_to_json][:]
    longitude_data = nc_dataset.variables[longitude_var_nc_to_json][:]
    time_data = nc_dataset.variables[time_var_nc_to_json][:]
    selected_time_index = np.where(time_data==float(selected_time_nc_to_json))[0][0]
    value_data = get_nc_data(nc_file_nc_to_json, latitude_var_nc_to_json, longitude_var_nc_to_json, time_var_nc_to_json, value_var_nc_to_json, selected_time_index)
    nc_to_geojson(latitude_data, longitude_data, value_data, geojson_name)


@dajaxice_register(method='GET')
def shapefile_to_kml(request, selected_shp, kml_name):
    if kml_name.split(".")[-1] != "kml":
        kml_name = "{0}.kml".format(kml_name)
    shp_to_kml(MEDIA_ROOT + MEDIA_URL + selected_shp + '.shp', MEDIA_ROOT + MEDIA_URL + kml_name)


@dajaxice_register(method='GET')
def clip_geotiff_by_shapefile(request, selected_geotiff, selected_shapefile, clipped_geotiff_name):
    if clipped_geotiff_name.split(".")[-1] != "tif" or clipped_geotiff_name.split(".")[-1] != "tiff":
        clipped_geotiff_name = "{0}.tif".format(clipped_geotiff_name)
    clip_geotiff_by_shp(MEDIA_ROOT + MEDIA_URL + selected_geotiff , MEDIA_ROOT + MEDIA_URL + selected_shapefile + '.shp', MEDIA_ROOT + MEDIA_URL + clipped_geotiff_name)


@dajaxice_register(method='GET')
def geotiff_to_kml(request, selected_geotiff, geotiff_to_kml_name):
    if geotiff_to_kml_name.split(".")[-1] != "kml":
        geotiff_to_kml_name = "{0}.kml".format(geotiff_to_kml_name)
    convert_geotiff_to_kml(selected_geotiff, geotiff_to_kml_name)
    return json.dumps({'status': 'Done'})


@dajaxice_register(method='GET')
def geotiff_resolution(request, selected_geotiff, geotiff_new_x_res, geotiff_new_y_res, geotiff_new_resolution_name):
    if geotiff_new_resolution_name.split(".")[-1] != "tif" or clipped_geotiff_name.split(".")[-1] != "tiff":
        geotiff_new_resolution_name = "{0}.tif".format(geotiff_new_resolution_name)
    change_geotiff_resolution(selected_geotiff, geotiff_new_x_res, geotiff_new_y_res, geotiff_new_resolution_name)
    return json.dumps({'status': 'Done'})

