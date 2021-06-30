#https://medium.com/ymedialabs-innovation/web-scraping-using-beautiful-soup-and-selenium-for-dynamic-page-2f8ad15efe25
#https://www.selenium.dev/documentation/en/worst_practices/file_downloads/ - use libcurl to download files

import os
import time
import json
import re
from private.config import url
from selenium import webdriver

PATH =  os.path.join("c:", os.sep, "Program Files (x86)", "chromedriver.exe")
download_folder = os.path.join("c:", os.sep, "Users", "Daniel", "Desktop", "2021-07-01 REALIS automation", "period_data")

saved_files = []

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
prefs = {"download.default_directory" : download_folder}
options.add_experimental_option("prefs",prefs)


#market_segment = "CCR"

YEAR, MONTH = "year", "month"
FROM, TO = "from", "to"

# Load REALIS project names
try:
    with open("project_names.txt") as file:
        project_names = json.load(file)
except:
    project_names = []


def main():
    load()
    agree()
    navigate()
    select_project()
    select_dates()
    search()
    download()
    logout()


"""
User functions
"""
def load():
    global driver 
    driver = webdriver.Chrome(PATH, options=options)
    driver.get(url)

def agree():
    # Click "Agree and Continue"
    driver.find_element_by_xpath("//button[text()='Agree and Continue']").click()

def navigate():
    # Click on resi > transaction > transaction search
    driver.find_element_by_xpath("//a[contains(text(),'Residential')]").click()
    driver.implicitly_wait(2)
    driver.find_element_by_xpath("//a[contains(text(),'Residential')]").find_element_by_xpath("..//*[contains(text(),'Transaction')]").click()
    driver.find_element_by_xpath("//a[contains(text(),'Residential')]").find_element_by_xpath("//*[contains(text(),'Transaction Search')]").click()

def select_project():
    # project name checker
    def enter_project_name():
        raw = input("Enter project name:\n")
        # print(raw)
        if raw.upper() in project_names:
            return raw.upper()
        else:
            print("Project name not in REALIS database.")
            return None
    
    # Input project name
    global project_name
    project_name = enter_project_name()
    if not project_name:
        print("Please re-enter project name")
        return
    # Select project by name
    driver.find_element_by_xpath("//*[@data-placeholder='Select project or location']").click()
    driver.implicitly_wait(6)
    driver.find_element_by_xpath(
        "//div[@id='projectName']"
        "//input[@placeholder='Project name']").send_keys(project_name)
    driver.find_element_by_xpath(
        "//div[@id='projectName']"
        "//div[@class='checkbox']"
        fr"//input[@value='{project_name}']").click()
    driver.find_element_by_id("apply").click()

def update_project_names():
    # Select project by name
    driver.find_element_by_xpath("//*[@data-placeholder='Select project or location']").click()
    
    # Update project_names.txt via json
    # also update dates
    # collect project name and dates upfront before loading chrome
    pass

def update_dates():
    pass

def select_dates():
    global dates
    dates = {FROM: {YEAR: None, MONTH: None},
             TO: {YEAR: None, MONTH: None}}
    
    # Select from and to dates
    def enter_dates():
        pattern = "^\d{2} \d{4}$"
        raw = input(f"Input start (from) date in MM YYYY format:\n")
        if re.findall(pattern, raw):
            temp = raw.split()
            dates[FROM][MONTH] = str(int(temp[0]))
            dates[FROM][YEAR] = temp[1]
        raw = input(f"Input end (to) date in MM YYYY format:\n")
        if re.findall(pattern, raw):
            temp = raw.split()
            dates[TO][MONTH] = str(int(temp[0]))
            dates[TO][YEAR] = temp[1]
        if dates[FROM][MONTH] in all_months and dates[TO][MONTH] in all_months:
            if dates[FROM][YEAR] in all_years and dates[TO][YEAR] in all_years:
                return dates
        print("Invalid entry, please re-enter dates.")
        return None
        
    # Collect all_years
    saleYearFrom = driver.find_element_by_id("saleYearFrom")
    saleYearFrom.click()
    all_years = []
    for element in saleYearFrom.find_elements_by_xpath("./option"):
        all_years.append(element.get_attribute("value"))
    all_years = [i for i in all_years if i]
    
    # Collect all_months
    saleMonthFrom = driver.find_element_by_id("saleMonthFrom")
    saleMonthFrom.click()
    all_months = []
    for element in saleMonthFrom.find_elements_by_xpath("./option"):
        all_months.append(element.get_attribute("value"))
    all_months = [i for i in all_months if i]
    
    # Select dates
    dates = enter_dates() 
    if dates is None:
        return
    
    # Input selected from dates
    saleYearFrom.find_element_by_xpath(f"//option[@value={dates[FROM][YEAR]}]").click()
    saleMonthFrom.find_element_by_xpath(f"//option[@value={dates[FROM][MONTH]}]").click()
    
    # Input selected to dates
    saleYearTo = driver.find_element_by_id("saleYearTo")
    saleYearTo.click()
    saleYearTo.find_element_by_xpath(f"./option[@value={dates[TO][YEAR]}]").click()
    saleMonthTo = driver.find_element_by_id("saleMonthTo")
    saleMonthTo.click()
    saleMonthTo.find_element_by_xpath(f"./option[@value={dates[TO][MONTH]}]").click()


def search():
    #search
    driver.find_element_by_id("submitSearch").click()


def download():
    download_folder_nfiles = 0
    
    #download file
    driver.find_element_by_xpath("//button//span[contains(text(),'Download')]").find_element_by_xpath("..").click()
    download_links = driver.find_elements_by_class_name("downloadCSV")
    #download_links[0].click()
    driver.find_element_by_xpath("//button//span[contains(text(),'Download')]").find_element_by_xpath("..").click()
    
    print(f"Total of {len(download_links)} file(s) to download")
    
    for link in download_links:
        driver.find_element_by_xpath("//button//span[contains(text(),'Download')]").find_element_by_xpath("..").click()
        link.click()
        print(f"Downloading file number: {int(download_folder_nfiles)+1}")
        
        # wait/test if a new file has arrived
        while download_folder_nfiles == len(os.listdir(download_folder)):
            time.sleep(3)
        
        download_folder_nfiles += 1
        time.sleep(3)
        
        # rename new file
        for file in os.listdir(download_folder):
            if file not in saved_files:
                new_file_name = "transaction_" + dates[FROM][MONTH] + "_" + dates[FROM][YEAR] + " " + str(download_folder_nfiles) + ".csv"
                try:
                    os.rename(os.path.join(download_folder, file), os.path.join(download_folder, new_file_name))
                except:
                    pass
                saved_files.append(new_file_name)
    
    os.startfile(download_folder)


def logout():
    #logout of account
    driver.find_element_by_xpath("//a[contains(text(),'My Account')]").click()
    driver.find_element_by_xpath("//a[contains(text(),'My Account')]").find_element_by_xpath("..//a[contains(text(),'Logout')]").click()
    
    #close webdriver
    driver.quit()

