import string
import sys
import urllib.parse
from django.shortcuts import render
from os import error, name, stat
from django.contrib.auth.decorators import user_passes_test
from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render
import requests
from requests import exceptions
from requests.api import get, head
from requests.models import HTTPError
from movies.models import PlayList, Actor, Season, Director, Episode, Country, Category
from .forms import GetLinkForm
from .forms import GetMultiLinkForm
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from PIL import Image
from sys import exit
from urllib.parse import urlparse
import re
import os
import time
import datetime
import random

# For your IP address to not get blocked I suggest you using different Proxies and randomly using them each time the bot runs

ip_addresses = [

        ]

# Categories and their IDs in the Database
categories = [
            ('Action', 1), ('Comedy', 5), ('Family', 9), ('History', 13), ('Mystery', 17), ('Sci-Fi', 21), ('War', 25), ('Thriller', 6), ('Horror', 14),
            ('Sport', 22), ('Animation', 3), ('Documentyry', 7), ('Adventure', 2), ('Drama', 8), ('Thriller', 24), ('Romance', 20), ('Biography', 24)
            ]

# Logging the bot function
def get_message(msg):
    with open('log.txt', 'a') as logfile:
        logfile.write(str(msg) + '\n\n')

def to_url(name):
    name = name.replace(' ', '-')
    name = name.lower()
    return name

def to_high(source):
    source = source.split('V1_')
    source = source[0] + 'V1_.jpg'
    return source

