# Image parser  by Aleksandr Pustovit 03.09.2017
# The program accepts URl address including protocol.
# Program downloads images (jpg, gif, png).
# Links of the images are stored in a file URLlist.txt
# Folder for storing pictures and URLlist.txt is projects/site-name

import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def make_dir(sitename):
    """Creates a directory and returns a path """
    path = "projects/" + sitename + "/"
    i=0
    if os.path.exists(path):
        result = True
        while result:
            i += 1
            newname = sitename + '(%d)' % i
            path = "projects/" + newname + "/"
            if not os.path.exists(path):
                os.makedirs(path)
                result = False

    else:
        os.makedirs(path)

    return path


def get_html(url):
    """Creates connection to server if connection is ok returns content, if not returns false """
    headers = {'user-agent': '"Mozilla/5.0 (Windows NT 6.1; Win64; x64) Chrome/60.0.3112.113 Safari/537.36"'}
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.RequestException as err:
        print("Something go wrong, error text below")
        print(err)
        return False
    return r.content


def get_full_img_url(imgsrc, sitename):
    """Checks that it is an image and creates full link to image.
     Returns a link if it is ok,
     otherwise returns false"""
    if imgsrc[len(imgsrc)-3: len(imgsrc)].lower() in "jpg gif png":

        if imgsrc[0:2] == "//":
            path = 'http:' + imgsrc
        elif imgsrc[0] == "/":
            path = sitename + imgsrc
        elif imgsrc[0:7] == "http://" or imgsrc[0:8] == "https://":
            path = imgsrc
        elif imgsrc[0:3] == "www.":
            path = 'http://' + imgsrc
        else:
            path = sitename + "/" + imgsrc
        return path
    else:
        return False


def take_name(inputname):
    """Returns name of image """
    start = inputname.rfind("/")
    end = len(inputname)
    if start != -1:
        return inputname[start+1:end]
    else:
        return inputname


def save_images(contenthtml, sitepath, sitename):
    """Finds images on website and creates a file list url.
        Returns amount of saved photos and quantity of errors """
    soup = BeautifulSoup(contenthtml, 'lxml')
    file_list = []
    count_photos = 0
    err = 0
    folder = ''
    for images in soup.find_all('img'):
        images_src = images.get('src')

        if images_src:
            img_full_url = get_full_img_url(images_src, sitepath)
            img_name = take_name(images_src)
            if img_full_url:
                file_list.append(img_full_url)
                p = get_html(img_full_url)
                if p:
                    count_photos += 1
                    if count_photos == 1:
                        folder = make_dir(sitename)
                    try:
                        out = open(folder + img_name, "wb")
                    except OSError:
                        err += 1
                        continue

                    print('|{0:^4}|{1:^33}|{2:^10}|'.format(count_photos, img_name, "Downloaded"))
                    out.write(p)
                    out.close()
                else:
                    err += 1
    if count_photos > 0:
        f = open(folder + "URLList.txt", 'w')
        for index in file_list:
            f.write(index + '\n')
        f.close()

    return count_photos, err, folder


def main(list_obj):
        url = list_obj
        allpage = get_html(url)
        if allpage:
            o = urlparse(url)
            sitepath = o.scheme + "://" + o.netloc
            sitename = o.netloc
            # folder = make_dir(sitename)
            print("Connection ok, start parsing")
            print("-"*51)
            print('|{0:^4}|{1:^33}|{2:^10}|'.format("№", "Name of the image", "Status"))
            print("-" * 51)
            count_photos, err, folder = save_images(allpage, sitepath, sitename)
            print("-" * 51)
            if count_photos > 0:
                print("The process is completed. Photos are downloaded  " + str(count_photos) + " Errors " + str(err)
                      +". You can see pictures and URLlist.txt in the folder " + folder)
            else:
                print("No images found")

            input("\n\nPress Enter to exit.")


if __name__ == '__main__':
    main(input('Copy and paste address of the site from the browser:>'))
