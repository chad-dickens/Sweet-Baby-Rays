"""
Scrapes the web page for the ABC news, opens every news link,
and saves the text of these news articles in txt files.
"""

import datetime
import os
import re
import urllib.request
from bs4 import BeautifulSoup, SoupStrainer

date_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
url_root = 'https://www.abc.net.au'
path_root = '/Users/chad/file_system/Daily_News/ABC {}'.format(date_stamp)

# Creating a new folder for the files
os.mkdir(path_root)
path_root += '/'

# Only collecting anchor tags from the front page
my_filter = SoupStrainer('a')
html = urllib.request.urlopen('{}/news/'.format(url_root)).read()
soup = BeautifulSoup(html, 'lxml', parse_only=my_filter)

# Getting links that start with this string ensures that they are actually news articles
tags = soup.find_all(href=re.compile('^/news/20'), limit=50)

# Opening each one of these links
for tag in tags:

    get_link = urllib.request.urlopen(url_root + tag['href']).read()
    link_soup = BeautifulSoup(get_link, 'lxml')

    # The ABC has recently introduced a new form of article that is image heavy and has
    # different characteristics to their normal articles. I have decided to skip these articles.
    if link_soup.body.has_attr('class') and \
            link_soup.body['class'] == ['platform-standard', 'news', 'story_page']:
        continue

    title_string = link_soup.title.string

    # In normal news articles, any p tags with only one class contain the main body text
    p_tags = [x for x in link_soup.find_all('p') if x.has_attr('class') and len(x['class']) == 1]

    with open('{}{}.txt'.format(path_root, title_string), 'w') as my_file:
        print(title_string, file=my_file)

        for num, sub_tag in enumerate(p_tags):

            # Adding in a blank line after the title, or if there is an author, adding a blank line
            # after the author.
            if num == 0 and sub_tag.text[:2] == 'By':
                print(sub_tag.text, file=my_file)
                print(file=my_file)
            elif num == 0:
                print(file=my_file)
                print(sub_tag.text, file=my_file)
            else:
                print(sub_tag.text, file=my_file)
