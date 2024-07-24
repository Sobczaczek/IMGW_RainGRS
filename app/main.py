from pathlib import Path
from datetime import datetime, timedelta
import logging

from imgw_raingrs import get_grs_data, plot_grs

# params
imgwGrsHost = "danepubliczne.imgw.pl/datastore/getfiledown/"
imgwGrsMode = "Oper/Nowcasting/"
imgwGrsData = "RainGRS/grs_60_asc/"
imgwGrsDataOffsetDays = 3

timeH = 24

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    
    # time
    now = datetime.now()
    timeWithOffset = now - timedelta(days=imgwGrsDataOffsetDays)
    timeRoundedH = timeWithOffset.replace(minute=0, second=0, microsecond=0)

    dateAsString = timeRoundedH.strftime("%Y%m%d")
    timeAsString = timeRoundedH.strftime("%H%M")

    dateStart = datetime.strptime(dateAsString, "%Y%m%d")
    timeStart = datetime.strptime(timeAsString, "%H%M")

    datetimeNow = dateStart.replace(hour=timeStart.hour, minute=timeStart.minute)

    # rainGRS data
    rainGrsData = get_grs_data(datetimeNow, timeH, imgwGrsHost, imgwGrsMode, imgwGrsData) 

    # heatmap
    plot_grs(rainGrsData, dateAsString, timeAsString, timeH)

    

if __name__ == "__main__":
    main()