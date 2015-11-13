#!/usr/bin/env python2
# Python 3 is used by default in Arch linux. Unlikely this will be used, but an extra character doesn't hurt.

import os
import requests
import shutil
from lxml import html
import hashlib
import tarfile, zipfile


# http://stackoverflow.com/a/16696317/1478636
# https://docs.python.org/3/library/hashlib.html
def download_file(url, md5_string=None):
    m = None
    if md5_string is not None:
        md5_string = md5_string.lower()
        m = hashlib.md5()
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                if m:
                    m.update(chunk)
    if m and not (md5_string == m.hexdigest().lower()):
        raise IOError("".join(["The MD5 (", m.hexdigest().lower(), ") did not match (", str(md5_string),
                               "), ergo the file did not download properly. Please try again."]))
    return local_filename


def download_jmeter():
    jmeter_download_page_url = "http://jmeter.apache.org/download_jmeter.cgi"
    print "Hitting JMeter download page: " + jmeter_download_page_url
    jmeter_page_tree = html.fromstring(requests.get(jmeter_download_page_url).content)
    jmeter_page_links = jmeter_page_tree.xpath('//a/@href')
    jmeter_tar_file_url = filter(lambda x: x.endswith(".tgz") and not "src" in x, jmeter_page_links)[0]
    jmeter_tar_md5_url = filter(lambda x: x.endswith(".tgz.md5") and not "src" in x, jmeter_page_links)[0]
    jmeter_md5_string = requests.get(jmeter_tar_md5_url).text.split(" ")[0]
    print "".join(["Downloading: ", jmeter_tar_file_url, " and will verify with MD5: ", jmeter_md5_string])
    tar_file = download_file(jmeter_tar_file_url, jmeter_md5_string)
    print tar_file + " was downloaded with correct MD5"
    return tar_file


def download_plugin():
    plugin_download_page_url = "http://jmeter-plugins.org"
    print "Hitting JMeter Plugin download page: " + plugin_download_page_url
    plugin_page_tree = html.fromstring(requests.get(plugin_download_page_url).content)
    plugin_download_link = "".join(
        [plugin_download_page_url, plugin_page_tree.xpath('/html/body/div/div/div[1]/a[1]/@href')[0]])
    print "Downloading: " + plugin_download_link
    zip_file = download_file(plugin_download_link)
    print zip_file + " was downloaded"
    return zip_file


# http://stackoverflow.com/a/6059458/1478636
def extract_tar(tar_file, extract_path='.'):
    # with tarfile.TarFile(tar_file, "r") as t:
    #     t.extractall(extract_path)
    tar = tarfile.open(tar_file, 'r')
    for item in tar:
        tar.extract(item, extract_path)
        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            tar.extract(item.name, "./" + item.name[:item.name.rfind('/')])


# http://stackoverflow.com/a/9432315/1478636
def extract_zip(zip_file, extract_path='.'):
    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(extract_path)


if __name__ == "__main__":
    # Check to make sure we're root. We need to be able to create symlinks and other things
    if (os.getuid() is not 0):
        exit("Cannot run script without root permissions. Please run this script as root.")
    # Download jmeter .tgz file.
    jmeter_tar_file = download_jmeter()
    extract_tar(jmeter_tar_file)
    extracted_tar_directory = os.path.splitext(jmeter_tar_file)[0]
    # Download plugin .zip file
    plugin_zip_file = download_plugin()
    extract_zip(plugin_zip_file, extracted_tar_directory)
    print "".join([plugin_zip_file, " was extracted to ", extracted_tar_directory])
    # Move to /usr/local
    print "Moving to /usr/local/"
    installed_directory = "/usr/local/" + extracted_tar_directory
    if (os.path.exists(installed_directory)):
        print "(Removing previous installation with identical folder name)"
        shutil.rmtree(installed_directory)
    shutil.move(extracted_tar_directory, installed_directory)
    # Creating/Updating symlink
    symlink_directory = "/opt/jmeter"
    if (os.path.islink(symlink_directory)):
        print "Updating symlink: " + symlink_directory
        os.unlink(symlink_directory)
    else:
        print "Creating symlink: " + symlink_directory
    os.symlink(installed_directory, symlink_directory)
