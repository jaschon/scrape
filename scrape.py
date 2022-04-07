#!/usr/bin/env python3

"""
Web Image Scraper
usage: scrape.py [-h] [--delimiter DELIMITER] [--csv CSV | --url URL [URL ...]]
"""

from bs4 import *
import requests
import os
import argparse
import re

HEADERS = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
"Accept-Encoding": "gzip, deflate", 
"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
"Dnt": "1", 
"Host": "httpbin.org", 
"Upgrade-Insecure-Requests": "1", 
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
}

ROOT_FOLDER = os.path.expanduser("~/Desktop/scrape")
INFO_FILE = "INFO.txt"
TAGS = {"div" : ("style",), "img" : ("data-lazyload", "data-srcset", "data-src", "src"),}

def image_fix(img, url):
    if img and not img.startswith("http"):
        if img.startswith("data:"):
            img = ""
        elif img.startswith("//"):
            img = f'http://{img.lstrip("/")}'
        elif img.startswith("/"):
            img = f'{url.rstrip("/")}{img}'
        else:
            img = f'{url.rstrip("/")}/{img.lstrip("/")}'
    return img

def string_fix(string):
    return re.sub('[^a-zA-Z0-9]', '_', string)

def http_fix(url):
    return f"http://{url}" if not url.startswith("http") else url.replace("https://", "http://")

def find_attr_url(string):
    for part in string.split(";"):
        if "background-image" in part:
            img = re.findall("\([\"']?(.*?)[\"']?\)", part)
            return img[0] if img else ""
    return ""

def make_subfolder_name(info):
    if info.get("first_name"):
        name = f'{info.get("first_name")} {info.get("last_name")}'
    else:
        name = f'{info.get("website")}'
    return string_fix(name)

def make_img_name(name):
    if os.path.isfile(name):
        try:
            file_name, file_ext = os.path.splitext(name)
            for counter in range(1, 100):
                name = f"{file_name}.{counter:02}{file_ext}"
                if not os.path.isfile(name): break
        except:
            pass
    return name

def make_folder(name):
    """Make URL Image Folder"""
    folder = os.path.join(ROOT_FOLDER, string_fix(name))
    if not os.path.isdir(folder): os.makedirs(folder)
    return folder

def get_paths(url):
    """Get a list of Image Src Paths from URL"""
    paths = []
    url = http_fix(url)
    try:
        soup = BeautifulSoup(requests.get(url, HEADERS).text, "html.parser")
    except:
        print("\t-- ERROR GETTING HTML", url)
        return []

    for tag in TAGS:
        for image in soup.findAll(tag):
            for attr in TAGS[tag]:
                img = image.get(attr)
                if not img: continue
                if attr == "style":
                    img = find_attr_url(img)
                paths.append(image_fix(img, url))
    return [p for p in paths if p]

def save_info(info, folder):
    try:
        with open(os.path.join(folder, INFO_FILE), "w") as f:
            for k in info:
                f.write(f'{k}:\t{info.get(k)}\n')
    except:
        print("\t-- ERROR SAVING INFO", folder)

def download_images(images, folder):
    """Download and save images paths"""
    i = 0
    for img in images:
        if not img: continue
        try:
            contents = requests.get(img, HEADERS).content
        except KeyboardInterrupt:
            exit()
        except:
            print("\t  -- ERROR GETTING IMAGE", img)
            continue
        try:
            with open(make_img_name(os.path.join(folder, os.path.basename(img))), "wb+") as f:
                f.write(contents)
                i += 1
        except KeyboardInterrupt:
            exit()
        except:
            print("\t  -- ERROR SAVING IMAGE", img)
    print(f"\t{i}/{len(images)} Images Downloaded")

def loop_urls(urls):
    i = 0
    total = len(urls)
    print()
    print(f'--- Starting {total} Items ---')
    print()
    for url in urls:
        try:
            if not url.get("website"): continue
            i += 1
            name = make_subfolder_name(url)
            print("+", name, f'[{i} of {total}]')
            folder = make_folder(name)
            save_info(url, folder)
            images = get_paths(url.get("website"))
            download_images(images, folder)
            print()
        except KeyboardInterrupt:
            exit()

def get_csv_info(filename, delimiter="\t"):
    """Return Array of Key/Val CSV Rows"""
    info = []
    with open(filename, "r") as f:
        lines = f.readlines()
    if lines:
        keys = [k.strip().lower().replace(" ", "_") for k in lines[0].split(delimiter)]
        for line in lines[1:]:
            info.append({ keys[i]: v.strip() for i, v in enumerate(line.split(delimiter)) })
    return info

def main(parser):
    """Arg logic"""
    args = parser.parse_args()
    if args.url:
        loop_urls([{'website': url} for url in args.url])
    elif args.csv:
        loop_urls(get_csv_info(args.csv, args.delimiter))

def setup_parser():
    """Setup Parser"""
    parser = argparse.ArgumentParser(description="Web Image Scraper")
    parser.add_argument("--delimiter", "-d", \
            help="Change CSV Delimiter. TAB is default.", \
            default="\t", action="store")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--csv", "-c", "--list", "-l", \
            help="Import Website List. NOTE: Needs Columns (first_name, last_name, website)", \
            action="store")
    group.add_argument("--url", "-u", "--website", "-w", \
            help="Scrape One or More Websites", \
            nargs="+", \
            action="store")
    return parser

if __name__ == "__main__":
        main(setup_parser())
