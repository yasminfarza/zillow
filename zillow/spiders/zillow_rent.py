from datetime import datetime
from inline_requests import inline_requests
import scrapy
from contextlib import suppress
from zillow.utils import cookie_parser, parse_new_url, get_home_id, binary_search, get_zillow_url
import json

URL = "https://www.zillow.com/async-create-search-page-state"
payload = '{"searchQueryState":{"pagination":{},"isMapVisible":false,"mapBounds":{"west":-75.38716493847656,"east":-74.86394106152343,"south":39.83240993228022,"north":40.15435271085413},"usersSearchTerm":"Philadelphia, PA","regionSelection":[{"regionId":13271,"regionType":6}],"filterState":{"isForRent":{"value":true},"isForSaleByAgent":{"value":false},"isForSaleByOwner":{"value":false},"isNewConstruction":{"value":false},"isComingSoon":{"value":false},"isAuction":{"value":false},"isForSaleForeclosure":{"value":false}},"isListVisible":true,"mapZoom":11},"wants":{"cat1":["listResults"]},"requestId":7,"isDebugRequest":false}'

class ZillowRentSpider(scrapy.Spider):
    name = "zillow_rent"
    allowed_domains = ["www.zillow.com"]

    def start_requests(self):
        yield scrapy.Request(
            url=URL,
            callback=self.parse,
            method="PUT",
            body=payload,
            cookies=cookie_parser(),
            meta={
                "currentPage": 1,
                "request_id": 2,
                "home_ids": get_home_id(),
                "zillow_urls": get_zillow_url(),
            },
        )

    def parse(self, response):
        current_page = response.meta["currentPage"]
        request_id = response.meta["request_id"]
        
        json_resp = json.loads(response.body)

        houses = json_resp.get("cat1").get("searchResults").get("listResults")
        if not houses:
            houses = json_resp.get("cat1").get("searchResults").get("mapResults")

        for i, house in enumerate(houses):
            # if i > 1:
            #     break
            detail_url = house.get("detailUrl")
            if "http" in detail_url:
                detail_link = detail_url
            else:
                detail_link = f"https://www.zillow.com{detail_url}"

            # if binary_search(response.meta["zillow_urls"], detail_link):
            #     print("Exist in File  ")
            #     break
            
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

        if current_page <= 25:
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
                meta={"currentPage": current_page, "request_id": request_id, 
                    "home_ids": response.meta["home_ids"],
                    "zillow_urls": response.meta["zillow_urls"],
                    },
            )

    @inline_requests
    def parse_apartment_details(self, response):
        referer_url = response.meta["detail_url"]
        unitNumber = (
            response.meta["unit_number"] if response.meta.get("unit_number") else ""
        )
        current_page = response.meta["current_page"]
        request_id = response.meta["request_id"]

        # For full building details link
        if full_building_link := response.xpath(
            "//ul[@class='zsg-tooltip-viewport']/li[1]/div/div/div[2]/a/@href"
        ).get():
            referer_url = f"https://www.zillow.com{full_building_link}"
            yield scrapy.Request(
                url=referer_url,
                callback=self.parse_apartment_details,
                cookies=cookie_parser(),
                meta={
                    "detail_url": response.meta["detail_url"],
                    "current_page": current_page,
                    "request_id": request_id,
                    "home_ids": response.meta["home_ids"],
                },
            )

        # For apartment floorplans
        next_response = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()

        # with open('before_Full2.json', 'w', encoding="utf-8") as f:
        #     print("file write")
        #     f.write(next_response)

        try:
            if json.loads(next_response)["props"]["pageProps"].get("initialReduxState"):
                buildings = json.loads(next_response)["props"]["pageProps"]["initialReduxState"]["gdp"]["building"]
            else:
                buildings = json.loads(next_response)["props"]["pageProps"]["componentProps"]["initialReduxState"]["gdp"]["building"]

            # What special
            description = buildings.get("description")

            if buildings.get("floorPlans"):
                title = response.xpath(
                    "//h1[@data-test-id='bdp-building-title']/text()"
                ).get()
                address = response.xpath(
                    "//h2[@data-test-id='bdp-building-address']/text()"
                ).get()
                prop_website = response.xpath(
                    "//a[@data-test-id='bdp-ppc-link']/@href"
                ).get()

                # Building Amenities
                amenity_list = []
                if (
                    response.xpath(
                        "//div[@class='styled__BuildingAmenitiesContainer-sc-1jv0y0i-4 enHuDw']/h3/text()"
                    ).get()
                    == "Building Amenities"
                ):
                    building_amenities = response.xpath(
                        "//div[@class='styled__BuildingAmenitiesContainer-sc-1jv0y0i-4 enHuDw'][1]/div"
                    )
                    for amenity in building_amenities:
                        services = amenity.xpath(".//ul/li")
                        for service in services:
                            amenity_list.append(service.xpath(".//text()").get())
                floorPlans = buildings["floorPlans"]
                lng = buildings["longitude"]
                lat = buildings["latitude"]
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
                    with suppress(KeyError):
                        agent_name = agent_info["propertyInfo"]["agentInfo"]["displayName"]
                        business_name = agent_info["propertyInfo"]["agentInfo"]["businessName"]
                        
                    zillow_days, contacts, subsidized = "", "", ""

                    if not agent_name and not business_name:
                        agent = "Name undisclosed"
                    elif not agent_name:
                        agent = business_name
                    elif not business_name:
                        agent = agent_name
                    else:
                        agent = f"{agent_name} - {business_name}"

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
                        referer_url = f"https://www.zillow.com{ungroupedUnit['hdpUrl']}"

                        yield scrapy.Request(
                            url=referer_url,
                            callback=self.parse_apartment_details,
                            cookies=cookie_parser(),
                            meta={
                                "detail_url": response.meta["detail_url"],
                                "unit_number": unitNumber,
                                "current_page": current_page,
                                "request_id": request_id,
                                "home_ids": response.meta["home_ids"],
                            },
                        )

        except KeyError as e:
            print(e)
            
            try:
                if json.loads(next_response)["props"]["pageProps"].get("*"):
                    gdpClientCache = json.loads(next_response)["props"]["pageProps"]["gdpClientCache"]
                else:
                    gdpClientCache = json.loads(next_response)["props"]["pageProps"]["componentProps"]["gdpClientCache"]
                page_Value = json.loads(gdpClientCache).values()
                properties = list(page_Value)[0]["property"]
                zpid = properties["zpid"]
                description = properties["description"]

                if not binary_search(response.meta["home_ids"], int(zpid)):
                    # Address
                    address = ""
                    for addr in response.xpath("//div[@class='hdp__sc-1h7w8w-0 gqiYGo']/h1"):
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
                            "Origin": "https://www.zillow.com",
                            "Referer": referer_url,
                        }
                    overview_resp = yield scrapy.Request(
                        url=f"https://www.zillow.com/graphql/?zpid={zpid}&operationName=ListingContactDetailsQuery",
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
                        "Title": "",
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
                        "Unit listing url": "",
                        "Building amenities": building_amenities,
                        "Zillow url": response.meta["detail_url"],
                        "Property website": "",
                        "Leasing Agent": agent,
                        "scrapeDate": datetime.now().date(),
                    }

            except Exception as ex:
                print(f"Error: {ex}")
                with open("log_error.txt", "a") as f:
                    f.write(response.meta["detail_url"])
                    f.write("\n")
                    f.close()
