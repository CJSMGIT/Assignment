from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import pandas as pd
import pymysql
import logging
import csv

class redbus:
    # Function to open the URL
    def open_url(url):
        try:
            option = Options()
            option.add_argument('--disable-notifications')
            driver = webdriver.Chrome(options=option)
            driver.get(url)
            logging.info("Page loaded successfully")
            return driver
        except Exception as e:
            logging.error(f"Error occurred when initializing WebDriver: {e}")
            return None

    # Maximize the browser window
    def maximize_window(driver):
        try:
            driver.maximize_window()
            print("Window maximized")
        except Exception as e:
            print("Error occurred when maximizing the window:", e)

    # Scroll down the page
    def scrolling(driver, times=3):
        try:
            for _ in range(times):
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
            print("Page scrolled")
        except Exception as e:
            print("Error occurred when scrolling the page:", e)

    def safe_find_element_with_refresh(driver, xpath, timeout=10, retries=1):
        """
        Tries to find an element by XPath with timeout. 
        If a TimeoutException occurs, it refreshes the page and retries.
        """
        attempts = 0
        while attempts < retries:
            try:
                # Attempt to find the element within the timeout period
                time.sleep(5)
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                return element  # If found, return the element
            except TimeoutException as e:
                print(f"TimeoutException: {e}. Attempt {attempts + 1}/{retries}. Ignoring and proceeding with the next steps...")
                attempts += 1  # Increment retry attempt count
                time.sleep(10)  # Wait for the page to load before retrying
        return None  # Return None if the element was not found after retries

    # Scroll to a specific element
    def scroll_to_element(driver, element):
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
        except Exception as e:
            print(f"Error scrolling to element: {e}")

    def save_data_to_csv(data, file_name):
        df = pd.DataFrame(data)
        df.to_csv(file_name, mode='a', header=False, index=False)

    def extract_government_name(driver):
        bus_names = []
        govt_bus_links = []
        state_text_list = []
        extract_govt_detail = {}
        
        # Navigate to RTC bus directory
        view_all = driver.find_element(By.CLASS_NAME, "rtcHeadViewAll")
        rtc_bus_directory = view_all.find_element(By.TAG_NAME, "a").get_attribute("href")
        driver.get(rtc_bus_directory)
        
        # Extract all states and their bus information
        all_state_list = driver.find_elements(By.XPATH, "//ul[@class='D113_ul_region_rtc']")
        
        for each_state in all_state_list:
            state_list = each_state.find_elements(By.XPATH, ".//li[not(@class='D113_item_rtc')]")  # Correct XPath for state items
            for state in state_list:
                state_text = state.text
                print(f"State: {state_text}")
                
                # Get bus names and links
                bus_name_elements = each_state.find_elements(By.XPATH, ".//li[@class='D113_item_rtc']")
                for bus_element in bus_name_elements:
                    bus_name = bus_element.text
                    bus_link = bus_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    # Append to respective lists
                    bus_names.append(bus_name)
                    govt_bus_links.append(bus_link)
                    
                    print(f"Bus Name: {bus_name}, Bus Link: {bus_link}")
                    state_text_list.append(state_text)
                extract_govt_detail = {
                    "state_text": state_text_list,
                    "bus_names": bus_names,
                    "govt_bus_links": govt_bus_links
                }
                print(extract_govt_detail)
        return bus_names, govt_bus_links, extract_govt_detail, state_text_list

    def route(driver,bus_names, govt_bus_links):
        route_link = []
        route_title = []
        govt_bus_names = []
        route_list = {}  
        bus_fare=[] # Initialize dictionary to store routes
        
        # Extract bus names and links
        # bus_names, govt_bus_links, extract_govt_detail, state_text_list = extract_government_name(driver)
        
        for bus_name, govt_bus_link in zip(bus_names, govt_bus_links):
            
            driver.get(govt_bus_link)
            time.sleep(2)
            
            # Check if pagination exists
            paginationTables = driver.find_elements(By.XPATH, "//div[@class='DC_117_paginationTable']//div[@class='DC_117_pageTabs ']")
            if paginationTables:
                for paginationTable in paginationTables:
                    route_details = driver.find_elements(By.CLASS_NAME, "route_details")
                    for route_detail in route_details:
                        route_link.append(route_detail.find_element(By.TAG_NAME, "a").get_attribute("href"))
                        route_text = route_detail.text
                        route_text, fare = route_text.split("\n", 1)
                        fare = fare.replace("From INR ", "")
                        route_title.append(route_text)
                        bus_fare.append(fare)
                        govt_bus_names.append(bus_name)
                    
                    # Scroll to the element (if necessary) and wait before clicking next pagination
                    c1.scroll_to_element(driver, paginationTable)
                    time.sleep(3)
                    paginationTable.click()
                    
                    print(f"Route Titles: {route_title}")
                    print(f"Route Links: {route_link}")
            
            # Store route details in a dictionary (ensure it's for all buses)
            route_list[bus_name] = {
                "route_titles": route_title,
                "route_links": route_link
            }

        return govt_bus_names, route_title, route_link, bus_fare

    # Extract bus details from each route
    def bus_details(driver, each_route_title, each_route_link):
        bus_datas = []
        all_id = []

        driver.get(each_route_link)
        next_button = c1.safe_find_element_with_refresh(driver, "//div[@class='onward d-block fl']//span[@class='next']", timeout=10, retries=3)
        time.sleep(3)
        if next_button:
            driver.execute_script("arguments[0].click();", next_button)

            time.sleep(20)
                        # Pause time to allow content to load
            SCROLL_PAUSE_TIME = 0.5

            # Get the initial scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to the bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for the page to load
                time.sleep(SCROLL_PAUSE_TIME)
                
                # Calculate new scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                
                # Break the loop if no new content is loaded
                if new_height == last_height:
                    break
                
                last_height = new_height
            
            # all_route_titles.append(route_titles)
            # all_route_links.append(route_links)
        
            time.sleep(20)
            start_element = c1.safe_find_element_with_refresh(driver, "//ul[@class='bus-items']", timeout=10, retries=3)
            if start_element:
                
                bus_details_Each = driver.find_elements(By.XPATH, "//ul[@class='bus-items']//li[@class='row-sec clearfix']")
                for each_id in bus_details_Each:
                    bus_details_Each_id = each_id.get_attribute("id")
                    all_id.append(bus_details_Each_id)

                for list_id in all_id:
                    try:
                        travel_element = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-two p-right-10 w-30 fl']//div[1]").text
                    except NoSuchElementException:
                        travel_element = None

                    try:
                        coach_element = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-two p-right-10 w-30 fl']//div[2]").text
                    except NoSuchElementException:
                        coach_element = None

                    try:
                        start_element = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-three p-right-10 w-10 fl']").text
                        length_start_elements=start_element.count("\n")
                        if length_start_elements==1:
                            start_time, start_bus_stand = start_element.split("\n", 1)
                        else:
                            start_time, start_bus_stand= None, None
                    except NoSuchElementException:
                        start_time, start_bus_stand = None, None

                    try:
                        duration_element = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-four p-right-10 w-10 fl']").text
                    except NoSuchElementException:
                        duration_element = None

                    try:
                        end_elements = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-five p-right-10 w-10 fl']").text
                        length_end_elements = end_elements.count("\n")
                        if length_end_elements == 3:
                            end_time, date, end_bus_stand = end_elements.split("\n", 2)
                        elif length_end_elements == 2:

                            end_time, end_bus_stand = end_elements.split("\n", 1)
                            date = None
                        elif length_end_elements == 1 or 0:
                            end_time, end_bus_stand, date = None, None, None

                    except NoSuchElementException:
                        end_time, end_bus_stand, date = None, None, None

                    try:
                        rating_element = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-six p-right-10 w-10 fl']").text
                        length_rating_element = rating_element.count("\n")
                        if length_rating_element == 1:
                            rating, persons = rating_element.split("\n", 1)
                        else:
                            rating = rating_element
                            rating = 0 if rating_element == '' else rating_element
                            persons = 0
                    except NoSuchElementException:
                        rating, persons = 0, 0

                    try:
                        seats_left_element = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-eight w-15 fl']").text
                        length_seats_left_element = seats_left_element.count("\n")
                        if length_seats_left_element == 1:
                            seats_left, windows = seats_left_element.split("\n", 1)
                        else:
                            seats_left = seats_left_element
                            windows = 0
                    except NoSuchElementException:
                        seats_left, windows = 0, 0

                    try:
                        rate_element = driver.find_element(By.XPATH, f"//ul[@class='bus-items']//li[@id={list_id}]//div[@class='column-seven p-right-10 w-15 fl']//div[@class='fare d-block']//span").text
                    except NoSuchElementException:
                        rate_element = 0
                    
                    bus_data = {
                        'bus_id': list_id,
                        'route_title': each_route_title,
                        'route_link': each_route_link,
                        'travel_name': travel_element,
                        'coach': coach_element,
                        'start_time': start_time,
                        'start_bus_stand': start_bus_stand,
                        'duration': duration_element,
                        'end_time': end_time,
                        'end_bus_stand': end_bus_stand,
                        'date': date,
                        'rating': rating,
                        'persons': persons,
                        'rate': rate_element,
                        'seats_left': seats_left,
                        'window': windows
                    }
                    bus_datas.append(bus_data)
        return bus_datas


    # MySQL connection and data insertion
    def mysql_connection(driver, batch_size=30000):
        try:
            # Connect to the MySQL database using PyMySQL
            mydb = pymysql.connect(
                host="localhost",
                user="root",
                password="root",
                database="RED_BUS_DATA"
            )
            
            # Create a cursor object
            mycursor = mydb.cursor()
            
            # Create a database if it does not exist
            mycursor.execute("CREATE DATABASE IF NOT EXISTS RED_BUS_DATA")
            mycursor.execute("USE RED_BUS_DATA")

            file_name = 'governmentbusdata.csv'
            file_name1 = 'routedetails.csv'
            file_name2 = 'busdetails.csv'

            bus_names, govt_bus_links, extract_govt_detail, state_text_list = c1.extract_government_name(driver)
            
            # Create table for govt bus details if not exists
            create_govt_bus_table = """
                CREATE TABLE IF NOT EXISTS redbus_govt_bus (
                    region VARCHAR(255),
                    government_bus_name VARCHAR(255),
                    links VARCHAR(255)
                )
            """
            mycursor.execute(create_govt_bus_table)
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Prepare and insert government bus details in batches
                writer.writerow(['Region Name', 'Bus Name', 'Government Bus Link'])
                govt_bus_data = [
                    (region_name, bus_name, govt_link)
                    for region_name, bus_name, govt_link in zip(state_text_list, extract_govt_detail["bus_names"], extract_govt_detail["govt_bus_links"])
                ]
                
                for i in range(0, len(govt_bus_data), batch_size):
                    batch = govt_bus_data[i:i+batch_size]
                    mycursor.executemany("INSERT INTO redbus_govt_bus (region, government_bus_name, links) VALUES (%s, %s, %s)", batch)
                
                    mydb.commit()
                    writer.writerows(batch)
                    


            # Now, process route data
            govt_bus_names, route_title, route_link, bus_fare = c1.route(driver, bus_names, govt_bus_links)

            # Create table for route details if not exists
            create_route_details = """
                CREATE TABLE IF NOT EXISTS redbus_route_details (
                    government_bus_name VARCHAR(255),
                    route_title VARCHAR(255),
                    bus_fare_starts_from INT,
                    route_link VARCHAR(255)
                )
            """
            mycursor.execute(create_route_details)
            with open(file_name1, mode='w', newline='') as file1:
                writer = csv.writer(file1)
                # Prepare and insert route data in batches
                writer.writerow(['Government Bus Name', 'Route Title', 'Fare', 'Route Link'])
                route_data = [
                    (govt_bus_name, route_titles, int(money), route_links)
                    for govt_bus_name, route_titles, money, route_links in zip(govt_bus_names, route_title, bus_fare, route_link)
                ]
                
                for i in range(0, len(route_data), batch_size):
                    batch = route_data[i:i + batch_size]
                    sql2 = "INSERT INTO redbus_route_details (government_bus_name, route_title, bus_fare_starts_from, route_link) VALUES (%s, %s, %s, %s)"
                    mycursor.executemany(sql2, batch)
                    mydb.commit()  # Commit each batch
                    writer.writerows(batch)
                
                # Create table for bus details if not exists
            create_bus_details_table = """
                    CREATE TABLE IF NOT EXISTS redbus_bus_details (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        bus_id VARCHAR(255) UNIQUE,
                        route_title VARCHAR(255),
                        route_link VARCHAR(255),
                        travel_name VARCHAR(255),
                        coach VARCHAR(255),
                        start_time VARCHAR(255),
                        start_bus_stand VARCHAR(255),
                        duration VARCHAR(255),
                        end_time VARCHAR(255),
                        end_bus_stand VARCHAR(255),
                        date VARCHAR(255),
                        rating VARCHAR(255),
                        persons INT,
                        bus_fare INT,
                        seats_left INT,
                        windows VARCHAR(255)
                    )
                """
            mycursor.execute(create_bus_details_table)

            # File to store bus details
            file_name2 = 'busdetails.csv'
            with open(file_name2, mode='w', newline='') as file2:
                writer = csv.writer(file2)
                # Write header (Optional, depending on structure)
                writer.writerow(['Bus ID', 'Route Title', 'Route Link', 'Travel Name', 'Coach', 'Start Time', 'Start Bus Stand', 
                                'Duration', 'End Time', 'End Bus Stand', 'Date', 'Rating', 'Rate', 'Persons', 'Seats Left', 'Window'])
            
                for each_route_title, each_route_link in zip(route_title, route_link):
                    # Now, process bus details
                    bus_datas = c1.bus_details(driver, each_route_title, each_route_link)

                
                    # Prepare and insert bus details in batches
                    bus_details_data = [
                        (
                            bus_data['bus_id'], bus_data['route_title'], bus_data['route_link'],
                            bus_data['travel_name'], bus_data['coach'], bus_data['start_time'],
                            bus_data['start_bus_stand'], bus_data['duration'], bus_data['end_time'],
                            bus_data['end_bus_stand'], bus_data['date'], bus_data['rating'],
                            float(''.join(filter(str.isdigit, bus_data['rate']))) if bus_data['rate'] else 0,
                            bus_data['persons'], 
                            int(''.join(filter(str.isdigit, bus_data['seats_left']))) if bus_data['seats_left'] else 0,  # Extract integer value from seats_left
                            bus_data['window']              )
                        for bus_data in bus_datas

                    ]

                    for i in range(0, len(bus_details_data), batch_size):
                        batch = bus_details_data[i:i + batch_size]
                        sql3 = """
                            INSERT IGNORE INTO redbus_bus_details 
                            (bus_id, route_title, route_link, travel_name, coach, start_time, start_bus_stand, 
                            duration, end_time, end_bus_stand, date, rating, persons, bus_fare, seats_left, windows) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        mycursor.executemany(sql3, batch)
                        mydb.commit()  # Commit each batch
                        writer.writerows(batch)
            print("Data inserted into redbus_govt_bus table successfully")
        except Exception as e:
            print(f"Error occurred while inserting data into the database: {e}")

# URL of the RedBus website
url = "https://www.redbus.in/"

# Open the URL using the open_url function
c1=redbus
driver = c1.open_url(url)
if driver:
    c1.maximize_window(driver)
    c1.scrolling(driver)
    c1.mysql_connection(driver)
    driver.quit()

