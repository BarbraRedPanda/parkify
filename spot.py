import os
import bosdyn.client
from dotenv import load_dotenv
import gpsd

import logging
import io
import time
import numpy as np
import datetime
#import numpy as np
import geopy.distance
import requests
import json
import csv
from bosdyn.client.image import ImageClient
from PIL import Image


unsentStreams = []
gpsd.connect() # Connects to satellites

# gets API token from .env file
load_dotenv()
USER = os.getenv('USER')
PASS = os.getevn('USER_PASSWORD')
TOKEN = os.getenv('API_TOKEN')

# Creates robot object
sdk = bosdyn.client.create_standard_sdk('understanding-spot')
robot = sdk.create_robot('192.168.80.3')
id_client = robot.ensure_client('robot-id')
robotID = id_client.get_id()

# Authenticates and sets up image services 
robot.authenticate(USER, PASS)
image_client = robot.ensure_client(ImageClient.default_service_name)
sources = image_client.list_image_sources()
[source.name for source in sources]

# Adds folder for images

today = str(datetime.date.today())
dirPath = f"./responses/{today}"
os.makedirs(dirPath, exist_ok=True)

# Iterate over the subfolders and create them if they don't already exist
os.makedirs(f'{dirPath}/images', exist_ok=True)

# implements SPOT camera 
#   returns 2-element array of image streams
def getImageStreamArray():
    image_responses = image_client.get_image_from_sources(['left_fisheye_image', "right_fisheye_image"])
    snapshots = [open(io.BytesIO(response.image.data), 'rb') for response in image_responses]
    image_streams = []
    for snapshot in snapshots:
        image_streams.append(io.BytesIO(snapshot))
    return image_streams

# Gets JSON response from API call
#   param   - image_stream - image stream to be sent to API
#   return  - response.json() - JSON of an API 
def getResponse(image_stream):
    response = requests.post(
        'https://exotek.co/api/misc/platerecognizer',
        files={'upload': image_stream},
        headers={'Authorization': f'Token {TOKEN}'}
    )
    print(response.json())
    return response.json()


# Adds data to CSV file ./responses/responsesDATE/data.csv
# data parameter is an array of [plate, confidence, vehicle type, coords, time, image path]
def addData(data):
    with open(f'./{dirPath}/data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


        
        
# Saves image stream in ./responses/images directory
def saveImage(image, filename):
    with open(f"./{dirPath}/images/image_{filename}", 'wb') as f:
            f.write(image.getvalue())
    print(f"Saved image as image_{filename}")

def prepareData(apiResponse, imageStream):

    # Gets timestamp of image and preliminary path for that image
    timestamp = datetime.datetime.now().strftime('%H-%M-%S')
    imagePath = f'./{dirPath}/images/image_{timestamp}'

    # Creates a new line in a CSV output for each result
    for result in apiResponse['results']:
        data = [result.get('plate'), 
                result.get('score'), 
                result.get('vehicle', {}).get('type'),
                coords[0],
                coords[1],
                timestamp,
                imagePath
                ]
        addData(data)
    # Saves image as image_{timestamp}
    saveImage(imageStream, timestamp) 
    

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

    imageStreams = getImageStreamArray()

    # Adds current image stream to queue for request
    unsentStreams.append(imageStreams)
    try:
        for stream in unsentStreams:
            response = getResponse(stream)
            # if there's no response for a plate, skip it
            if not response.get('results'):
                continue
            prepareData(response, stream)
    except:
         print('No internet!')
