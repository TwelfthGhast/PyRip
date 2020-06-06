from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver

CHROME_OPTIONS = ChromeOptions()
CHROME_OPTIONS.add_argument("--headless")

driver = webdriver.Chrome(chrome_options=CHROME_OPTIONS)
VERSION_CHROME = driver.capabilities['version']
VERSION_CHROME_SHORT = driver.capabilities['version'].split('.')[0]
VERSION_CHROMEDRIVER = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
VERSION_CHROMEDRIVER_SHORT = ".".join(VERSION_CHROMEDRIVER.split('.')[:2])

driver.quit()
del driver
