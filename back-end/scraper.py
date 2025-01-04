import requests
import time
import json
import bisect
from datetime import datetime
import pytz

url = "https://graphql.anilist.co"

query = """
query ($name: String) {
  Media(search: $name, type: ANIME, status: RELEASING) {
    id
    title {
      romaji
      english
    }
    airingSchedule {
      edges {
        node {
          episode
          airingAt
        }
      }
    }
  }
}
"""

def get_release_times(anime_title, time_zone):
    variables = {
        "name": anime_title
    }
    
    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()
    
    
    if 'data' in data and data['data']['Media']:
        anime = data['data']['Media']
        if anime['title']['english'] is not None:
            title = anime['title']['english']
        else:
            title = anime['title']['romaji']
        airing_schedule = anime['airingSchedule']['edges']

        
        airing_times = [schedule['node']['airingAt'] for schedule in airing_schedule]
        episodes = [schedule['node']['episode'] for schedule in airing_schedule]
        index = find_first_unreleased(airing_times)

        print(f"Anime: {title}")
        print("Airing Schedule:")
        for i in range(index, len(airing_schedule)):
            episode = episodes[i]
            airing_time = airing_times[i]
            print(f"Episode {episode} airs at {convert_time_zone(airing_time, time_zone)}.")
    else:
        print("No currently airing anime found with that name.")


def find_first_unreleased(airing_times):
    current_time = time.time()
    index = bisect.bisect_left(airing_times, current_time)    
    return index


def convert_time_zone(timestamp, time_zone):
    utc_time = datetime.fromtimestamp(timestamp, tz = pytz.UTC)
    converted_time = utc_time.astimezone(pytz.timezone(time_zone))
    return converted_time.strftime('%Y-%m-%d %H:%M')
