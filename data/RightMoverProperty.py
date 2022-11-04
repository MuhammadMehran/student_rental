import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import re
import json


class RightmoveScraper:

    def __init__(self):
        self.results = []
        self.df = pd.DataFrame([])

    def fetch(self, url):
        print('HTTP GET request to URL: %s' % url, end='')
        response = requests.get(url)
        print(' | Status code: %s' % response.status_code)

        return response

    def parse(self, html):
        content = BeautifulSoup(html, 'lxml')

        titles = [title.text.strip() for title in content.findAll(
            'h2', {'class': 'propertyCard-title'})]
        links = ['https://www.rightmove.co.uk' +
                 link.get('href') for link in content.findAll('a', {'class': 'propertyCard-link'})]
        addresses = [address['content'] for address in content.findAll(
            'meta', {'itemprop': 'streetAddress'})]
        descriptions = [description.text for description in content.findAll(
            'span', {'data-test': 'property-description'})]
#         prices = [price.text.strip() for price in content.findAll('div', {'class': 'propertyCard-priceValue'})]
        prices = []
        sqfts = []

        for div in content.find('div', {'id', 'l-searchResults'}).findAll('div', {'class': 'l-searchResult is-list'}):

            if div.get('id') == 'property-0':
                continue
            try:
                prices.append(
                    div.find('div', {'class': 'propertyCard-priceValue'}).text.strip())
            except:
                prices.append(np.nan)

            try:
                sqfts.append(
                    div.find('span', attrs={
                             'class': 'propertyCard-commercial-sizing--link'}).text.replace('sq. ft.', '').replace(',', '').strip())
            except:
                sqfts.append(np.nan)

        dates = [date.text.split(' ')[-1] for date in content.findAll(
            'span', {'class': 'propertyCard-branchSummary-addedOrReduced'})]
        sellers = [seller.text.split('by')[-1].strip() for seller in content.findAll(
            'span', {'class': 'propertyCard-branchSummary-branchName'})]
        images = [image['src']
                  for image in content.findAll('img', {'itemprop': 'image'})]
        beds = []
        types = []

        for bed in content.findAll('h2', {'class': 'propertyCard-title'}):
            bed = bed.text.strip()
            nbed = bed.split(' ')[0]

            if nbed.isdigit():
                beds.append(nbed)

            else:
                if bed.split(' ')[0].lower() == 'studio':
                    beds.append('studio')
                elif bed.split(' ')[-1].lower() == 'share':
                    beds.append(1)
                else:
                    beds.append(np.nan)

            types.append(bed.split(' ')[-1])

        for index in range(0, len(prices)):
            self.results.append({
                'title': titles[index],
                'link': links[index],
                'address': addresses[index],
                'description': descriptions[index],
                'price': prices[index],
                'sq_ft': sqfts[index],
                'date': dates[index],
                'seller': sellers[index],
                'image': images[index],
                'bed': beds[index],
                'type': types[index].lower(),
            })

    def save(self, city_name):
        self.df = pd.DataFrame(self.results)
        try:
            self.df['price'] = self.df['price'].str.split(' ').str[0].replace(
                '[\$Â£,)]', '', regex=True).replace('[(]', '-',   regex=True)
            self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce')
        except:
            pass

        self.df['bed'] = self.df['bed'].astype(str)

        def get_lat_lon(address, city):
            address = address + ' ' + city + ' uk'
            url = 'https://nominatim.openstreetmap.org/search/' + address + '?format=json'

            response = requests.get(url).json()
            time.sleep(.8)
            try:
                return response[0]["lat"], response[0]["lon"]
            except:
                url = 'https://nominatim.openstreetmap.org/search/' + city + ' uk' + '?format=json'
                response = requests.get(url).json()
                try:
                    return response[0]["lat"], response[0]["lon"]
                except:
                    return np.nan, np.nan

        self.df['lat_lon'] = self.df['address'].apply(
            get_lat_lon, city=city_name)
        self.df['lat'], self.df['lon'] = zip(*self.df['lat_lon'])

        self.df['lat'] = self.df['lat'].astype(float)
        self.df['lon'] = self.df['lon'].astype(float)

        # def get_sq_ft(link):
        #     print('GET', link)
        #     r = requests.get(link)
        #     try:
        #         data = json.loads(r.text.split('window.PAGE_MODEL = ')[
        #                           1].split('</script>')[0].strip())
        #         similar_url = 'https://www.rightmove.co.uk' + \
        #             data['propertyData']['propertyUrls']['similarPropertiesUrl']
        #     except:
        #         similar_url = np.nan
        #     try:
        #         words = r.text.lower().split(' ')
        #         index = words.index('sq.')
        #         return words[index-1], similar_url
        #     except:
        #         try:
        #             words = r.text.lower().split(' ')
        #             index = words.index('nbsp;sq.')
        #             return words[index-1], similar_url
        #         except:
        #             return np.nan, similar_url

        # self.df['sq_ft_sim'] = self.df['link'].apply(get_sq_ft)
        self.df['sq_ft'] = self.df['sq_ft'].str.split(
            '–').str[-1]

    def run(self, city=None, city_name=None):
        if city == None:
            return None, None
        page = 0
        pages = 2
        while page < pages:
            index = page * 24
            print(f'Page: {page+1}')
            url = f'https://www.rightmove.co.uk/commercial-property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%{city}&index=' + \
                str(index) + '&insId=1&radius=0.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=commercial&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false'

            response = self.fetch(url)
            if response.status_code != 200:
                break
            if page == 0:
                soup = BeautifulSoup(response.text)
                nres = int(
                    soup.find('span', {'class': 'searchHeader-resultCount'}).text.replace(',', ''))
                pages = nres/24
                if int(pages) < pages:
                    pages = int(pages) + 1

            try:
                self.parse(response.text)
            except:
                pass
            page += 1

        self.save(city_name=city_name)
        self.df['nres'] = nres
        self.df.to_csv(city_name+'.csv', index=False)
