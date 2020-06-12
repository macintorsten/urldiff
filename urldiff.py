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
import difflib
from collections import ChainMap
from urllib.parse import urlsplit, parse_qs, unwrap
import bisect
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
    diff = map(lambda t: t[0] != t[1], zip(i1, i2))
    num_extra_objects = abs(len(i1) - len(i2))
    return sum(diff) + num_extra_objects


@parse_url
def file_distance(u1, u2):
    raise NotImplementedError()


@parse_url
def url_distance(u1, u2, threshold=8000):
    d = 0

    # no special handling for these
    if u1.path != u2.path:

        # path
        d += path_distance(u1, u2)

        if d >= threshold:
            return threshold

        # extension
        d += ext_distance(u1, u2)

    if d >= threshold:
        return threshold

    if u1.query != u2.query:
        d += query_distance(u1, u2) * 2

    if d >= threshold:
        return threshold

    # normally static url components
    d += iter_distance(
        (u1.scheme, u1.username, u1.password, u1.hostname, u1.port, u1.fragment),
        (u2.scheme, u2.username, u2.password, u2.hostname, u2.port, u1.fragment)
    )

    if d >= threshold:
        return threshold

    return d


@parse_url
def path_distance(u1, u2):
    return 3.0 * (1 -  difflib.SequenceMatcher(lambda c: c in {'/', '.'}, u1.path, u2.path).quick_ratio())
    #paths1 = u1.path.split('/')
    #paths2 = u2.path.split('/')

    #return iter_distance(paths1, paths2)


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
def query_distance(u1, u2, keys_only=True):
    """ Calculates distance for querystring """
    qs1 = parse_qs(u1.query, keep_blank_values=False) if u1 else {}
    qs2 = parse_qs(u2.query, keep_blank_values=False) if u2 else {}

    d = 0
    if len(qs1) > len(qs2):
        qs1, qs2 = qs2, qs1

    d += abs(len(qs1) - len(qs2))

    for p1, v1 in qs1.items():
        d += 0 if qs2.get(p1) else 1
        if not keys_only:
            d += 0 if qs2.get(p1) == v1 else 1

    return d


def main():

    unique_urls = list()

    for line in fileinput.input():
        raw_new_url = line.strip()
        new_url = urlsplit(raw_new_url)

        start_index = bisect.bisect(unique_urls, new_url)

        found_low_distance = False

        # Loop in reverse order from insert points
        # todo: implement logic to not loop over all old urls
        for i in range(len(unique_urls)):
            index = (start_index + 3 - i) % len(unique_urls)
            old_url = unique_urls[index]
            distance = url_distance(new_url, old_url, threshold=THRESHOLD)

            if distance < THRESHOLD:
                found_low_distance = True
                break

        if not found_low_distance:
            bisect.insort(unique_urls, new_url)

            print("[Score >= {}]".format(THRESHOLD),
                file=sys.stderr, end=" ", flush=True)
            print(raw_new_url)


if __name__ == "__main__":
    main()
