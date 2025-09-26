from datetime import datetime
from inline_requests import inline_requests
import scrapy
from contextlib import suppress
from zillow.utils import cookie_parser, get_home_id, binary_search, get_zillow_url
from zillow.functions import get_agent
import json
import random
from zillow import settings

BASE_URL = "https://www.zillow.com"
URL = f"{BASE_URL}/async-create-search-page-state"
payload = settings.PAYLOAD
PROXY_LIST = settings.PROXY_LIST

class ZillowRentSpider(scrapy.Spider):
    name = "zillow_rent"

    def _get_proxy(self):
        """Get a random proxy from settings"""
        proxy_list = None
        if proxy_list:
            return random.choice(proxy_list)
        return None

    def start_requests(self):
        print("proxy url", self._get_proxy())
        yield scrapy.Request(
            url=URL,
            callback=self.parse,
            method="PUT",
            body=payload,
            cookies=cookie_parser(),
            meta={
                "currentPage": 1,
                "request_id": 3,
                "home_ids": get_home_id(),
                "zillow_urls": get_zillow_url(),
                "proxy": self._get_proxy(),
            },
        )

    def parse(self, response):
        current_page = response.meta.get("currentPage", 1)
        request_id = response.meta.get("request_id", 3)
        print(f"Current Page: {current_page}")

        # Load the JSON response
        json_resp = json.loads(response.body)
        houses = json_resp.get("cat1", {}).get("searchResults", {}).get("listResults") or \
                json_resp.get("cat1", {}).get("searchResults", {}).get("mapResults", [])

        # Iterate over houses
        for i, house in enumerate(houses):
            # if i > 0:
            #     break
            
            detail_url = house.get("detailUrl")
            if not detail_url:
                continue

            detail_link = detail_url if detail_url.startswith("http") else f"{BASE_URL}{detail_url}"

            # Skip if URL already processed
            if binary_search(response.meta["zillow_urls"], detail_link):
                self.logger.info("URL already exists in file, skipping.")
                continue
            
            # Yield request for apartment details
            yield scrapy.Request(
                url=detail_link,
                callback=self.parse_apartment_details,
                cookies=cookie_parser(),
                meta={
                    "detail_url": detail_link,
                    "current_page": current_page,
                    "request_id": request_id,
                    "home_ids": response.meta["home_ids"],
                    "zillow_urls": response.meta["zillow_urls"],
                    "proxy": self._get_proxy(),
                },
            )

        # Pagination: Proceed if within page limit
        if current_page < 25:
            current_page += 1
            request_id += 1

            # Update query for next page
            query_string = json.loads(payload)
            query_string["requestId"] = request_id
            query_string["searchQueryState"]["pagination"] = {"currentPage": current_page}

            # Yield request for the next page
            yield scrapy.Request(
                url=URL,
                callback=self.parse,
                method="PUT",
                body=json.dumps(query_string),
                cookies=cookie_parser(),
                meta={
                    "currentPage": current_page,
                    "request_id": request_id,
                    "home_ids": response.meta["home_ids"],
                    "zillow_urls": response.meta["zillow_urls"],
                    "proxy": self._get_proxy(),
                },
            )

    @inline_requests
    def parse_apartment_details(self, response):
        data = {
                "home_id": "",
                "Title": "",
                "Address": "",
                "Name": "",
                "Beds": "",
                "Baths": "",
                "UnitNumber": "",
                "Price": "",
                "Sqft": "",
                "Longitude": "",
                "Latitude": "",
                "Property Type": "",
                "Days on zillow": "",
                "Contacts": "",
                "Applications": '',
                "Availability": "",
                "Tags": "",
                "Description": "",
                "Image": "",
                "FloorImage": "",
                "Special offer": "",
                "Subsidized": "", 
                "Unit listing url": "",
                "Interior": "",
                "Unit features": "",
                "Building amenities": "",
                "Property": "",
                "Building details": "",
                "Policy": "",
                "Price history": "",
                "Zillow url": "",
                "Property website": "",
                "Getting around": "",
                "Nearby schools": "",
                "Leasing Agent": "",
                "scrapeDate": datetime.now().date(),
                "Source": "Zillow",
            }
        referer_url = response.meta["detail_url"]
        
        # with open("body_content.html", "w", encoding="utf-8") as file:
        #     file.write(response.text)
                
        title = response.meta.get("title", "")
        unitNumber = (
            response.meta["unit_number"] if response.meta.get("unit_number") else ""
        )
        current_page = response.meta["current_page"]
        request_id = response.meta["request_id"]
        
        # # Parent start
        if parent_title := response.xpath(
            "//h1[@data-test-id='bdp-building-title']/text()"
        ).get():
            title = parent_title

        tags = response.xpath("//div[@aria-label='insights tags']/span/text()").getall()
        special_all_text = response.xpath("//ul[contains(@id, 'special-offers-details')]//text()").getall()
        special_offers = " ".join(text.strip() for text in special_all_text if text.strip())
        
        interior_list, unit_features_list, building_amenities_list, property_list, building_details, policy_details = [], [], [], [], [], []
        category_features = response.xpath("//div[contains(@class, 'styles__StyledCategoryGroupHeadingContainer')]")
        
        for category in category_features:
            
            # Interior
            if (category.xpath( ".//h3/text()").get().lower() in ["interior"]):
                interior_features = category.xpath(".//following-sibling::div[1]/div")
                
                for interior in interior_features:
                    intor_heading = interior.xpath(".//h5/text()").get() or interior.xpath(".//h6/text()").get()
                    for idx, service in enumerate(interior.xpath(".//ul/li")):
                        interior_text = ""
                        for text in service.xpath(".//span"):
                            interior_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if intor_heading and idx < 1:
                            interior_text = f"{intor_heading}: {interior_text}"
                                
                        interior_list.append(interior_text)
            
            # unit_features_list
            if (category.xpath( ".//h3/text()").get().lower() in ["unit features", "special features"]):
                unit_features = category.xpath(".//following-sibling::div[1]/div")
                
                for amenity in unit_features:
                    unit_heading = amenity.xpath(".//h5/text()").get() or amenity.xpath(".//h6/text()").get()
                    for idx, service in enumerate(amenity.xpath(".//ul/li")):
                        unit_text = ""
                        for text in service.xpath(".//span"):
                            unit_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if unit_heading and idx < 1:
                            unit_text = f"{unit_heading}: {unit_text}"
                            
                        unit_features_list.append(unit_text)
            
            # Building Amenities
            if (category.xpath( ".//h3/text()").get().lower() in ["building amenities"]):
                building_amenities = category.xpath(".//following-sibling::div[1]/div")
                
                for amenity in building_amenities:
                    b_heading = amenity.xpath(".//h5/text()").get() or amenity.xpath(".//h6/text()").get()
                    for idx, service in enumerate(amenity.xpath(".//ul/li")):
                        service_text = ""
                        for text in service.xpath(".//span"):
                            service_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if b_heading and idx < 1:
                            service_text = f"{b_heading}: {service_text}"
                            
                        building_amenities_list.append(service_text)
            
            # property_list
            if (category.xpath( ".//h3/text()").get().lower() in ["property", "properties"]):
                property_content = category.xpath(".//following-sibling::div[1]/div")
                
                for amenity in property_content:
                    property_heading = amenity.xpath(".//h5/text()").get() or amenity.xpath(".//h6/text()").get()
                    for idx, service in enumerate(amenity.xpath(".//ul/li")):
                        property_text = ""
                        for text in service.xpath(".//span"):
                            property_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if property_heading and idx < 1:
                            property_text = f"{property_heading}: {property_text}"
                            
                        property_list.append(property_text)
                        
            # building_details
            if (category.xpath( ".//h3/text()").get().lower() in ["building"]):
                building_details_content = category.xpath(".//following-sibling::div[1]/div")
                
                for amenity in building_details_content:
                    building_heading = amenity.xpath(".//h5/text()").get() or amenity.xpath(".//h6/text()").get()
                    for idx, service in enumerate(amenity.xpath(".//ul/li")):
                        building_text = ""
                        for text in service.xpath(".//span"):
                            building_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if building_heading and idx < 1:
                            building_text = f"{building_heading}: {building_text}"
                            
                        building_details.append(building_text)
                        
            # policy_details
            if (category.xpath( ".//h3/text()").get().lower() in ["policies"]):
                policy_details_content = category.xpath(".//following-sibling::div[1]/div")
                
                for amenity in policy_details_content:
                    p_heading = amenity.xpath(".//h5/text()").get() or amenity.xpath(".//h6/text()").get()
                    for idx, service in enumerate(amenity.xpath(".//ul/li")):
                        policy_text = ""
                        for text in service.xpath(".//span"):
                            policy_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if p_heading and idx < 1:
                            policy_text = f"{p_heading}: {policy_text}"
                            
                        policy_details.append(policy_text)
        # # Parent end
        
        # For full building details link
        if full_building_link := response.xpath(
            "//ul[@class='zsg-tooltip-viewport']/li[1]/div/div/div[2]/a/@href"
        ).get():
            referer_url = f"{BASE_URL}{full_building_link}"
            yield scrapy.Request(
                url=referer_url,
                callback=self.parse_apartment_details,
                cookies=cookie_parser(),
                meta={
                    "detail_url": response.meta["detail_url"],
                    "title": title,
                    "current_page": current_page,
                    "request_id": request_id,
                    "home_ids": response.meta["home_ids"],
                    # "proxy": proxy_url,
                },
            )

        # For apartment floorplans
        next_response = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        page_response = json.loads(next_response)
        
        # with open('before_Full.json', 'w', encoding="utf-8") as f:
        #     print("file write")
        #     f.write(next_response)

        try:
            if page_response["props"]["pageProps"].get("initialReduxState"):
                buildings = page_response["props"]["pageProps"]["initialReduxState"]["gdp"]["building"]
            else:
                buildings = page_response["props"]["pageProps"]["componentProps"]["initialReduxState"]["gdp"]["building"]

            # What special
            description = buildings.get("description")
            home_type = buildings.get("homeTypes")

            image_link = []
            if photos := buildings.get("photos"):
                for photo in photos:
                    if photo.get("mixedSources"):
                        if webp_photos := photo["mixedSources"]["webp"][-1]['url']:
                            image_link.append(webp_photos)
                        elif jpg_photos := photo["mixedSources"]["jpeg"][-1]['url']:
                            image_link.append(jpg_photos)
            
                
            # Price History
            price_history = []
            priceHistory_list = buildings.get("priceHistory", "")
            for priceHistory in priceHistory_list:
                price_history.append(f"Date: {priceHistory.get('date')}, Event: {priceHistory.get('event')}, Price: {priceHistory.get('price')}, pricePerSquareFoot: {priceHistory.get('pricePerSquareFoot')}, Rate: {priceHistory.get('priceChangeRate')}, Source: {priceHistory.get('source', '-')}")

            # Nearby schools
            assigne_schools = buildings.get("assignedSchools", [])
            schools = []
            for school in assigne_schools:
                school_info = {
                    "name": school.get("name", ""),
                    "rating": school.get("rating", ""),
                    "level": school.get("level", ""),
                    "grades": school.get("grades", ""),
                    "link": school.get("link", ""),
                    "type": school.get("type", ""),
                }
                schools.append(school_info)
            
            # scores
            getting_around = []
            if walk_scores := buildings.get("walkScore"):
                walk_score = {
                                "description": walk_scores.get("description", ""),
                                "walkscore": walk_scores.get("walkscore", ""),
                                "ws_link": walk_scores.get("ws_link", "")
                            }
                getting_around.append(f"Walk Score: {walk_score}")
            if transit_scores := buildings.get("transitScore"):
                transit_score = {
                                "description": transit_scores.get("description", ""),
                                "transit_score": transit_scores.get("transit_score", ""),
                                "ws_link": transit_scores.get("ws_link", "")
                            }
                getting_around.append(f"Transit Score: {transit_score}")
            if bike_scores := buildings.get("bikeScore"):
                bike_score = {
                                "description": bike_scores.get("description", ""),
                                "bikescore": bike_scores.get("bikescore", ""),
                            }
                getting_around.append(f"Bike Score: {bike_score}")
                
            data.update({
                "Getting around": getting_around,
                "Nearby schools": schools,
            })

            if buildings.get("floorPlans"):
                address = response.xpath(
                    "//h2[@data-test-id='bdp-building-address']/text()"
                ).get()
                prop_website = response.xpath(
                    "//a[@data-test-id='bdp-ppc-link']/@href"
                ).get() or response.xpath("//div[@class='ds-pay-per-click-link-text']/text()").get()
                            
                floorPlans = buildings["floorPlans"]
                lng = buildings["longitude"]
                lat = buildings["latitude"]
                
                if not unit_features_list:
                    unit_features_list = buildings["amenityDetails"]["unitFeatures"]

                for floor in floorPlans:
                    if binary_search(response.meta["home_ids"], int(floor["zpid"])):
                        break

                    payload = {
                        "zpid": floor["zpid"],
                        "pageType": "BDP",
                        "isInstantTourEnabled": False,
                        "isCachedInstantTourAvailability": True,
                        "tourTypes": [],
                    }
                    headers = {
                            "Content-Type": "application/json;charset=UTF-8",
                            "Origin": f"{BASE_URL}",
                            "Referer": response.meta["detail_url"],
                        }
                    agent_resp = yield scrapy.Request(
                        url=f"{BASE_URL}/rentals/api/rcf/v1/rcf",
                        method="POST",
                        body=json.dumps(payload),
                        cookies=cookie_parser(),
                        headers=headers,
                        # meta={"proxy": proxy_url,}
                    )
                    agent_info = json.loads(agent_resp.body)
                    agent = get_agent(agent_info)
                        
                    zillow_days, contacts, subsidized = "", "", ""
                    
                    # Subsidized
                    subsidized = (
                        "Yes"
                        if agent_info["propertyInfo"]["maxLowIncomeList"]
                        else "No"
                    )
                    
                    # Gallery Photos
                    floor_image_link = []
                    if photos := floor.get("photos"):
                        for photo in photos:
                            if photo.get("mixedSources"):
                                if webp_photos := photo["mixedSources"]["webp"][-1]['url']:
                                    floor_image_link.append(webp_photos)
                                elif jpg_photos := photo["mixedSources"]["jpeg"][-1]['url']:
                                    floor_image_link.append(jpg_photos)

                    if floor.get("units"):
                        for unit in floor["units"]:
                            availablity = unit.get("availableFrom")
                            zpid = unit.get("zpid")
                            
                            unit_image_link = []
                            if photos := unit.get("photos"):
                                for photo in photos:
                                    if photo.get("mixedSources"):
                                        if webp_photos := photo["mixedSources"]["webp"][-1]['url']:
                                            unit_image_link.append(webp_photos)
                                        elif jpg_photos := photo["mixedSources"]["jpeg"][-1]['url']:
                                            unit_image_link.append(jpg_photos)

                            data.update({
                                "home_id": zpid,
                                "Title": title,
                                "Address": address,
                                "Name": floor.get("name"),
                                "Beds": floor.get("beds"),
                                "Baths": floor.get("baths"),
                                "UnitNumber": unit["unitNumber"]
                                if unit.get("unitNumber")
                                else unitNumber,
                                "Price": unit.get("price"),
                                "Sqft": unit.get("sqft"),
                                "Longitude": lng,
                                "Latitude": lat,
                                "Property Type": home_type,
                                "Days on zillow": zillow_days,
                                "Contacts": contacts,
                                "Applications": '',
                                "Availability": "Available Now"
                                if availablity == "0"
                                else "",
                                "Tags": tags,
                                "Description": description,
                                "Image": image_link,
                                "FloorImage": unit_image_link,
                                "Special offer": special_offers,
                                "Subsidized": subsidized, 
                                "Unit listing url": f"{response.meta['detail_url']}#unit-{zpid}",
                                "Interior": interior_list,
                                "Unit features": unit_features_list,
                                "Building amenities": building_amenities_list,
                                "Property": property_list,
                                "Building details": building_details,
                                "Policy": policy_details,
                                "Price history": price_history,
                                "Zillow url": response.meta["detail_url"],
                                "Property website": prop_website,
                                "Leasing Agent": agent,
                            })
                            yield data
                    else:
                        availablity = floor.get("availableFrom")
                        zpid = floor.get("zpid")

                        data.update({
                            "home_id": zpid,
                            "Title": title,
                            "Address": address,
                            "Name": floor.get("name"),
                            "Beds": floor.get("beds"),
                            "Baths": floor.get("baths"),
                            "UnitNumber": unitNumber,
                            "Price": f"{floor.get('minPrice')}+",
                            "Sqft": floor.get("sqft"),
                            "Longitude": lng,
                            "Latitude": lat,
                            "Property Type": home_type,
                            "Days on zillow": zillow_days,
                            "Contacts": contacts,
                            "Applications": "",
                            "Availability": "Available Now"
                            if availablity == "0"
                            else "",
                            "Tags": tags,
                            "Description": description,
                            "Image": image_link,
                            "FloorImage": floor_image_link,
                            "Special offer": special_offers,
                            "Subsidized": subsidized,
                            "Unit listing url": f"{response.meta['detail_url']}#unit-{zpid}",
                            "Interior": interior_list,
                            "Unit features": unit_features_list,
                            "Building amenities": building_amenities_list,
                            "Property": property_list,
                            "Building details": building_details,
                            "Policy": policy_details,
                            "Price history": price_history,
                            "Zillow url": response.meta["detail_url"],
                            "Property website": prop_website,
                            "Leasing Agent": agent,
                            "scrapeDate": datetime.now().date(),
                            "Source": "Zillow",
                        })
                        yield data

            else:
                ungroupedUnits = buildings["ungroupedUnits"]
                for ungroupedUnit in ungroupedUnits:
                    if ungroupedUnit["listingType"] == "FOR_RENT":
                        unitNumber = ungroupedUnit["unitNumber"]
                        referer_url = f"{BASE_URL}{ungroupedUnit['hdpUrl']}"

                        yield scrapy.Request(
                            url=referer_url,
                            callback=self.parse_apartment_details,
                            cookies=cookie_parser(),
                            meta={
                                "detail_url": response.meta["detail_url"],
                                "title": title,
                                "unit_number": unitNumber,
                                "current_page": current_page,
                                "request_id": request_id,
                                "home_ids": response.meta["home_ids"],
                                # "proxy": proxy_url,
                            },
                        )

        except KeyError as e:
            print(e)

            try:  
                # Get orginal request path
                unit_listing_url = page_response["query"].get("originalReqUrlPath")
                
                if page_response["props"]["pageProps"].get("*"):
                    gdpClientCache = page_response["props"]["pageProps"]["gdpClientCache"]
                else:
                    gdpClientCache = page_response["props"]["pageProps"]["componentProps"]["gdpClientCache"]
                page_Value = json.loads(gdpClientCache).values()
                properties = list(page_Value)[0]["property"]
                zpid = properties["zpid"]
                description = properties.get("description")
                prop_schools = properties.get("schools", [])
                
                schools = []
                for school in prop_schools:
                    school_info = {
                        "name": school.get("name", ""),
                        "rating": school.get("rating", ""),
                        "level": school.get("level", ""),
                        "grades": school.get("grades", ""),
                        "link": school.get("link", ""),
                        "type": school.get("type", ""),
                    }
                    schools.append(school_info)
                
                image_link, home_type = [], properties.get("homeType")
                if photos := properties.get("responsivePhotos"):
                    for photo in photos:
                        if photo.get("mixedSources"):
                            if webp_photos := photo["mixedSources"]["webp"][-1]['url']:
                                image_link.append(webp_photos)
                            elif jpg_photos := photo["mixedSources"]["jpeg"][-1]['url']:
                                image_link.append(jpg_photos)
                        
                    if not home_type:
                        home_type = photos[0]["homeType"]
                
                # Price History
                price_history = []
                priceHistory_list = properties.get("priceHistory", "")
                for priceHistory in priceHistory_list:
                    price_history.append(f"Date: {priceHistory.get('date')}, Event: {priceHistory.get('event')}, Price: {priceHistory.get('price')}, pricePerSquareFoot: {priceHistory.get('pricePerSquareFoot')}, Rate: {priceHistory.get('priceChangeRate')}, Source: {priceHistory.get('source', '-')}")

                if not binary_search(response.meta["home_ids"], int(zpid)):
                    # Address
                    address = ""
                    for addr in response.xpath("//div[contains(@class, 'styles__AddressWrapper')]/h1"):
                        address = "".join([i.get() for i in addr.xpath(".//text()")])

                    # availablity
                    available = ""
                    if properties.get("resoFacts") and properties["resoFacts"].get("atAGlanceFacts"):   
                        facts = properties["resoFacts"]["atAGlanceFacts"]
                        for fact in facts:
                            if (
                                fact["factLabel"] == "Date available"
                                and fact["factValue"] == "Available Now"
                            ):
                                available = "Available Now"

                    if not available:
                        if response.xpath("//div[contains(@class, 'styles__StyledDataModule')]//span[contains(text(), 'Available')]"):
                            available = "Available Now"

                    payload = {
                        "zpid": zpid,
                        "pageType": "BDP",
                        "isInstantTourEnabled": False,
                        "isCachedInstantTourAvailability": True,
                        "tourTypes": [],
                    }
                    headers = {
                            "Content-Type": "application/json;charset=UTF-8",
                            "Origin": f"{BASE_URL}",
                            "Referer": response.meta["detail_url"],
                        }
                    agent_resp = yield scrapy.Request(
                        url="https://www.zillow.com/rentals/api/rcf/v1/rcf",
                        method="POST",
                        body=json.dumps(payload),
                        cookies=cookie_parser(),
                        headers=headers,
                        # meta={"proxy": proxy_url,}
                    )
                    agent_info = json.loads(agent_resp.body)
                    agent = get_agent(agent_info)

                    # Subsidized
                    subsidized = (
                        "Yes" if agent_info["propertyInfo"]["maxLowIncomeList"] else "No"
                    )
                    
                    # Contacts
                    q = """
                        query ListingContactDetailsQuery($zpid: ID!) {
                            viewer {
                                roles {
                                isLandlordLiaisonMember
                            isLlpRenter
                            }
                        }
                        property(zpid: $zpid) {
                                zpid
                            brokerId
                            isHousingConnectorExclusive
                            rentalListingOwnerReputation {
                                responseRate
                            responseTimeMs
                            contactCount
                            applicationCount
                            isLandlordIdVerified
                            }
                            isFeatured
                            isListedByOwner
                            rentalListingOwnerContact {
                                displayName
                            businessName
                            phoneNumber
                            agentBadgeType
                            photoUrl
                            reviewsReceivedCount
                            reviewsUrl
                            ratingAverage      isBrokerLocalCompliance
                            }
                            postingProductType
                            postingContact {
                                brokerName
                            brokerageName
                            name
                            }
                            postingUrl
                            rentalMarketingTreatments
                            building {
                                bdpUrl
                            buildingName
                            housingConnector {
                                    hcLink {
                                    text
                                }
                            }
                            ppcLink {
                                    text
                            }
                            }
                            roomForRent {
                                postedBy
                            }
                        }
                        }
                        """

                    contact_payload = {
                        "query": q,
                        "operationName": "ListingContactDetailsQuery",
                        "variables": {
                            "zpid": zpid,
                        },
                    }
                    headers = {
                            "Content-Type": "application/json;charset=UTF-8",
                            "Origin": f"{BASE_URL}",
                            "Referer": referer_url,
                        }
                    overview_resp = yield scrapy.Request(
                        url=f"{BASE_URL}/graphql/?zpid={zpid}&operationName=ListingContactDetailsQuery",
                        method="POST",
                        body=json.dumps(contact_payload),
                        cookies=cookie_parser(),
                        headers=headers,
                        # meta={"proxy": proxy_url,}
                    )
                    
                    overview_data = json.loads(overview_resp.body)
                    contact, application, views = "", "", ""
                    with suppress(KeyError):
                        contact = overview_data["data"]["property"]["rentalListingOwnerReputation"]["contactCount"]
                        application = overview_data["data"]["property"]["rentalListingOwnerReputation"]["applicationCount"]

                    # UnitNumber
                    with suppress(KeyError):
                        if properties.get("adTargets") and properties["adTargets"].get("aamgnrc2"):
                            target_unitNumber = properties["adTargets"]["aamgnrc2"]
                            if target_unitNumber in address:
                                if not "Unit" in target_unitNumber:
                                    unitNumber = f"Unit {target_unitNumber}"
                                
                    # Walk, Transit and Bike Score
                    score_q = """
                        query WalkTransitAndBikeScoreQuery($zpid: ID!) {
                            property(zpid: $zpid) {
                                id
                                walkScore {
                                walkscore
                                description
                                ws_link
                                }
                                transitScore {
                                transit_score
                                description
                                ws_link
                                }
                                bikeScore {
                                bikescore
                                description
                                }
                            }
                            }
                        """

                    score_payload = {
                        "query": score_q,
                        "operationName": "WalkTransitAndBikeScoreQuery",
                        "variables": {
                            "zpid": zpid,
                        },
                    }
                    headers = {
                            "Content-Type": "application/json",
                            "Origin": f"{BASE_URL}",
                            "Referer": referer_url,
                        }
                    score_resp = yield scrapy.Request(
                        url=f"{BASE_URL}/graphql/?zpid={zpid}&operationName=WalkTransitAndBikeScoreQuery",
                        method="POST",
                        body=json.dumps(score_payload),
                        cookies=cookie_parser(),
                        headers=headers,
                        # meta={"proxy": proxy_url,}
                    )
                    score_data = json.loads(score_resp.body)
                    getting_around = []
                    with suppress(KeyError):
                        getting_around_prop = score_data["data"]["property"]
                        if walk_scores := getting_around_prop.get("walkScore"):
                            walk_score = {
                                "description": walk_scores.get("description", ""),
                                "walkscore": walk_scores.get("walkscore", ""),
                                "ws_link": walk_scores.get("ws_link", "")
                            }
                            getting_around.append(f"Walk Score: {walk_score}")
                            
                        if transit_scores := getting_around_prop.get("transitScore"):
                            transit_score = {
                                "description": transit_scores.get("description", ""),
                                "transit_score": transit_scores.get("transit_score", ""),
                                "ws_link": transit_scores.get("ws_link", "")
                            }
                            getting_around.append(f"Transit Score: {transit_score}")
                            
                        if bike_scores := getting_around_prop.get("bikeScore"):
                            bike_score = {
                                "description": bike_scores.get("description", ""),
                                "bikescore": bike_scores.get("bikescore", ""),
                            }
                            getting_around.append(f"Bike Score: {bike_score}")
                    
                    if properties.get("adTargets"):
                        data.update({"Sqft": properties["adTargets"].get("sqft")})
                    else:
                        data.update({"Sqft": properties.get("livingArea")})
                    
                    data.update({
                        "home_id": zpid,
                        "Title": title,
                        "Address": address,
                        "Name": "",
                        "Beds": properties.get("bedrooms"),
                        "Baths": properties.get("bathrooms"),
                        "UnitNumber": unitNumber,
                        "Price": properties.get("price"),
                        "Longitude": properties.get("longitude"),
                        "Latitude": properties.get("latitude"),
                        "Property Type": home_type,
                        "Days on zillow": properties.get("daysOnZillow"),
                        "Contacts": contact,
                        "Applications": application,
                        "Availability": available,
                        "Tags": tags,
                        "Description": description,
                        "Image": image_link,
                        "Special offer": special_offers,
                        "Subsidized": subsidized,
                        "Unit listing url": f"https://www.zillow.com{unit_listing_url}",
                        "Interior": interior_list,
                        "Unit features": unit_features_list,
                        "Building amenities": building_amenities_list,
                        "Property": property_list,
                        "Building details": building_details,
                        "Policy": policy_details,
                        "Price history": price_history,
                        "Zillow url": response.meta["detail_url"],
                        "Property website": "",
                        "Getting around": getting_around,
                        "Nearby schools": schools,
                        "Leasing Agent": agent,
                    })
                    yield data

            except Exception as ex:
                print(f"Error: {ex}")

                with open("log_error.txt", "a") as f:
                    f.write(response.meta["detail_url"])
                    f.write("\n")
