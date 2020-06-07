# PyRip

## About

This is a python script aimed at scraping images off websites, similar to [RipMeApp](https://github.com/RipMeApp/ripme)

## Setting Up

You will need to install dependencies found in `requirements.txt`.

```sh
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

You will need to install [chromedriver](https://chromedriver.chromium.org/) and [Google Chrome](https://www.google.com/chrome/). Note that some websites (Douyin, etc) detect the use of selenium, and workarounds are needed to prevent this. The easiest way is to use [an older version of chromedriver and Google Chrome (v61 or earlier)](https://stackoverflow.com/a/51236874) - this can be found in the `chromedriver` folder.

```sh
$ cd chromedriver/ubuntu
$ sudo cp chromedriver /usr/bin/chromedriver
$ sudo apt install google-chrome-stable_61.0.3163.100-1_amd64.deb
```