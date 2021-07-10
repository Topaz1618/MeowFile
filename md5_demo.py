__copyright__ = """ Copyright (c) 2021 HangYan. """
__license__ = 'MIT license'
__version__ = '1.0'
__author__ = 'topaz1668@gmail.com'

import os
import hashlib


def generate_file_md5(file_path):
    m = hashlib.md5()
    blocksize = 1024 * 1024 * 2

    with open(file_path, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


if __name__ == "__main__":

    file_path = "1.zip"
    a = generate_file_md5(file_path)
    print(a)

