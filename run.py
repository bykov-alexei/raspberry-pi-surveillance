import io
import os
import cv2
import sys
import time
import boto3
import logging
import botocore
import picamera

import numpy as np
import pickle as pkl
import matplotlib.pyplot as plt

from PIL import Image
from uuid import uuid4 as uuid
from decimal import Decimal
from threading import Thread
from datetime import datetime, timedelta
from face_recognition import face_locations, face_encodings

from config import device_id, mode, duration


os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
codec = cv2.VideoWriter_fourcc(*'DIVX')


def recording():
    cap = cv2.VideoCapture('rtsp://127.0.0.1:8554/')
    
    time.sleep(5)
    
    dt = datetime.utcnow()
    filename = f'{device_id}_{dt.year}_{dt.month}_{dt.day}_{dt.hour}_{dt.minute}_{dt.second}.avi'
    out = cv2.VideoWriter(filename, codec, 20.0, (640, 480))
    
    while True:
        if (datetime.utcnow() - dt).seconds < duration * 60:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (640, 480))
            out.write(frame)
        else:
            out.release()
            print('saved')
            os.replace(filename, os.path.join('recordings', filename))
            
            dt = datetime.utcnow()
            filename = f'{device_id}_{dt.year}_{dt.month}_{dt.day}_{dt.hour}_{dt.minute}_{dt.second}.avi'
            out = cv2.VideoWriter(filename, codec, 20.0, (640, 480))

    
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

def face_recognition():
    cap = cv2.VideoCapture('rtsp://127.0.0.1:8554/')
    
    while True:
        # stream = io.BytesIO()
        # camera.capture(stream, format='jpeg')
        dt = datetime.utcnow()
        ret, image = cap.read()
        image = image[:, :, ::-1].astype(np.uint8)
        # image = np.array(Image.open(stream), dtype=np.uint8)
        locations = face_locations(image)
        print(locations)
        encodings = face_encodings(image, locations)
        if len(locations) > 0:
            with open(os.path.join('recognition', 'faces', str(uuid()) + '.pkl'), 'wb') as f:
                pkl.dump((dt, locations, encodings, (cap.get(3), cap.get(4),)), f)
            
def recognition_results_uploading():
    dynamodb = boto3.resource('dynamodb')
    faces_table = dynamodb.Table(f'recognized-faces-{mode}')
    
    while True:
        faces_files = os.listdir(os.path.join('recognition', 'faces'))
        for filename in faces_files:
            with open(os.path.join('recognition', 'faces', filename), 'rb') as f:
                dt, locations, encodings, (width, height) = pkl.load(f)
            for location, encoding in zip(locations, encodings):
                item = {
                    'id': str(uuid()),
                    'device_id': device_id,
                    'top': Decimal(str(location[0] / height)),
                    'right': Decimal(str(location[1] / width)),
                    'bottom': Decimal(str(location[2] / height)),
                    'left': Decimal(str(location[3] / width)),
                    'datetime': str(dt),
                }
                item.update({f'e{i+1}': Decimal(str(encoding[i])) for i in range(128)})
                faces_table.put_item(Item=item)
            os.remove(os.path.join('recognition', 'faces', filename))
            
recording_thread = Thread(target=recording)
video_uploading_thread = Thread(target=video_uploading)
face_recognition_thread = Thread(target=face_recognition)
recognition_uploading_thread = Thread(target=recognition_results_uploading)

recording_thread.start()
print('Recording thread started')

video_uploading_thread.start()
print('Video uploading thread started')

face_recognition_thread.start()
print('Face recognition thread started')

recognition_uploading_thread.start()
print('Recognition uploading thread started')

recording_thread.join()
video_uploading_thread.join()
face_recognition_thread.join()
recognition_uploading_thread.join()
