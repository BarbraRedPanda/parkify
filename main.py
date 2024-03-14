import os
import bosdyn.client
from dotenv import load_dotenv
import gpsd

import logging
import io
import time
import numpy as np
import geopy.distance
import requests

from PIL import Image

from bosdyn.client.image import ImageClient


gpsd.connect() # Connects to satellites

# Gets SPOT's username and password for the user account
load_dotenv()
USER = os.getenv('USER')
PASS = os.getenv('USER_PASSWORD')
TOKEN = os.getenv('API_TOKEN')

# Creates the SDK and robot objects
sdk = bosdyn.client.create_standard_sdk('understanding-spot')
robot = sdk.create_robot("192.168.80.3")
id_client = robot.ensure_client('robot-id')
robotID = id_client.get_id();

robot.authenticate(USER, PASS)  # Authenticates with SPOT

# Starts getting images 
image_client = robot.ensure_client(ImageClient.default_service_name)
sources = image_client.list_image_sources()
[source.name for source in sources]


i = 0

coordsPrev = (0.0, 0.0)
while(True):
    time.sleep(3)
    # Receive GPS packet
    packet = gpsd.get_current();
    coords = (packet.lat, packet.lon)

    if (geopy.distance.geodesic(coordsPrev, coords).km < 0.003) :
        continue

    coordsPrev = coords
    image_responses = image_client.get_image_from_sources(["left_fisheye_image", "right_fisheye_image"])

    snapshots = [open(io.BytesIO(response.image.data), 'rb') for response in image_responses]

    for i, snapshot in snapshots:
        with io.BytesIO(snapshot) as image_stream:
            response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                files=dict(upload=image_stream),
                headers={'Authorization': f'Token {TOKEN}'}
            )
    #(Image.open(io.BytesIO(image_left.shot.image.data))).save("./images/" + str(i+1) + "left_fisheye.png")
    #(Image.open(io.BytesIO(image_right.shot.image.data))).save("./images/"+ str(i+1)+"right_fisheye.png")


    




