import os
import requests

def download_model(url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded to {save_path}")
    else:
        print(f"Failed to download. Status code: {response.status_code}")

if __name__ == "__main__":
    url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/lite/float16/1/pose_landmarker_lite.task"
    save_path = "fall_detection/models/pose_landmarker_lite.task"
    download_model(url, save_path)
