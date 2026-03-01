# pi_home_assistant


# setup

## flash pi

We use the Raspberry Pi Imager to Flash Ubuntu 24.04 onto the Pi Zero 2 W. We configure, before flashing, to enable ssh and auto-connect to the network.

## setup pi

We login to the pi va ssh, scanning hosts on the network to find the pi's ip address.

### mjpeg streamer

We use: `https://github.com/jacksonliam/mjpg-streamer` and opencv.

```
sudo apt-get update
sudo apt-get install cmake libjpeg8-dev gcc g++ git python3-pip
cd $HOME
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer
cd mjpg-streamer-experimental
make
sudo make install
```

Now we configure mjpeg streamer to start using systemd

```
sudo nano /etc/systemd/system/webcam.service
```
```
[Unit] 
Description=Webcam Service
After=network-online.target 
Wants=network-online.target systemd-networkd-wait-online.service 

[Service] 
ExecStart=mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 1280x720 -f 10" -o "output_http.so -w /usr/local/share/mjpg-streamer/www"

[Install] 
WantedBy=multi-user.target 
```

```
sudo systemctl start webcam
sudo systemctl enable webcam
sudo reboot
```

Should result in webpage `http://10.0.0.110:8080/index.html` with examples, instructions, snapshots, and streams.


Single commands (not needed if using systemd)
```
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/jpg-streamer/mjpg-streamer-experimental
#export PATH=$PATH:$HOME/jpg-streamer/mjpg-streamer-experimental
mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 1280x720 -f 10" -o "output_http.so -w /usr/local/share/mjpg-streamer/www"
```

### timelapse

```
sudo apt-get install ffmpeg
cd $HOME
git clone https://github.com/MZandtheRaspberryPi/pi_home_assistant.git
cd pi_home_assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```