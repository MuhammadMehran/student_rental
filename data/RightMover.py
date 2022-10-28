from symbol import except_clause
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import re


class RightmoveScraper:
    results = []
    df = pd.DataFrame([])

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
        prices_weekly = []
        for div in content.find('div', {'id', 'l-searchResults'}).findAll('div', {'class': 'l-searchResult is-list'}):

            if div.get('id') == 'property-0':
                continue
            try:
                prices.append(
                    div.find('span', {'class': 'propertyCard-priceValue'}).text.strip())

            except:
                prices.append(np.nan)

            try:
                prices_weekly.append(
                    div.find('span', {'class': 'propertyCard-secondaryPriceValue'}).text.strip())
            except:
                prices_weekly.append(np.nan)

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
                'price_weekly': prices_weekly[index],
                'date': dates[index],
                'seller': sellers[index],
                'image': images[index],
                'bed': beds[index],
                'type': types[index].lower(),
            })

    def to_csv(self, city, city_name):
        self.df = pd.DataFrame(self.results)
        self.df['price'] = self.df['price'].str.split(' ').str[0].replace(
            '[\$Â£,)]', '', regex=True).replace('[(]', '-',   regex=True).astype(float)
        self.df['price_weekly'] = self.df['price_weekly'].str.split(' ').str[0].replace(
            '[\$Â£,)]', '', regex=True).replace('[(]', '-',   regex=True).astype(float)
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

        def get_sq_ft(link):
            print('GET', link)
            r = requests.get(link)

            try:
                words = r.text.lower().split(' ')
                index = words.index('sq.')
                return words[index-1]
            except:
                try:
                    words = r.text.lower().split(' ')
                    index = words.index('nbsp;sq.')
                    return words[index-1]
                except:
                    return np.nan
        self.df['sq_ft'] = self.df['link'].apply(get_sq_ft)

    def run(self, city=None, city_name=None):
        if city == None:
            return None, None
        page = 0
        pages = 2
        while page < pages:
            index = page * 24
            print(f'Page: {page+1}')
            url = f'https://www.rightmove.co.uk/student-accommodation/find.html?locationIdentifier=REGION%{city}&index=' + \
                str(index) + '&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords='

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
        self.df['nres'] = nres
        self.df.to_csv(city_name+'.csv', index=False)
