import os
from dotenv import load_dotenv
import gpsd

import logging
import io
import time
#import numpy as np
import geopy.distance
import requests

from PIL import Image
from picamera import PiCamera


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
    return response
        
def svImg(image, filename):
    with open(f'image_{filename}', 'wb') as f:
            f.write(image)
    print(f"Saved image as image_{filename}")

gpsd.connect() # Connects to satellites

# gets API token
load_dotenv()
TOKEN = os.getenv('API_TOKEN')

i = 0

coordsPrev = (0.0, 0.0)
while(True):
    time.sleep(3)
    # Receive GPS packet
    packet = gpsd.get_current();
    coords = (packet.lat, packet.lon)

    if (geopy.distance.geodesic(coordsPrev, coords).km < 0.00001) :
        continue

    coordsPrev = coords
    i= i+1
    imageStream = getImageStream()
    #svImg(imageStream.getvalue(), i)
    getResponse(imageStream)

