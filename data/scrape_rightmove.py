from RightMover import RightmoveScraper

codes = {'London': '5E87490', 'Glasgow': '5E550', 'Liverpool': '5E813', 'Manchester': '5E904',
         'Leeds': '5E787', 'Nottingham': '5E1019', 'Edinburgh': '5E475', 'Bristol': '5E219', 'Durham': '5E460'}

for city_name in list(codes.keys()):
    scraper = RightmoveScraper()
    city = codes[city_name]
    print(city_name)
    scraper.run(city, city_name)

    del scraper
