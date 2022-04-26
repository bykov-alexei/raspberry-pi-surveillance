libcamera-vid -o - -n -t 0 | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264 &
/usr/bin/python3 /home/pi/raspberry-pi-surveillance/run.py &
wait
