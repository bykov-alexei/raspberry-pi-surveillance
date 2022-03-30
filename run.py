import boto3
import cv2
from cv2 import VideoCapture
from recognize import recognize_faces
from config import mode, device_id
from datetime import datetime
from threading import Thread

fourcc = cv2.VideoWriter_fourcc(*"MJPG")

cap = VideoCapture(0)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(f'faces-recognition-{mode}')

recognize_faces_thread = None

duration = 60 # seconds
fps = 15
videoWriter = None
n_frames = 0
prev_frame = datetime.utcnow()

while datetime.utcnow().second != 0:
    pass


while True:

    ret, frame = cap.read()
    now = datetime.utcnow()
    timestamp = now.timestamp()
    if (now - prev_frame).microseconds < 1_000_000 // fps:
        continue
    prev_frame = now

    if not ret:
        print('Cannot get video stream')
        exit(-1)

    if videoWriter is None or n_frames == fps * duration:
        if videoWriter is not None:
            n_frames = 0
            videoWriter.release()
        videoWriter = cv2.VideoWriter(
            filename=f'{device_id}_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}.avi',
            fourcc=fourcc,
            fps=15,
            frameSize=(frame.shape[0], frame.shape[1]),
        )

    frame = frame[:, :, ::-1]
    videoWriter.write(frame)
    n_frames += 1
    print(n_frames, fps * duration)
    # if recognize_faces_thread is None or not recognize_faces_thread.is_alive():
    #     # print('123')
    #     recognize_faces_thread = Thread(target=recognize_faces, args=(frame, timestamp, table))
    #     recognize_faces_thread.start()
    # recognize_faces(frame, timestamp, table)

    # print(recognize_faces_thread, recognize_faces_thread.is_alive())
    # print('1')
