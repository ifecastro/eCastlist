from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import requests
from . import models
from urllib.parse import quote_plus
import demjson
import re


def home(request):
    return render(request, 'base.html')


# Page url, Concatenating search parameters to base url
olist_url = 'https://olist.ng/filter?keyword={}&city_name='
ali_url = "https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20200706145831&SearchText={}"
RATES_URL = 'https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=NGN'


@csrf_exempt
def new_search(request):
    searches = request.POST.get('search')
    models.Search.objects.create(search=searches)

    # OLIST SCRAPPING BEGINS HERE

    # Extracting page HtmL
    final_url = olist_url.format(quote_plus(searches))
    response = requests.get(final_url)
    data = response.content

    # Parsing html
    soup = BeautifulSoup(data, 'html.parser')
    all_listing_details = soup.find_all('a', {'class': 'item'})

    item_details = []

    # Looping through the html "a" tag to get Product details
    for all_items in all_listing_details:
        title = all_items.find(class_='title').text
        price = all_items.find(class_='price').text
        description = all_items.find(class_='content-body').text
        location = all_items.find(class_='regionMessage').text
        url = all_items.get('href')
        image = all_items.find('img').get('src')
        item_details.append((title[:33], image, description[:50], price, location, description[50:], url))

    # OLIST SCRAPPING ENDS HERE

    # ALIEXPRESS SCRAPPING BEGINS HERE
    final_url = ali_url.format(quote_plus(searches))

    # Extracting page Html
    response = requests.get(final_url)
    data = response.content

    # Parsing html
    soup = BeautifulSoup(data, 'html.parser')

    # Fetching contents of a script tag, spliting it, converting to string and eliminating unwanted data, then index.
    all_listing_details = soup.findAll('script', {'type': 'text/javascript'})[3]
    script_to_string = all_listing_details.string.split(" = ")[2]
    string_finetune = re.sub('\s+', ' ', script_to_string).split("; ")[0]

    # converting string to dictionary
    string_to_dict = demjson.decode(string_finetune)

    item_details_2 = []

    #Looping through the dictionary to get Product details
    for index in range(len(string_to_dict["items"])):
        title = string_to_dict["items"][index]["title"]
        price = string_to_dict["items"][index]["price"]
        image = string_to_dict["items"][index]["imageUrl"]
        link = string_to_dict["items"][index]["productDetailUrl"]
        item_details_2.append((title, price, image, link))

    # ALIEXPRESS SCRAPPING ENDS HERE

    # Pushing all retrieved details to front end
    front_end = {
        'searching': searches,
        'item_details': item_details,
        'item_details_2': item_details_2,

    }

    return render(request, 'myapp/new_search.html', front_end)
