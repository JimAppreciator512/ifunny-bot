from bs4 import BeautifulSoup as soup
import requests
import pickle

from .post import Post
from ..utils.utils import *

# reading in headers
headers = None
with open("headers.pickle", "rb") as fd:
    headers = pickle.load(fd)

def get_post(url: str):

    # getting the post, assuming that it is a proper link
    response = requests.get(url, headers=headers, allow_redirects=False)

    # testing the response code
    if response.status_code != requests.codes.ok:
        # do something here
        return

    # transforming the response into something useable

    ## the response was OK, now scraping information
    info = Post()

    # getting the datatype of the url
    datatype = iFunnyDatatype(url)
    if not datatype:
        # do something here
        return

    # setting the data type of the post
    info.post_type = datatype

    ## getting the content of the post
    if info.post_type != PostType.MEME:
        # getting selectors & attributes
        selector, attribute = html_selectors[info.post_type]

        # using BeautifulSoup to get what I want

    return Post()

