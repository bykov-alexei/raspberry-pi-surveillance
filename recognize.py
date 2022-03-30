import boto3
from face_recognition import face_locations, face_encodings
from decimal import Decimal
from uuid import uuid4 as uuid
from credentials import device_id


def recognize_faces(frame, timestamp, table):
    locations = face_locations(frame)
    encodings = face_encodings(frame, locations)
    with table.batch_writer() as batch:
        for location, encoding in zip(locations, encodings):
            item = {
                'id': str(uuid()),
                'device_id': device_id,
                'timestamp': Decimal(timestamp), 
                'top': location[0], 
                'right': location[1],
                'bottom': location[2],
                'left': location[3],
            }
            item.update({f'e{i+1}': Decimal(number) for i, number in enumerate(encoding)})
            
            batch.put_item(Item=item)