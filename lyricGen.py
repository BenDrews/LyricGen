import sys
import codecs
import time
import math
import nltk
import re
import random
import requests
from bs4 import BeautifulSoup


BASE_URL = "http://api.genius.com"
PAGE_URL = "http://genius.com"
headers = {'Authorization': 'Bearer qK6Ma2I4_LRiYGEWm0h8HA_oSD90SYZgGPFbAwaZucBr15NZ6pcIdEtACYmxPki6'}

def clean(lyrics):
    results = []
    for line in lyrics.split("\n"):
        if '[' not in line and ']' not in line and len(line)>0:
            line = re.sub('([,!?:;()\"\-])', r' \1 ', line)
            line = re.sub('\s{2,}', ' ', line)
            results.append(line.strip().lower())

    return results

def getArtists():
    artistUrl = PAGE_URL + "/verified-artists?"
    page = requests.get(artistUrl)
    html = BeautifulSoup(page.text, "html.parser")
    results = []

    for userDetails in html.find_all("div"):
        if userDetails.has_attr("class") and "user_details" in userDetails["class"]:
            href = userDetails.a['href']
            # Split CamelCase into spaces
            artist = str(href)[href.rfind("/") + 1:]
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', artist)
            artist = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
            results.append(artist)

    return results


def getSongsForArtist(artist):
    print ("Getting songs for: " + artist)
    searchUrl = BASE_URL + "/search?q=" + artist
    page = 0
    response = requests.get(searchUrl, headers=headers)
    
    json = response.json()
    songList = []
    
    while len(json["response"]["hits"]) > 1 and page < 4:
        print ("Getting page " + str(page) + " for artist " + artist)
        songList.extend(json["response"]["hits"])
        page += 1
        response = requests.get(searchUrl + "&page=" + str(page), headers=headers)
        json = response.json()

    return songList


def lyricsFromSongPath(songPath):
  songUrl = BASE_URL + songPath
  response = requests.get(songUrl, headers=headers)
  json = response.json()
  path = json["response"]["song"]["path"]

  #gotta go regular html scraping... come on Genius
  pageUrl = "http://genius.com" + path
  page = requests.get(pageUrl)
  html = BeautifulSoup(page.text, "html.parser")

  #remove script tags that they put in the middle of the lyrics
  [h.extract() for h in html('script')]
  #at least Genius is nice and has a tag called 'lyrics'!
  lyrics = html.find(class_="lyrics").get_text()
  results = clean(lyrics)
  
  return '\n'.join(results)


if __name__ == "__main__":
    print ("Grabbing list of verified artists...")
    artists = getArtists()

    for artist in artists:
        songList = getSongsForArtist(artist)

        for i, song in enumerate(songList):
            lyrics = lyricsFromSongPath(song["result"]["api_path"])
            
            print ("Writing song " + song["result"]["title"] \
                   + " to file... [" + artist + "_" + str(i) + "]")
            with codecs.open("lyrics/" + artist + "_" + str(i), 'w', encoding="utf-8") as output:
                output.write(lyrics)
            output.close()
        
