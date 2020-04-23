import urllib.request, urllib.error, urllib.parse
import random
import json
from bs4 import BeautifulSoup
import time
from twython import Twython
import shutil
import requests

#Function to check if the site has an image link according to the img_link_regex
def siteHasImage(soup):
    if soup.find("meta", property="og:image"):
        return True
    else:
        return False

#Function to add a certain linkID to a list of pages without images
def addToBlacklist(number):
    blacklisted_linkIDs = json.loads(open('Blacklist.json').read())
    blacklisted_linkIDs.append(number)
    json.dump(blacklisted_linkIDs, open('Blacklist.json', 'w'))

#Checks a number with the blacklist
def isBlacklisted(number):
    blacklisted_linkIDs = json.loads(open('Blacklist.json').read())
    for element in blacklisted_linkIDs:
        if number == element:
            return True
    return False

extracted = [] #Array which contains extracted information from webpage
exitImgFindLoop = False #Boolean to track if the program should stop searching
findValidLink = True #Boolean which keeps track of whether or not to stop searching for a valid URL

#Twitter account authentification
API_key = ''
API_secret_key = ''
Access_token = ''
Access_token_secret = ''
ArtEveryHour = Twython(API_key, API_secret_key, Access_token, Access_token_secret)

while not exitImgFindLoop:
    #Build link and catch 404 errors
    findValidLink = True
    linkID = random.randint(0, 100000)
    while isBlacklisted(linkID):
        linkID = random.randint(0, 100000)

    while findValidLink:
        link = 'https://www.nga.gov/collection/art-object-page.%d.html' %(linkID)
        try:
            raw = urllib.request.urlopen(link).read()
            findValidLink = False
        except:
            addToBlacklist(linkID)
            linkID = random.randint(0, 100000)
            while isBlacklisted(linkID):
                linkID = random.randint(0, 100000)

    soupLink = BeautifulSoup(raw, "lxml")

    if siteHasImage(soupLink):
        title = soupLink.find("meta", property="og:title")
        artist = soupLink.find("meta", property="og:description")
        img_link = soupLink.find("meta", property="og:image")
        extracted.append(title["content"])
        extracted.append(artist["content"])
        extracted.append(img_link["content"])
        exitImgFindLoop = True
    else:
        addToBlacklist(linkID)
        linkID = random.randint(0, 100000)
        while isBlacklisted(linkID):
            linkID = random.randint(0, 100000)

    time.sleep(2) #To prevent NGA servers from thinking something is up

#Download image to be sent
image_stream = requests.get(extracted[2], stream=True)
time.sleep(20)
local_image = open('localImage.jpg', 'wb')
time.sleep(5)
image_stream.decode_content = True
shutil.copyfileobj(image_stream.raw, local_image)
time.sleep(20)

#Send Tweet
artPhoto = open('localImage.jpg', 'rb')
time.sleep(5) #To allow image time to be completely opened
response = ArtEveryHour.upload_media(media=artPhoto)
time.sleep(5) #To allow image time to load onto Twitter
ArtEveryHour.update_status(status='%s, %s.\n%s'%(extracted[1], extracted[0], link), media_ids=[response['media_id']])
