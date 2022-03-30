apt-get install -y python3-dev 
pip3 install opencv-contrib-python face_recognition boto3

id=$(uuidgen)
echo "device_id=\"$id\"" > credentials.py
echo "Enter public AWS key:"
read public_aws_key
echo "public_key=\"$public_aws_key\"" >> credentials.py
echo "Enter private AWS key:"
read private_aws_key
echo "private_key=\"$private_aws_key\"" >> credentials.py
echo "Enter working mode (dev, prod)"
read mode
echo "mode=\"$mode\"" >> credentials.py
