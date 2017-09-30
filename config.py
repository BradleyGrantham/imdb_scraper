import os

'''
Hardcoded configurations
'''

IMDB_URL = 'http://www.imdb.com'

DATA_DIR = './data/'
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

IMAGES_DIR = './images/'

ACTOR_LINKS_FILEN = os.path.join(DATA_DIR, 'actor_links.csv')

GALLERY_LINKS_FILEN = os.path.join(DATA_DIR, 'gallery_links.csv')

PICTURE_LINKS_FILEN = os.path.join(DATA_DIR, 'picture_links.csv')

CHROMEDRIVER = './Chromedriver/chromedriver'
