mkdir recordings
mkdir recognition
mkdir recognition/cars
mkdir recognition/faces

OPENCV_VERSION=4.3.0 
PYTHON_VERSION=3.9 
PYTHON_VERSION_SHORT=39

apt install -y uuid-runtime

cp surveillance.service /lib/systemd/system/

apt-get update
apt-get remove -y ffmpeg x264 libx264-dev
apt-get install -y python3-dev \
    build-essential \
    cmake \
    libjack-jackd2-dev \
    libmp3lame-dev \
    libopencore-amrnb-dev \
    libopencore-amrwb-dev \
    libsdl1.2-dev \
    libtheora-dev \
    libva-dev \
    libvdpau-dev \
    libvorbis-dev \
    libx11-dev \
    libxfixes-dev \
    libxvidcore-dev \
    texi2html \
    zlib1g-dev \
    wget \
    unzip \
    yasm \
    pkg-config \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavformat-dev \
    python${PYTHON_VERSION} \
    python3-pip \
    libpq-dev

apt-get remove -y x264 ffmpeg libx264-dev && \
    apt-get install -y x264 libx264-dev && \
    apt-get install -y ffmpeg && \
    pip3 install numpy

wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip && \
    unzip ${OPENCV_VERSION}.zip && \
    mkdir opencv-${OPENCV_VERSION}/build

cd opencv-${OPENCV_VERSION}/build

cmake \
  -DBUILD_TIFF=ON \
  -DBUILD_opencv_java=OFF \
  -DWITH_CUDA=OFF \
  -DWITH_OPENGL=ON \
  -DWITH_OPENCL=ON \
  -DWITH_IPP=ON \
  -DWITH_TBB=ON \
  -DWITH_EIGEN=ON \
  -DWITH_V4L=ON \
  -DBUILD_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=RELEASE \
  -DCMAKE_INSTALL_PREFIX=$(python${PYTHON_VERSION} -c "import sys; print(sys.prefix)") \
  -DPYTHON_EXECUTABLE=$(which python${PYTHON_VERSION}) \
  -DPYTHON_INCLUDE_DIR=$(python${PYTHON_VERSION} -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
  -DPYTHON_PACKAGES_PATH=$(python${PYTHON_VERSION} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
  -DPYTHON_DEFAULT_EXECUTABLE=$(which python${PYTHON_VERSION}) \
  -DBUILD_NEW_PYTHON_SUPPORT=ON \
  -DBUILD_opencv_python3=ON \
  -DHAVE_opencv_python3=ON \
  -DBUILD_opencv_gapi=OFF \
  -DPYTHON3_NUMPY_INCLUDE_DIRS=/usr/local/lib/python${PYTHON_VERSION}/dist-packages/numpy/core/include \
  .. \
 && make install

 mv \
  lib/python3/cv2.cpython-${PYTHON_VERSION_SHORT}m-x86_64-linux-gnu.so \
  /usr/local/lib/python${PYTHON_VERSION}/dist-packages/cv2.so

pip3 install face_recognition boto3

mkdir /home/pi/.aws

echo "[default]" > /home/pi/.aws/config
echo "region=us-west-2" >> /home/pi/.aws/config
echo "[default]" > /home/pi/.aws/credentials

id=$(uuidgen)
echo "device_id=\"$id\"" > config.py
echo "Enter public AWS key:"
read public_aws_key
echo "aws_access_key_id=\"$public_aws_key\"" >> /home/pi/.aws/credentials
echo "Enter private AWS key:"
read private_aws_key
echo "aws_secret_access_key=\"$private_aws_key\"" >> /home/pi/.aws/credentials
echo "Enter working mode (dev, prod)"
read mode
echo "mode=\"$mode\"" >> config.py
echo "duration=30" >> config.py
