from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriveropts import CHROME_OPTIONS
from bs4 import BeautifulSoup
import logging
import re
from time import sleep

log = logging.getLogger(__name__)

def importer(url):
    # user page
    # format: https://www.douyin.com/share/user/102563642709
    if ".douyin.com/share/user/" in url:
        parse_user(url)
    # video page
    # format: https://www.iesdouyin.com/share/video/6833280543530994947/?mid=aaa
    # note mid argument must be present else redirect to main page
    elif ".iesdouyin.com/share/video" in url:
        parse_video(url)
    # video page
    # format: http://v.douyin.com/Hdfkq4/
    # this is redirect to previous format
    elif "v.douyin.com" in url:
        pass
    else:
        log.error(f"'{url}' not supported format for importer")
        pass

def parse_user(url):
    with webdriver.Chrome() as driver:
        driver.implicitly_wait(10)
        driver.get(url)
        # believe DOM loads all music-items at once, otherwise sleep may be needed
        # https://www.douyin.com/share/user/83404616899
        # 音乐
        try:
            music_tab = driver.find_element_by_class_name("music-tab")
            music_tab.click()
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "music-item"))
            )
            soup = BeautifulSoup(driver.page_source, "lxml")
            user_id_text = soup.find_all("p", attrs={
                "class" : "shortid"
            })[0].text
            print(user_id_text)
            print(user_id_text.split()[-1])
            user_id = re.findall(r'\d+', url)[0]
            music_vid_li = soup.find_all("li", attrs={
                "class" : "music-item"
            })
            music_vid_ids = []
            for music_vid in music_vid_li:
                music_vid_ids.append(music_vid["data-id"])
            for vid in music_vid_ids:
                parse_video(f"https://www.iesdouyin.com/share/video/{vid}/?mid=a", folder=user_id)
        except (NoSuchElementException, TimeoutException):
            logging.warning("Could not find 'music-item' class in body")
        # https://www.douyin.com/share/user/111424174425
        # 作品
        # API call is failing for item goWork!
        try:
            user_tab = driver.find_element_by_class_name("user-tab")
            user_tab.click()
            WebDriverWait(driver, 500).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item goWork"))
            )
        except (NoSuchElementException, TimeoutException):
            logging.warning("Could not find 'item goWork' class in body")

def parse_video(url, folder=None, recurse=False):
    print(url)
    soup = None
    with webdriver.Chrome(chrome_options=CHROME_OPTIONS) as driver:
        driver.get(url)
        # we don't need to load whole page as we can scrape from script
        soup = BeautifulSoup(driver.page_source, "lxml")
    vid_div = None
    try:
        vid_div = soup.find_all("script")[-1]
    except IndexError:
        if recurse:
            logging.error(f"Invalid url: {url[:-3]}")
            return
        if not url.endswith("/"):
            url = f"{url}/"
        url = f"{url}?mid=badurl"
        parse_video(url, recurse=True)
    '''
    vid_div
    <script>$(function(){
            require('web:component/reflow_video/index').create({
                hasData: 1,
                videoWidth: 1080,
                videoHeight: 1920,
                playAddr: "https://aweme.snssdk.com/aweme/v1/playwm/?s_vid=93f1b41336a8b7a442dbf1c29c6bbc56d49df62b51a0928186f5365f74f87c98fdd361922bd22950d37fc5cbd52e90625ba8d01eebf06401caec46813c695a1b&amp;line=0",
                cover: "https://p1.pstatp.com/large/tos-cn-p-0015/53e6f53542eb41eca284d6033be9dd42_1590997128.jpg",
                dytk: "755d71f43c9b753565a37965469ba963e2609271d10a58351943ee6ca5abeda0",
            });
        });</script>
    '''
    vid_link = str(vid_div).split("\"")[1]
    if not(vid_link):
        logging.warning(f"Invalid link: {url}")
        return
    vid_id = re.findall(r'\d+', url)[0]
    from dl import requests_stream, wrapper
    # Note, headers must have user-agent set otherwise will return 403
    # set in requests_stream() in dl
    wrapper(requests_stream, {
        "url" : vid_link,
        "website" : "douyin.com",
        "folder" : folder,
        "fname" : f"{vid_id}.mp4"
    })