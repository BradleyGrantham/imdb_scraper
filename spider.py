import os
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import config

'''
TODO
Need to rewrite get_picture_links() so that it gets all the picture links (at the moment) it is only getting
the picture links for the first 6 actors
Need to delete all the current actor directories
Then need to rewrite get_images() so that it gets more than just the first 4 pictures

The functions in this actually run independently of each other. They just read in the relevant csv and spit
out a new one
'''

def get_actor_links():
    '''
    Uses the list of top 250 rated movies on IMDb and gets a list of the most prominent actors from those
    250 films
    :return: actor_links.csv
    '''
    r = requests.get(config.IMDB_URL + '/chart/top?ref_=nv_mv_250_6')
    soup = BeautifulSoup(r.content, 'lxml')

    movies = soup.find_all('tbody', {'class':'lister-list'})

    actual_movies = movies[0].find_all('a', href=True)

    movie_links = [movie['href'] for movie in actual_movies]

    actor_links = {}
    for movie_link in movie_links:
        r = requests.get(config.IMDB_URL + movie_link)
        soup_ = BeautifulSoup(r.content, 'lxml')
        actors = soup_.find_all('td', {'itemprop': 'actor'})
        for actor in actors:
            actor_links[actor.find_next('span').text] = actor.find_next('a', href=True)['href']

    df = pd.DataFrame(data=list(actor_links.items()), columns = ['name', 'link'])
    df.drop_duplicates(inplace=True)
    df.to_csv(config.ACTOR_LINKS_FILEN)


def get_gallery_links():
    '''
    This adds a column to actor_links.csv. The new column includes a link to each of the actors
    respective 'galleries' (a place where their pictures are stored)
    :return: gallery_links.csv
    '''
    actor_links = pd.read_csv(config.ACTOR_LINKS_FILEN, index_col=0)
    gallery_links = []
    for link in actor_links.link:
        r = requests.get(config.IMDB_URL + link)
        soup_ = BeautifulSoup(r.content, 'lxml')
        gallery_links.append(soup_.find_all('div', {'class': 'see-more'})[0].find_next('a', href=True)['href'])
    actor_links['gallery_link'] = gallery_links
    actor_links.columns = ['name', 'actor_link', 'gallery_link']
    actor_links.to_csv(config.GALLERY_LINKS_FILEN)


def get_picture_links():
    '''
    This adds a column to gallery_links.csv. The new column includes a list of links to individual pictures
    :return: picture_links.csv
    '''
    gallery_links = pd.read_csv(config.GALLERY_LINKS_FILEN, index_col=0)
    all_picture_links = []
    for gallery_link in gallery_links['gallery_link']:
        r = requests.get(config.IMDB_URL + gallery_link)
        soup_ = BeautifulSoup(r.content, 'lxml')
        links = soup_.find_all('a', {'itemprop': 'thumbnailUrl'})
        picture_links = [link['href'] for link in links]
        all_picture_links.append(picture_links)
    gallery_links['picture_links'] = pd.Series(all_picture_links)
    gallery_links.to_csv(config.PICTURE_LINKS_FILEN)


def get_images():
    '''
    Using picture_links, this goes through and downloads the images of the actor, storing them in directories
    :return: directories, named by actor, of images of that actor
    '''
    driver = webdriver.Chrome(config.CHROMEDRIVER)
    picture_links = pd.read_csv(config.PICTURE_LINKS_FILEN)
    picture_links['picture_links'] = picture_links['picture_links'].apply(eval)  # convert picture links to lists
    for index, row in picture_links.iterrows():
        num=0
        dirc = os.path.join(config.IMAGES_DIR, row['name'])
        if not os.path.exists(dirc):
            os.makedirs(dirc)
        for picture_link in row['picture_links']:
            driver.get(config.IMDB_URL + picture_link)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            pictures = soup.find_all('img', {'class': 'pswp__img'})
            with open(os.path.join(dirc, str(num) + '.jpeg'), 'wb') as f:
                f.write(requests.get(pictures[3]['src']).content)
            num += 1
    driver.quit()


if __name__ == '__main__':

    # get_actor_links()
    # get_gallery_links()
    get_picture_links()
    get_images()
