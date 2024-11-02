from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
from pandas import read_csv
import json


def cookie_parser():
    cookie_string = 'zguid=24|%24e407de08-dc0a-44e0-b1d8-73e80700c6ce; zgsession=1|e9f221ca-b993-4270-88e2-da3e7f12ec90; zjs_anonymous_id=%22e407de08-dc0a-44e0-b1d8-73e80700c6ce%22; zjs_user_id=null; zg_anonymous_id=%22a6f6bca0-6691-40f9-8f26-e4c0e2d3363f%22; _ga=GA1.2.1149609097.1730056765; _gid=GA1.2.2024784294.1730056765; pxcts=6144ddeb-9498-11ef-816c-d53c9eabac19; _pxvid=6144d37d-9498-11ef-816c-5cf6b7a805c4; _gcl_au=1.1.1360065301.1730056767; _tt_enable_cookie=1; _ttp=LDt9C1a7VWVe8qftnoIU2VV43qf; _scid=HBxdVgmcNNGRkfutcS5rujkhGdDVNc_-; _pin_unauth=dWlkPVpETmlZekZpWVRrdE5HUmpZeTAwWlRnekxXSmtNRFF0WVRjMk56WTVPVGxrTjJJeg; DoubleClickSession=true; _ScCbts=%5B%5D; _sctr=1%7C1730052000000; FSsampler=30183893; _clck=1untuzj%7C2%7Cfqe%7C0%7C1761; JSESSIONID=2F032818CEDABBD95779775031FBAB97; _rdt_uuid=1730056767134.919fa33b-bccb-4182-bb75-3c5f4d04d552; _scid_r=JpxdVgmcNNGRkfutcS5rujkhGdDVNc_-PBZ4-g; _px3=6a1158ccb1ec9cf333cd44367e806f7ae84bb95e3c86b4de30c95c0fddd029d7:Oa9ly2KyuHO2Da3y9Crdze9Fgfoa5Rh8MQdChWguY49lEHWm0RgH17LXjtrh3Ob1BuhrHp/1e5v5W9mKn36jLA==:1000:prfKXyWBBLVQaLpfsBAlEsn4AS0nVTK9xd3sLLyFjhcPFl5mNJ6Iz/k3W3vqqJxnCGyj0Nxcjj3aUtET1dE25xSkcbEDEwCuqo2v0nkECsuEKpyBTHW6GyB18v3lSK9K94LHx4N/7G3V4xgq8tyZerlRn8c91EG26rO+YmLn2OXYZqIWJ9ni9I3w6tzCxLiuO+bKMmzzW7ssx5wqkU5wbhNqNxSW2MsgySD6yUyU+M4=; AWSALB=GQvDB3nUWjbaVw89XA/MvZrtsDSl2WIxtB5JBtkvWtIzTkdX3FcEJEtkw+EWrcib8pZgG3c+TmCYP/FOP1ndqOlp+uNgyst0NX4i17kbDI5vu7SpZI5GMFjrGVec; AWSALBCORS=GQvDB3nUWjbaVw89XA/MvZrtsDSl2WIxtB5JBtkvWtIzTkdX3FcEJEtkw+EWrcib8pZgG3c+TmCYP/FOP1ndqOlp+uNgyst0NX4i17kbDI5vu7SpZI5GMFjrGVec; _uetsid=6229d0f0949811efb3699f37c8408317; _uetvid=6229dca0949811ef933783761be78084; _clsk=xri9ds%7C1730131093841%7C8%7C0%7Cu.clarity.ms%2Fcollect; search=6|1732723094212%7Crect%3D40.137992%2C-74.955763%2C39.848844%2C-75.295343%26rid%3D13271%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26listPriceActive%3D1%26type%3Dhouse%2Ccondo%2Ctownhouse%2Capartment%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26singlestory%3D0%26housing-connector%3D0%26parking-spots%3Dnull-%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26student-housing%3D0%26income-restricted-housing%3D0%26military-housing%3D0%26disabled-housing%3D0%26senior-housing%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26ita%3D0%26stl%3D0%26fur%3D0%26os%3D0%26ca%3D0%26np%3D0%26hasDisabledAccess%3D0%26hasHardwoodFloor%3D0%26areUtilitiesIncluded%3D0%26highSpeedInternetAvailable%3D0%26elevatorAccessAvailable%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%0913271%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Afalse%7D%09%09%09%09%09'
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
    # data = read_csv("25_04_23.csv")

    # # converting column data to list
    # home_ids = data["home_id"].tolist()
    # return sorted(home_ids)
    return []

def get_zillow_url():
    # reading CSV file
    # data = read_csv("25_04_23.csv")

    # # converting column data to list
    # zillow_urls = data["Zillow url"].tolist()
    # return sorted(zillow_urls)
    return []

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
