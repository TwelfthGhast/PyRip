from selenium.webdriver.chrome.options import Options as ChromeOptions
import os

CHROME_OPTIONS = ChromeOptions()
if os.path.isdir("driver-ext"):
    if os.path.isdir(os.path.join("driver-ext", "chrome")):
        fpath = os.path.join("driver-ext", "chrome")
        for extension in os.listdir(fpath):
            CHROME_OPTIONS.add_argument(f"load-extension={os.path.join(fpath, extension)}")
