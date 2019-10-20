import requests
import sys
import os
from multiprocessing.dummy import Pool as ThreadPool


def main():
    target_path = get_target_path()

    for page in range(1, 50):
        response = query_ffz(page, "")
        enqueue_emoticons(response.get_emoticons(), target_path)
        if response.get_num_pages() < page + 1:
            break


def get_target_path():
    if len(sys.argv) < 2:
        print("you should pass the target directory in the commandline arguments!")
        exit(1)

    target_path = sys.argv[1]

    if not os.path.exists(target_path):
        if os.path.exists(os.getcwd() + '/' + target_path):
            target_path = os.getcwd() + '/' + target_path
        else:
            print("passed argument is not a valid path!")
            exit(1)

    return target_path


def query_ffz(page, query):
    url = "https://api.frankerfacez.com/v1/emoticons?_scheme=https"
    url += "&page=" + str(page)
    url += "&q=" + query
    url += "&sort=count-desc"

    response = requests.get(url)

    if response.status_code != 200:
        print("Got bad response from frankerfacez")
        exit(1)

    json = response.json()
    num_pages = json['_pages']
    emoticons = emoticon_json_to_emoticon_object_array(json['emoticons'])

    print("Loading: " + url)

    return FFZQueryResponse(num_pages, emoticons)


def emoticon_json_to_emoticon_object_array(json):
    emoticons = []

    for emoticon in json:
        emoticons.append(Emoticon("https:" + emoticon["urls"]["1"], emoticon["name"]))

    return emoticons


def enqueue_emoticons(emoticons, target_path):
    pool = ThreadPool(10)
    pool.map(download_emoticon, zip(emoticons, [target_path] * len(emoticons)))
    pool.close()
    pool.join()


def download_emoticon(data):
    emoticon = data[0]
    target_path = data[1]

    response = requests.get(emoticon.get_url())

    ext = emoticon.get_url().rsplit('/', 1)[1].rsplit('.', 1)[1].lower()
    target_file_name = emoticon.get_name() + '.' + ext
    target_file_path = target_path + '/' + target_file_name

    file = open(target_file_path, 'wb')
    file.write(response.content)

    print("DOWNLOADED: " + target_file_path)

    file.close()


class Emoticon:
    def __init__(self, url, name):
        self._url = url
        self._name = name

    def get_url(self):
        return self._url

    def get_name(self):
        return self._name

    def __str__(self):
        return self._name + ' ' + self._url


class FFZQueryResponse:
    def __init__(self, num_pages, emoticons):
        self._num_pages = num_pages
        self._emoticons = emoticons

    def get_num_pages(self):
        return self._num_pages

    def get_emoticons(self):
        return self._emoticons


if __name__ == "__main__":
    # execute only if run as a script
    main()
