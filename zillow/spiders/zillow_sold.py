import scrapy
from datetime import datetime
from zillow.utils import cookie_parser, parse_new_url
from inline_requests import inline_requests
from contextlib import suppress
import json
import w3lib.html

URL = "https://www.zillow.com/async-create-search-page-state"
payload = '{"searchQueryState":{"isMapVisible":false,"mapBounds":{"west":-74.46505874999998,"east":-73.41037124999998,"south":40.373674787685594,"north":40.93522673530129},"usersSearchTerm":"Brooklyn, New York, NY","filterState":{"sortSelection":{"value":"globalrelevanceex"},"isAllHomes":{"value":true},"isRecentlySold":{"value":true},"isForSaleByAgent":{"value":false},"isForSaleByOwner":{"value":false},"isNewConstruction":{"value":false},"isComingSoon":{"value":false},"isAuction":{"value":false},"isForSaleForeclosure":{"value":false}},"isListVisible":true},"wants":{"cat1":["listResults"],"regionResults":["regionResults"]},"requestId":6,"isDebugRequest":false}'

class ZillowSoldSpider(scrapy.Spider):
    name = "zillow_sold"
    allowed_domains = ["www.zillow.com"]
    
    def start_requests(self):
        yield scrapy.Request(
            url=URL,
            callback=self.parse,
            method="PUT",
            body=payload,
            cookies=cookie_parser(),
            meta={
                'currentPage': 1,
                "request_id": 6,
            }
        )

    def parse(self, response):
        current_page = response.meta['currentPage']
        request_id = response.meta["request_id"]
        json_resp = json.loads(response.body)
        houses = json_resp.get('cat1').get('searchResults').get('listResults')
        
        for i, house in enumerate(houses):
            if i > 2:
                break
            detail_url = house.get("detailUrl")
            if "http" in detail_url:
                detail_link = detail_url
            else:
                detail_link = f"https://www.zillow.com{detail_url}"

            data = {
                    "home_id": house["zpid"],
                    "Address": house["address"],
                    "Home Type": house["hdpData"]["homeInfo"]["homeType"],
                    "Beds": house.get("beds"),
                    "Baths": house.get("baths"),
                    "Price": house["soldPrice"],
                    "Sqft": house.get("area"),
                    "Longitude": house["hdpData"]["homeInfo"].get("longitude"),
                    "Latitude": house["hdpData"]["homeInfo"].get("latitude"),
                    "Days on zillow": house["hdpData"]["homeInfo"]["daysOnZillow"],
                    "Views": "",
                    "Subsidized": "",
                    "Unit features": "",
                    "Building amenities": "",
                    "Zillow url": detail_url,
                    "Leasing Agent": "",
                    "scrapeDate": datetime.now().date()
                }
            
            yield scrapy.Request(
                url=detail_link,
                callback=self.parse_apartment_details,
                cookies=cookie_parser(),
                meta={"data": data, "detail_url": detail_link}
            )

        # if current_page <= 24:
        #     current_page += 1
        #     request_id += 1

        #     query_string = json.loads(payload)
        #     query_string["requestId"] = request_id
        #     search_query_state = query_string["searchQueryState"]
        #     search_query_state["pagination"] = {"currentPage": current_page}
        #     query_string["searchQueryState"] = search_query_state

        #     yield scrapy.Request(
        #         url=URL,
        #         callback=self.parse,
        #         method="PUT",
        #         body=json.dumps(query_string),
        #         cookies=cookie_parser(),
        #         meta={"currentPage": current_page, "request_id": request_id},
        #     )

    @inline_requests
    def parse_apartment_details(self, response):
        data = response.meta["data"]
        # For apartment floorplans
        next_response = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()

        gdpClientCache = json.loads(next_response)["props"]["pageProps"]["componentProps"]["gdpClientCache"]
        page_Value = json.loads(gdpClientCache).values()
        properties = list(page_Value)[0]["property"]

        # featurs
        unit_features, building_amenities = [], []
        spacer_res = response.xpath(
            "//div[@class='Spacer-c11n-8-84-3__sc-17suqs2-0 hJwtCN']"
        )

        for spacer in spacer_res:
            features_resp = spacer.xpath(".//div/div")
            for feature in features_resp:
                if feature.xpath(".//h6/text()").get() == "Bedrooms & bathrooms":
                    continue
                listing = feature.xpath(".//ul/li")
                for fact in listing:
                    full_string = ""
                    for text in fact.xpath(".//span"):
                        full_string = "".join(
                            [i.get() for i in text.xpath(".//text()")]
                        )

                    if spacer.xpath(".//h5/text()").get() == "Interior":
                        unit_features.append(full_string)

                    if spacer.xpath(".//h5/text()").get() == "Property":
                        building_amenities.append(full_string)

        payload = {
            "zpid": data['home_id'],
            "pageType": "BDP",
            "isInstantTourEnabled": False,
            "isCachedInstantTourAvailability": True,
            "tourTypes": [],
        }
        headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": "https://www.zillow.com",
                "Referer": response.meta["detail_url"],
            }
        agent_resp = yield scrapy.Request(
            url="https://www.zillow.com/rentals/api/rcf/v1/rcf",
            method="POST",
            body=json.dumps(payload),
            cookies=cookie_parser(),
            headers=headers,
        )
        agent_info = json.loads(agent_resp.body)
        
        agent_name, business_name = None, None
        if agent_info["propertyInfo"].get("agentInfo"):
            agent_name = agent_info["propertyInfo"]["agentInfo"].get("displayName")
            business_name = agent_info["propertyInfo"]["agentInfo"].get("businessName")

        if not agent_name and not business_name:
            agent = "Name undisclosed"
        elif not agent_name:
            agent = business_name
        elif not business_name:
            agent = agent_name
        else:
            agent = f"{agent_name} - {business_name}"

        data.update({
            "Subsidized": "Yes" if "This is an HDFC" in properties["description"] else "No",
            "Unit features": unit_features,
            "Building amenities": building_amenities,
            "Leasing Agent": agent,
            })
        
        for history in properties["priceHistory"]:
            history_dict = {
                "HistoryDate": history["date"],
                "HistoryEvent": history["event"],
                "HistoryPrice": history["price"],
                "HistoryChange(%)": history["priceChangeRate"],
            }
            data.update(**history_dict)
            yield data
