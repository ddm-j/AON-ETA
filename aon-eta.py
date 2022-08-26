import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import sys
import os
from scipy.stats import linregress
import datetime
import pandas as pd
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
import time

def parse_date(text):
    data = text.split("Time: ")[1]
    data = pd.to_datetime(data)
    return data

def parse_time(text):
    data = text.split("Time: ")[1]
    dhms=data.split(':')
    extra_hours = int(dhms[0])*24
    hours = int(dhms[1])+extra_hours
    hms = ':'.join([str(hours)]+dhms[-2:])
    data = pd.to_timedelta(hms)
    return data

def parse_percentage(text):
    data = float(text.split(' ')[1][:-1])
    return data

def extrapolate(x, y):
    result = linregress(x, y)
    return pd.to_datetime(100.0*result.slope + result.intercept)

def main(sample_rate, n):

    url = 'http://10.10.10.37/'
    browser = webdriver.Chrome("chromedriver.exe", options=chrome_options)

    browser.get(url)

    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    time.sleep(2)

    job = None
    p = None
    start = None
    elapsed = None
    for element in browser.find_elements_by_class_name('status-pair'):
        if "Job" in element.text:
            job = element
        elif "Complete" in element.text:
            p = element
        elif "Start" in element.text:
            start = element
        elif "Elapsed" in element.text:
            elapsed = element


    print_start = parse_date(start.text)
    data = pd.DataFrame(columns=['p'])
    data.loc[print_start] = 0.0

    while 1:
        # Get Status Information
        percentage = parse_percentage(p.text)
        dt = parse_time(elapsed.text)

        # Add to dataframe
        data.loc[print_start+dt] = percentage

        # Extrapolate Finish time
        if len(data) > n:
            eta = extrapolate(data[-n:].to_numpy().T[0], data.index[-n:].values.astype('float'))
        else:
            eta = extrapolate(data.to_numpy().T[0], data.index.values.astype('float'))

        os.system('cls')
        sys.stdout.write('{0}\nCompletion: {1}%\nETA: {2}           '.format(job.text, percentage, eta))

        time.sleep(sample_rate)

main(300, 30)
#body = soup.find('body')
#topdiv = body.find('div')
#print(topdiv)

