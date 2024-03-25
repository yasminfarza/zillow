import scrapy
from datetime import datetime
from zillow.utils import cookie_parser, get_home_id, binary_search
from inline_requests import inline_requests
from contextlib import suppress
import json
import w3lib.html

URL = "https://www.zillow.com/async-create-search-page-state"
payload = '{"searchQueryState":{"pagination":{},"isMapVisible":false,"mapBounds":{"west":-74.20138687499998,"east":-73.67404312499998,"south":40.514505764601275,"north":40.79528195967464},"usersSearchTerm":"Brooklyn, New York, NY","regionSelection":[{"regionId":37607,"regionType":17}],"filterState":{"sortSelection":{"value":"globalrelevanceex"},"isForSaleByAgent":{"value":false},"isForSaleByOwner":{"value":false},"isNewConstruction":{"value":false},"isComingSoon":{"value":false},"isAuction":{"value":false},"isForSaleForeclosure":{"value":false},"isPreMarketForeclosure":{"value":false},"isPreMarketPreForeclosure":{"value":false},"isRecentlySold":{"value":true},"isSingleFamily":{"value":false},"isTownhouse":{"value":false},"isMultiFamily":{"value":false},"isLotLand":{"value":false},"isApartment":{"value":false},"isManufactured":{"value":false}},"isListVisible":true,"mapZoom":11},"wants":{"cat1":["listResults"]},"requestId":71,"isDebugRequest":false}'

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
                "home_ids": get_home_id()
            }
        )

    def parse(self, response):
        current_page = response.meta['currentPage']
        request_id = response.meta["request_id"]
        json_resp = json.loads(response.body)
        houses = json_resp.get('cat1').get('searchResults').get('listResults')
        
        for i, house in enumerate(houses):
            # if i > 2:
            #     break
            detail_url = house.get("detailUrl")
            if "http" in detail_url:
                detail_link = detail_url
            else:
                detail_link = f"https://www.zillow.com{detail_url}"

            yield scrapy.Request(
                url=detail_link,
                callback=self.parse_apartment_details,
                cookies=cookie_parser(),
                meta={"detail_url": detail_link, "home_ids": response.meta["home_ids"]},
            )

        if current_page <= 24:
            current_page += 1
            request_id += 1

            query_string = json.loads(payload)
            query_string["requestId"] = request_id
            search_query_state = query_string["searchQueryState"]
            search_query_state["pagination"] = {"currentPage": current_page}
            query_string["searchQueryState"] = search_query_state

            yield scrapy.Request(
                url=URL,
                callback=self.parse,
                method="PUT",
                body=json.dumps(query_string),
                cookies=cookie_parser(),
                meta={"currentPage": current_page, "request_id": request_id, "home_ids": response.meta["home_ids"]},
            )

    @inline_requests
    def parse_apartment_details(self, response):
        detail_url = response.meta["detail_url"]
        # For apartment floorplans
        next_response = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()

        try:
            gdpClientCache = json.loads(next_response)["props"]["pageProps"]["componentProps"]["gdpClientCache"]
            page_Value = json.loads(gdpClientCache).values()
            properties = list(page_Value)[0]["property"]
            zpid = properties["zpid"]

            if not binary_search(response.meta["home_ids"], int(zpid)):
                # features
                unit_features = []
                features = properties["resoFacts"]

                if features.get('hasHeating') == 'true':
                    unit_features.append(f"Heating: {str(features['heating'])}")

                if features.get('hasCooling') == 'true':
                    unit_features.append(f"Cooling: {str(features['cooling'])}")

                if features.get('appliances'):
                    unit_features.append(f"Appliances: {str(features['appliances'])}")

                if features.get('flooring'):
                    unit_features.append(f"Flooring: {str(features['flooring'])}")

                if features.get('basement'):
                    unit_features.append(f"Basement: {str(features['basement'])}")

                if features.get('laundryFeatures'):
                    unit_features.append(f"Laundry: {str(features['laundryFeatures'])}")

                if features.get('interiorFeatures'):
                    unit_features.append(f"Other Interior Features: {str(features['interiorFeatures'])}")
                
                if features.get('fireplaces') and str(features['fireplaces']) > str(0):
                    unit_features.append(f"Fireplaces: {str(features['fireplaces'])}")

                if features.get('bathroomsFull') and str(features['bathroomsFull']) > str(0):
                    unit_features.append(f"Bathrooms Full: {str(features['bathroomsFull'])}")

                if features.get('bathroomsHalf') and str(features['bathroomsHalf']) > str(0):
                    unit_features.append(f"Bathrooms Half: {str(features['bathroomsHalf'])}")

                address = ""
                for addr in response.xpath("//h1[@class='Text-c11n-8-84-3__sc-aiai24-0 hrfydd']"):
                    address = "".join([i.get() for i in addr.xpath(".//text()")])

                # subsidized
                subsidized = "No"
                if properties.get("description"):
                    if "This is an HDFC" in properties["description"]:
                        subsidized = "Yes" 
                

                data = {
                        "home_id": zpid,
                        "Address": address,
                        "Home Type": "",
                        "Beds": properties.get("bedrooms"),
                        "Baths": properties.get("bathrooms"),
                        "Price": properties.get("price"),
                        "Sqft": properties["adTargets"].get("sqft")
                        or properties.get("livingArea"),
                        "Views": properties.get("pageViewCount"),
                        "Longitude": properties.get("longitude"),
                        "Latitude": properties.get("latitude"),
                        "Days on zillow": properties.get("daysOnZillow"),
                        "Subsidized": subsidized,
                        "Unit features": "",
                        "Zillow url": detail_url,
                        "Leasing Agent": "",
                        "scrapeDate": datetime.now().date()
                    }
                
                payload = {
                    "zpid": zpid,
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
                try:
                    agent_name = agent_info["propertyInfo"]["agentInfo"]["displayName"]
                    business_name = agent_info["propertyInfo"]["agentInfo"]["businessName"]
                except:
                    pass

                if not agent_name and not business_name:
                    agent = "Name undisclosed"
                elif not agent_name:
                    agent = business_name
                elif not business_name:
                    agent = agent_name
                else:
                    agent = f"{agent_name} - {business_name}"

                data.update({
                    "Home Type": features.get("homeType"),
                    "Unit features": unit_features,
                    "Leasing Agent": agent,
                    })
                
                if priceHistory := properties.get("priceHistory"):
                    for history in priceHistory:
                        history_dict = {
                            "HistoryDate": history["date"],
                            "HistoryEvent": history["event"],
                            "HistoryPrice": history["price"],
                            "HistoryChange(%)": history["priceChangeRate"],
                        }
                        data.update(**history_dict)
                        yield data
                else:
                    history_dict = {
                        "HistoryDate": "",
                        "HistoryEvent": "",
                        "HistoryPrice": "",
                        "HistoryChange(%)": "",
                    }
                    data.update(**history_dict)
                    yield data

        except Exception as ex:
            print(f"Error: {ex}")
            with open("log_error.txt", "a") as f:
                f.write(response.meta["detail_url"])
                f.write("\n")
                f.close()
