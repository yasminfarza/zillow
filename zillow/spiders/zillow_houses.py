import scrapy
from scrapy.loader import ItemLoader
from zillow.utils import cookie_parser
from zillow.items import ZillowItem
import json
import w3lib.html

URL = "https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%22usersSearchTerm%22%3A%22Philadelphia%2C%20PA%22%2C%22mapBounds%22%3A%7B%22west%22%3A-75.295343%2C%22east%22%3A-74.955763%2C%22south%22%3A39.848844%2C%22north%22%3A40.137992%7D%2C%22isMapVisible%22%3Afalse%2C%22filterState%22%3A%7B%22isForSaleByAgent%22%3A%7B%22value%22%3Afalse%7D%2C%22isForSaleByOwner%22%3A%7B%22value%22%3Afalse%7D%2C%22isNewConstruction%22%3A%7B%22value%22%3Afalse%7D%2C%22isForSaleForeclosure%22%3A%7B%22value%22%3Afalse%7D%2C%22isComingSoon%22%3A%7B%22value%22%3Afalse%7D%2C%22isAuction%22%3A%7B%22value%22%3Afalse%7D%2C%22isForRent%22%3A%7B%22value%22%3Atrue%7D%2C%22isAllHomes%22%3A%7B%22value%22%3Atrue%7D%2C%22isMultiFamily%22%3A%7B%22value%22%3Afalse%7D%2C%22isManufactured%22%3A%7B%22value%22%3Afalse%7D%2C%22isLotLand%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A13271%7D%5D%2C%22pagination%22%3A%7B%7D%7D&wants={%22cat1%22:[%22listResults%22],%22regionResults%22:[%22regionResults%22]}&requestId=3"

class ZillowHousesSpider(scrapy.Spider):
    name = "zillow_houses"
    allowed_domains = ["www.zillow.com"]
    # start_urls = [URL]
    
    def start_requests(self):
        yield scrapy.Request(
            url=URL,
            callback=self.parse_details,
            cookies=cookie_parser(),
            meta={
                'currentPage': 1
            }
        )

    def parse(self, response):
        current_page = response.meta['currentPage']
        json_resp = json.loads(response.body)
        houses = json_resp.get('cat1').get('searchResults').get('mapResults')
        
        for house in houses:
            loader = ItemLoader(item=ZillowItem())
            loader.add_value('id', house.get('id'))
            loader.add_value('address', house.get('address'))
            loader.add_value('building_id', house.get('buildingId'))
            loader.add_value('detail_url', house.get('detailUrl'))
            loader.add_value('image_urls', house.get('imgSrc'))
            loader.add_value('latitude', house.get('latLong').get('latitude'))
            loader.add_value('longitude', house.get('latLong').get('longitude'))
            loader.add_value('lot_id', house.get('lotId'))
            loader.add_value('price', house.get('price'))
            loader.add_value('min_area', house.get('minArea'))
            loader.add_value('min_baths', house.get('minBaths'))
            loader.add_value('min_beds', house.get('minBeds'))
            loader.add_value('status_text', house.get('statusText'))
            yield loader.load_item()
        
        total_pages = json_resp.get('cat1').get('searchList').get('totalPages')
        if current_page <= total_pages:
            current_page += 1
            yield scrapy.Request(
                url=parse_new_url(URL, page_number=current_page),
                callback=self.parse,
                cookies=cookie_parser(),
                meta={
                    'currentPage': current_page
                }
        )
        
        # with open('initial_response.json', 'wb') as f:
        #     f.write(response.body)

    def parse_details(self, response):
        json_resp = json.loads(response.body)

        with open('initial_response_01.json', 'wb') as f:
            f.write(response.body)
            
        houses = json_resp.get('cat1').get('searchResults').get('listResults')

        for i, house in enumerate(houses):
            if i > 3:
                break
            
            detail_url = house.get('detailUrl')
            detail_link = f"https://www.zillow.com{detail_url}"

            yield scrapy.Request(
                url=detail_link,
                callback=self.parse_apartment_details,
                cookies=cookie_parser(),
                meta={
                    'detail_url': detail_link
                }
            )

    def parse_apartment_details(self, response):
        # For house details
        # for row in response.xpath("//div[@data-test-id='building-units-card-groups-container-for-rent']/div/div"): 

        # For apartment floorplans
        next_response = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        floorPlans = json.loads(next_response)['props']['pageProps']['initialReduxState']['gdp']['building']['floorPlans']

        for floor in floorPlans:
            zpid = floor['zpid']

            if floor.get("units"):
                for unit in floor["units"]:
                    yield {
                        "Title": response.xpath("//h1[@data-test-id='bdp-building-title']/text()").get(),
                        "Address": response.xpath("//h2[@data-test-id='bdp-building-address']/text()").get(),
                        "Zpid": zpid,
                        "Name": floor.get('name'),
                        "Beds": floor.get('beds'),
                        "Baths": floor.get('baths'),
                        "UnitNumber": unit.get('unitNumber'),
                        "Price": unit.get('price'),
                        "Sqft": unit.get('sqft'),
                    }
                
    # def parse_home_details(self, response):
    #     price = response.xpath("//div[@class='hdp__sc-1ct91g9-1 dXQfMK']/span")
    #     area = response.xpath("//span[@data-testid='bed-bath-beyond']/span[4]")
    #     address = w3lib.html.remove_comments(response.xpath("//div[@class='hdp__sc-1h7w8w-0 gqiYGo']/h1/text()").get())
        

    #     print(w3lib.html.remove_comments(area.xpath(".//span/text()").get()))
    #     print(response.xpath("//div[@class='hdp__sc-1h7w8w-0 gqiYGo']/h1").get())
    #     print(address)

    #     yield {
    #         "price": f'{price.xpath(".//text()").get()}{price.xpath(".//span/text()").get()}',
    #         "area": f'{area.xpath(".//strong/text()").get()}{w3lib.html.remove_comments(area.xpath(".//span/text()").get())}',
    #         "address": address
    #     }


