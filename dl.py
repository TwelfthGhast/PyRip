import requests
import logging

log = logging.getLogger(__name__)

def requests_img(img_url):
    if not img_url.startswith("http"):
        img_url = f"http://{img_url}"
    log.debug(f"{img_url} requested.")
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        log.debug(f"{img_url} returned status code {r.status_code}")
        with open("test", 'wb') as f:
            for chunk in r:
                f.write(chunk)
    else:
        log.warning(f"{img_url} returned status code {r.status_code}")
    return r.status_code