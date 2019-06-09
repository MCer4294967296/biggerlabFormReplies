import requests

def shorten(URL):
    if URL == "":
        return ""
    service = "https://tinyurl.com/api-create.php"
    return requests.get(url=service, params={"url" : URL}).text