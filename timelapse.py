import datetime
from enum import Enum
import os
import shutil
import subprocess
import time

import requests

IP_ADDRESS = "localhost"
PORT = 8080
START_TIME = datetime.time(hour=6, minute=00, second=00)
DURATION_SECONDS = 60*120 # 2 hours
SNAPSHOT_INTERVAL = 5.0
DATA_DIR = "/home/darsh/timelapse"
# URL of the mjpg-streamer snapshot endpoint
ENDPOINT = f"http://{IP_ADDRESS}:{PORT}/?action=snapshot"
FILE_DELETION_DAYS = 14

N_ZEROS_IMG_NAME = 6

class Status(Enum):
    WAIT = 0
    TAKING_TIMELAPSE = 1


def take_snapshot(output_filename='snapshot.jpg'):
    response = requests.get(ENDPOINT, timeout=5)
    response.raise_for_status()
    with open(output_filename, 'wb') as f:
        f.write(response.content)

def make_video(filename_path: str, vid_dir: str, fps: float):
    in_dir_pattern = os.path.join(vid_dir, f"*.jpg")
    ffmpeg_cmd = ["ffmpeg", "-y", "-framerate", str(fps), "-pattern_type", "glob", "-i", f"{in_dir_pattern}", "-c:v", "mjpeg", filename_path]
    res = subprocess.run(ffmpeg_cmd, shell=False, capture_output=True, timeout=240)
    assert res.returncode == 0, f"{res}"


def main():

    status = Status.WAIT
    timelapse_subdir = None
    img_ctr = 0

    while True:
        cur_time = datetime.datetime.now()
        timelapse_start = datetime.datetime.combine(datetime.date.today(), START_TIME)
        timelapse_end = timelapse_start + datetime.timedelta(seconds=DURATION_SECONDS)
        if status == Status.WAIT:
            # clean up old files
            stuff = os.listdir(DATA_DIR)
            for f in stuff:
                f_path = os.path.join(DATA_DIR, f)
                mod_time = os.stat(f_path).st_mtime
                file_time_sec = time.time() - mod_time
                file_time_days = file_time_sec / (60 * 60 * 24)
                if file_time_days > FILE_DELETION_DAYS:
                    if os.path.isfile(f_path):
                        os.remove(f_path)
                    elif os.path.isdir(f_path):
                        shutil.rmtree(f_path)

            # check if time to do another timelapse
            if cur_time > timelapse_start and cur_time < timelapse_end:
                status = Status.TAKING_TIMELAPSE
                continue
        
        if status == Status.TAKING_TIMELAPSE:
            # check if started, if not init variables
            if timelapse_subdir is None:
                timelapse_subdir = cur_time.strftime("%Y-%m-%d_%H-%M-%S")
                timelapse_subdir = os.path.join(DATA_DIR, timelapse_subdir)
                os.makedirs(timelapse_subdir, exist_ok=False)

            # take photo
            photo_name = f"my_img_{str(img_ctr).zfill(N_ZEROS_IMG_NAME)}" + ".jpg"
            photo_name = os.path.join(timelapse_subdir, photo_name)
            take_snapshot(photo_name)

            img_ctr += 1

            # check if done, if so make video and reset variables
            if cur_time > timelapse_end:
                make_video(timelapse_subdir + ".avi", timelapse_subdir, 30)
                timelapse_subdir = None
                img_ctr = 0
                status = Status.WAIT

        time.sleep(SNAPSHOT_INTERVAL)





if __name__ == "__main__":
    main()
