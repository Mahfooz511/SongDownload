#!/usr/bin/python3
import requests
import os
from bs4 import BeautifulSoup
from pprint import pprint
import sys
import validators

###
# This program works with sites  :
#    https://pagalnew.com
#    https://pagalsong.in
#    https://www.pagalworld.ws
###


def dir_create(directory):
    # Path
    mypath = os.path.join(os.getcwd(), directory)
    if not os.path.exists(mypath):
        os.mkdir(mypath)
    return mypath


def get_name(data):
    count = 1
    for ultag in data.find_all('ul', {'class': 'breadcrumb'}):
        for litag in ultag.find_all('li'):
            # print(litag.text)
            name = litag.text
    # Check if 'name' variable is created
    if 'name' in vars():
        return name
    else:
        print("Check the page. Something looks wrong.")
        exit()


def download_mp3(destination, filename, url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    response = requests.get(url, headers=headers)
    with open(destination+'\\'+filename+'.mp3', 'wb') as mp3:
        mp3.write(response.content)


def download_songs(dir_name, site_name, song_url_list):
    #print("dir_name, site_name, song_url_list  ---->" , dir_name, site_name, song_url_list )
    for song, song_item in song_url_list.items():
        # song_item -> {'Dance Ka Bhoot - Brahmastra Mp3': ['/download128/32737', '/download320/32737'] }
        download320_exist = False
        download_url = ""
        # first try to get url for 320kbps
        for res in song_url_list[song]:
            if site_name == 'https://pagalsong.in':
                if '320 KBPS' in res:
                    download_url = res
            if site_name == 'https://www.pagalworld.ws':
                if not 'variation/190K' in res:
                    download_url = res
            if 'download320' in res:
                download_url = site_name + res
        # if 320kbps is not found then whatever first is available (usually 128kbps)
        if site_name == 'https://pagalsong.in' and  download_url == "":
            for res in song_item:
                download_url = res
                break
        if site_name == 'https://www.pagalworld.ws' and download_url == "":
            for res in song_item:
                download_url = res
                break
        if download_url == "":
            for res in song_item:
                download_url = site_name + res
                break
        song = song.replace(" Mp3", "")
        print("Downloading... => ", song)
        # print(dir_name, "#", song, download_url)
        download_mp3(dir_name, song, download_url)


#######################################################################
#  Main
#
if len(sys.argv) <= 1:
    url = input("Please enter the URL: ")
else:
    url = sys.argv[1]

if url in ["-h", "--help"]:
    print("Usage: ", sys.argv[0], " URL")
    exit()
if not validators.url(url):
    print("Please enter a valid URL. Ex. https://pagalnew.com/album/gully-boy-2019.html")
    exit()

# ex. https://pagalnew.com
site_name = "/".join(url.split('/')[0:3])

data = requests.get(url)

html = BeautifulSoup(data.text, 'html.parser')

# Find the Album name
album = get_name(html)

# check if directory with Album name exist. If not then create
album = album.replace(" Mp3 Songs", "")
print("Found Album -> ", album)
dir_name = dir_create(album)

# now make song list of the Album
song_list = []
# Below for loop works for - https://pagalnew.com
for song_box in html.find_all(attrs={"class": "main_page_category_music"}):
    a_tag = song_box.find('a', href=True)
    song_list.append(a_tag['href'])

if site_name in ['https://pagalsong.in'] :
    for song_box in html.find_all(attrs={"class": "listbox"}):
        a_tag = song_box.find('a', href=True)        
        song_list.append(a_tag['href'])

if site_name in ['https://www.pagalworld.ws' ] :
    for song_box_list in html.find_all(attrs={"class": "files-list"}):
        for song_box in song_box_list.find_all(attrs={"class": "listbox"}):
            a_tag = song_box.find('a', href=True)
            if site_name == 'https://www.pagalworld.ws':
                a_tag = a_tag 
            song_list.append('https://www.pagalworld.ws' +  a_tag['href'])


# from each page of the song download the song
resolution_list = []
song_url_list = {}

for song_url in song_list:
    songdata = requests.get(song_url)
    soup = BeautifulSoup(songdata.text, 'html.parser')
    song_name = get_name(soup)
    song_url_list[song_name] = []
    for song_resolution in soup.find_all(attrs={"class": "dbutton"}):
        song_url_list[song_name].append(song_resolution['href'])

# Download the song
download_songs(dir_name, site_name, song_url_list)


# All done
print("Check directory ->", dir_name)
