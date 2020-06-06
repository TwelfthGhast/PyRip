import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriveropts import CHROME_OPTIONS
from tld import get_tld

log = logging.getLogger(__name__)

def importer(url):
    log.debug(f"Importer loaded: {url}")
    album_parser(url)

def album_parser(url):
    with webdriver.Chrome(chrome_options=CHROME_OPTIONS) as driver:
        driver.get(url)
        driver.implicitly_wait(1000)
        image_urls = set()
        # get initial loaded images
        soup = BeautifulSoup(driver.page_source, "lxml")
        post_images = soup.find_all("img", attrs={
            "class" : "post-image-placeholder"
        })
        for image in post_images:
            image_urls.add(image['src'][2:])
        # note imgur dynamically loads and removes images as page is scrolled
        # simulate scrolling
        iternum = 0
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_length = 200
        while iternum * scroll_length < page_height:
            driver.execute_script(f"window.scrollTo({iternum * scroll_length}, {(iternum + 1) * scroll_length})")
            iternum += 1
            # get loaded images
            soup = BeautifulSoup(driver.page_source, "lxml")
            post_images = soup.find_all("img", attrs={
                "class" : "post-image-placeholder"
            })
            for image in post_images:
                image_urls.add(image['src'][2:])
        from dl import requests_stream, wrapper
        for i in image_urls:
            wrapper(requests_stream, {
                "url" : i,
                "folder" : url.split(get_tld(url, as_object=True).fld)[-1][1:].replace("/","."),
                "fname" : i.split("/")[-1]
            })