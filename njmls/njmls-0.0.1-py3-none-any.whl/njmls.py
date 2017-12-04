import yaml
import requests
import lxml.html

__version__ = '0.0.1'

# response = requests.get("http://www.njmls.com/search.cfm")

def get_listing_detail(mlsnum):
    response = requests.get(f"http://www.njmls.com/listings/index.cfm?action=dsp.info&mlsnum={mlsnum}")
    return response.text

# county search
"http://www.njmls.com/listings/index.cfm?action=dsp.results&county=PASSAIC&state=NJ&proptype=1%2C3a%2C3b&searchtype=county_search&status=A"

# zip code radius search
"http://www.njmls.com/listings/index.cfm?action=dsp.results&zipcode=07013&radius=1&proptype=1%2C3a%2C3b&searchtype=zipcode_search&status=A"

# multi-city search
# njmlsLOC
# {"city":"CLIFTON","state":"NJ","county":"PASSAIC","zip":"07011"}|{"city":"WAYNE","state":"NJ","county":"PASSAIC","zip":"07470"}
"http://www.njmls.com/listings/index.cfm?action=dsp.results&city=&county=&state=&zipcode=&openhouse=&keywords=&mls_number=&searchtype=sale&style=&proptype=1&checktwn=&location=&beds=&baths=&minprice=&maxprice=&status=A"

valid_actions = [
    'dsp.results',
    'xhr.results.view.photo',
    'xhr.results.view.list',
    'dsp.search.new',
    'xhr.results.view.list.search']

# proptypes = {
#     "Single Family": "1",
#     "Condo/Townhouse": "3a",
#     "Coop": "3b",
#     "2-4 Family": "2",
#     "Land": "8",
#     "Commercial": "5",
#     "Business": "7",
#     "5+ Family/Mixed Use": "9"
# }

# year_built = {
#     "2000s - New": "2010'S|2000'S|NEW|TBB|TO BE BLT",
#     "1950s - 1990s": "1950'S|1960'S|1970'S|1980'S|1990'S",
#     "Before 1950": "PRE 1900|1900-1939|1900'S|1910'S|1920'S|1930'S|1940'S",
# }

def get_listings_inner(
    page,
    display=30,
    min_beds=0,
    min_baths=0,
    zipcode='',
    radius='',
    city='',
    location='',
    max_price='',
    min_price='',
    days_since='',
    new_listings='',
    price_changed='',
    keywords='',
    mls_number='',
    garage='',
    basement='',
    fireplace='',
    pool='',
    open_house='',
    open_house_date='',
    style='',
    status='A',
    year_built="",
    sort_by="newest",
    counties=[],
    county_search='',
    proptypes=[]):

    response = requests.get("http://www.njmls.com/listings/index.cfm", params={
        "zoomlevel": "0",
        "action": "xhr.results.view.list",
        "page": page,
        "display": display,
        "sortBy": sort_by,
        "location": location,
        "city": city,
        "state": "NJ",
        "county": ','.join(counties),
        "zipcode": zipcode,
        "radius": radius,
        "proptype": ','.join(proptypes),
        "maxprice": max_price,
        "minprice": min_price,
        "beds": str(min_beds),
        "baths": str(min_baths),
        "dayssince": days_since,
        "newlistings": str(new_listings).lower(),
        "pricechanged": str(price_changed).lower(),
        "keywords": keywords,
        "mls_number": mls_number,
        "garage": str(garage).lower(),
        "basement": str(basement).lower(),
        "fireplace": str(fireplace).lower(),
        "pool": str(pool).lower(),
        "yearBuilt": "",
        "building": "",
        "officeID": "",
        "openhouse": str(open_house).lower(),
        "countysearch": str(county_search).lower(),
        "ohdate": open_house_date,
        "style": style,
        "status": status,
        "emailalert_yn": "N", # what is this?
    })

    return response

def parse_row(row):
    data_str = row.get('class').lstrip('houseresults listingrecord')
    # Yaml requres a space after the colon
    # http://pyyaml.org/wiki/YAMLColonInFlowContext
    data_str = data_str.replace(":'", ": '")
    data = yaml.load(data_str)
    data.pop('oh') # don't care about open house temporarily
    data.pop('detailurl') # don't care about detailurl for now, mls_number should be enough
    # /listings/index.cfm?action=dsp.info&mlsnum=1746570&dayssince=15&countysearch=true
    return data

def get_listings(**kwargs):

    response = get_listings_inner(page=1, **kwargs)
    doc = lxml.html.fromstring(response.text)
    current_page = int([x.text for x in doc.cssselect('#pagelist2 ol.pagenumbers li:not(.currentPage)') if not x.get('a')][0])
    last_page = int(doc.cssselect('#pagelist2 ol.pagenumbers li.currentPage:last-child')[0].text.replace('of ', ''))
    result_count = int(doc.cssselect("#resultcount")[0].text)
    # if result_count == 500:
    #     logging.warning("only returning first 500 results")
    # print("page", current_page, "of", last_page)
    # print("result count", )
    yield from [parse_row(x) for x in doc.cssselect("#list-view-wrap .houseresults")]

    for i in range(2, last_page+1):
        # print(f"getting page {i}")
        response = get_listings_inner(page=i, **kwargs)
        doc = lxml.html.fromstring(response.text)
        yield from [parse_row(x) for x in doc.cssselect("#list-view-wrap .houseresults")]
