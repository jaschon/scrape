#!/usr/bin/env python3

import pytest
import os
from bs4 import *
from scrape import *
import tempfile

## FIXES

@pytest.mark.parametrize("img, url, expected", [
    ("", "fdafdasfsd", ""),
    ("data:image/png;ABCDEF", "fdafdafdsafd", "data:image/png;ABCDEF"),
    ("mysite.jpg", "this.site.com", "this.site.com/mysite.jpg"),
    ("//mysite.jpg", "/this.site/", "http://mysite.jpg"),
    ("/mysite.jpg", "this.site.com", "this.site.com/mysite.jpg"),
    ("/mysite.jpg?ABCDEFG=ABC", "this.site.com", "this.site.com/mysite.jpg"),
])
def test_image_fix(img, url, expected):
    assert expected == image_fix(img, url)


@pytest.mark.parametrize("string, expected", [
    ("[]ABC!@#", "__ABC___"),
    ("(ZAza0123456789)", "_ZAza0123456789_"),
    ("abcdefg&?", "abcdefg__"),
    ("abcxyzABCXYZ1234567890", "abcxyzABCXYZ1234567890"),
])
def test_string_fix(string, expected):
    assert expected == string_fix(string)


@pytest.mark.parametrize("url, expected", [
    ("", ""),
    ("mywebsite.com/awesome/", "http://mywebsite.com/awesome/"),
    ("https://mywebsite.com/awesome/", "http://mywebsite.com/awesome/"),
    ("http://mywebsite.com/awesome/", "http://mywebsite.com/awesome/"),
])
def test_http_fix(url, expected):
    assert expected == http_fix(url)

## PATH FIND
@pytest.mark.parametrize("string, expected", [
    ("", ""),
    ("background-image:", ""),
    ("background-image: url(this_should_match)", "this_should_match"),
    ("background-image: url('this_should_match')", "this_should_match"),
    ('background-image: url("this_should_match")', "this_should_match"),
    ('background-image: "this_should_not_match"', ""),
    ('color: #12345; background-image: url("this_should_match")', "this_should_match"),
])
def test_find_attr_url(string, expected):
    assert expected == find_attr_url(string)

@pytest.mark.parametrize("html, url, expected", [
    #fail
    ("", "", []),
    ("<source style='background-image: url(should_fail.jpg)'>", "fail.com", []),
    #pass
    ("<img src='find_me.jpg'>", "add_me.com", ['add_me.com/find_me.jpg',]),
    ("<div style='background-image: url(find_me.jpg)'>", "add_me.com", ['add_me.com/find_me.jpg',]),
    ("<source src='http://findme.com/success.jpg'>", "fail.com", ['http://findme.com/success.jpg']),
    #two src
    ("<img src='find_me.jpg' data-src='me_too.png'>", "add_me.com", 
        ['add_me.com/me_too.png', 'add_me.com/find_me.jpg']),
    #large html
    ( """
    <img src='find_me1.jpg'>
    <p>skip me</p>
    <img src='find_me2.jpg'>
    <p>skip me</p>
    <source src='find_me3.jpg'>
    <p>skip me</p>
    <div style="color: blue; margin: 0; background-image: url('find_me4.jpg')"></div>
    <div style="background-image: url('http://newsite.com/find_me8.jpg')"></div>
    <img data-lazyload='find_me5.jpg'>
    <img data-srcset='find_me6.jpg'>
    <img data-src='find_me7.jpg'>
    """, "add_me.com", [
        'add_me.com/find_me1.jpg',
        'add_me.com/find_me2.jpg',
        'add_me.com/find_me3.jpg',
        'add_me.com/find_me4.jpg',
        'add_me.com/find_me5.jpg',
        'add_me.com/find_me6.jpg',
        'add_me.com/find_me7.jpg',
        'http://newsite.com/find_me8.jpg',
        ]),
])
def test_search_tags(html, url, expected):
    soup = BeautifulSoup(html, "html.parser")
    paths = search_tags(soup, url)
    assert set(paths) == set(expected)

# @pytest.mark.parametrize("url, images", [
#     ("http://pypi.org", ["logo-small.95de8436.svg", "logo-large.6bdbb439.svg"]), 
#     ("http://pypi.org/help", ["logo-small.95de8436.svg",]), 
# ])
# def test_get_paths(url, images):
#     paths = [os.path.basename(p) for p in get_paths(url)]
#     for img in images:
#         assert img in paths

