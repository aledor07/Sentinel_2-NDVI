import os, rasterio, re
from datetime import datetime


class Raster:
    # Raster class to associate the bands nir and red with their date

    def __init__(self, date, band_4, band_8):
        self.d = date
        self.b4 = band_4
        self.b8 = band_8


def date_check():
    # Check the dates of the ndvi files present in the folder

    folder_files.append(os.listdir(path_ndvi))
    for file in folder_files[0]:
        match = re.search(r"\d{2}-\d{2}-\d{2}", file)
        date = datetime.strptime(match.group(), "%y-%m-%d").date().strftime("%y-%m-%d")
        folder_dates.append(date)
    return folder_dates


def directories_search(directory_path):
    # Search for folders and subfolders within the folder

    subfolders = [f.path for f in os.scandir(directory_path) if f.is_dir()]
    for directory_path in list(subfolders):
        subfolders.extend(directories_search(directory_path))
    return subfolders


def bands_dn():
    # Getting the dates of the bands and the name of the file

    for directory in directories_list:
        os.chdir(directory)
        pictures = os.listdir()

        for p in pictures:
            match = re.search(r"\d{4}\d{2}\d{2}", p)
            date = (
                datetime.strptime(match.group(), "%Y%m%d").date().strftime("%y-%m-%d")
            )

            if "B08" in p:
                bands_8.append(p)
                sentinel_dates.append(date)

            elif "B04" in p:
                bands_4.append(p)
                sentinel_dates.append(date)

    return


def del_duplicates():
    # Delete existing dates and bands in the NDVI folder

    for i in duplicate_dates:
        sentinel_dates.pop(i)
        bands_8.pop(i)
        bands_4.pop(i)
        directories_list.pop(i)

    return


def absolute_paths():
    # Store of the absolute paths of the bands

    if len(sentinel_dates) > len(duplicate_dates):
        for i in range(0, len(directories_list)):
            bands_8[i] = directories_list[i] + "\\" + bands_8[i]
            bands_4[i] = directories_list[i] + "\\" + bands_4[i]

    return bands_8, bands_4


def calc_ndvi(raster):
    # Specify the output path of the NDVI output raster

    output_path = path + "\\NDVI\\NDVI"

    b4 = raster.b4
    b8 = raster.b8

    # we open the bands with rasterio
    with rasterio.open(b4) as red:
        RED = red.read()
    with rasterio.open(b8) as nir:
        NIR = nir.read()

    # we calculate the NDVI
    NDVI = (NIR.astype(float) - RED.astype(float)) / (NIR + RED)

    profile = red.meta
    profile.update(driver="GTiff")
    profile.update(dtype=rasterio.float32)

    with rasterio.open(output_path + "_" + raster.d + ".tif", "w", **profile) as dst:
        dst.write(NDVI.astype(rasterio.float32))

    return


# Start the script

path = os.getcwd()
path_ndvi = path + "\\NDVI"

folder_files = []
folder_dates = []
bands_8 = []
bands_4 = []
sentinel_dates = []

date_check()  # Check the date of the processed files in the folder

# The names of the files and the directories where the bands to be processed are located

directories = directories_search(path)
directories_list = [d for d in directories if "R10m" in d]

bands_dn()

# Create a list with the dates of the downloaded files
sentinel_dates = list(set(sentinel_dates))
duplicate_dates = [
    sentinel_dates.index(d) for d in sentinel_dates if d in folder_dates
]  # List of duplicate date indexes
duplicate_dates = sorted(duplicate_dates, reverse=True)

# Create a list with the names to assign to the rasters
raster_names = ["raster_" + str(d) for d in range(1, len(sentinel_dates) + 1)]
raster_objects = []


if len(sentinel_dates) > len(duplicate_dates):
    del_duplicates()
    absolute_paths()

    for k in range(0, len(raster_names)):
        raster_objects.append(Raster(sentinel_dates[k], bands_4[k], bands_8[k]))

    for raster in raster_objects:
        calc_ndvi(raster)

    if len(sentinel_dates) > 1:
        print(str(len(sentinel_dates)) + " Images have been processed.")

    else:
        print(str(len(sentinel_dates)) + " Image has been processed.")

else:
    print("There are no new images to process.")
