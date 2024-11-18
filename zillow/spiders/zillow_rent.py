from datetime import datetime
from inline_requests import inline_requests
import scrapy
from contextlib import suppress
from zillow.utils import cookie_parser, get_home_id, binary_search, get_zillow_url
from zillow.functions import get_agent
import json
from zillow import settings

BASE_URL = "https://www.zillow.com"
URL = f"{BASE_URL}/async-create-search-page-state"
payload = settings.PAYLOAD

class ZillowRentSpider(scrapy.Spider):
    name = "zillow_rent"

    def start_requests(self):
        yield scrapy.Request(
            url=URL,
            callback=self.parse,
            method="PUT",
            body=payload,
            cookies=cookie_parser(),
            meta={
                "currentPage": 1,
                "request_id": 5,
                "home_ids": get_home_id(),
                "zillow_urls": get_zillow_url(),
            },
        )

    def parse(self, response):
        current_page = response.meta.get("currentPage", 1)
        request_id = response.meta.get("request_id", 2)

        # Load the JSON response
        json_resp = json.loads(response.body)
        houses = json_resp.get("cat1", {}).get("searchResults", {}).get("listResults") or \
                json_resp.get("cat1", {}).get("searchResults", {}).get("mapResults", [])

        # Iterate over houses
        for house in houses:
            detail_url = house.get("detailUrl")
            if not detail_url:
                continue

            detail_link = detail_url if detail_url.startswith("http") else f"{BASE_URL}{detail_url}"

            # Skip if URL already processed
            if binary_search(response.meta["zillow_urls"], detail_link):
                self.logger.info("URL already exists in file, skipping.")
                continue
            
            # Yield request for apartment detailslliiut   7
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
                },
            )

    @inline_requests
    def parse_apartment_details(self, response):
        referer_url = response.meta["detail_url"]
        
        if response.status == 403:
            with open("log_error.txt", "a") as f:
                f.write(referer_url)
                f.write("\n")
                
        title = response.meta.get("title", "")
        unitNumber = (
            response.meta["unit_number"] if response.meta.get("unit_number") else ""
        )
        current_page = response.meta["current_page"]
        request_id = response.meta["request_id"]
        
        # Parent start
        if parent_title := response.xpath(
            "//h1[@data-test-id='bdp-building-title']/text()"
        ).get():
            title = parent_title

        amenity_list, features, property_list = [], [], []
        building_features = response.xpath("//div[@class='styles__StyledCategoryGroupHeadingContainer-sc-464t92-2 lewVis']")
        for building_feature in building_features:
            
            # Building Amenities
            if (building_feature.xpath( ".//h3/text()").get().lower() in ["building amenities"]):
                building_amenities = building_feature.xpath(".//following-sibling::div[1]/div")
                for amenity in building_amenities:
                    b_heading = amenity.xpath(".//h5/text()").get()
                    for idx, service in enumerate(amenity.xpath(".//ul/li")):
                        service_text = ""
                        for text in service.xpath(".//span"):
                            service_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if b_heading and idx < 1:
                            service_text = f"{b_heading}: {service_text}"
                            
                        amenity_list.append(service_text)
                        
            # Unit features
            if (building_feature.xpath( ".//h3/text()").get().lower() in ["unit features", "interior"]):
                unit_features = building_feature.xpath(".//following-sibling::div[1]/div")
                for u_feature in unit_features:
                    u_heading = u_feature.xpath(".//h5/text()").get()
                    for idx, service in enumerate(u_feature.xpath(".//ul/li")):
                        service_text = ""
                        for text in service.xpath(".//span"):
                            service_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if u_heading and idx < 1:
                            service_text = f"{u_heading}: {service_text}"
                            
                        features.append(service_text)
                        
            # Property list
            if (building_feature.xpath( ".//h3/text()").get().lower() in ["property", "properties"]):
                property_features = building_feature.xpath(".//following-sibling::div[1]/div")
                for p_feature in property_features:
                    p_heading = p_feature.xpath(".//h5/text()").get()
                    for idx, service in enumerate(p_feature.xpath(".//ul/li")):
                        service_text = ""
                        for text in service.xpath(".//span"):
                            service_text = "".join(
                                [i.get() for i in text.xpath(".//text()")]
                            )
                        if p_heading and idx < 1:
                            service_text = f"{p_heading}: {service_text}"
                        property_list.append(service_text)
        # Parent end
        
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

            if buildings.get("floorPlans"):
                address = response.xpath(
                    "//h2[@data-test-id='bdp-building-address']/text()"
                ).get()
                prop_website = response.xpath(
                    "//a[@data-test-id='bdp-ppc-link']/@href"
                ).get()
                            
                floorPlans = buildings["floorPlans"]
                lng = buildings["longitude"]
                lat = buildings["latitude"]
                
                if not features:
                    features = buildings["amenityDetails"]["unitFeatures"]

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

                    if floor.get("units"):
                        for unit in floor["units"]:
                            availablity = unit.get("availableFrom")
                            zpid = unit.get("zpid")

                            yield {
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
                                "Days on zillow": zillow_days,
                                "Contacts": contacts,
                                "Availability": "Available Now"
                                if availablity == "0"
                                else "",
                                "Description": description,
                                "Subsidized": subsidized,
                                "Unit features": features,
                                "Unit listing url": f"{response.meta['detail_url']}#unit-{zpid}",
                                "Building amenities": amenity_list,
                                "Property": property_list,
                                "Zillow url": response.meta["detail_url"],
                                "Property website": prop_website,
                                "Leasing Agent": agent,
                                "scrapeDate": datetime.now().date(),
                            }
                    else:
                        availablity = floor.get("availableFrom")
                        zpid = floor.get("zpid")

                        yield {
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
                            "Days on zillow": zillow_days,
                            "Contacts": contacts,
                            "Availability": "Available Now"
                            if availablity == "0"
                            else "",
                            "Description": description,
                            "Subsidized": subsidized,
                            "Unit features": features,
                            "Unit listing url": f"{response.meta['detail_url']}#unit-{zpid}",
                            "Building amenities": amenity_list,
                            "Property": property_list,
                            "Zillow url": response.meta["detail_url"],
                            "Property website": prop_website,
                            "Leasing Agent": agent,
                            "scrapeDate": datetime.now().date(),
                        }

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
                description = properties["description"]

                if not binary_search(response.meta["home_ids"], int(zpid)):
                    # Address
                    address = ""
                    for addr in response.xpath("//div[@class='styles__AddressWrapper-fshdp-8-100-2__sc-13x5vko-0 jrtioM']/h1"):
                        address = "".join([i.get() for i in addr.xpath(".//text()")])

                    # availablity
                    facts = properties["resoFacts"]["atAGlanceFacts"]
                    available = ""
                    for fact in facts:
                        if (
                            fact["factLabel"] == "Date available"
                            and fact["factValue"] == "Available Now"
                        ):
                            available = "Available Now"

                    # featurs
                    amenities, u_features, f_property_list = [], [], []
                    building_features = response.xpath("//div[@class='styles__StyledCategoryGroupHeadingContainer-fshdp-8-100-2__sc-1mj0p8k-2 ibHRlf']")
                    for building_feature in building_features:
                        
                        # Building Amenities
                        if (building_feature.xpath( ".//h3/text()").get().lower() in ["building amenities"]):
                            building_amenities = building_feature.xpath(".//following-sibling::div[1]/div")
                            for amenity in building_amenities:
                                b_heading = amenity.xpath(".//h6/text()").get()
                                for idx, service in enumerate(amenity.xpath(".//ul/li")):
                                    service_text = ""
                                    for text in service.xpath(".//span"):
                                        service_text = "".join(
                                            [i.get() for i in text.xpath(".//text()")]
                                        )
                                    if b_heading and idx < 1:
                                        service_text = f"{b_heading}: {service_text}"
                                    amenities.append(service_text)
                                    
                        # Unit features
                        if (building_feature.xpath( ".//h3/text()").get().lower() in ["unit features", "interior"]):
                            unit_features = building_feature.xpath(".//following-sibling::div[1]/div")
                            for u_feature in unit_features:
                                u_heading = u_feature.xpath(".//h6/text()").get()
                                for idx, service in enumerate(u_feature.xpath(".//ul/li")):
                                    service_text = ""
                                    for text in service.xpath(".//span"):
                                        service_text = "".join(
                                            [i.get() for i in text.xpath(".//text()")]
                                        )
                                    if u_heading and idx < 1:
                                        service_text = f"{u_heading}: {service_text}"
                                    u_features.append(service_text)
                                    
                        # Property list
                        if (building_feature.xpath( ".//h3/text()").get().lower() in ["property", "properties"]):
                            property_features = building_feature.xpath(".//following-sibling::div[1]/div")
                            for p_feature in property_features:
                                p_heading = p_feature.xpath(".//h6/text()").get()
                                for idx, service in enumerate(p_feature.xpath(".//ul/li")):
                                    service_text = ""
                                    for text in service.xpath(".//span"):
                                        service_text = "".join(
                                            [i.get() for i in text.xpath(".//text()")]
                                        )
                                    if p_heading and idx < 1:
                                        service_text = f"{p_heading}: {service_text}"
                                    f_property_list.append(service_text)
                                    
                    
                    unit_features = u_features if u_features else features
                    building_amenities = amenities if amenities else amenity_list
                    property_list = f_property_list if f_property_list else property_list

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
                    )
                    overview_data = json.loads(overview_resp.body)
                    contact = ""
                    with suppress(KeyError):
                        contact = overview_data["data"]["property"]["rentalListingOwnerReputation"]["contactCount"]

                    # UnitNumber
                    with suppress(KeyError):
                        target_unitNumber = properties["adTargets"]["aamgnrc2"]
                        if target_unitNumber in address:
                            if not "Unit" in target_unitNumber:
                                unitNumber = f"Unit {target_unitNumber}"

                    yield {
                        "home_id": zpid,
                        "Title": title,
                        "Address": address,
                        "Name": "",
                        "Beds": properties.get("bedrooms"),
                        "Baths": properties.get("bathrooms"),
                        "UnitNumber": unitNumber,
                        "Price": properties.get("price"),
                        "Sqft": properties["adTargets"].get("sqft")
                        or properties.get("livingArea"),
                        "Longitude": properties.get("longitude"),
                        "Latitude": properties.get("latitude"),
                        "Days on zillow": properties.get("daysOnZillow"),
                        "Contacts": contact,
                        "Availability": available,
                        "Description": description,
                        "Subsidized": subsidized,
                        "Unit features": unit_features,
                        "Unit listing url": f"https://www.zillow.com{unit_listing_url}",
                        "Building amenities": building_amenities,
                        "Property": property_list,
                        "Zillow url": response.meta["detail_url"],
                        "Property website": "",
                        "Leasing Agent": agent,
                        "scrapeDate": datetime.now().date(),
                    }

            except Exception as ex:
                print(f"Error: {ex}")
