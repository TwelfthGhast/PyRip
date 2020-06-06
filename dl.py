import requests
import logging
from tld import get_tld
import os
import shutil
import hashlib
from datetime import datetime
from collections import deque
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger(__name__)

delay = {
    "imgur.com" : 2
}

# keeps track of last scheduled download for each domain
last_dl = {}

queue = {}

def process_queue():
    log.info("Manager of Worker Threadpool started.")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        while True:
            task_details = next(get_next_task(), None)
            if task_details is None:
                for future in as_completed(futures):
                    future.result()
                sleep(1)
            else:
                print(task_details)
                futures.append(executor.submit(task_details["action"], *task_details["args"], **task_details["kwargs"]))
    

def get_next_task():
    for key in queue:
        if queue[key][0]["time"] <= int(datetime.now().timestamp()):
            details = queue[key].popleft()
            if len(queue[key]) == 0:
                del queue[key]
            yield details
    raise StopIteration()

def wrapper(func, *args, **kwargs):
    log.debug(f"{args} {kwargs} submitted to queue")
    url = args[0]["url"]
    if not url.startswith("http"):
        url = f"http://{url}"
    fld = get_tld(url, as_object=True).fld
    if fld in last_dl and "nodelay" not in kwargs:
        # 10 second default delay
        dl_delay = 10
        if fld in delay:
            dl_delay = delay[fld]
        else:
            log.debug(f"No crawl delay found for {fld}")
        curtime = int(datetime.now().timestamp())
        last_dl[fld] = last_dl[fld] + dl_delay if last_dl[fld] + dl_delay > curtime else curtime
    else:
        last_dl[fld] = int(datetime.now().timestamp())
    if fld not in queue:
        queue[fld] = deque()
    queue[fld].append({
        "action": func,
        "args": args,
        "kwargs" : kwargs,
        "time": last_dl[fld]
    })

# https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def file_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def requests_stream(data: dict):
    if not data["url"].startswith("http"):
        data["url"] = f"http://{data['url']}"
    log.debug(f"{data['url']} requested.")
    headers = {'user-agent' : 'Wget/1.19.4 (linux-gnu)'}
    r = requests.get(data["url"], stream=True, headers=headers)
    if not os.path.isdir("downloads"):
        os.mkdir("downloads")
    group = ""
    # get group of download (i.e. site - reddit/imgur/etc)
    if "website" in data:
        group = data["website"]
    else:
        group = get_tld(data["url"], as_object=True).fld
    folder_path = os.path.join("downloads", group)
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
    # Construct folder for our particular download
    folder = ""
    if "folder" in data:
        folder = data["folder"]
    else:
        temp = get_tld(data["url"], as_object=True).fld
        folder = data["url"].split(temp)[-1][1:].replace("/",".")
    if folder is not None:
        folder_path = os.path.join(folder_path, folder)
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
    file_path = os.path.join(folder_path, data["fname"])
    if r.status_code == 200:
        log.debug(f"{data['url']} returned status code {r.status_code}")
        if os.path.isfile(file_path):
            f_hash = file_md5(file_path)
            hash_md5 = hashlib.md5()
            for chunk in r:
                hash_md5.update(chunk)
            d_hash = hash_md5.hexdigest()
            if f_hash == d_hash:
                log.info(f"{data['url']} skipped as duplicate at '{file_path}'")
                return
        with open(file_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)   
    else:
        log.warning(f"{data['url']} returned status code {r.status_code}")

