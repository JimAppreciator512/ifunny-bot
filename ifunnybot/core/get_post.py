import requests
from typing import Union
from bs4 import BeautifulSoup as soup

from ifunnybot.data import Headers
from ifunnybot.types import Post, PostType
from ifunnybot.utils import get_datatype, html_selectors

# TODO: refactor this to Optional[Post]?
def get_post(url: str, _headers=Headers) -> Union[Post, str]:

    # getting the post, assuming that it is a proper link
    response = requests.get(url, headers=_headers, allow_redirects=False)

    # testing the response code
    if response.status_code != requests.codes.ok:
        # do something here
        return f"There was an error making the HTTP request to {url}"

    # transforming the response into something useable
    dom = soup(response.text, "html.parser")
    if not dom.css:
        return f"There was an internal error with BeautifulSoup, cannot use CSS selectors"

    ## the response was OK, now scraping information
    info = Post()

    # saving the url
    info.url = url

    # getting the datatype of the url
    datatype = get_datatype(url)
    if not datatype:
        # do something here
        return f"Could not find any content at {url}."
    print(f"Found {datatype} at {url}")

    # setting the data type of the post
    info.post_type = datatype

    # the targeted HTML element
    element = None

    ## getting the content of the post
    if info.post_type != PostType.MEME:
        # getting selectors & attributes
        selector, attribute = html_selectors[info.post_type]

        # using BeautifulSoup to get what I want
        element = dom.css.select(selector)
        if not element:
            return f"Could not grab the content from {url}"
        info.content_url = element[0].get(attribute)
    else:
        # need to iterate through all the selectors to find the proper
        # one because ifunny lol
        for _type in html_selectors.keys():
            ## searching for the right one

            # getting selectors & attributes
            selector, attribute = html_selectors[_type]

            # using BeautifulSoup to get what I want
            element = dom.css.select(selector)
            if not element:
                print(f"Post at {url} is not {_type}")
                continue

            
            print(f"Post at {url} is {_type}")
            info.post_type = _type
            info.content_url = element[0].get(attribute)
            break

    ## scraping other info about the post
    info.op = dom.css.select("div._9JPE > a.WiQc > span.IfB6")[0].text.replace(" ", "")
    info.icon_url = dom.css.select("div._9JPE > a.WiQc > img.dLxH")[0].get("data-src")
    info.likes = dom.css.select("div._9JPE > button.Cgfc > span.Y2eM > span")[0].text
    info.comments = dom.css.select("div._9JPE > button.Cgfc > span.Y2eM > span")[1].text

    # returning the collected information
    return info

