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

# url = ' https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%27usersSearchTerm%27%3A+%27Philadelphia%2C+PA%27%2C+%27mapBounds%27%3A+%7B%27west%27%3A+-75.295343%2C+%27east%27%3A+-74.955763%2C+%27south%27%3A+39.848844%2C+%27north%27%3A+40.137992%7D%2C+%27isMapVisible%27%3A+False%2C+%27filterState%27%3A+%7B%27isForSaleByAgent%27%3A+%7B%27value%27%3A+False%7D%2C+%27isForSaleByOwner%27%3A+%7B%27value%27%3A+False%7D%2C+%27isNewConstruction%27%3A+%7B%27value%27%3A+False%7D%2C+%27isForSaleForeclosure%27%3A+%7B%27value%27%3A+False%7D%2C+%27isComingSoon%27%3A+%7B%27value%27%3A+False%7D%2C+%27isAuction%27%3A+%7B%27value%27%3A+False%7D%2C+%27isForRent%27%3A+%7B%27value%27%3A+True%7D%2C+%27isAllHomes%27%3A+%7B%27value%27%3A+True%7D%2C+%27isMultiFamily%27%3A+%7B%27value%27%3A+False%7D%2C+%27isManufactured%27%3A+%7B%27value%27%3A+False%7D%2C+%27isLotLand%27%3A+%7B%27value%27%3A+False%7D%7D%2C+%27isListVisible%27%3A+True%2C+%27regionSelection%27%3A+%5B%7B%27regionId%27%3A+13271%7D%5D%2C+%27pagination%27%3A+%7B%27currentPage%27%3A+21%7D%7D&wants=%7B%22cat1%22%3A%5B%22listResults%22%5D%2C%22regionResults%22%3A%5B%22regionResults%22%5D%7D&requestId=13'

def cookie_parser():
    cookie_string = 'zguid=24|%24a7e27322-3a0e-4326-b418-e8aa4c07519e; _ga=GA1.2.1940155959.1710689132; _pxvid=98d9e8c1-e472-11ee-bc8b-b5ba793165aa; zjs_anonymous_id=%22a7e27322-3a0e-4326-b418-e8aa4c07519e%22; zjs_user_id=null; zg_anonymous_id=%226bfd33f3-c430-4d46-8d40-7a9ff04ed61f%22; _gcl_au=1.1.1649066619.1710689135; __pdst=afe2ba49c9444fbea6ef80ced25c9d69; _fbp=fb.1.1710689136507.609940117; _pin_unauth=dWlkPU5URmpOMlJqWlRRdE9UVTNPQzAwWW1NeExUazJZemd0TnpNM1pXRXlZbVE1TW1RNA; FSsampler=419012691; zgsession=1|8cc1928f-4375-4f60-af92-d17212139a95; pxcts=9ba44664-ea8f-11ee-b951-c4585d93a625; JSESSIONID=EA8EA888E0635A3A74D1CE531E5D1722; _gid=GA1.2.1428057759.1711361302; DoubleClickSession=true; _hp2_id.1215457233=%7B%22userId%22%3A%224640597236753568%22%2C%22pageviewId%22%3A%222426717364600698%22%2C%22sessionId%22%3A%22880331524317276%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; tfpsi=74e9a543-a812-4b15-97b9-a32372d4b2a7; _clck=1v2asss%7C2%7Cfkd%7C0%7C1537; _hp2_ses_props.1215457233=%7B%22ts%22%3A1711361306164%2C%22d%22%3A%22www.zillow.com%22%2C%22h%22%3A%22%2F%22%7D; _pxff_tm=1; __gads=ID=e128818d8ac9cf1c:T=1710689241:RT=1711361359:S=ALNI_MaDuF-uXAAZ8_PvGThIyhM-kWZtUg; __gpi=UID=00000d3e16131912:T=1710689241:RT=1711361359:S=ALNI_MZsSTVVs4A0SwiHuCg3MEcS1ZC2pg; __eoi=ID=c4eaef58a3ee243d:T=1710689241:RT=1711361359:S=AA-AfjYLXIuCtG0_lu5eGBSvRUX9; search=6|1713953450696%7Crb%3DPhiladelphia%252C-PA%26rect%3D40.137992%252C-74.955763%252C39.848844%252C-75.295343%26disp%3Dmap%26mdm%3Dauto%26sort%3Dpersonalizedsort%26listPriceActive%3D1%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%09%0913271%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Afalse%7D%09%09%09%09%09; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; _pxff_cfp=1; _pxff_bsco=1; AWSALB=4iKF0/UNpnxLCr0PVynvSILbmGceTzd0iqZ66LNINDVIQj5l1C0SOozavLQzK39Z4r6/S5rRdCCNxIhqYA4cHn6aw2Cj0lqj4jhztFWw9RZ3EyXox/QdbCdKF0V1; AWSALBCORS=4iKF0/UNpnxLCr0PVynvSILbmGceTzd0iqZ66LNINDVIQj5l1C0SOozavLQzK39Z4r6/S5rRdCCNxIhqYA4cHn6aw2Cj0lqj4jhztFWw9RZ3EyXox/QdbCdKF0V1; _gat=1; _px3=a0bc56f836b3e8b5f3075d853863d7951b6cd8c6e2744da75210dc01d73600f3:FJP8FB0PYKrSpm46jPFjP+JgnbKD0AQy6SIqxAQVsqc5vb8ym2JRU5A0y9YGjLd3sCqwalrxZjE4e+Xb1lEH/Q==:1000:YJiFXs71Nx9MCREaZKPRNkvVq1+ixnK75qpdhkG2Iqj8JyL01MiUEZlEbd2wYu35n5UkSL+OsAFVfJxpz7PQwXnBMr8h8gBkwI09CSjyvpRihymEDCwxHNJmBaTH3u2SxxN6+/mogk1PyAp/qdB/Qp3M8BnZoa8RvcF540larDxK23LpDP2dY0Z7wsdJmdkj25mjrexsLInbn5IsmCDM1x4UNrw8weajH20sdggt4jE=; _uetsid=9e7a1140ea8f11ee8a6721c1fd6af208; _uetvid=9a68fe70e47211eeb734b78faf876523; _clsk=12smhqt%7C1711361479242%7C3%7C0%7Ck.clarity.ms%2Fcollect'
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
    data = read_csv("25-march-24.csv")

    # converting column data to list
    home_ids = data["home_id"].tolist()
    return sorted(home_ids)
    # return []

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