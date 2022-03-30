import io
import os
import sys
import time
import boto3
import logging
import botocore
import picamera

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from uuid import uuid4 as uuid
from threading import Thread
from datetime import datetime, timedelta
from face_recognition import face_locations, face_encodings

from config import device_id, mode, duration

camera = picamera.PiCamera(resolution=(1024, 768))

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
)

def recording(camera):
    camera.start_recording('1.h264')
    camera.wait_recording(5)
    while True:
        dt = datetime.utcnow()
        timestamp = dt.timestamp()
        
        filename = f'{device_id}_{dt.year}_{dt.month}_{dt.day}_{dt.hour}_{dt.minute}_{dt.second}.h264'
        
        camera.split_recording(filename)
        camera.wait_recording(duration)
        
        # Moving ready video to recordings folder
        os.replace(filename, os.path.join('recordings', filename))
        
    camera.stop_recording()
    
def video_uploading():
    # Uploading videos from recordings folder
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(f'recordings-{mode}')
    
    # rds_client = boto3.client('rds')
    # token = client.generate_db_auth_token(DBHostname=db_endpoint, Port=3306, DBUsername=db_user, Region='us-west-2')  
    
    while True:
        files = os.listdir('recordings')
        for filename in files:
            try:
                response = s3_client.upload_file(os.path.join('recordings', filename), f'surveillance-app-{mode}', filename)
                os.remove(os.path.join('recordings', filename))
                
                str_date = list(map(int, filename.replace('.h264', '').split('_')[1:]))
                start_datetime = datetime(*str_date)
                print(start_datetime)
                end_datetime = start_datetime + timedelta(seconds=duration)
                print(end_datetime)
                table.put_item(
                    Item={
                        'id': str(uuid()),
                        'start_datetime': str(start_datetime),
                        'end_datetime': str(end_datetime),
                        'filename': filename,
                    }
                )
                
            except botocore.exceptions.EndpointConnectionError as e:
                print('Video uploader connection error')
                time.sleep(60)

def face_recognition(camera):
    while True:
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')
        image = np.array(Image.open(stream), dtype=np.uint8)
        plt.imsave('123.png', image)
        locations = face_locations(image)
        print(locations)
        encodings = face_encodings(image, locations)
        print([e[0] for e in encodings])
        time.sleep(1)

recording_thread = Thread(target=recording, args=(camera,))
video_uploading_thread = Thread(target=video_uploading)
face_recognition_thread = Thread(target=face_recognition, args=(camera,))

recording_thread.start()
print('Recording thread started')

video_uploading_thread.start()
print('Video uploading thread started')

# face_recognition_thread.start()
# print('Face recognition thread start')

recording_thread.join()