# This funcgtion fetches only one movie based on the given URL by the user
def single_scraper(url):
    get_message('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~    ' + str(datetime.datetime.now()) +
     '    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n                                LOGGING STARTED\n')
    movie_data = {
        'movie_details': [],
        'actor_details': [],
        'dir_details': [],
    }

    # It's always best practice to use headers within scrapers for better functionality
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
    main_url = 'https://www.imdb.com'
    get_message('Sending request to : ' + url)

    # Randomly selecting a proxy server each time the bot runs
    proxy_index = random.randint(0, len(ip_addresses) - 1)
    proxy = {"http": ip_addresses[proxy_index], "https": ip_addresses[proxy_index]}
    try:
        r = requests.get(url, headers=headers, timeout=10, proxies=proxy)
        get_message('Using : ' + proxy)
    except:
        r = requests.get(url, headers=headers, timeout=10)
        get_message('Normal request')
    
    get_message('Using : ' + proxy)
    r = requests.get(url, headers=headers, timeout=10, proxies=proxy)
    # If reqeust is successful only then the rest of the code runs
    if r.status_code != 200:
        get_message('Response status: ' + str(r.status_code))
    else:
        get_message('Response status: ' + str(r.status_code) + '\n')
        soup = BeautifulSoup(r.text, 'lxml')
        
        # Fetch title of the movie
        try:
            title = soup.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0').text
        except:
            get_message('Title not found')
            title = 'title not found'

        try:
            type_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
            content_type = type_parent.find_all('li', role='presentation')[0].text
        except:
            type_parent = '___type_parent___notfound__-'
            get_message('Type not found')
            content_type = 'TV Series'

        # Here I seperate Movies from Series by giving them a Type( 1: Movie, 2: Series)
        try:
            if content_type == 'TV Series':
                film_type = 2
                dur = ' '
                get_message('Type = ' + film_type)
            else:
                film_type = 1

                # Fetching movie duration
                try:
                    dur_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
                    duration = dur_parent.find_all('li', role='presentation')[2].text
                    try:
                        dur = duration.replace("h", "Hours")
                        dur = dur.replace("min", "Minutes")
                    except:
                        dur = duration
                except:
                    dur = ''
                    Exception('time not found')
                
        except:
            get_message('Could not set Type for this object')
            film_type = 1
            dur = ' '

        get_message('Fetching actor data')

        ## Here I fetch the info of first 5 actors of each movie and append them to a list

        i = 0
        while i < 5:
            try:
                actor_url = soup.find_all('a', class_='StyledComponents__ActorName-y9ygcu-1')[i].get('href')
                r_actor = requests.get(main_url + actor_url, headers=headers, timeout=10).text
                soup_actor = BeautifulSoup(r_actor, 'lxml')
                actor_name = soup_actor.find('span', class_='itemprop').text
                actor_bio = soup_actor.find('div', class_='inline').text
                movie_data['actor_details'].append({'name': actor_name, 'summary': actor_bio})
                get_message('Successfully fetched actor ' + str(i))

                # Downloading actor pictures from their profile in IMDB
                try:
                    l_actor_pic = soup_actor.find('img', id='name-poster').get('src')
                    l_actor_pic_r = requests.get(l_actor_pic, headers=headers, timeout=10)
                    l_actor_img = Image.open(BytesIO(l_actor_pic_r.content))
                    l_actor_img.save('media/' + to_url(actor_name) + '.webp')
                    get_message('Successfully saved actor image')
                except:
                    get_message('Actor image not found')
                    l_actor_pic = Image.open('/home/ubuntu/evafilm/avatar.jpg')
                    l_actor_pic_r = l_actor_pic
                    l_actor_img = l_actor_pic_r
                i += 1

            except:
                get_message('Actor URL not found')
                actor_name = ' '
                actor_bio = ' '

            get_message('Fetching actor images')
                     

        try:
            year = str(soup.find_all('span', class_='jedhex')[0].text)
            get_message('Successfully found Year')

        except:
            year = '0000'
            get_message('Could not find Year')

        # This code snippet is for getting the high quality image of the movie. It sometimes ran into errors so I commented it.   
        # High quality image
        """get_message('~~~~~~~~~~~~~~~~~~~~~~~~   Fetching High Quality Image   ~~~~~~~~~~~~~~~~~~~~~~~~ ')
        try:
            image_url = soup.find('a', class_='ipc-lockup-overlay').get('href')
            img_r = requests.get('https://www.imdb.com' + image_url, headers=headers, timeout=30).text
            img_soup = BeautifulSoup(img_r, 'lxml')
            img_url = img_soup.find('img', class_='MediaViewerImagestyles__PortraitImage-sc-1qk433p-0').get('src')
            img_obj = requests.get(img_url,  headers=headers, timeout=30)
            img = Image.open(BytesIO(img_obj.content))
            img_title = to_url(title)
            img.save('/home/ubuntu/scraper/movies/' + img_title + '.webp')
            get_message('~~~~~~~~~~~ Successfully downloaded High Quality Image ~~~~~~~~~~~~~~~~')
        except requests.Timeout as e:
            get_message('High quality image request timed out')"""

        # Downloading the low quality of the movie
        get_message('Fetching Low Quality Image')
        try:
            l_image_url = soup.find('img', class_='ipc-image').get('src')
            l_img_obj = requests.get(l_image_url, headers=headers, timeout=10)
            l_img = Image.open(BytesIO(l_img_obj.content))
            l_img_title = to_url(title)
            l_img.save('media/' + l_img_title + '.webp')
        except:
            get_message('Low quality image failed')

        # Fetching the tv-pg

        try:
            tv_pg = soup.find_all('span', class_='jedhex')[1].text
            
        except:
            get_message('TV-PG failed')
            tv_pg = 'R'

        # Fetch movie rating
        try:
            rating = soup.find('span', class_='fhMjqK').text
        except:
            get_message('Rating not found')
            rating = 0
        
        # Fetch movie summary text
        try:
            summary = soup.find('span', class_="GenresAndPlot__TextContainerBreakpointXL-cum89p-4").text
            summary = summary.strip()
        except:
            summary = ' '
            get_message('Summary not found')

        # Fetching the director of the movie
        try:
            director1 = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')[0].get('href')
            r_dir = requests.get(main_url + director1, headers=headers, timeout=10).text
            dir_soup = BeautifulSoup(r_dir, 'lxml')
            dir_name = dir_soup.find('span', class_='itemprop').text
            dir_bio = dir_soup.find('div', class_='inline').text
            movie_data['dir_details'].append({'name': dir_name, 'summary': dir_bio})

            # Downloading high quality image of the director. It also ran into errors sometimes so I commented it.
            """get_message('Fetching Director High Q image')
            try:
                dir_pic = dir_soup.find('img', id='name-poster').get('src')
                dir_pic_r = requests.get(to_high(dir_pic))
                dir_img = Image.open(BytesIO(dir_pic_r.content))
                os.mkdir('/home/ubuntu/scraper/' + title + '/directors')
                dir_img.save('/home/ubuntu/scraper/directors/' + to_url(dir_name) + '.webp')
            except requests.Timeout as e:
                get_message('Director High Q Image failed')"""

            # Downloading low quality image of the director
            try:
                l_dir_pic = dir_soup.find('img', id='name-poster').get('src')
                l_dir_pic_r = requests.get(l_dir_pic, headers=headers, timeout=10)
                l_dir_img = Image.open(BytesIO(l_dir_pic_r.content))
                l_dir_img.save('media/' + to_url(dir_name) + '.webp')
                get_message('Director Low Q Image fetched')
            except:
                get_message('Director Low Q Image failed')

            # Fetching 2nd director info( If exists )
            get_message('Fetching 2nd Director')
            try:
                director2 = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')[1].get('href')
                r_dir2 = requests.get(main_url + director2, headers=headers, timeout=10).text
                dir2_soup = BeautifulSoup(r_dir2, 'lxml')
                dir2_name = dir_soup.find('span', class_='itemprop').text
                dir2_bio = soup_actor.find('div', class_='inline').text
                movie_data['dir_details'].append({'name': dir2_name, 'summary': dir2_bio})
                
                try:
                    l_dir2_pic = dir2_soup.find('img', id='name-poster').get('src')
                    l_dir2_pic_r = requests.get(l_dir2_pic, headers=headers, timeout=10)
                    l_dir2_img = Image.open(BytesIO(l_dir2_pic_r.content))
                    l_dir2_img.save('media/' + to_url(dir2_name) + '.webp')
                except:
                    get_message('Director 2 Low Q pic failed')
            except:
                director2 = ' '
                Exception('No 2nd director')
        except:
            director1 = ' '
            Exception('No director')
        with open('log.txt', 'a') as logfile:
            logfile.write('line 274\n')

        get_message('~~~~~~~~~~~~  Fetching Genres ~~~~~~~~~~~~~')
        
        # Fetching the categories based on their ids in the list and tuples defined on line 37
        try:
            category1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text
            genre1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text

            for c in categories:
                if genre1 == c[0]:
                    genre1 = c[1]

        except:
            genre1 = None
            category1 = None
            Exception('Could not set genre 1')
        
        try:
            category2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
            genre2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
            get_message('Fetched Genre 2')

            try:
                for c in categories:
                    if genre2 == c[0]:
                        genre2 = c[1]
            except:
                genre2 = None
                Exception('Could not set genre')

        except:
            category2 = None
            genre2 = None
            Exception('Genre 2 not found')

        try:
            category3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
            genre3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
            get_message('Fetched Genre 3')

            try:
                for c in categories:
                    if genre3 == c[0]:
                        genre3 = c[1]
                
            except:
                genre3 = None
                Exception('Could not set genre')

        except:
            genre3 = None
            category3 = None
            Exception('Genre 3 not found')

        try:
            category4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
            genre4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
            get_message('Fetched Genre 4')

            try:
                for c in categories:
                    if genre4 == c[0]:
                        genre4 = c[1]
                
            except:
                genre4 = None
                Exception('Could not set genre')

        except:
            category4 = None
            genre4 = None
            Exception('Genre 4 not found')

        get_message('Fetching Trailer URL')

        trailer = soup.find('a', class_='hero-media__slate-overlay').get('href')
        trailer = main_url + trailer
        users_view = soup.find('div', class_='AggregateRatingButton__TotalRatingAmount-sc-1il8omz-3').text
        users_view = re.sub('\D', '', users_view)
        if 'M' in users_view:
            users_view = users_view.replace('M', 'Million')
        elif 'K' in users_view:
            users_view = users_view.replace('K', 'Thousand')
        else:
            users_view = users_view

        c = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')
        get_message('Fetcing Country...')
        for child in c:
            if 'country' in child.get('href'):
                country = child.text
                
            else:
                country = ''

        movie_data['movie_details'].append(
            {'title': title, 'summary': summary, 'country': country, 'rating': float(rating), 'user_views': float(users_view),
            'year': year, 'time': dur, 'tv_pg': tv_pg, 'trailer_url': trailer, 'category1': genre1, 'category2': genre2,
            'category3': genre3, 'category4': genre4})

        get_message('End of Process')

    return movie_data, category1, category2, category3, category4, film_type

