import os
import requests
import rasterio
import logging

import numpy as np

from pathlib import Path
from datetime import datetime, timedelta

import geopandas as gpd
import matplotlib.pyplot as plt

def plot_grs(
        grs_df, 
        date_str, 
        time_str,
        time_h
):
    output_dir = Path(__file__).parent / f"output/{date_str}{time_str}{time_h}"
    plt.figure(figsize=(20, 15))
    plt.imshow(np.flip(grs_df), cmap='Blues', 
               extent=[50000, 
                        50000 + 900 * 1000,
                        30000, 
                        30000 + 800 * 1000])
    plt.colorbar(label='Suma opadu [mm]')

    plt.xlabel('X [m]', fontsize=16)
    plt.ylabel('Y [m]', fontsize=16)
    plt.title(f'Opad, dane GRS: {date_str}, {time_str}, {time_h}', fontsize=18)
    plt.grid(True)
    plt.legend(fontsize=16)

    os.makedirs(output_dir, exist_ok=True)

    output_file = output_dir / f"{date_str}_{time_str}_{time_h}_grs.png"
    plt.savefig(output_file) 


def parse_metadata(file_path):
    with open(file_path, 'r') as f:
        # Read the first 6 lines
        header_lines = [next(f) for _ in range(6)]

    # Parse metadata from header lines
    metadata = {}
    for line in header_lines:
        key, value = line.split()
        metadata[key.strip()] = value.strip()

    return {
        "ncols": int(metadata['ncols']),
        "nrows": int(metadata['nrows']),
        "xllcorner": float(metadata['xllcorner']),
        "yllcorner": float(metadata['yllcorner']),
        "cellsize": int(metadata['cellsize']),
        "nodata_value": float(metadata['NODATA_value'])
    }


def load_data(file_path, filename):
    with rasterio.open(file_path) as src:
        grs_rain_data = src.read(1, masked=True)

    metadata = parse_metadata(file_path)

    grs_rain_data = np.ma.masked_equal(grs_rain_data, metadata['nodata_value'])
    
    return {
        "data": grs_rain_data,
        "meta": metadata
    }


def get_grs_file(
        date,
        time, 
        imgw_host,
        imgw_mode, 
        imgw_data_name
):
    url = f"https://{imgw_host}{imgw_mode}{imgw_data_name}{date}{time}_acc0060_grs.asc"
    
    filename = f"{date}{time}_acc0060_grs.asc"
    save_path = os.path.join(Path(__file__).parent / "grs_asc", filename)

    logging.info(f"Searching file: '{filename}'")

    if os.path.exists(save_path):
        logging.info(f"File already exists: '{filename}'! Loading content...")
        return load_data(save_path, filename)

    response = requests.get(url)
    
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as file:
            file.write(response.content)

        logging.info(f"New IMGW GRS data file downloaded: '{filename}'")
        return load_data(save_path, filename)

    else:
        logging.warning("Failed to download the requested IMGW GRS file!")
        return None   


def get_grs_data(
    datetime_now,
    time_h,
    imgw_host,
    imgw_mode,
    imgw_data   
):
    start = datetime_now
    grs_data = []
    rainfall_sums = 0

    # get grs data
    logging.info(f"Getting `{imgw_mode}` GRS data... Start time: {start}")

    for h in range(int(time_h)):
        grs_data.append(
            get_grs_file(
                datetime_now.strftime("%Y%m%d"),
                datetime_now.strftime("%H%M"), 
                imgw_host,
                imgw_mode,  
                imgw_data))
        datetime_now -= timedelta(hours=1)
    
    # calculate grs sum
    logging.info("Calculating GRS data sum...")
    for hour_rainfall in grs_data:
        rainfall_sums += hour_rainfall['data']

    logging.info(f"IMGW RainGRS data ready. \n \
                START: {start} \n \
                END: {datetime_now} \n \
                TIME SPAN: {time_h}h   ")

    return rainfall_sums