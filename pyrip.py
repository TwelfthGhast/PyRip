import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
import importers
import re
from tld import get_tld

log = logging.getLogger()

funcdict = {
    "generic" : importers.import_generic.importer,
    "imgur.com" : importers.import_imgur.importer
}

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
