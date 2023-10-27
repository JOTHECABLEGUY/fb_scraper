# Author: jordan dube
# Date: 2023-10-26
# Version: 1.0.1
# Usage: python main.py

# Import the necessary libraries.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import getpass
import os
import time
import sqlite3
import tkinter as tk
import customtkinter as ctk
import pandas as pd

# Define a Selenium class to automate the browser.
class Selenium():
    # Define a method to initialize the browser.
    def __init__(self):
        global USER
        # Close the Chrome instance if it is already running.
        os.system("taskkill /f /im chrome.exe")
        # Set the options for the Chrome browser.
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # Add a user data directory as an argument for options.
        chrome_options.add_argument(
            f"--user-data-dir=C:\\Users\\{USER}\\AppData\\Local\\Google\\Chrome\\User Data")
        chrome_options.add_argument("profile-directory=Default")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--headless=new')

        # Initialize the Chrome browser using the ChromeDriverManager.
        self.browser = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options)

    # Define a method to get the page source using Selenium.
    def get_page_source(self, url):
        # Try to get the page source.
        try:
            # Load the URL.
            self.browser.get(url)
            
            # Wait for the page to load.
            WebDriverWait(self.browser, 20).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class='x9f619 x1n2onr6 x1ja2u2z']")))

            for i in range(1, 5):
                # Scroll down to the bottom of the page to load all items.
                self.browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")

                # Wait for the page to finish loading.
                sleep(5)
            

            # Get the page source.
            page_source = self.browser.page_source
            
            return page_source

        # Catch any exceptions.
        except TimeoutException:
            print("Timed out waiting for page to load.")
            return None

        except NoSuchElementException:
            print("Element not found.")
            return None

    # Define a method to close the browser.
    def close_browser(self):
        self.browser.quit()

    # Define a method tp scrape the Facebook Marketplace page using Selenium, BeautifulSoup, and SQLite.
    def scrape_facebook_marketplace(self, max_price = 0, min_price = 0, query = None, categories = None, location = None, listbox = None, condition = ""):
        global URL, CATEGORIES

        start = time.time()
        # Initialize the Selenium class.
        # sel = Selenium()
        rows = []
        headers = ['image', 'price', 'title', 'condition', 'location', 'category', 'url']
        # Initialize the database connection.
        db_path = f"{os.getcwd()}/facebook_marketplace.db"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Create the tables if they don't exist.
        c.execute('''CREATE TABLE IF NOT EXISTS facebook_marketplace_posts
                  (id INTEGER PRIMARY KEY, title TEXT, image TEXT, price TEXT, location TEXT, category TEXT, url TEXT, condition TEXT, date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        cats = []
        if categories:
            for index in categories:
                cats.append(CATEGORIES[index])
        if categories:
            for category in cats:
                URL = URL.replace('category', f"{category}")
                if max_price:
                    URL = URL.replace('max_price', f"maxPrice={max_price}&")
                else:
                    URL = URL.replace('max_price', f"")
                if min_price:
                    URL = URL.replace('min_price', f"minPrice={min_price}&")
                else:
                    URL = URL.replace('min_price', f"")
                if query:
                    URL = URL.replace('query', f"query={query}&")
                else:
                    URL = URL.replace('query', f"")
                if location:
                    URL = URL.replace('location', f"{location}/")
                else:
                    URL = URL.replace('location', f"")
                if condition:
                    URL = URL.replace('item_cond', f"itemCondition={condition}&")
                else:
                    URL = URL.replace('item_cond', f"")
                URL = URL.strip('&')
                # Keeping the number of iterations below 5 for now to avoid getting blocked by Facebook and also to keep the results from being too far away from Pullman.
                for i in range (1, 5):
                    # Scroll down to the bottom of the page to load all items.
                    self.browser.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    # Sleep for 5 seconds then scroll again.
                    time.sleep(1)
               
                # Get the page source using Selenium.
                page_source = self.get_page_source(URL)
                # Parse the page source using BeautifulSoup.
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Get the items.
                div = soup.find_all('div', class_='x8gbvx8 x78zum5 x1q0g3np x1a02dak x1nhvcw1 x1rdy4ex xcud41i x4vbgl9 x139jcc6')
                # print(len(div))
                # print(div[0].find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft').text.strip())
                # Iterate through the items.
                for d in div:
                    # print(d)
                    try:
                        # Get the item image.
                        image = d.find('img', class_='xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3')['src']
                        # Get the item title from span.
                        title = d.find('span', class_ = 'x1lliihq x6ikm8r x10wlt62 x1n2onr6').text.strip()
                         # Get the item price.
                        price = d.find('span', class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u').text.strip()
                        # Get the item URL.
                        url = d.find('a', class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv')['href']
                        # Get the item location.
                        location = d.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84').text.strip()
                        url = "https://www.facebook.com" + url
                        # Print the item information.
                        print(f"Image: {image}")
                        print(f"Price: {price}")
                        print(f"Title: {title}")
                        print(f"Location: {location}")
                        print(f"Category: {category}")
                        print(f"Condition: {condition.replace('%2C', ' OR ')}")
                        print(f"URL: {url}")
                        print("------------------------")
                        rows.append([image, price, title, condition.replace('%2C', " OR "), location, category, url])
                        # Add the item to the database including the image.
                        c.execute("INSERT INTO facebook_marketplace_posts (title, image, price, location, category, URL, condition) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, image, price, location, category, URL, condition.replace('%2C', " OR ")))
                        conn.commit()
                    except Exception as e:
                        # print(str(e))
                        # print(d)
                        pass
        else:
            URL = URL.replace('category', "")
            if max_price:
                URL = URL.replace('max_price', f"maxPrice={max_price}&")
            else:
                URL = URL.replace('max_price', f"")
            if min_price:
                URL = URL.replace('min_price', f"minPrice={min_price}&")
            else:
                URL = URL.replace('min_price', f"")
            if query:
                URL = URL.replace('query', f"query={query}&")
            else:
                URL = URL.replace('query', f"")
            if location:
                URL = URL.replace('location', f"{location}/")
            else:
                URL = URL.replace('location', f"")
            if condition:
                URL = URL.replace('item_cond', f"itemCondition={condition}&")
            else:
                URL = URL.replace('item_cond', f"")
            URL = URL.strip('&')
            # Keeping the number of iterations below 5 for now to avoid getting blocked by Facebook and also to keep the results from being too far away from Pullman.
            for i in range (1, 5):
                # Scroll down to the bottom of the page to load all items.
                self.browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                # Sleep for 5 seconds then scroll again.
                time.sleep(1)
           
            # Get the page source using Selenium.
            page_source = self.get_page_source(URL.strip('&'))

            # Parse the page source using BeautifulSoup.
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Get the items.
            div = soup.find_all('div', class_='x8gbvx8 x78zum5 x1q0g3np x1a02dak x1nhvcw1 x1rdy4ex xcud41i x4vbgl9 x139jcc6')
            # print(len(div))
            # print(div[0].find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft').text.strip())
            # Iterate through the items.
            for d in div:
                # print(d)
                try:
                    # Get the item image.
                    image = d.find('img', class_='xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3')['src']
                    # Get the item title from span.
                    title = d.find('span', class_ = 'x1lliihq x6ikm8r x10wlt62 x1n2onr6').text.strip()
                     # Get the item price.
                    price = d.find('span', class_='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u').text.strip()
                    # Get the item URL.
                    url = d.find('a', class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv')['href']
                    # Get the item location.
                    location = d.find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84').text.strip()

                    url = "https://www.facebook.com" + url
                    # Print the item information.
                    print(f"Image: {image}")
                    print(f"Price: {price}")
                    print(f"Title: {title}")
                    print(f"Location: {location}")
                    # print(f"Category: {category}")
                    print(f"Condition: {condition.replace('%2C', ' OR ')}")
                    print(f"URL: {url}")
                    print("------------------------")
                    rows.append([image, price, title, condition.replace('%2C', " OR "), location, "", url])
                    # Add the item to the database including the image.
                    c.execute("INSERT INTO facebook_marketplace_posts (title, image, price, location, category, URL, condition) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, image, price, location, "", url, condition.replace('%2C', " OR ")))
                    conn.commit()
                except Exception as e:
                    # print(str(e))
                    # print(d)
                    pass

        print(f"found {len(rows)} items in {time.time()-start:.3f} seconds of scraping. \nSearch URL used: {URL}")
        df = pd.DataFrame(rows, columns = headers)
        csv_path = f'{os.getcwd()}/web_scraping_output.csv'
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode = 'a', header = False, index = False)
        else:
            df.to_csv(csv_path, mode = 'w', header = True, index = False)
        
        # Close the database connection.
        conn.close()
        
        # Close the browser.
        self.close_browser()

        print(f"output of this scrping session can be found in the file at {csv_path}, or in the SQLite Database at {db_path}")
        return

class MainWindow(ctk.CTk):
    def __init__(self):
        global LOCATIONS, CATEGORIES, CONDITIONS
        super().__init__()
        ctk.set_appearance_mode("dark")

        # Set the window title and size.
        self.title("Facebook Marketplace Scraper")
        self.geometry("600x600")
        r = 0
        self.search_label = ctk.CTkLabel(self, text = "search query: ")
        self.search_label.grid(row = r, column = 0)
        self.search_entry = ctk.CTkEntry(self)
        self.search_entry.grid(row = r, column = 1)
        r += 1
        self.min_price_label = ctk.CTkLabel(self, text = "Minimum price: ")
        self.min_price_label.grid(row = r, column = 0)
        self.min_price_entry = ctk.CTkEntry(self)
        self.min_price_entry.grid(row = r, column = 1)
        r += 1
        self.max_price_label = ctk.CTkLabel(self, text = "Maximum price: ")
        self.max_price_label.grid(row = r, column = 0)
        self.max_price_entry = ctk.CTkEntry(self)
        self.max_price_entry.grid(row = r, column = 1)
        r += 1
        self.conditions_label = ctk.CTkLabel(self, text = "Select desired qualities below")
        self.conditions_label.grid(row = r, column = 0, columnspan = 2)
        r += 1 
        new_sv = tk.IntVar(value = 0)
        u_ln_sv = tk.IntVar(value = 0)
        u_g_sv = tk.IntVar(value = 0)
        u_f_sv = tk.IntVar(value = 0)
        self.intvars = [new_sv, u_ln_sv, u_g_sv, u_f_sv]
        self.condition_checkboxes = [ctk.CTkCheckBox(self, text = cond, variable = var, onvalue = 1, offvalue = 0) for (cond, var) in zip(CONDITIONS, self.intvars)]
        for cb in self.condition_checkboxes:
            cb.grid(row = r, column = 1, columnspan = 2)
            r += 1
        r += 1
        self.local = tk.StringVar(value = list(LOCATIONS.keys())[0])
        self.local_label = ctk.CTkLabel(self, text = "Location: ")
        self.local_label.grid(row = r, column = 0)
        self.local_combobox = ctk.CTkComboBox(self, values = LOCATIONS.keys(), variable = self.local)
        self.local_combobox.grid(row = r, column = 1)
        r += 1
        self.listbox_label = ctk.CTkLabel(self, text = "Select categories to check: ")
        self.listbox_label.grid(row = r, columnspan = 3)

        r += 1
        self.cat_listbox = tk.Listbox(self, selectmode = tk.MULTIPLE)
        for cat in CATEGORIES:
            self.cat_listbox.insert(tk.END, cat)
        self.cat_listbox.grid(row = r, column = 0, columnspan = 3)
        r += 1
        # Add a label to the window.
        self.label = ctk.CTkLabel(self, text="Click the button to start scraping Facebook Marketplace.")
        self.label.grid(row = r, column = 1, columnspan = 2)
        r += 1
        # Add a button to the window.
        self.button = ctk.CTkButton(self, text="Scrape Marketplace", command=self.scrape_marketplace, corner_radius = 10)
        self.button.grid(row = r, column = 1, columnspan = 2)
        r += 2
        # Add a label to write "Developed by" to the window.
        self.label = ctk.CTkLabel(self, text="Developed by: Jordan Dube")
        self.label.grid(row = r, column = 2, rowspan = 2)

    # Define a method to scrape Facebook Marketplace.
    def scrape_marketplace(self):
        global CONDITIONS, LOCATIONS
        # Initialize the Selenium class.
        sel = Selenium()
        try:
            query = self.search_entry.get()
        except:
            query = ""
        try:
            min_price = self.min_price_entry.get()
        except:
            min_price = 0
        try:
            max_price = self.max_price_entry.get()
        except:
            max_price = 0
        condition = ""
        for (var, cond) in zip(self.intvars, CONDITIONS):
            try:
                if var.get():
                    condition += f"{cond}%2C"
            except:
                continue
        condition = condition.rstrip('%2C')
        location = self.local.get()
        categories = self.cat_listbox.curselection()
        # Call the scrape_facebook_marketplace method.
        sel.scrape_facebook_marketplace(max_price, min_price, query, categories, LOCATIONS[location], self.cat_listbox, condition)

if __name__ == "__main__":
    global URL, LOCATIONS, CATEGORIES, USER, CONDITIONS
    URL = 'https://www.facebook.com/marketplace/locationcategory?sortBy=creation_time_descend&exact=false&deliveryMethod=local_pick_up&min_pricemax_pricequeryitem_cond'
    LOCATIONS = {'colonial_heights': '111769818838660', 'richmond': 'richmond'}
    CATEGORIES = ['appliances', 'electronics', 'furniture', 'vehicles', 'propertyrentals', 
                    'apparel', 'classifieds', 'entertainment', 'family', 'free', 'garden', 
                    'hobbies', 'home', 'home-improvements', 'propertyforsale', 'instruments',
                    'office-supplies', 'pets', 'sports', 'toys', 'boats']
    USER = getpass.getuser()
    CONDITIONS = ['new', 'used_like_new', 'used_good', 'used_fair']
    app = MainWindow()
    app.mainloop()

                