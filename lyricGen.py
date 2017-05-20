import sys
import codecs
import time
import math
import nltk
import random
import requests
from bs4 import BeautifulSoup


BASE_URL = "http://api.genius.com"
PAGE_URL = "http://genius.com"
headers = {'Authorization': 'Bearer qK6Ma2I4_LRiYGEWm0h8HA_oSD90SYZgGPFbAwaZucBr15NZ6pcIdEtACYmxPki6'}

def getVerifiedArtists():
    vArtistUrl = PAGE_URL + "/verified-artists?"
    page = requests.get(vArtistUrl)
    html = BeautifulSoup(page.text, "html.parser")
    results = []

    for userDetails in html.find_all("div"):
        if userDetails.has_attr("class") and "user_details" in userDetails["class"]:
            href = userDetails.a['href']
            print href
            artist = str(href)[href.rfind("/") + 1:]
            results.append(artist)
            print "\t" + artist

    return results


def getSongsForArtist(artist):
    print ("Getting songs for: " + artist)
    searchUrl = BASE_URL + "/search?q="
    page = 0
    data = {'q': artist}
    response = requests.get(searchUrl + artist, headers=headers)
    
    json = response.json()
    songList = []
    
    while len(json["response"]["hits"]) > 1:
        print ("Getting page " + str(page) + " for artist " + artist)
        songList.extend(json["response"]["hits"])
        page += 1
        data['page'] = str(page)
        response = requests.get(searchUrl, data=data, headers=headers)
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
  return lyrics

if __name__ == "__main__":
    print ("Grabbing list of verified artists...")
    vArtists = getVerifiedArtists()

    songList = []
    for artist in vArtists:
        songList.extend(getSongsForArtist(artist))

    numWritten = 0
    for song in songList:
        lyrics = lyricsFromSongPath(song["result"]["api_path"])

        print ("Writing song " + song["result"]["title"] + " to file... [" + numWritten + "]")
        with codecs.open("lyrics-" + song["result"]["title"], 'w', 'cp437') as output:
            output.write(lyrics)

        numWritten += 1
        output.close()
        

