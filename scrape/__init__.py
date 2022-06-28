#!/usr/bin/env python3
"""Web Image Scaper"""

from bs4 import *
from io import BytesIO
from PIL import Image
import requests
import os
import re
import base64

__author__ = "Jason Rebuck"
__copyright__ = "2022"
__version__ = "0.15"

HEADERS = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
"Accept-Encoding": "gzip, deflate", 
"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
}

ROOT_FOLDER = os.path.expanduser("~/Desktop/scrape")
INFO_FILE = "INFO.txt"
TAGS = {"div" : ("style",), "source": ("src",), "img" : ("data-lazyload", "data-srcset", "data-src", "src"),}

## FIXES
def image_fix(img, url):
    """Fix partial urls"""
    #TEST test_image_fix
    if not img: return ""
    if img.startswith("data"):
        return img
    if not img.startswith("http"):
        if img.startswith("//"):
            img = f'http://{img.lstrip("/")}'
        elif img.startswith("/"):
            img = f'{url.rstrip("/")}{img}'
        else:
            img = f'{url.rstrip("/")}/{img.lstrip("/")}'
    return img.split("?")[0]

def string_fix(string):
    #TEST test_string_fix
    """Remove special chars"""
    return re.sub('[^a-zA-Z0-9]', '_', string)

def http_fix(url):
    #TEST test_http_fix
    """"Make sure url has http"""
    if not url: return ""
    return f"http://{url}" if not url.startswith("http") else url.replace("https://", "http://")

## MAKE NAMES and FOLDERS
def make_img_name(name):
    """Make sure image name is unique."""
    if os.path.isfile(name):
        try:
            file_name, file_ext = os.path.splitext(name)
            for counter in range(1, 200):
                name = f"{file_name}.{counter:02}{file_ext}"
                if not os.path.isfile(name): break
        except:
            pass
    return name

def make_folder(name):
    """Make URL image folder"""
    folder = os.path.join(ROOT_FOLDER, string_fix(name))
    if not os.path.isdir(folder): os.makedirs(folder)
    return folder

## GET PATHS
def get_paths(url):
    """Download html from url and find urls"""
    url = http_fix(url)
    try:
        soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=10).text, "html.parser")
    except:
        print("\t-XX- ERROR GETTING URL", url)
        return []
    return search_tags(soup, url)

def find_attr_url(string):
    """Find background-image url in style"""
    #TEST test_find_attr_url
    for part in string.split(";"):
        if "background-image" in part:
            img = re.findall("\([\"']?(.*?)[\"']?\)", part)
            return img[0] if img else ""
    return ""

def search_tags(soup, url):
    """Search html for tags and grab paths"""
    #TEST test_search_tags
    paths = []
    for tag in TAGS:
        for image in soup.findAll(tag):
            for attr in TAGS[tag]:
                img = image.get(attr)
                if not img: continue
                if attr == "style":
                    img = find_attr_url(img)
                paths.append(image_fix(img, url))
    return [p for p in paths if p]

## SAVE FILES
def save_info(info, images, folder):
    """Save key value pairs in a file"""
    try:
        with open(os.path.join(folder, INFO_FILE), "w") as f:
            f.write("\nImages:\n")
            for i, img in enumerate(images, 1):
                f.write(f'{i:02})\t{img}\n')
    except:
        print("\t-XX- ERROR SAVING INFO", folder)

def save_image_data(data, folder):
    """Save base64 Images"""
    ext = re.search("^data:image\/([a-z]{3,4})", data)[1]
    if ext:
        img_data = re.sub('^data:image/.+;base64,', '', data)
        img = Image.open(BytesIO(base64.b64decode(img_data)))
        img.save(make_img_name(os.path.join(folder, f"data_image.{ext}")), \
                ext.replace("jpg", "jpeg").upper())

def save_image_contents(img, folder):
    contents = requests.get(img, headers=HEADERS, timeout=10).content
    with open(make_img_name(os.path.join(folder, os.path.basename(img))), "wb+") as f:
        f.write(contents)

## MAIN LOOPS
def download_images(images, folder):
    """Download and save images paths"""
    ok = 0
    for i, img in enumerate(images, 1):
        if not img: continue
        try:
            if img.startswith("data:"):
                save_image_data(img, folder)
            else:
                save_image_contents(img, folder)
                ok += 1
            print(f"\t---- {i:02}) {img[:150]}")
        except KeyboardInterrupt:
            exit()
        except:
            print(f"\t-XX- {i:02}) {img[:150]} (FAILED)")
    print(f"\t{ok}/{len(images)} Images Downloaded")

def loop_urls(urls):
    """Loop list of url info"""
    print()
    print(f'--- Starting {len(urls)} Item(s) ---')
    print()
    for i, url in enumerate(urls, 1):
        print("+", url, f'[{i} of {len(urls)}]')
        images = get_paths(url)
        folder = make_folder(url)
        save_info(url, images, folder)
        download_images(images, folder)
        print()

