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
sudo apt-get install -y ffmpeg python3-venv
cd $HOME
git clone https://github.com/MZandtheRaspberryPi/pi_home_assistant.git
cd pi_home_assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```
sudo nano /etc/systemd/system/timelapse.service
```

```
[Unit] 
Description=Timelapse Service
After=network-online.target 
Wants=network-online.target systemd-networkd-wait-online.service 

[Service] 
ExecStart=/home/darsh/pi_home_assistant/venv/bin/python3 /home/darsh/pi_home_assistant/timelapse.py

[Install] 
WantedBy=multi-user.target 
```

```
sudo systemctl start timelapse
sudo systemctl enable timelapse
sudo reboot
```

### copying timelapses and converting them

The images are stored on the remote computer if using the python based client `timelapse.py`. They are in the `DATA_DIR` which by default is `/home/darsh/timelapse`. By default they will be kept for `FILE_DELETION_DAYS` which is set to `14` by default, then images and videos will be deleted to avoid filling up the drive.

Connect to the computer, see the timelapses available
```
ssh darsh@10.0.0.110
ls /home/darsh/timelapse/*.avi
```

Now note the name of the .avi file and on your computer that you wish to have the file on, copy it out using scp:
```
scp darsh@10.0.0.110:/home/darsh/timelapse/2026-03-01_06-00-01.avi .
```

On your output computer, use ffmpeg to convert it to an mp4. In testing, converion on the raspberry pi didn't work well though this could probably be resolved with more testing...
```
ffmpeg -i /home/darsh/timelapse/2026-03-01_06-00-01.avi -strict -2 /home/darsh/timelapse/2026-03-01_06-00-01.avi.mp4
```

### seeing camera settings

This can be done through MJPEG Streamer through the control tab `http://10.0.0.110:8080/index.html`.

Or, using v4l-utils.

```
sudo apt-get install v4l-utils
v4l2-ctl -d /dev/video0 -l # see the controls available
```

Change a channel
```
v4l2-ctl -d /dev/video0 -c example_channel=0
```

### changing timelapse settings

By default the python client can take one timelapse a day. It has a start time `START_TIME` set to 6:00 AM by default, and a duration, `DURATION_SECONDS` set to 2 hours by default. Between these times it takes a snapshot every `SNAPSHOT_INTERVAL` seconds, set to 5 by default. When it is past the end time, it processes the snapshots into a video (a `.avi` file). The `.avi` format is more legacy whereas `.mp4` is more widely used on the internet and what's app. Hence conversion of the video may be needed before sharing.