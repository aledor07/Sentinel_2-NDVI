import os, rasterio, re
from datetime import datetime


class Raster:
    
    # Definimos la clase raster para asociar las bandas nir y red con su fecha #
    
    def __init__(self, date, band_4, band_8):
        
        self.d = date
        self.b4 = band_4
        self.b8 = band_8


def date_check():
    
    ## Comprueba las fechas de los archivos de ndvi presentes en la carpeta ##
    
    folder_files.append(os.listdir(path_ndvi))
    for file in folder_files[0]:
        match = re.search(r'\d{2}-\d{2}-\d{2}', file)
        date = datetime.strptime(match.group(),'%y-%m-%d').date().strftime('%y-%m-%d')
        folder_dates.append(date)
    return folder_dates

def directories_search(directory_path):
    
    ## Búsqueda de carpetas y subcarpetas dentro de la carpeta ##
    
    subfolders= [f.path for f in os.scandir(directory_path) if f.is_dir()]
    for directory_path in list(subfolders):
        subfolders.extend(directories_search(directory_path))
    return subfolders


def bands_dn():
    
    # Obtenemos las fechas de las bandas y el nombre del archivo #
    
    for directory in directories_list:

        os.chdir(directory)
        pictures=os.listdir()

        for p in pictures:
            
            match = re.search(r'\d{4}\d{2}\d{2}', p)
            date = datetime.strptime(match.group(), '%Y%m%d').date().strftime('%y-%m-%d')

            if 'B08' in p:

                bands_8.append(p)
                sentinel_dates.append(date)

            elif 'B04' in p:

                bands_4.append(p)
                sentinel_dates.append(date)

    return


def del_duplicates():

    #Elimina fechas y bandas existentes en la carpeta NDVI#
    
    for i in duplicate_dates:

        sentinel_dates.pop(i)
        bands_8.pop(i)
        bands_4.pop(i)
        directories_list.pop(i)
            
    return


def absolute_paths():
    
    # Guardamos las rutas absolutas de las bandas #

    if len(sentinel_dates) > len(duplicate_dates):

        for i in range(0,len(directories_list)):

            bands_8[i]=directories_list[i]+"\\"+bands_8[i]
            bands_4[i]=directories_list[i]+"\\"+bands_4[i]

    return bands_8, bands_4

def calc_ndvi(raster):
    
    # Especificamos la ruta de salida de los ráster de salida NDVI #
    
    output_path = path+'\\NDVI\\NDVI'

    b4 = raster.b4
    b8 = raster.b8

    #abrimos las bandas con rasterio
    with rasterio.open(b4) as red:
        RED = red.read()
    with rasterio.open(b8) as nir:
        NIR = nir.read()

    #calculamos el NDVI
    NDVI = (NIR.astype(float) - RED.astype(float)) / (NIR+RED)

    profile = red.meta
    profile.update(driver='GTiff')
    profile.update(dtype=rasterio.float32)

    with rasterio.open(output_path+'_'+raster.d+'.tif', 'w', **profile) as dst:
        dst.write(NDVI.astype(rasterio.float32))

    return



## Se inicia el script

path=os.getcwd()
path_ndvi= path+'\\NDVI'

folder_files=[];folder_dates=[];bands_8=[];bands_4=[];sentinel_dates=[]

date_check() ## Se comprueba la fecha de los archivos procesados en la carpeta

# Se obtienen los nombres de los archivos y los directorios donde se encuentran las bandas a procesar

directories=directories_search(path)
directories_list=[d for d in directories if 'R10m' in d]

bands_dn()

##Creamos una lista con las fechas de los archivos descargados           
sentinel_dates=list(set(sentinel_dates))
duplicate_dates=[sentinel_dates.index(d) for d in sentinel_dates if d in folder_dates] ##Lista de indices de fechas duplicadas
duplicate_dates=sorted(duplicate_dates, reverse=True)

##Creamos lista con los nombres a asignar a los rasters
raster_names=['raster_'+str(d) for d in range(1,len(sentinel_dates)+1)]
raster_objects=[]


    
if len(sentinel_dates)> len(duplicate_dates):
    
    del_duplicates()
    absolute_paths()
    
    for k in range(0,len(raster_names)):
    
        raster_objects.append(Raster(sentinel_dates[k],bands_4[k], bands_8[k]))
        
    for raster in raster_objects:
        
        calc_ndvi(raster)
        
    if len(sentinel_dates)>1:
        
        print(str(len(sentinel_dates))+" Images have been processed.")
        
    else:
        
        print(str(len(sentinel_dates))+" Image has been processed.")
    
else:
    
    print("There are no new images to process.")
    