# This function fetches several movies based on the selected movie info (Year, Rating, Category, ...)
# Most parts of this function are similar to the previous one so I didn't comment on all the lines
def multiple_scraper(multi_url):
    get_message('Starting Multi scraping')
    my_list = {
        'test_data' : []
    }
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

    try:
        proxy_index = random.randint(0, len(ip_addresses) - 1)
        proxy = {"http": ip_addresses[proxy_index], "https": ip_addresses[proxy_index]}
        r = requests.get(multi_url, headers=headers, timeout=10, proxies=proxy)
        get_message('Multi scraper Using : ' + proxy)
    except:
        r = requests.get(multi_url, headers=headers, timeout=10)
        get_message('Multi scraper using normal request')

    

    soup = BeautifulSoup(r.text, 'lxml')

    movie_url = soup.find_all('h3', class_='lister-item-header', limit=3).find('a').get('href')
    i = 0
    mov_i = 1
    for a in movie_url:
        get_message('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~    ' + str(datetime.datetime.now()) +
        '    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n                                Multi scraping' + str(mov_i) + ' first movie\n')
        movie_data = {
            'movie_details': [],
            'actor_details': [],
            'dir_details': [],
        }

        delay = random.uniform(1.2, 4.6)
        delay = str(delay)[:4]
        delay = float(delay)

        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
        main_url = 'https://www.imdb.com'
        get_message('Sending request to : ' + a)


        try:
            proxy_index = random.randint(0, len(ip_addresses) - 1)
            proxy = {"http": ip_addresses[proxy_index], "https": ip_addresses[proxy_index]}
            r = requests.get(a, headers=headers, timeout=10, proxies=proxy)
        except:
            r = requests.get(a, headers=headers, timeout=10)

        if r.status_code != 200:
            get_message('Response status: ' + str(r.status_code))
        else:
            get_message('Response status: ' + str(r.status_code) + '\n')
            soup = BeautifulSoup(r.text, 'lxml')
            

            try:
                title = soup.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0').text
            except:
                get_message('Title not found')
                title = 'title not found'

            try:
                type_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
                content_type = type_parent.find_all('li', role='presentation')[0].text
            except:
                type_parent = '___type_parent___notfound__-'
                get_message('Type not found')
                content_type = 'TV Series'
            try:
                if content_type == 'TV Series':
                    film_type = 2
                    dur = ' '
                    get_message('Type = ' + film_type)
                else:
                    film_type = 1
                    try:
                        dur_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
                        duration = dur_parent.find_all('li', role='presentation')[2].text
                        try:
                            dur = duration.replace("h", "Hours")
                            dur = dur.replace("min", "Minutes")
                        except:
                            dur = duration
                    except:
                        dur = ' '
                        Exception('time not found')
                    
            except:
                get_message('Could not set Type for this object')
                film_type = 1
                dur = ' '

            get_message('Fetching actor data')

            i = 0
            while i < 5:
                try:
                    actor_url = soup.find_all('a', class_='StyledComponents__ActorName-y9ygcu-1')[i].get('href')
                    r_actor = requests.get(main_url + actor_url, headers=headers, timeout=10).text
                    soup_actor = BeautifulSoup(r_actor, 'lxml')
                    actor_name = soup_actor.find('span', class_='itemprop').text
                    actor_bio = soup_actor.find('div', class_='inline').text
                    movie_data['actor_details'].append({'name': actor_name, 'summary': actor_bio})
                    get_message('Successfully fetched actor ' + str(i))
                    try:
                        l_actor_pic = soup_actor.find('img', id='name-poster').get('src')
                        l_actor_pic_r = requests.get(l_actor_pic, headers=headers, timeout=10)
                        l_actor_img = Image.open(BytesIO(l_actor_pic_r.content))
                        l_actor_img.save('media/' + to_url(actor_name) + '.webp')
                        get_message('Successfully saved actor image')
                    except:
                        get_message('Actor image not found')
                        l_actor_pic = Image.open('/home/ubuntu/evafilm/avatar.jpg')
                        l_actor_pic_r = l_actor_pic
                        l_actor_img = l_actor_pic_r
                    i += 1

                except:
                    get_message('Actor URL not found')
                    actor_name = ' '
                    actor_bio = ' '

                get_message('Fetching actor images')
                
                
                

        #        with open('log.txt', 'a') as logfile:
        #           logfile.write('start actor_pic = soup_actor.find line 155 \n')
        #        try:
        #            actor_pic = soup_actor.find('img', id='name-poster').get('src')
        #            # actor_pic_r = requests.get(to_high(actor_pic))
        #            #actor_img = Image.open(BytesIO(actor_pic.content))
        #            # actor_img.save('/home/ubuntu/scraper/actors/' + to_url(actor_name) + '.webp')
        #        except:
        #            print('actor_pic not found')
        #            actor_pic = Image.open('/home/ubuntu/evafilm/avatar.jpg')
        #            with open('log.txt', 'a') as logfile:
        #                logfile.write('this happen because Actor image not found line 127\n')
        #            actor_img = actor_pic
        #
        #        with open('log.txt', 'a') as logfile:
        #            logfile.write('end actor_pic = soup_actor.find line 169 \n')

                

            try:
                year = str(soup.find_all('span', class_='jedhex')[0].text)
                get_message('Successfully found Year')

            except:
                year = '0000'
                get_message('Could not find Year')

            # High quality image
            """get_message('~~~~~~~~~~~~~~~~~~~~~~~~   Fetching High Quality Image   ~~~~~~~~~~~~~~~~~~~~~~~~ ')
            try:
                image_url = soup.find('a', class_='ipc-lockup-overlay').get('href')
                img_r = requests.get('https://www.imdb.com' + image_url, headers=headers, timeout=30).text
                img_soup = BeautifulSoup(img_r, 'lxml')
                img_url = img_soup.find('img', class_='MediaViewerImagestyles__PortraitImage-sc-1qk433p-0').get('src')
                img_obj = requests.get(img_url,  headers=headers, timeout=30)
                img = Image.open(BytesIO(img_obj.content))
                img_title = to_url(title)
                img.save('/home/ubuntu/scraper/movies/' + img_title + '.webp')
                get_message('~~~~~~~~~~~ Successfully downloaded High Quality Image ~~~~~~~~~~~~~~~~')
            except requests.Timeout as e:
                get_message('High quality image request timed out')"""

            get_message('Fetching Low Quality Image')
            try:
                l_image_url = soup.find('img', class_='ipc-image').get('src')
                l_img_obj = requests.get(l_image_url, headers=headers, timeout=10)
                l_img = Image.open(BytesIO(l_img_obj.content))
                l_img_title = to_url(title)
                l_img.save('media/' + l_img_title + '.webp')
            except:
                get_message('Low quality image failed')

            try:
                tv_pg = soup.find_all('span', class_='jedhex')[1].text
                
            except:
                get_message('TV-PG failed')
                tv_pg = 'R'

            try:
                rating = soup.find('span', class_='fhMjqK').text
            except:
                get_message('Rating not found')
                rating = 0
            try:
                summary = soup.find('span', class_="GenresAndPlot__TextContainerBreakpointXL-cum89p-4").text
                summary = summary.strip()
            except:
                summary = ' '
                get_message('Summary not found')

            try:
                director1 = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')[0].get('href')
                r_dir = requests.get(main_url + director1, headers=headers, timeout=10).text
                dir_soup = BeautifulSoup(r_dir, 'lxml')
                dir_name = dir_soup.find('span', class_='itemprop').text
                dir_bio = dir_soup.find('div', class_='inline').text
                movie_data['dir_details'].append({'name': dir_name, 'summary': dir_bio})
                """get_message('Fetching Director High Q image')
                try:
                    dir_pic = dir_soup.find('img', id='name-poster').get('src')
                    dir_pic_r = requests.get(to_high(dir_pic))
                    dir_img = Image.open(BytesIO(dir_pic_r.content))
                    os.mkdir('/home/ubuntu/scraper/' + title + '/directors')
                    dir_img.save('/home/ubuntu/scraper/directors/' + to_url(dir_name) + '.webp')
                except requests.Timeout as e:
                    get_message('Director High Q Image failed')"""

                try:
                    l_dir_pic = dir_soup.find('img', id='name-poster').get('src')
                    l_dir_pic_r = requests.get(l_dir_pic, headers=headers, timeout=10)
                    l_dir_img = Image.open(BytesIO(l_dir_pic_r.content))
                    l_dir_img.save('media/' + to_url(dir_name) + '.webp')
                    get_message('Director Low Q Image fetched')
                except:
                    get_message('Director Low Q Image failed')

                get_message('Fetching 2nd Director')
                try:
                    director2 = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')[1].get('href')
                    r_dir2 = requests.get(main_url + director2, headers=headers, timeout=10).text
                    dir2_soup = BeautifulSoup(r_dir2, 'lxml')
                    dir2_name = dir_soup.find('span', class_='itemprop').text
                    dir2_bio = soup_actor.find('div', class_='inline').text
                    movie_data['dir_details'].append({'name': dir2_name, 'summary': dir2_bio})
                    
                    try:
                        l_dir2_pic = dir2_soup.find('img', id='name-poster').get('src')
                        l_dir2_pic_r = requests.get(l_dir2_pic, headers=headers, timeout=10)
                        l_dir2_img = Image.open(BytesIO(l_dir2_pic_r.content))
                        l_dir2_img.save('media/' + to_url(dir2_name) + '.webp')
                    except:
                        get_message('Director 2 Low Q pic failed')
                except:
                    director2 = ' '
                    Exception('No 2nd director')
            except:
                director1 = ' '
                Exception('No director')
            with open('log.txt', 'a') as logfile:
                logfile.write('line 274\n')

            get_message('~~~~~~~~~~~~  Fetching Genres ~~~~~~~~~~~~~')
            try:
                category1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text
                genre1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text

                for c in categories:
                    if genre1 == c[0]:
                        genre1 = c[1]
            except:
                genre1 = None
                category1 = None
                Exception('Could not set genre 1')
            
            try:
                category2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
                genre2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
                get_message('Fetched Genre 2')

                try:
                    for c in categories:
                        if genre2 == c[0]:
                            genre2 = c[1]
                except:
                    genre2 = None
                    Exception('Could not set genre')

            except:
                category2 = None
                genre2 = None
                Exception('Genre 2 not found')

            try:
                category3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
                genre3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
                get_message('Fetched Genre 3')
                try:
                    for c in categories:
                        if genre3 == c[0]:
                            genre3 = c[1]
                except:
                    genre3 = None
                    Exception('Could not set genre')

            except:
                genre3 = None
                category3 = None
                Exception('Genre 3 not found')

            try:
                category4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
                genre4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
                get_message('Fetched Genre 4')
                try:
                    for c in categories:
                        if genre1 == c[0]:
                            genre1 = c[1]
                except:
                    genre4 = None
                    Exception('Could not set genre')

            except:
                category4 = None
                genre4 = None
                Exception('Genre 4 not found')

            get_message('Fetching Trailer URL')

            trailer = soup.find('a', class_='hero-media__slate-overlay').get('href')
            trailer = main_url + trailer
            users_view = soup.find('div', class_='AggregateRatingButton__TotalRatingAmount-sc-1il8omz-3').text
            users_view = re.sub('\D', '', users_view)
            if 'M' in users_view:
                users_view = users_view.replace('M', 'Million')
            elif 'K' in users_view:
                users_view = users_view.replace('K', 'Thousand')
            else:
                users_view = users_view
            c = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')
            get_message('Fetcing Country...')
            for child in c:
                if 'country' in child.get('href'):
                    country = child.text
                else:
                    country = ''

            # Appending all the variables fetched to the list array below
            movie_data['movie_details'].append(
                {'title': title, 'summary': summary, 'country': country, 'rating': float(rating), 'user_views': float(users_view),
                'year': year, 'time': dur, 'tv_pg': tv_pg, 'trailer_url': trailer, 'category1': genre1, 'category2': genre2,
                'category3': genre3, 'category4': genre4})

            get_message('End of the Scraping')
            time.sleep(delay)
            mov_i += 1

    return movie_data, category1, category2, category3, category4, film_type


                                        #### AND FINALLY INSERTING ALL THE INFOS IN THE DATABASE

