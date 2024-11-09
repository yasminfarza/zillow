from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
from pandas import read_csv
import json


def cookie_parser():
    cookie_string = 'zguid=24|%24e407de08-dc0a-44e0-b1d8-73e80700c6ce; zgsession=1|e9f221ca-b993-4270-88e2-da3e7f12ec90; zjs_anonymous_id=%22e407de08-dc0a-44e0-b1d8-73e80700c6ce%22; zjs_user_id=null; zg_anonymous_id=%22a6f6bca0-6691-40f9-8f26-e4c0e2d3363f%22; _ga=GA1.2.1149609097.1730056765; pxcts=6144ddeb-9498-11ef-816c-d53c9eabac19; _pxvid=6144d37d-9498-11ef-816c-5cf6b7a805c4; _gcl_au=1.1.1360065301.1730056767; _tt_enable_cookie=1; _ttp=LDt9C1a7VWVe8qftnoIU2VV43qf; _scid=HBxdVgmcNNGRkfutcS5rujkhGdDVNc_-; _pin_unauth=dWlkPVpETmlZekZpWVRrdE5HUmpZeTAwWlRnekxXSmtNRFF0WVRjMk56WTVPVGxrTjJJeg; DoubleClickSession=true; FSsampler=30183893; _sctr=1%7C1730656800000; _ScCbts=%5B%22570%3Bchrome.2%3A2%3A5%22%5D; _gac_UA-21174015-56=1.1730701661.Cj0KCQjwvpy5BhDTARIsAHSilynjC5X6D86-lsJwLqrWRDktewG13nNEw08hBcMg_OQ6qeNwsV09YNgaAtM6EALw_wcB; _gcl_gs=2.1.k1$i1730701658$u52198818; _gcl_aw=GCL.1730701671.Cj0KCQjwvpy5BhDTARIsAHSilynjC5X6D86-lsJwLqrWRDktewG13nNEw08hBcMg_OQ6qeNwsV09YNgaAtM6EALw_wcB; optimizelyEndUserId=oeu1730702326416r0.6930416223827567; zgcus_aeut=AEUUT_71b35b60-9a77-11ef-90cd-16bbc6a8bf0f; zgcus_aeuut=AEUUT_71b35b60-9a77-11ef-90cd-16bbc6a8bf0f; _cs_c=0; kn_cs_visitor_id=36a64613-f5c6-4b7c-940f-67cbeb62c022; _cs_id=58eb3207-0bf8-a188-93da-d7d1bb6f4a22.1730702608.1.1730703114.1730702608.1.1764866608712.1; _gid=GA1.2.888882581.1731091696; _clck=1untuzj%7C2%7Cfqp%7C0%7C1761; JSESSIONID=F8A689E7E64965848987957338F81C65; _rdt_uuid=1730056767134.919fa33b-bccb-4182-bb75-3c5f4d04d552; _scid_r=NZxdVgmcNNGRkfutcS5rujkhGdDVNc_-PBZ4Jg; _dd_s=rum=0&expire=1731101900830; _uetsid=06c89b609e0211ef89f1799cd3b3554f; _uetvid=6229dca0949811ef933783761be78084; AWSALB=8f6D+Wv6rSVSiw9Q2sKD1S5A/yGk93wRFE5jE3Xi0aKD2dyG5Lmbd/OKPStMuGFJh7mBZWGtfhYG00YrNbhqgV1tinusK+xi0ftQOizljflGHZ2gNNekMR1Kp3GW; AWSALBCORS=8f6D+Wv6rSVSiw9Q2sKD1S5A/yGk93wRFE5jE3Xi0aKD2dyG5Lmbd/OKPStMuGFJh7mBZWGtfhYG00YrNbhqgV1tinusK+xi0ftQOizljflGHZ2gNNekMR1Kp3GW; _px3=70a9b7bd1dfd9bdd46384fcd2af99204be96251cf7df00480f3f93b8b83d28b1:O21P01nEtdxjkn8GT41WFiEDeLRTePiKvnNUARWO4WdtD0WssTGl4UD7TvePePKgydRdrTjGQYizzcP4eMneQA==:1000:Kg7d5ZYQJySr2rroPCLqWuQZxWy0UBElVPIvaCNdHU/UcZnZe32PHYDkwCIuaElQ8xLnGXYIrKnttCOUbWQdrvFQgq8Vz6ImIkrssImL0TMA7GMBTAt1AgcFaF0k7cmDWoFkEY01XuJJN2j7E1BMUQmQfk8+x5DzzjtdHY6rRwS2kE5d5orB+tFhFxvFCLRRu9UytQeZMPmPxjL1cYe7x13pLjhVd3xQf1f4qhRTTlk=; search=6|1733693120539%7Crect%3D40.917577%2C-73.700272%2C40.477399%2C-74.25909%26rid%3D25320%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26listPriceActive%3D1%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26singlestory%3D0%26housing-connector%3D0%26parking-spots%3Dnull-%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26onlyRentalStudentHousingType%3D0%26onlyRentalIncomeRestrictedHousingType%3D0%26onlyRentalMilitaryHousingType%3D0%26onlyRentalDisabledHousingType%3D0%26onlyRentalSeniorHousingType%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26ita%3D0%26stl%3D0%26fur%3D0%26os%3D0%26ca%3D0%26np%3D0%26hasDisabledAccess%3D0%26hasHardwoodFloor%3D0%26areUtilitiesIncluded%3D0%26highSpeedInternetAvailable%3D0%26elevatorAccessAvailable%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%0925320%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Afalse%7D%09%09%09%09%09; _clsk=hgesbn%7C1731101121323%7C19%7C0%7Cs.clarity.ms%2Fcollect'
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
    data = read_csv("Jersey_Rent_09_Nov_24.csv")

    # converting column data to list
    home_ids = data["home_id"].tolist()
    return sorted(home_ids)
    # return []

def get_zillow_url():
    # reading CSV file
    data = read_csv("Jersey_Rent_09_Nov_24.csv")

    # converting column data to list
    zillow_urls = data["Zillow url"].tolist()
    return sorted(zillow_urls)
    # return []

def binary_search(alist, item):
    if not alist:  # list is empty -- our base case
        return False

    midpoint = len(alist) // 2
    
    if isinstance(alist[midpoint], str):
        item = str(item)
        
    if alist[midpoint] == item:  # found it!
        return True

    if item < alist[midpoint]:  # item is in the first half, if at all
        return binary_search(alist[:midpoint], item)

    # otherwise item is in the second half, if at all
    return binary_search(alist[midpoint + 1:], item)
