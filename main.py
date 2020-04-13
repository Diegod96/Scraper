
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from os import path
from url import *


class Job:

    def __init__(self):
        self.driver = webdriver.Chrome(r"C:\Program Files\chromedriver")  # Path of Chrome web driver
        self.delay = 10  # The delay the driver gives when loading the web page

    # Load up the web page
    # Gets all relevant data on the page
    # Goes to next page until we are at the last page
    def load_craigslist_url(self, url):
        data = []
        self.driver.get(url)
        while True:
            try:
                wait = WebDriverWait(self.driver, self.delay)
                wait.until(EC.presence_of_element_located((By.ID, "searchform")))
                data.append(self.extract_post_titles())
                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="searchform"]/div[3]/div[3]/span[2]/a[3]'))).click()
            except:
                break
        return data

    # # Extracts all relevant information from the web-page and returns them as individual lists
    def extract_post_titles(self):
        all_posts = self.driver.find_elements_by_class_name("result-row")

        dates_list = []
        titles_list = []
        prices_list = []
        distance_list = []

        for post in all_posts:

            title = post.text.split("$")

            if title[0] == '':
                title = title[1]
            else:
                title = title[0]

            title = title.split("\n")
            price = title[0]
            title = title[-1]
            title = title.split(" ")
            month = title[0]
            day = title[1]
            title = ' '.join(title[2:])
            date = month + " " + day

            if not price[:1].isdigit():
                price = "0"
            int(price)

            raw_distance = post.find_element_by_class_name(
                'maptag').text
            distance = raw_distance[:-2]

            titles_list.append(title)
            prices_list.append(price)
            dates_list.append(date)
            distance_list.append(distance)

        return titles_list, prices_list, dates_list, distance_list

    # # Kills browser
    def kill(self):
        self.driver.close()

    @staticmethod
    def organizeResults(results):
        titles_list = results[0][0]
        prices_list = list(map(int, results[0][1]))
        dates_list = results[0][2]
        distance_list = list(map(float, results[0][3]))

        list_of_attributes = []

        for i in range(len(titles_list)):
            content = {'Listing': titles_list[i], 'Price': prices_list[i], 'Date posted': dates_list[i],
                       'Distance from zip': distance_list[i]}
            list_of_attributes.append(content)

        list_of_attributes.sort(key=lambda x: x['Distance from zip'])

        return list_of_attributes

    @staticmethod
    def to_csv(dictionary):
        df = pd.DataFrame(dictionary)
        df.to_csv('data.csv', index=False)


if __name__ == '__main__':

    # This should be called only once!!!
    # Then the 'url' should be used every time main.py is built and ran, and not be constructed again by calling 'UrlObj().url'

    if not path.exists('url.txt'):
        url = UrlObj().url
        text_file = open('url.txt', 'w')
        text_file.write(url)


    x = open('url.txt', 'r')
    y = x.read()
    scraper = Job()
    results = scraper.load_craigslist_url(y)
    scraper.kill()
    dictionary_of_listings = scraper.organizeResults(results)
    scraper.to_csv(dictionary_of_listings)


