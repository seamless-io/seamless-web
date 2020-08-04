import requests


def read_news():
    res = requests.get('https://en.wikipedia.org/wiki/List_of_news_media_APIs')
    for line in res.content:
        print(line)
    return "Everything is alright"
