#!/usr/bin/env python3

""" Command line tool to check how similar two urls are two each other

`python3 urldiff.py < wikipedia_urls.txt 2>/dev/null`
"""

import time
import functools
import sys
import fileinput
from urllib.parse import urlparse, parse_qs
import unittest

def iter_distance(i1, i2):
    diff = map(lambda t: t[0]!=t[1], zip(i1, i2))
    extra_objects = abs(len(i1) - len(i2))
    return sum(diff) + extra_objects

def url_distance(u1, u2, weight=1.0):
    d = 0
    d += iter_distance(u1, u2)
    d += path_distance(u1.path, u2.path)
    d += qs_distance(u1.query, u2.query)
    return d * weight

def path_distance(p1, p2, weight=0.5):
    paths1 = list(filter(None, p1.split('/')))
    paths2 = list(filter(None, p2.split('/')))

    d = 0
    d += abs(len(paths1)-len(paths2))
    d += iter_distance(paths1, paths2)
    return d * weight

def ext_distance():
    raise NotImplementedError()

def qs_distance(q1, q2, weight=0.5):
    """ Calculates distance for querystring """
    qs1 = parse_qs(q1)
    qs2 = parse_qs(q2)

    d = 0
    if len(qs1) > len(qs2):
        qs2, qs2 = qs2, qs1

    d += abs(len(qs1) - len(qs2))

    for p1, v1 in qs1.items():
        d += 0 if qs2.get(p1) else 1
        d += 0 if qs2.get(p1) == v1 else 1

    return d

if __name__ == "__main__":

    threshold = 4.0
    unique_urls = []

    for line in fileinput.input():
        raw_url = line.strip()

        url = urlparse(line)

        if not unique_urls:
            unique_urls.append(url)

        distance_this_url = functools.partial(url_distance, url)

        all_distances = map(distance_this_url, unique_urls)
        mindistance = min(all_distances)

        if mindistance >= threshold:
            unique_urls.append(url)
            print("[Size = {}] Minimum distance {} exceeded threshold {} for URL {}".format(len(unique_urls), mindistance, threshold, raw_url), file=sys.stderr)
            print(raw_url)

