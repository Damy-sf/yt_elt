import requests as req 
import json
from datetime import date

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
MAXRESULTS = 50

def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
        response = req.get(url)
        response.raise_for_status()
  
        data = response.json()
        ##print (json.dumps(data,indent=4))
        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return channel_playlistId  
    except req.exceptions.RequestException as e:     
        raise e

def get_videos_ids(playlistId):
    video_ids =[]
    pageToken = None
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAXRESULTS}&playlistId={playlistId}&key={API_KEY}'    
    try:
        while True:
            url = base_url
            if pageToken:
                url += f"&pageToken={pageToken}"
            
            response = req.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items',[]):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            pageToken = data.get('nextPageToken')
            
            if not pageToken:
                
                break
        return video_ids
    except req.exceptions.RequestException as e:
        raise e

    
def batch_list(video_id_list,batch_size):
    for video_id in range(0,len(video_id_list),batch_size):
        yield video_id_list[video_id:video_id + batch_size]

    

def extract_video_data(video_ids):

    extrated_data = []

    def batch_list(video_id_list,batch_size):
        for video_id in range(0,len(video_id_list),batch_size):
                yield video_id_list[video_id:video_id + batch_size]

             
    try:
        for batch in batch_list( video_ids,MAXRESULTS):
            video_ids_str = ",".join(batch)
            url_ext = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}'
            response = req.get(url_ext)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('items',[]):
                video_id = item['id']
                snippet= item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']


                video_data ={
                    "video_id": video_id,
                    "title": snippet['title'],
                    "published_at": snippet['publishedAt'],
                    "duration": contentDetails['duration'],
                    "view_count":statistics.get('viewCount',None),
                    "like_count":statistics.get('likeCount',None),
                    "comment_count":statistics.get('commentCount',None)
                }

                extrated_data.append(video_data)
        
        return extrated_data
    
    except req.exceptions.RequestException as e:
        raise e

def save_to_json(extrated_data):
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"YT_data_{date.today()}.json")

    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extrated_data, json_outfile, indent=4, ensure_ascii=False)
        
if __name__ == "__main__":
    playlist_id = get_playlist_id()
    video_ids= get_videos_ids(playlist_id)
    video_data =extract_video_data(video_ids)
    save_to_json(video_data)

