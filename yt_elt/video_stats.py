import requests as req 
import json

import os 
from dotenv import load_dotenv

load_dotenv(dotenv_path ="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "LaLigaDeLosSuperCuates&key"


def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}={API_KEY}"
        response = req.get(url)
        response.raise_for_status()
  
        data = response.json()
        ##print (json.dumps(data,indent=4))
        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        print (channel_playlistId)
        return 1   
    except req.exceptions.RequestException as e:     
        raise e


if __name__ == "__main__":
    get_playlist_id()