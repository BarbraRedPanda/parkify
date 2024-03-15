import os
from dotenv import load_dotenv
import gpsd

import logging
import io
import time
import datetime
#import numpy as np
import geopy.distance
import requests
import json

from PIL import Image
from picamera import PiCamera


gpsd.connect() # Connects to satellites

# gets API token from .env file
load_dotenv()
TOKEN = os.getenv('API_TOKEN')


# Adds folder for images

today = str(datetime.date.today())
dirPath = f"./responses/{today}"
os.makedirs(dirPath, exist_ok=True)

# Iterate over the subfolders and create them if they don't already exist
os.makedirs(f'{dirPath}/images', exist_ok=True)

# implements the Raspberry Pi camera 
# returns image stream 
def getImageStream():
    camera = PiCamera()
    image_stream = io.BytesIO()
    camera.capture(image_stream, format='jpeg')
    image_stream.seek(0)
    camera.close()
    return image_stream

def getResponse(image_stream):
    response = requests.post(
        'https://api.platerecognizer.com/v1/plate-reader/',
        files={'upload': image_stream},
        headers={'Authorization': f'Token {TOKEN}'}
    )
    print(response.json())
    return response.json()


def associateData(result, location, time):
    # Parses information from result
    plate = result.get('plate')
    newData = { 'confidence': result.get('score'),
                'vehicle': result.get('vehicle', {}).get('type'),
                'location': location
                }
    path = f"./{dirPath}/images/image_{time}"
    with open(f"./{dirPath}/data.txt", 'a') as f:
        f.write(f"{plate} {newData.get('location')} {path}\n")
        
        
# Saves image stream in ./responses/images directory
def saveImage(image, filename):
    with open(f"./{dirPath}/images/image_{filename}", 'wb') as f:
            f.write(image.getvalue())
    print(f"Saved image as image_{filename}")

i = 0

# Takes a picture every 3 seconds if user has moved 
coordsPrev = (0.0, 0.0)
while(True):
    time.sleep(3)
    # Receive GPS packet
    packet = gpsd.get_current();
    coords = (packet.lat, packet.lon)

    # Reiterates loop until GPS has moved significantly 
    """if (geopy.distance.geodesic(coordsPrev, coords).km < 0.00001) :
        continue"""

    coordsPrev = coords

    imageStream = getImageStream()

    api_response = getResponse(imageStream)

    # Reiterates loop if no plate is found 
    if not api_response.get('results'):
         continue
   
    timestamp = datetime.datetime.now().strftime('%H-%M-%S')
    i += 1
    for result in api_response['results']:
        associateData(result, coords, timestamp)
    saveImage(imageStream, timestamp) 
    
