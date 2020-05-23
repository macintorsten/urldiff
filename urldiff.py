#!/usr/bin/env python3

"""
Command line tool to check how similar two urls are two each other

`python3 urldiff.py < wikipedia_urls.txt 2>/dev/null`
"""

import time
import functools
import sys
import os
import fileinput
from urllib.parse import urlsplit, parse_qs, unwrap
import unittest

THRESHOLD = 1

def parse_url(func):
    """ Decorator that parses positional arguments to urls if needed """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args = map(lambda u: urlsplit(u) if type(u) == str else u, args)
        return func(*args, **kwargs)
    return wrapper

def iter_distance(i1, i2):
    diff = map(lambda t: t[0]!=t[1], zip(i1, i2))
    num_extra_objects = abs(len(i1) - len(i2))
    return sum(diff) + num_extra_objects

@parse_url
def file_distance(u1, u2):
    raise NotImplementedError()

@parse_url
def url_distance(u1, u2):
    # no special handling for these
    d = iter_distance(
        (u1.scheme, u1.username, u1.password, u1.hostname, u1.port, u1.fragment),
        (u2.scheme, u2.username, u2.password, u2.hostname, u2.port, u1.fragment)
    )

    d += ext_distance(u1.path, u2.path)
    
    # path
    d += path_distance(u1.path, u2.path)

    # querytring
    d += qs_distance(u1.query, u2.query) * 2

    return d

@parse_url
def path_distance(u1, u2):

    paths1 = list(filter(None, u1.path.split('/')))
    paths2 = list(filter(None, u2.path.split('/')))

    return iter_distance(paths1, paths2)

@parse_url
def is_url_subset(u1, u2):
    u1_base = (u1.scheme, u1.hostname, u1.username, u1.password, u1.port) 
    u2_base = (u2.scheme, u2.hostname, u2.username, u2.password, u2.port)

    if u1_base != u2_base:
        return False

    if not u2.path.startswith(u1.path):
        return False

    q1 = parse_qs(u1.query, keep_blank_values=False)
    q2 = parse_qs(u2.query, keep_blank_values=False)
    if not all(key in q2 for key in q1):
        return False

    return True

@parse_url
def ext_distance(u1, u2):
    _, ext1 = os.path.splitext(u1.path)
    _, ext2 = os.path.splitext(u2.path)

    def is_extension(ext):
        return (ext.isalnum() and not ext.isnum())

    d = 0

    if is_extension(ext1) or is_extension(ext2):
        d = 0 if ext1 == ext2 else 1

    return d

@parse_url
def qs_distance(u1, u2, keys_only=True):
    """ Calculates distance for querystring """
    qs1 = parse_qs(u1.query, keep_blank_values=False)
    qs2 = parse_qs(u2.query, keep_blank_values=False)

    d = 0
    if len(qs1) > len(qs2):
        qs1, qs2 = qs2, qs1

    d += abs(len(qs1) - len(qs2))

    for p1, v1 in qs1.items():
        d += 0 if qs2.get(p1) else 1
        if not keys_only:
            d += 0 if qs2.get(p1) == v1 else 1

    return d

if __name__ == "__main__":

    unique_urls = []

    for line in fileinput.input():
        raw_url = line.strip()

        #url = urlsplit(raw_url)
        url = raw_url

        if not unique_urls:
            unique_urls.append(url)

        distance_this_url = functools.partial(url_distance, url)

        all_distances = map(distance_this_url, unique_urls)
        mindistance = min(all_distances)

        if mindistance > THRESHOLD:
            unique_urls.append(url)
            print("[Score {}]".format(mindistance), file=sys.stderr, end=" ")
            print(raw_url)
