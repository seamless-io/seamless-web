import requests


def main():
    res = requests.get('https://en.wikipedia.org/wiki/List_of_news_media_APIs')
    print(res.text)
    return "Everything is alright"


if __name__ == '__main__':
    main()
