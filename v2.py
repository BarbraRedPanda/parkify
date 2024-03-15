import os
from dotenv import load_dotenv
import gpsd

import logging
import io
import time
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
os.makedirs("responses", exist_ok=True)
subfolders = ['images', 'data']

# Iterate over the subfolders and create them if they don't already exist
for subfolder in subfolders:
    subfolder_path = os.path.join('responses', subfolder)
    os.makedirs(subfolder_path, exist_ok=True)

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
    print(response)
    return json.loads(response)

# Returns an image stream with plates
def addMetadata(image_stream, result):
    # Parses information from result
    plate = result.get('plate')
    newData = { 'confidence': result.get('score'),
                'vehicle': result.get('vehicle', {}).get('type')
                }

    img = Image.open(image_stream)                          
    currentData = json.loads(img.info.get('metadata', {}))  # gets current metadata
    currentData[plate] = newData                            # appends newly parsed info into metadata
    img.info['metadata'] = json.dumps(currentData)          # n.b. the key for the data is the plate
    
    # returns as image stream
    newStream = io.BytesIO()
    img.save(newStream, format='JPEG')
    return newStream
        
# Saves image stream in ./responses/images directory
def saveImage(image, filename):
    with open(f"./responses/images/image_{filename}", 'wb') as f:
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
    if (geopy.distance.geodesic(coordsPrev, coords).km < 0.00001) :
        continue

    coordsPrev = coords

    imageStream = getImageStream()

    api_response = getResponse(imageStream)

    # Reiterates loop if no plate is found 
    if not api_response.get('results'):
         continue
    
    i += 1
    for result in api_response['results']:
        finalStream = addMetadata(imageStream, result)
    saveImage(finalStream, i) 
    
