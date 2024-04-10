from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
from pandas import read_csv
import json


def cookie_parser():
    cookie_string = 'zguid=24|%24a7e27322-3a0e-4326-b418-e8aa4c07519e; _ga=GA1.2.1940155959.1710689132; _pxvid=98d9e8c1-e472-11ee-bc8b-b5ba793165aa; zjs_anonymous_id=%22a7e27322-3a0e-4326-b418-e8aa4c07519e%22; zjs_user_id=null; zg_anonymous_id=%226bfd33f3-c430-4d46-8d40-7a9ff04ed61f%22; _gcl_au=1.1.1649066619.1710689135; __pdst=afe2ba49c9444fbea6ef80ced25c9d69; _fbp=fb.1.1710689136507.609940117; _pin_unauth=dWlkPU5URmpOMlJqWlRRdE9UVTNPQzAwWW1NeExUazJZemd0TnpNM1pXRXlZbVE1TW1RNA; FSsampler=419012691; _scid=cdd5fff7-8a08-4f62-acb8-beaf3790468e; _tt_enable_cookie=1; _ttp=kQuKpQndZ98LJhe8okBLOzcllZn; zgsession=1|10ec3f65-cc76-4a1b-b178-f9c656fa8992; _gid=GA1.2.1908887392.1712680867; pxcts=f7f1353f-f68f-11ee-bd7d-72067409a6f8; _rdt_uuid=1711449796950.3a442d87-9039-4654-8484-ec1a97545d0a; _scid_r=cdd5fff7-8a08-4f62-acb8-beaf3790468e; _hp2_id.1215457233=%7B%22userId%22%3A%224640597236753568%22%2C%22pageviewId%22%3A%22151688407072348%22%2C%22sessionId%22%3A%225784434264779670%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; DoubleClickSession=true; _sctr=1%7C1712599200000; _uetsid=fcfeab20f68f11ee980e052a684ad62f; _uetvid=9a68fe70e47211eeb734b78faf876523; __gads=ID=e128818d8ac9cf1c:T=1710689241:RT=1712680932:S=ALNI_MaDuF-uXAAZ8_PvGThIyhM-kWZtUg; __gpi=UID=00000d3e16131912:T=1710689241:RT=1712680932:S=ALNI_MZsSTVVs4A0SwiHuCg3MEcS1ZC2pg; __eoi=ID=c4eaef58a3ee243d:T=1710689241:RT=1712680932:S=AA-AfjYLXIuCtG0_lu5eGBSvRUX9; _clck=1v2asss%7C2%7Cfks%7C0%7C1537; _clsk=1mdpjt6%7C1712683604625%7C1%7C0%7Ck.clarity.ms%2Fcollect; JSESSIONID=6E966216D5865E62447AD863D1655F6A; search=6|1715275608156%7Crb%3DPhiladelphia%252C-PA%26rect%3D40.137992%252C-74.955763%252C39.848844%252C-75.295343%26disp%3Dmap%26mdm%3Dauto%26sort%3Dpersonalizedsort%26listPriceActive%3D1%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26excludeNullAvailabilityDates%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%09%0913271%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; _pxff_cfp=1; _pxff_bsco=1; AWSALB=VVuhVYYBZD01aCT+zTR4m4H9s+HiqNDGQGfS73cP4I37didzWNnlWggG/8INak5fvw9vA98h/JXT4wBjJW82u1Me3+XaSnyOM5DTnC/nK+4nh7OEbKezegr8qNXC; AWSALBCORS=VVuhVYYBZD01aCT+zTR4m4H9s+HiqNDGQGfS73cP4I37didzWNnlWggG/8INak5fvw9vA98h/JXT4wBjJW82u1Me3+XaSnyOM5DTnC/nK+4nh7OEbKezegr8qNXC; _gat=1; _px3=74db7368b2899c3023e2b171f7f601b8b8e7175d9fbe226acb520be3fbf189fc:mc3VpbNFsvbVUzsWpJH8RB/Xpgeu/WyR3ZNiaaXSn+nN/kU5ik/HdDicpm1zrqgh4V8NnbFoQ0K//eXprlIrMA==:1000:g8xa/6246DYbzRR/d5ILnxa2ND6csqJkEMgSZeDVBksoUc25ExwhwYNMHUyHRvapPdv+lo4FuJSgzKDCAf25NRG2WLxvcwiS7Xr6dhBOWhTyJSEHlMhQgl0lysEzIJLJesPK1NhQXBcn0BlK99Ad+gvnWrTwibMBgncfidgQxSOC6EwuupvozLQEUEi5cXtNowLsbywA5JXiBJEHNtRtKh31FROe/xPFppicUfzOsSM='
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
    data = read_csv("9_April_24.csv")

    # converting column data to list
    home_ids = data["home_id"].tolist()
    return sorted(home_ids)
    return []

def get_zillow_url():
    # reading CSV file
    data = read_csv("9_April_24.csv")

    # converting column data to list
    zillow_urls = data["Zillow url"].tolist()
    return sorted(zillow_urls)
    # return []

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