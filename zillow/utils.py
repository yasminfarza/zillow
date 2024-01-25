from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
from pandas import read_csv
import json


import requests
from random import randint

SCRAPEOPS_API_KEY = '07a4f2f6-0748-4bb0-837e-e6bc81b35cf3'

def get_headers_list():
#   response = requests.get('http://headers.scrapeops.io/v1/browser-headers?api_key=' + SCRAPEOPS_API_KEY)
#   json_response = response.json()
#   return json_response.get('result', [])
    return [
        {
        "authority": "www.zillow.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,lt;q=0.7",
    },
    {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "upgrade-insecure-requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,lt;q=0.7",
    },
    {
        "Host": "127.0.0.1:65432",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    ]

def get_random_header(header_list):
  random_index = randint(0, len(header_list) - 1)
  return header_list[random_index]


header_list = get_headers_list()

def cookie_parser():
    cookie_string = '_pxvid=cf116793-5ea4-11ee-bc90-285452356a38; zguid=24|%24cf7580da-6294-4a0b-b21e-db2f4beaccdd; _ga=GA1.2.1812983331.1696089611; _gcl_au=1.1.831567837.1696089615; zjs_anonymous_id=%22cf7580da-6294-4a0b-b21e-db2f4beaccdd%22; zjs_user_id=null; zg_anonymous_id=%22c4deb244-07a2-43aa-83ed-477e190abd7f%22; __pdst=10d349c319084187920bad215c9c140a; _pin_unauth=dWlkPU1UbG1Zek0xWkRrdE16SmlPQzAwWWpJNUxUbGxaamN0WXpReE1qUTBZMlZsWldVeg; zgsession=1|80ff386e-d33c-4040-89c7-1dc590909bd8; _gid=GA1.2.1828580235.1701436999; DoubleClickSession=true; pxcts=cce5a0ad-904c-11ee-aacf-b138d3481479; FSsampler=1031129495; _clck=1qe6irt%7C2%7Cfh6%7C0%7C1368; JSESSIONID=CDF3DCC520421A201F83604B4F747960; g_state={"i_p":1703859572891,"i_l":4}; _pxff_tm=1; _hp2_id.1215457233=%7B%22userId%22%3A%225531365861820555%22%2C%22pageviewId%22%3A%226506294918371924%22%2C%22sessionId%22%3A%226756906636994045%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _hp2_ses_props.1215457233=%7B%22ts%22%3A1701440713184%2C%22d%22%3A%22www.zillow.com%22%2C%22h%22%3A%22%2F%22%7D; _gat=1; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; _pxff_cfp=1; _pxff_bsco=1; AWSALB=2T+oQHWnSUK6wB9ebPNK+CUVtbf3mZvV5V17kJ55Y+J3Yon8IFF0HhE9MhWbNkA7PogDsHYibNBFScm1kS+R8G8+cM4LP2vQMDZ+cLJWNDGdLeGSZEqF2Yp/fPOz; AWSALBCORS=2T+oQHWnSUK6wB9ebPNK+CUVtbf3mZvV5V17kJ55Y+J3Yon8IFF0HhE9MhWbNkA7PogDsHYibNBFScm1kS+R8G8+cM4LP2vQMDZ+cLJWNDGdLeGSZEqF2Yp/fPOz; _px3=610194be473957a01f30e1f9cc57c3eb08077100ab6dff5e3da0c31cc44aad7a:fKxcfPu4Y3DzY+xKcAdM70Fm2s2BQb/e2SGDIsPQZZQmcAI1kT9ViXjFVSuIQhTgSuZS6qAejaEVQGT6CQYTeg==:1000:bIkDkbDjSM6pfrIShp0/ML8D+7MPKYiZd6077RAiXJkoWJIECbhGwHxtvveCbZJ+81BI3aDiBV4d5tu4y4aPNk85TBN+NC4MFjBEwNIiLjBMVBW0KLh3TWybQfVYjzkfyTtNe7nVKYg213cm1HOEl72doiGt2g8Z368N/9JLSWVDk6eDZI/iW+9BAAK4LdPZvzOZCwV7EYQipIML6IYYLqMMvCzM/8allCKNSlxJVHI=; _uetsid=dcd2fb90904c11eea1f6ef2e66e81dbb; _uetvid=79402f905faa11ee9242c31316c69a86; search=6|1704032809598%7Crect%3D40.137992%2C-74.955763%2C39.848844%2C-75.295343%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D1%26listPriceActive%3D1%26type%3Dhouse%2Ccondo%2Ctownhouse%2Capartment%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26excludeNullAvailabilityDates%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%09%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Afalse%7D%09%09%09%09%09; _clsk=8d6zws%7C1701440813676%7C5%7C0%7Cu.clarity.ms%2Fcollect'
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    cookies = {}

    for key, morsel in cookie.items():
        cookies[key] = morsel.value

    return cookies


def parse_new_url(url, page_number, request_id):
    url_parsed = urlparse(url)
    query_string = parse_qs(url_parsed.query)
    query_string.get("requestId")[0] = request_id
    search_query_state = json.loads(query_string.get("searchQueryState")[0])
    search_query_state["pagination"] = {"currentPage": page_number}
    query_string.get("searchQueryState")[0] = search_query_state
    encoded_qs = urlencode(query_string, doseq=1)
    new_url = f"https://www.zillow.com/search/GetSearchPageState.htm?{encoded_qs}"
    return new_url




def get_home_id():
    # reading CSV file
    # data = read_csv("Rent_1_Dec_23.csv")

    # # converting column data to list
    # home_ids = data["home_id"].tolist()
    # return sorted(home_ids)
    return []

# def duplicate_value(mylist):
    
#     import numpy as np
    
#     unique, counts = np.unique(mylist, return_counts=True)
#     new_list = unique[np.where(counts > 1)]
 
#     print(new_list)

# if __name__ == "__main__":
#     duplicate_value(get_home_id())

def binary_search(alist, item):
    if not alist:  # list is empty -- our base case
        return False

    midpoint = len(alist) // 2
    if alist[midpoint] == item:  # found it!
        return True

    if item < alist[midpoint]:  # item is in the first half, if at all
        return binary_search(alist[:midpoint], item)

    # otherwise item is in the second half, if at all
    return binary_search(alist[midpoint + 1:], item)


# testlist = [0, 1, 2, 8, 13, 17, 19, 32, 42]
# binary_search(testlist, 3)  # => False
# binary_search(testlist, 13)  # => True