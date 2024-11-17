from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
import pandas as pd
import json


def cookie_parser():
    cookie_string = 'zguid=24|%24260b6aef-556e-46a4-a5a9-6a89823abe11; zgsession=1|fdab21e5-d986-49dc-86b9-2cf284d98f1c; zjs_anonymous_id=%22260b6aef-556e-46a4-a5a9-6a89823abe11%22; zjs_user_id=null; zg_anonymous_id=%228bdb64f8-d59d-49a7-a3d0-03ffb0b2dd99%22; pxcts=c40c720e-a44a-11ef-980e-7ca81b09f52a; _pxvid=c40c6814-a44a-11ef-980c-58c264b76fa1; _ga=GA1.2.1500817772.1731782648; _gid=GA1.2.498806217.1731782648; _gcl_au=1.1.1703189823.1731782651; _scid=bVOy5eYI3XL_8NljRIGiPppofmApgFIR; _ScCbts=%5B%5D; DoubleClickSession=true; _tt_enable_cookie=1; _ttp=eiCW1ifxM_V2GCdA6MVtKvHiQEP.tt.1; _sctr=1%7C1731780000000; _pin_unauth=dWlkPU1qbGlNVGd6WTJVdE1UVTNOUzAwT0dJMkxUZ3pZek10TWpWak56ZzVOREkyT1RFMQ; _clck=urivn8%7C2%7Cfqy%7C0%7C1781; _scid_r=d9Oy5eYI3XL_8NljRIGiPppofmApgFIRD3m_fg; JSESSIONID=1A9CE1A887ACAF0C8565A99ED694AC62; _rdt_uuid=1731782651842.405dab70-87f0-4c55-bdf4-78a17407fd80; _px3=2d2109319600916b11360b5bc2e9c0e512f4402e19446ccc29110e63479adb2a:Evp+Xlqhmdv+NLvsd5lde9DaudjK42K4JHRVHEbGyiSuNqPTMWrbf1jugOGSyoC3Woblf7phl4Yln7AF833QNQ==:1000:QVOdE0NP4jZgQ4zb0cj4vtz2h+4jIdqvkKrDnZFJQQ/bT2kpq2tJltsVGPA6VXUpEzXDtsbZzgZEO4K8LId6JN/p1FAx52d0bdipq0kGOqijqhjcMrnjCnvYaDEWq3GuVhK3eja0P2T08D6u7NqnQFNA4CgjDFH4UqY3F745a3ZDgwFNEYtbTveFJI5H861ATCzkbKOMmVVvz+mZnL39hao/Vm+zYF2w1UR3ldaSvS0=; AWSALB=CbbP0p0tyvMw80GeXMzt/kJ9wvrLmccrrpmicNX8UMYvGr0qW6pwxXaJ5ahngrqQs3OkHkaEyot+coBHUETFoiSaFes9/RL0SgEjxoufdG1pGJIu8r5LfR1hKYi7; AWSALBCORS=CbbP0p0tyvMw80GeXMzt/kJ9wvrLmccrrpmicNX8UMYvGr0qW6pwxXaJ5ahngrqQs3OkHkaEyot+coBHUETFoiSaFes9/RL0SgEjxoufdG1pGJIu8r5LfR1hKYi7; _uetsid=c63b7120a44a11ef9293076bf9642bb2; _uetvid=c63b6300a44a11efa613e53956c48747; _clsk=ar2s2v%7C1731834007481%7C5%7C0%7Cw.clarity.ms%2Fcollect; search=6|1734426012044%7Crect%3D42.398867%2C-70.904137%2C42.22788%2C-71.191113%26rid%3D44269%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26listPriceActive%3D1%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26singlestory%3D0%26housing-connector%3D0%26parking-spots%3Dnull-%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26showcase%3D0%26featuredMultiFamilyBuilding%3D0%26onlyRentalStudentHousingType%3D0%26onlyRentalIncomeRestrictedHousingType%3D0%26onlyRentalMilitaryHousingType%3D0%26onlyRentalDisabledHousingType%3D0%26onlyRentalSeniorHousingType%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26ita%3D0%26stl%3D0%26fur%3D0%26os%3D0%26ca%3D0%26np%3D0%26hasDisabledAccess%3D0%26hasHardwoodFloor%3D0%26areUtilitiesIncluded%3D0%26highSpeedInternetAvailable%3D0%26elevatorAccessAvailable%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%0944269%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Afalse%7D%09%09%09%09%09'
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    return {key: morsel.value for key, morsel in cookie.items()}


def get_home_id():
    # Read the CSV and directly get sorted 'home_id' column
    return pd.read_csv("Boston_Rent_17_Nov_24.csv")["home_id"].sort_values().tolist()
    # return []

def get_zillow_url():
    # Read the CSV and directly get sorted 'Zillow url' column
    return pd.read_csv("Boston_Rent_17_Nov_24.csv")["Zillow url"].sort_values().tolist()
    # return []

    
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

