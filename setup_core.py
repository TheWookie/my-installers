#!/usr/bin/env python2
# Python 3 is used by default in Arch linux. Unlikely this will be used, but an extra character doesn't hurt.

import requests
import hashlib
import tarfile, zipfile

# http://stackoverflow.com/a/16696317/1478636
# https://docs.python.org/3/library/hashlib.html
import sys


def download_file(url, md5_string=None):
    m = None
    if md5_string is not None:
        md5_string = md5_string.lower()
        m = hashlib.md5()
    local_filename = url.split('/')[-1]
    if not m:
        print "".join(["Downloading: ", url, " to: ", local_filename])
    else:
        print "".join(["Downloading: ", url, " to: ", local_filename, " verifying with MD5: ", md5_string])
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


# https://docs.python.org/2/library/platform.html#cross-platform
def is_64bit():
    return sys.maxsize > 2 ** 32
