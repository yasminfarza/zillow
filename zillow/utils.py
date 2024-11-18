from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
import pandas as pd
import json
from zillow import settings


def cookie_parser():
    cookie_string = settings.COOKIES
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    return {key: morsel.value for key, morsel in cookie.items()}


def get_home_id():
    # Read the CSV and directly get sorted 'home_id' column
    if file := settings.FILENAME:
        return pd.read_csv(file)["home_id"].sort_values().tolist()
    return []

def get_zillow_url():
    # Read the CSV and directly get sorted 'Zillow url' column
    if file := settings.FILENAME:
        return pd.read_csv(file)["Zillow url"].sort_values().tolist()
    return []

    
def binary_search(alist, item):
    low, high = 0, len(alist) - 1  # Initialize pointers

    while low <= high:
        midpoint = (low + high) // 2  # Find the midpoint

        # If types mismatch, convert item to the type of the list element (only once)
        if isinstance(alist[midpoint], str):
            item = str(item)

        if alist[midpoint] == item:
            return True  # Found the item

        elif alist[midpoint] < item:
            low = midpoint + 1  # Search the right half

        else:
            high = midpoint - 1  # Search the left half

    return False  # If the item is not found

