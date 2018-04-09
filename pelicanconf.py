#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Nightblade'
SITENAME = 'Adventures in Python'
SITEURL = 'https://nightblade9.github.io/adventures-in-python'
PATH = 'content'

TIMEZONE = 'Canada/Eastern'

DEFAULT_LANG = 'English'

THEME = 'notmyidea'
USE_FOLDER_AS_CATEGORY = False
# Permalink structure
ARTICLE_SAVE_AS = '{date:%Y}/{slug}.html'
ARTICLE_URL = ARTICLE_SAVE_AS

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = "atom.xml"
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (("Profile", "https://github.com/nightblade9"),)

# Social widget
SOCIAL = (('Twitter', 'https://twitter.com/nightblade99'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
