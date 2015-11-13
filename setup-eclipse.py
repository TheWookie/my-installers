#!/usr/bin/env python2
# Python 3 is used by default in Arch linux. Unlikely this will be used, but an extra character doesn't hurt.

import os
import requests
from lxml import html
import setup_core


def download_eclipse():
    eclipse_download_page_url = "https://www.eclipse.org/downloads/"
    print "Hitting Eclipse download page: " + eclipse_download_page_url
    # Find the appropriate download
    if setup_core.is_64bit():
        xpath = '//*[@id="download-packages"]/div[1]/div/div[3]/div[2]/div/ul/li[3]/a/@href'
    else:
        xpath = '//*[@id="download-packages"]/div[1]/div/div[3]/div[2]/div/ul/li[1]/a/@href'
    eclipse_page_tree = html.fromstring(requests.get(eclipse_download_page_url).content)
    secondary_page = eclipse_download_page_url + eclipse_page_tree.xpath(xpath)[0]
    print "".join(["Following to: ", secondary_page])
    eclipse_page_tree = html.fromstring(requests.get(secondary_page).content)
    eclipse_download_link = eclipse_page_tree.xpath('//*[@id="novaContent"]/div[1]/div/div[1]/div[1]/p[1]/a/@href')[0]
    setup_core.download_file(eclipse_download_page_url + eclipse_download_link)


if __name__ == "__main__":
    # Check to make sure we're root. We need to be able to create symlinks and other things
    # if (os.getuid() is not 0):
    #     exit("Cannot run script without root permissions. Please run this script as root.")
    download_eclipse()
