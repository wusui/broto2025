# Copyright (C) 2025 Warren Usui, MIT License
"""
General I/O routines
"""
import os
import json
import unicodedata
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_webpage(html_page):
    """
    Extract webpage data using selenium.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    wval = WebDriverWait(driver, 100)
    driver.get(html_page)
    wval.until(EC.presence_of_all_elements_located(
                (By.TAG_NAME, "table")))
    norm_text = unicodedata.normalize('NFD', driver.page_source)
    return norm_text.encode('ascii', 'ignore').decode('utf-8')

def save_data(out_data, fname):
    """
    Stash json output in file.
    """
    json_data = json.dumps(out_data, indent=4)
    ofile = os.sep.join(['data', f'b{fname}.json'])
    with open(ofile, 'w', encoding='utf-8') as outfile:
        outfile.write(json_data)
