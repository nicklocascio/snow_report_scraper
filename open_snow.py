#!/usr/bin/env python3

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

import sys
import os
import re

WEBSITE = 'https://opensnow.com'

def usage(status=0):
    '''
    Display program usage to user
    '''
    print('''Usage: {} [flags]

    -s STATE		Select a state that you want info for
    '''.format(os.path.basename(sys.argv[0])))

    sys.exit(status)

def get_response(state):
    ''' 
    Makes an HTTP GET request on the provided url
    Returns text content if its HTML/XML, otherwise returns None
    '''
    full_url = WEBSITE + '/state/' +  state
    print(full_url)

    try:
        with closing(get(full_url, stream=True)) as response:
            if check_response(response):
                return response.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def check_response(response):
    ''' 
    Returns True of response is HTML, otherwise returns False
    '''
    content_type = response.headers['Content-Type'].lower()
    return (response.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    '''
    Simply prints the errors
    '''
    print(e)

def parse_data(response):
    '''
    Parse the website content for desired information
    '''

    forecast_data = {}
    report_data = {}

    html = BeautifulSoup(response, 'html.parser')
    resorts = html.find_all("div", class_="compare-sort")
    for resort in resorts:
        name = resort.find("div", class_="title-location")

        # Get forecast data
        snow_f = resort.find("div", class_=re.compile("text .*"))
        forecast_data[name.string.strip()] = snow_f.string.strip()

        # Get report data
        snow_r = resort.find("div", class_=re.compile("summary-data-value .*"))
        try:
            report_data[name.string.strip()] = snow_r.string.strip()
        except AttributeError:
            continue
   
    # Display data
    print("\nForecasts:\n")
    for key, value in forecast_data.items():
        print(f'{key:>30}: {value:>5}')
    print("\nReports:\n")
    for key, value in report_data.items():
        print(f'{key:>30}: {value:>5}')

def add_item(data_dict, key, value):
    data_dict[key.string.strip()] = value.string.strip()
    return data_dict

def main():
    # Parse command line arguments
    state = None

    arguments = sys.argv[1:]

    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        # Check flag
        if argument == '-h':
                usage(0)
        elif argument == '-s':
                state = arguments.pop(0)
        else:
                usage(1)

    if state:
        parse_data(get_response(state))
    else:
        usage(1)

if __name__ == '__main__':
    main()
