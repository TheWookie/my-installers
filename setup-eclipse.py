#!/usr/bin/env python2
# Python 3 is used by default in Arch linux. Unlikely this will be used, but an extra character doesn't hurt.

import os, platform
import requests
import shutil
from lxml import html
import setup_core


def download_eclipse():
    eclipse_download_page_url = "https://www.eclipse.org/downloads/"
    print "Hitting Eclipse download page: " + eclipse_download_page_url
    # Find the appropriate download
    current_os = platform.system().lower()
    if "win" in current_os:
        if setup_core.is_64bit():
            xpath = '//*[@id="page-download"]/div/div[2]/div[1]/div[2]/div/div[2]/ul/li[3]/a'
        else:
            xpath = '//*[@id="page-download"]/div/div[2]/div[1]/div[2]/div/div[2]/ul/li[2]/a'
    elif "linux" in current_os:
        if setup_core.is_64bit():
            xpath = '//*[@id="page-download"]/div/div[2]/div[1]/div[2]/div/div[3]/ul/li[3]/a'
        else:
            xpath = '//*[@id="page-download"]/div/div[2]/div[1]/div[2]/div/div[3]/ul/li[2]/a'
    elif "osx" in current_os:
        xpath = '//*[@id="page-download"]/div/div[2]/div[1]/div[2]/div/div[1]/ul/li[2]/a'
    xpath += '/@href'
    eclipse_page_tree = html.fromstring(requests.get(eclipse_download_page_url).content)
    secondary_page = eclipse_download_page_url + eclipse_page_tree.xpath(xpath)[0]
    print "".join(["Following to: ", secondary_page])
    eclipse_page_tree = html.fromstring(requests.get(secondary_page).content)
    # We have to traverse yet another page before being presented with a download url
    secondary_page = eclipse_page_tree.xpath('//*[@id="novaContent"]/div[1]/div/div[1]/div[1]/p[1]/a/@href')[0]
    eclipse_page_tree = html.fromstring(requests.get(eclipse_download_page_url + secondary_page).content)
    href_ = eclipse_page_tree.xpath('//*[@id="novaContent"]/div/div/div/span/p/a/@href')[0]
    eclipse_zip_file = setup_core.download_file(href_)
    return eclipse_zip_file


def install_plugin(plugin_url, plugin_identifier):
    "".join(["/opt/eclipse/"])
    os.system()
    pass


if __name__ == "__main__":
    # Check to make sure we're root. We need to be able to create symlinks and other things
    # if (os.getuid() is not 0):
    #     exit("Cannot run script without root permissions. Please run this script as root.")
    eclipse_archive_file = download_eclipse()
    eclipse_folder_name = os.path.splitext(os.path.splitext(eclipse_archive_file)[0])[0]
    if ".zip" in eclipse_archive_file:
        setup_core.extract_zip(eclipse_archive_file)
    elif ".tar" in eclipse_archive_file:
        setup_core.extract_tar(eclipse_archive_file)
    installed_directory = "/usr/local/" + eclipse_folder_name
    print "Moving to ", installed_directory
    if os.path.exists(installed_directory):
        print "(Removing previous installation with identical folder name)"
    shutil.move("eclipse", installed_directory)
    symlink_directory = "/opt/eclipse"
    if os.path.islink(symlink_directory):
        print "Updating symlink: " + symlink_directory
        os.unlink(symlink_directory)
    else:
        print "Creating symlink: " + symlink_directory
    os.symlink(installed_directory, symlink_directory)
