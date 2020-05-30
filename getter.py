import requests
import json
import os
import sys
from PIL import Image
from io import BytesIO
import time
import random

#working directory where you want to store your wallpapers
workingDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



#check if there is a wallpaper folder and saved urls 
def check_directory():
    if "backgrounds" not in os.listdir(workingDir):
        os.mkdir(os.path.join(workingDir,'backgrounds'))   
    if "downloaded.txt" not in os.listdir(workingDir):
        f = open(os.path.join(workingDir,'downloaded.txt'),"a+")
        f.close()


#check if requires a specific number of wallpapers
def check_input():
    if len(sys.argv) != 1:
        try:
            numPic = int(sys.argv[1])
        except TypeError:
            print("only int accepted as number of wallpapers to take down")
            sys.exit(1)

#return picture format
def return_format(url):
    f = url[-10:len(url)].split(".")[1].lower()
    if f == "jpg":
        return "jpeg"
    elif f == "png":
        return "png" 

#clean title of bad characters
def clean_title(title):
    invalidChars = ["\"","?","!",".","@","|",","]
    newString = []
    for letter in title:
        if letter == " ":
            newString.append("_")

        elif letter not in invalidChars:
            newString.append(letter)
    if len(newString) > 20:
        return "".join(newString[-20:len(newString)-1:])
    return "".join(newString)

#check if already downloaded
def is_unique(url):
    if url not in downloaded:
        return True
    else:
        return False

#get request for top posts 
def get_top(url):

    r = requests.get(url,headers={'User-agent':'myobot'})

    if not r:
        print("error in the request")
        sys.exit()

    data = r.json()
    return data

#populate dictinary with title and url
def extract_data(inputDict,raw):
    for img in raw['data']['children']:
        if img['data']['url'] not in list(inputDict.values()):
            inputDict[clean_title(img['data']['title'])] = img['data']['url']
    return inputDict

#return Image object
def download_pic(url):
    resp = requests.get(url)
    return Image.open(BytesIO(resp.content))

#write url for no repeats
def log_url(url):
    with open(workingDir + "\downloaded.txt","a+") as d:
        d.write(url+"\n")


#return list of downloaded urls 
def retrieve_downloaded():
    temp =[]
    
    with open(os.path.join(workingDir,'downloaded.txt',"r+") as d:
        for line in d:
            line = line.strip()
            temp.append(line)
    return temp

#check internet, up to 5 minutes
def wait_for_internet(timeout):
    for i in range(timeout):
        r = requests.get("http://google.com")
        if r:
            return True
        else:
            time.sleep(30)
    print("request timed out")
    return False


#main

if __name__ == "__main__":

    urls = ["https://www.reddit.com/r/wallpaper/.json?count=25?sort=new","https://www.reddit.com/r/wallpaper/.json?count=25?sort=hot","https://www.reddit.com/r/wallpaper/.json?count=25?sort=top"]

    if not wait_for_internet(5):
        print("Internet connection: NOT OKIE DOKIE")
        sys.exit(1)
    else:
        print("internet connection: OK")



    if len(sys.argv) == 2:

        if sys.argv[1] == "set":
            wallpapers = os.listdir("backgrounds")
            wall = wallpapers[random.randint(0,len(wallpapers))]

            path = os.path.join(os.path.abspath("."),"backgrounds",wall)

            os.system("gsettings set org.gnome.desktop.background picture-uri file:'{}'".format(path))
            sys.exit()
    #get input and check dirs
    check_input()
    check_directory()

    #get already downloaded urls
    downloaded = retrieve_downloaded()
    
    #retrieve top 50
    '''
    for url in urls:
        raw = get_top(url)
        print(extract_data(imageUrls,raw))

    '''
    raw = get_top(urls[0])
    imageUrls = extract_data({},raw)

    print("{} images found".format(len(imageUrls)))
    
    #go over each image, if it exists skip, if it doesnt download
    for title,url in imageUrls.items():

        if is_unique(url):
            print(title)
            log_url(url)
            image = download_pic(url) 
            image.save(workingDir + "\\backgrounds/{}.{}".format(title,return_format(url)),format=return_format(url))
    

