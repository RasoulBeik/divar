import time
import random
import json
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import simple_request
import jalali
from persiantext import PersianText

class Divar:
    def __init__(self, city, category):
        self.__city__ = city
        self.__category__ = category
        return

    def get_url(self, city=None, category=None):
        city = self.__city__ if city is None else city
        category = self.__category__ if category is None else category
        return 'https://divar.ir/s/{}/{}'.format(city, category)

    def get_post_info(self, post_url, verbose=True):
        post_url = post_url.replace('\n', '')
        if verbose:
            print('** get_post_info:', post_url)

        post_values = {}
        post_values['post_id'] = post_url.split('/')[-1]

        try:
            url = 'https://divar.ir{}'.format(post_url)
            post = BeautifulSoup(simple_request.simple_get(url), 'html.parser')
            post_values['get_date'] = str(datetime.now().date())
            post_values['post_date'] = post.find('span', class_='post-header__publish-time').text
            post_types = post.find_all('div', class_='section')
            if post_types:
                post_values['main_category']  = post_types[-2].text
                post_values['sub_category'] = post_types[-1].text
            post_fields = post.find_all('div', class_='post-fields-item')
            for pf in post_fields:
                try:
                    post_values[pf.span.text] = pf.div.text if pf.div else pf.a.text if pf.a else None
                except AttributeError:
                    continue
        except AttributeError:
            pass
        except Exception:
            return None
        return post_values

    def get_posts_url(self, city=None, category=None, max_pages=1, post_date_before='دیروز', file_path=None, verbose=True):
        url = self.get_url(city, category)

        if verbose:
            print('** get_posts_url:', url)

        try:
            browser = webdriver.Firefox(firefox_binary = '/opt/firefox-dev/firefox')
            browser.get(url)

            len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            match = False
            pages = 0
            div_index_offset = 48
            while not match:
                last_count = len_of_page
                len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if last_count == len_of_page:
                    match = True

                time.sleep(random.randint(3, 6))

                # max_pages is used to prevent scrolling to the end of page.
                pages = pages + 1
                if pages >= max_pages:
                    break

                div_index = 24 * (pages-1) + div_index_offset
                try:
                    post_time_div = browser.find_element_by_xpath('/html/body/div[1]/div[2]/main/div[1]/div[2]/a[{}]/div[1]/div[3]'.format(div_index))
                    if post_date_before in post_time_div.text:
                        break
                except NoSuchElementException:
                    if verbose:
                        print(match, 'Page', pages, 'ERROR! Post not found! Waiting ...')
                    time.sleep(random.randint(6, 10))
                    continue
                except Exception as e:
                    print('UNKNOWN ERROR!!!!!', e)
                    continue

                if verbose:
                    print('{} Page {}/{}, {}'.format(match, pages, max_pages, PersianText.reshape(post_time_div.text)))

            time.sleep(3)
            posts_html = BeautifulSoup(browser.page_source, 'html.parser')
            posts_div = posts_html.find('div', class_='browse-post-list')
            posts_a = posts_div.find_all('a', class_='col-xs-12')
            posts_href = [pa['href'] for pa in posts_a]
            
            if file_path:
                with open(file_path, 'w') as fp:
                    fp.write('\n'.join(posts_href))
            return posts_href
        except TimeoutException:
            return None
        except WebDriverException:
            return None

    def browse_and_save_items(self, urls_file_path, items_file_path, from_index, to_index=None, verbose=True):
        if verbose:
            print('** browse_and_save_items:', urls_file_path, items_file_path)
            
        # ITEMS_PER_PAGE = 24
        # max_pages = round(max_items/ITEMS_PER_PAGE)
        # posts_url = self.get_posts_url(max_pages=max_pages)

        with open(urls_file_path, 'r') as fp:
            posts_url = fp.readlines()

        if os.path.exists(items_file_path):
            fp = open(items_file_path, 'r')
            posts_items = json.load(fp)
            fp.close()
        else:
            posts_items = []

        if to_index is None:
            to_index = len(posts_url)
        for url in posts_url[from_index:to_index]:
            items = self.get_post_info(url)
            if items:
                posts_items.append(items)
            # time.sleep(random.random())
            # time.sleep(random.randint(0, 2))
        posts_items_str = json.dumps(posts_items)
        with open(items_file_path, 'w') as fp:
            fp.write(posts_items_str)

        print('*** Last index:', to_index)
        if to_index >= len(posts_url):
            print('***** End of URLs reached. ***')
        return

# --------------------------------------------------------------------------
if __name__ == "__main__":
    # city = 'karaj'
    city = 'isfahan'
    # city = 'mashhad'
    # city = 'shiraz'
    category = 'real-estate'

    gd = str(datetime.now().date())
    jd = jalali.Gregorian(gd).persian_string(date_format='{}{:02d}{:02d}')
    urls_file_path = './data/{}--{}--{}.url'.format(city, category, jd)
    items_file_path = './data/{}--{}--{}.json'.format(city, category, jd)

    divar = Divar(city=city, category=category)
    # divar.get_posts_url(city=city, category=category, max_pages=3000, post_date_before='هفتهٔ پیش', file_path=urls_file_path)

    divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=13000, to_index=14000)

    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=0, to_index=1000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=1000, to_index=2000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=2000, to_index=3000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=3000, to_index=4000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=4000, to_index=5000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=5000, to_index=6000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=6000, to_index=7000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=7000, to_index=8000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=8000, to_index=9000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=9000, to_index=10000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=10000, to_index=11000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=11000, to_index=12000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=12000, to_index=13000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=13000, to_index=14000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=14000, to_index=15000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=15000, to_index=16000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=16000, to_index=17000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=17000, to_index=18000)
    # time.sleep(random.randint(10, 20))
    # *divar.browse_and_save_items(urls_file_path=urls_file_path, items_file_path=items_file_path, from_index=18000)

    # posts = divar.get_posts_url(max_pages=3)
    # print(len(posts))
    # post_items = divar.get_post_info('/v/103متر-فول-کلیدنخورده-ستارخان_آپارتمان_تهران_ستارخان_دیوار/gX4qmViT')
    # print(post_items)
    # s = json.dumps(post_items)
    # fp = open('test.json', 'w')
    # fp.write(s)
    # fp.close()
    # fp = open('test.json', 'r')
    # items = json.load(fp)
    # print(items)
    pass
