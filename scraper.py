from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from pandas import DataFrame, ExcelWriter
import json


class CraigslistScraper(object):

    # Constructor of the URL that is being scraped
    def __init__(self):
        self.location = self.get_location()  # Location(i.e. City) being searched
        self.postal_code = self.get_postal_code()  # Postal code of location being searched
        self.max_price = self.get_max_price()  # Max price of the items that will be searched
        self.query = self.get_query()  # Search for the type of items that will be searched
        self.radius = self.get_radius()  # Radius of the area searched derived from the postal code given previously

        self.url = f"https://{self.location}.craigslist.org/search/sss?&max_price={self.max_price}&postal={self.postal_code}&query={self.query}&20card&search_distance={self.radius}"
        self.driver = webdriver.Chrome(r"C:\Program Files\chromedriver")  # Path of Chrome web driver
        self.delay = 5  # The delay the driver gives when loading the web page


    def get_location(self):
        location = input("Please enter the location: ")
        return location

    def get_postal_code(self):
        postal_code = input("Please enter the postal code: ")
        return postal_code

    def get_query(self):
        query = input("Please enter the item: ")
        return query

    def get_max_price(self):
        max_price = input("Please enter the max price: ")
        return max_price

    def get_radius(self):
        radius = input("Please enter the radius: ")
        return radius

    def return_url(self):
        return self.url


    # Load up the web page
    # Gets all relevant data on the page
    # Goes to next page until we are at the last page
    def load_craigslist_url(self):

        data = []
        self.driver.get(self.return_url())
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

    # Extracts all relevant information from the web-page and returns them as individual lists
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

    # Kills browser
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

    # # Gets price value from dictionary and computes average
    # @staticmethod
    # def get_average(sample_dict):
    #
    #     price = list(map(lambda x: x['Price'], sample_dict))
    #     sum_of_prices = sum(price)
    #     length_of_list = len(price)
    #     average = round(sum_of_prices / length_of_list)
    #
    #     return average
    #
    # # Displays items around the average price of all the items in prices_list
    # @staticmethod
    # def get_items_around_average(avg, sample_dict, counter, give):
    #     print("Items around average price: ")
    #     print("-------------------------------------------")
    #     raw_list = []
    #     for z in range(len(sample_dict)):
    #         current_price = sample_dict[z].get('Price')
    #         if abs(current_price - avg) <= give:
    #             raw_list.append(sample_dict[z])
    #     final_list = raw_list[:counter]
    #     for index in range(len(final_list)):
    #         print('\n')
    #         for key in final_list[index]:
    #             print(key, ':', final_list[index][key])
    #
    # # Displays nearest items to the zip provided
    # @staticmethod
    # def get_items_around_zip(sample_dict, counter):
    #     final_list = []
    #     print('\n')
    #     print("Closest listings: ")
    #     print("-------------------------------------------")
    #     x = 0
    #     while x < counter:
    #         final_list.append(sample_dict[x])
    #         x += 1
    #     for index in range(len(final_list)):
    #         print('\n')
    #         for key in final_list[index]:
    #             print(key, ':', final_list[index][key])

    @staticmethod
    def to_csv(dictionary):
        df = pd.DataFrame(dictionary)
        df.to_csv('data.csv', index=False)


if __name__ == "__main__":
    scraper = CraigslistScraper()  # Constructs the URL with the given parameters
    results = scraper.load_craigslist_url()  # Inserts the result of the scrapping into a large multidimensional list
    scraper.kill()
    dictionary_of_listings = scraper.organizeResults(results)
    scraper.to_csv(dictionary_of_listings)
    scraper.to_excel(dictionary_of_listings)



    # # Below function calls:
    #     # # Get average price and prints it
    #     # # Gets/prints listings around said average price
    #     # # Gets/prints 5 nearest listings
    #
    #     # average = scraper.get_average(list_of_attributes)
    #     # print(f'Average price of items searched: ${average}')
    #     # num_items_around_average = int(input("How many listings around the average price would you like to see?: "))
    #     # avg_range = int(input("Range of listings around the average price: "))
    #     # scraper.get_items_around_average(average, list_of_attributes, num_items_around_average, avg_range)
    #     # print("\n")
    #     # num_items = int(input("How many items would you like to display based off of proximity to zip code?: "))
    #     # print(f"Items around you: ")
    #     # scraper.get_items_around_zip(list_of_attributes, num_items)
    #     # print("\n")
    # print(f"Link of listings : {scraper.url}")
