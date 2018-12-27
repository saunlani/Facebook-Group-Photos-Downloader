from PIL import Image
import os
import time
import urllib.request
import requests
import configparser
import datetime


config = configparser.ConfigParser()
config.read('config.ini')
page_counter = 0
this_dict = {}

histogram_check = config.get('main', 'histogram_check')

files = []

apiRequest = requests.get("https://graph.facebook.com/"
                          + config.get('main', 'api_version')
                          + "/" + config.get('main', 'group_number')
                          + "/feed?fields=created_time,from,full_picture,message,link,updated_time,type&limit="
                          + config.get('main', 'results_limit')
                          + "&access_token="
                          + config.get('main', 'access_token'))

next_page_link = ""


def get_all_files_in_folder():
    file_list = os.listdir(config.get('main', 'download_folder'))
    for file in file_list:
        files.append(file)


def print_files_in_folder():
    for x in files:
        print(x)
    print(len(files))


def compare_one_image_to_folder(image, path):
    filecount = 0
    for x in files:
        filecount = filecount + 1
        print(str(filecount))
        image_similarity(image, path + x)
    print(len(files))


def compare_one_image_to_another_image(x, y):
        image_similarity(x, y)


def download_image(imgurl, imgid):
    urllib.request.urlretrieve(imgurl, config.get('main', 'download_folder')+imgid)
    if histogram_check == 'true':
        compare_one_image_to_folder((config.get('main', 'download_folder')+imgid),
                                    config.get('main', 'download_folder'))



def get_file_array_from_folder():
    file_array = os.listdir(config.get('main', 'download_folder'))
    return file_array


def get_next_page_link():
    global next_page_link
    next_page_link = (apiRequest.json()['paging']['next'])
    return next_page_link


def get_page_results():
    limit = int(config.get('main', 'results_limit'))
    for x in range(0, limit, 1):
        if 'full_picture' in apiRequest.json()['data'][x] and apiRequest.json()['data'][x]['type'] == 'photo':
            if apiRequest.json()['data'][x]['id'] + ".jpg" in files:
                print('file already exists')
            elif apiRequest.json()['data'][x]['id'] + ".jpeg" in files:
                print('file already exists')
            elif apiRequest.json()['data'][x]['id'] + ".png" in files:
                print('file already exists')
            else:
                image_link = apiRequest.json()['data'][x]['full_picture']
                img_id = apiRequest.json()['data'][x]['id']
                image_ext = ".jpg"
                image_name = img_id + image_ext
                download_image(image_link, image_name)
    global page_counter
    page_counter += 1


def set_request_for_next_page():
    global apiRequest
    apiRequest = requests.get(next_page_link)


def get_multiple_pages():
    global page_counter
    pages_desired = int(config.get('main', 'pages_desired'))
    while page_counter < pages_desired:
        print("page " + str(page_counter))
        get_page_results()
        get_next_page_link()
        set_request_for_next_page()
    print(str(page_counter) + " pages printed")


files = get_file_array_from_folder()


def image_similarity(image1_filepath, image2_filepath):
    sim_list = begin_similarty_compare(image1_filepath, image2_filepath)
    return sim_list


def begin_similarty_compare(image_filepath1, image_filepath2):
    t1 = time.time()

    similarity = image_similarity_histogram_via_pil(image_filepath1, image_filepath2)
    similarity_histogram_via_pil = similarity

    duration = "%0.1f" % ((time.time() - t1) * 1000)
    print("DEBUG image_similarity: histogram_via_pil => %s took %s ms" % (similarity, duration))
    if similarity < 22:
        with open('duplicate-log.txt', encoding='utf-8', mode='a') as file:
            file.write(str(datetime.datetime.now()) + ' - POTENTIAL DUPLICATE: ' + image_filepath1 + ' &&& ' +
                       image_filepath2 + " Similarity: " + str(similarity) + '\n')

    return similarity_histogram_via_pil


def image_similarity_histogram_via_pil(filepath1, filepath2):
    from PIL import Image
    import math
    import operator
    from functools import reduce

    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)

    image1 = get_thumbnail(image1)
    image2 = get_thumbnail(image2)

    h1 = image1.histogram()
    h2 = image2.histogram()

    rms = math.sqrt(reduce(operator.add, list(map(lambda a, b: (a - b) ** 2, h1, h2))) / len(h1))
    return rms


def get_thumbnail(image, size=(128, 128), stretch_to_fit=False, greyscale=False):
    if not stretch_to_fit:
        image.thumbnail(size, Image.ANTIALIAS)
    else:
        image = image.resize(size);  # for faster computation
    if greyscale:
        image = image.convert("L")  # Convert it to grayscale.
    return image


get_multiple_pages()

