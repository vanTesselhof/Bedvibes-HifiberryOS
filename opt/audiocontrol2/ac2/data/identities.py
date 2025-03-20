'''
Copyright (c) 2019 Modul 9/HiFiBerry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import logging

my_uuid = None
my_release = None


def host_uuid():
    global my_uuid

    if my_uuid is not None:
        return my_uuid

    try:
        with open('/etc/uuid', 'r') as file:
            my_uuid = file.readline().strip()
    except IOError:
        logging.warning("can't read /etc/uuid, using empty UUID")
        my_uuid = "unknown"

    return my_uuid


def release():
    global my_release

    if my_release is not None:
        return my_release

    try:
        with open('/etc/hifiberry.version', 'r') as file:
            my_release = file.readline().strip()
    except IOError:
        logging.warning("can't read /etc/hifiberry.version, using empty release id")
        my_release = "unknown"

    return my_release
