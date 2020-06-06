import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
import importers
import threading
from tld import get_tld
from dl import process_queue
from webdriveropts import VERSION_CHROME, VERSION_CHROMEDRIVER, VERSION_CHROMEDRIVER_SHORT, VERSION_CHROME_SHORT

log = logging.getLogger()

funcdict = {
    "generic" : importers.import_generic.importer,
    "imgur.com" : importers.import_imgur.importer,
    "iesdouyin.com" : importers.import_douyin.importer,
    "douyin.com" : importers.import_douyin.importer
}

log.info(f"ChromeDriver version '{VERSION_CHROMEDRIVER}' detected.")
log.info(f"Chrome version '{VERSION_CHROME}' detected.")
if int(VERSION_CHROME_SHORT) > 61:
    log.warning("Selenium can be detected by some websites due to services such as distil. It is recommended to use Chrome version 61 or lower, with the corresponding ChromeDriver to match.")
    log.warning("https://stackoverflow.com/questions/42169488/how-to-make-chromedriver-undetectable")
x = threading.Thread(target=process_queue, args=())
x.start()
while True:
    url = input("Please enter a url to crawl:")
    try:
        if not url.startswith("http"):
            url = f"http://{url}"
        res = get_tld(url, as_object=True)
        
        if res.fld in funcdict:
            funcdict[res.fld](url)
        else:
            funcdict["generic"](url)
    except Exception as e:
        log.error(e)
