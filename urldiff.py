#!/usr/bin/env python3

import time
import fileinput
from urllib.parse import urlparse, parse_qs 
import argparse
import unittest

class TestUrlDistance(unittest.TestCase):
    """ Run with `python3 -m unittest urldiff.py` """

    u1 = urlparse("http://www.google.com/search?q=term#fragment")
    u2 = urlparse("http://www.google.com/search/path/?q=term#fragment")
    u4 = urlparse("http://www.google.com/search/path/again?q=term#fragment")

    def test_url_distance_equal(self):
        self.assertEqual(url_distance(self.__class__.u1, self.__class__.u1), 0)

    def test_url_distance_not_equal(self):
        self.assertNotEqual(url_distance(self.__class__.u1, self.__class__.u2), 0)

    def test_path_distance_equal(self):
        self.assertEqual(path_distance(self.__class__.u1.path, self.__class__.u1.path), 0)

    def test_path_distance_not_equal(self):
        self.assertNotEqual(path_distance(self.__class__.u1.path, self.__class__.u2.path), 0)

    def test_url_distance_less(self):
        d12 = path_distance(self.__class__.u1.path, self.__class__.u2.path)
        d13 = path_distance(self.__class__.u1.path, self.__class__.u3.path)
        self.assertLess(d12, d13)

def iter_distance(i1, i2):
    diff = map(lambda t: t[0]!=t[1], zip(i1, i2))
    return sum(diff)

def url_distance(u1, u2, weight=1.0):
    d = 0
    d += iter_distance(u1, u2)
    d += path_distance(u1.path, u2.path)
    d += qs_distance(u1.query, u2.query)
    return d / weight

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
        d += 1 if qs2.get(p1) else 0
        d += 1 if qs2.get(p1) == v1 else 0

    return d

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    print(args.url)
    print(type(args.url))
    args.url
    cmd_url = urlparse(args.url)
    print(cmd_url)
    for line in fileinput.input(files="-"):
        raw_url = line.strip()
        url = urlparse(line)
        ud = url_distance(url, cmd_url)
        pd = path_distance(url.path, cmd_url.path)
        print("Distance {} (URL: {}, Path: {}) - {}".format(ud + pd, ud, pd, raw_url))