@user_passes_test(lambda u: u.is_superuser)
def MovieView(request):
    creator = User.objects.get(id=1)
    if request.method == 'POST':
        form = GetLinkForm(request.POST)
        form2 = GetMultiLinkForm(request.POST)
        if form.is_valid():
            movie_data, category1, category2, category3, category4, film_type = single_scraper(form.cleaned_data['url'])
            title = movie_data['movie_details'][0]['title']
            summary = movie_data['movie_details'][0]['summary']
            rating = movie_data['movie_details'][0]['rating']
            view = movie_data['movie_details'][0]['user_views']
            year = movie_data['movie_details'][0]['year']
            time = movie_data['movie_details'][0]['time']
            tv_pg = 0
            trailer = movie_data['movie_details'][0]['trailer_url']
            PlayList.objects.get_or_create(type=film_type, name_en=title, name_fa=title, summary=summary,
                                           imdb_score=rating, is_free=False, year=year, time=time,
                                           tv_pg=tv_pg, trailer_url=trailer, thumb_image=to_url(title) + '.webp',
                                           created_by=creator)
            m = PlayList.objects.get(name_en=title)
            m.page_url = 'movie/' + str(m.id) + '/' + to_url(title) + '/' + to_url(title)
            m.save()

            ### SEASON
            Season.objects.get_or_create(name=1, playlist=m)
            s = Season.objects.get(playlist=m)
            ### ACtor
            i = 0
            for actor in movie_data['actor_details']:
                name = movie_data['actor_details'][i]['name']
                summary = movie_data['actor_details'][i]['summary']
                Actor.objects.get_or_create(name=name, summary=summary, thumb_image=to_url(name) + '.webp')
                a = Actor.objects.get(name=movie_data['actor_details'][i]['name'])
                m.actor.add(a)
                i += 1
            ### DIRECTOR
            try:
                dir_name = movie_data['dir_details'][0]['name']
                dir_bio = movie_data['dir_details'][0]['summary']
                Director.objects.get_or_create(name=dir_name, summary=dir_bio, thumb_image=to_url(dir_name) + '.webp')
                d = Director.objects.get(name=movie_data['dir_details'][0]['name'])
                m.director.add(d)
                try:
                    dir2_name = movie_data['dir_details'][1]['name']
                    dir2_bio = movie_data['dir_details'][1]['bio']
                    Director.objects.get_or_create(name=dir2_name, summary=dir2_bio,
                                                   thumb_image=to_url(dir2_name) + '.webp')
                    d2 = Director.objects.get(name=movie_data['dir_details'][1]['name'])
                    m.director.add(d2)
                except:
                    Exception('director not available')
            except:
                Exception('director not available')

            # COUNTRY
            try:
                Country.objects.get_or_create(name=movie_data['movie_details'][0]['country'])
                country = Country.objects.get(name=movie_data['movie_details'][0]['country'])
                m.country.add(country)
            except:
                Exception('could not insert country')

            ### CATEGORY
            try:
                if len(category1) > 1:
                    c1 = Category.objects.get(index=movie_data['movie_details'][0]['category1'])
                    c1.page_url = category1
                    m.category.add(c1)
            except:
                Exception('Could not innsert category')

            try:
                if len(category2) > 1:
                    c2 = Category.objects.get(index=movie_data['movie_details'][0]['category2'])
                    c2.page_url = category2
                    m.category.add(c2)
            except:
                Exception('Category 2 not inserted')
            try:
                if len(category3) > 1:
                    c3 = Category.objects.get(index=movie_data['movie_details'][0]['category3'])
                    c3.page_url = category3
                    m.category.add(c3)
            except:
                Exception('Category 3 not inserted')
            try:
                if len(category4) > 1:
                    c4 = Category.objects.get(index=movie_data['movie_details'][0]['category4'])
                    c4.page_url = category4
                    m.category.add(c4)
            except:
                Exception('Category 4 not inserted')

            ### EPISODE
            Episode.objects.get_or_create(playlist=m, season=s, stream_url='https://ss.evafilm.stream/ss-video/',
                                          download_url='https://ss.evafilm.stream/dl-video/',
                                          subtitle_vtt_url='https://ss.evafilm.stream/ss-video/',
                                          subtitle_srt_url='https://ss.evafilm.stream/ss-video/')
            ep = Episode.objects.get(playlist=m)
            ep.page_url = 'p/' + str(ep.id) + '/'
            ep.save()
        
        if form2.is_valid():
            movie_data, category1, category2, category3, category4, film_type = multiple_scraper(form2.cleaned_data['multi_url'])
            i = 0
            for movie in movie_data['movie_details']:
                title = movie_data['movie_details'][i]['title']
                summary = movie_data['movie_details'][i]['summary']
                rating = movie_data['movie_details'][i]['rating']
                view = movie_data['movie_details'][i]['user_views']
                year = movie_data['movie_details'][i]['year']
                time = movie_data['movie_details'][i]['time']
                tv_pg = 0
                trailer = movie_data['movie_details'][i]['trailer_url']
                PlayList.objects.get_or_create(type=film_type, name_en=title, name_fa=title, summary=summary,
                                            imdb_score=rating, is_free=False, year=year, time=time,
                                            tv_pg=tv_pg, trailer_url=trailer, thumb_image=to_url(title) + '.webp',
                                            created_by=creator)
                m = PlayList.objects.get(name_en=title)
                m.page_url = 'movie/' + str(m.id) + '/' + to_url(title) + '/' + to_url(title)
                m.save()

                ### SEASON
                Season.objects.get_or_create(name=1, playlist=m)
                s = Season.objects.get(playlist=m)
                ### ACtor
                actor_i = 0
                for actor in movie_data['actor_details']:
                    name = movie_data['actor_details'][actor_i]['name']
                    summary = movie_data['actor_details'][actor_i]['summary']
                    Actor.objects.get_or_create(name=name, summary=summary, thumb_image=to_url(name) + '.webp')
                    a = Actor.objects.get(name=movie_data['actor_details'][actor_i]['name'])
                    m.actor.add(a)
                    actor_i += 1
                ### DIRECTOR
                try:
                    dir_name = movie_data['dir_details'][0]['name']
                    dir_bio = movie_data['dir_details'][0]['summary']
                    Director.objects.get_or_create(name=dir_name, summary=dir_bio, thumb_image=to_url(dir_name) + '.webp')
                    d = Director.objects.get(name=movie_data['dir_details'][0]['name'])
                    m.director.add(d)
                    try:
                        dir2_name = movie_data['dir_details'][1]['name']
                        dir2_bio = movie_data['dir_details'][1]['bio']
                        Director.objects.get_or_create(name=dir2_name, summary=dir2_bio,
                                                    thumb_image=to_url(dir2_name) + '.webp')
                        d2 = Director.objects.get(name=movie_data['dir_details'][1]['name'])
                        m.director.add(d2)
                    except:
                        Exception('director not available')
                except:
                    Exception('director not available')

                # COUNTRY
                try:
                    Country.objects.get_or_create(name=movie_data['movie_details'][0]['country'])
                    country = Country.objects.get(name=movie_data['movie_details'][0]['country'])
                    m.country.add(country)
                except:
                    Exception('could not insert country')

                ### CATEGORY
                try:
                    if len(category1) > 1:
                        c1 = Category.objects.get(index=movie_data['movie_details'][0]['category1'])
                        c1.page_url = category1
                        m.category.add(c1)
                except:
                    Exception('Could not innsert category')

                try:
                    if len(category2) > 1:
                        c2 = Category.objects.get(index=movie_data['movie_details'][0]['category2'])
                        c2.page_url = category2
                        m.category.add(c2)
                except:
                    Exception('Category 2 not inserted')
                try:
                    if len(category3) > 1:
                        c3 = Category.objects.get(index=movie_data['movie_details'][0]['category3'])
                        c3.page_url = category3
                        m.category.add(c3)
                except:
                    Exception('Category 3 not inserted')
                try:
                    if len(category4) > 1:
                        c4 = Category.objects.get(index=movie_data['movie_details'][0]['category4'])
                        c4.page_url = category4
                        m.category.add(c4)
                except:
                    Exception('Category 4 not inserted')

                ### EPISODE
                Episode.objects.get_or_create(playlist=m, season=s, stream_url='https://ss.evafilm.stream/ss-video/',
                                            download_url='https://ss.evafilm.stream/dl-video/',
                                            subtitle_vtt_url='https://ss.evafilm.stream/ss-video/',
                                            subtitle_srt_url='https://ss.evafilm.stream/ss-video/')
                ep = Episode.objects.get(playlist=m)
                ep.page_url = 'p/' + str(ep.id) + '/'
                ep.save()
                i += 1


    else:
        form = GetLinkForm()
        form2 = GetMultiLinkForm()

    # Here I display all the movies that are fetched and inserted in the database on a single HTML page that I created.
    qs = PlayList.objects.all()
    movie_count = qs.count()
    act_qs = Actor.objects.all()
    actor_count = act_qs.count()

    context = {
        'qs': qs,
        'movie_count': movie_count,
        'form': form,
        'form2': form2,
        'actor_count': actor_count,
    }

    return render(request, 'imdb_scraper/main.html', context)