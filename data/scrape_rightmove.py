from RightMover import RightmoveScraper

codes = {'London': '5E87490', 'Glasgow': '5E550', 'Liverpool': '5E813', 'Manchester': '5E904',
         'Leeds': '5E787', 'Nottingham': '5E1019', 'Edinburgh': '5E475', 'Brighton': '5E61480', 'Durham': '5E460'}

# for city_name in list(codes.keys()):
#     scraper = RightmoveScraper()
#     city = codes[city_name]
#     print(city_name)
#     scraper.run(city, city_name)

#     del scraper
scraper_London = RightmoveScraper()
city = codes["London"]
scraper_London.run(city, "London")

scraper_Glasgow = RightmoveScraper()
city = codes["Glasgow"]
scraper_Glasgow.run(city, "Glasgow")

scraper_Liverpool = RightmoveScraper()
city = codes["Liverpool"]
scraper_Liverpool.run(city, "Liverpool")

scraper_Manchester = RightmoveScraper()
city = codes["Manchester"]
scraper_Manchester.run(city, "Manchester")

scraper_Leeds = RightmoveScraper()
city = codes["Leeds"]
scraper_Leeds.run(city, "Leeds")

scraper_Nottingham = RightmoveScraper()
city = codes["Nottingham"]
scraper_Nottingham.run(city, "Nottingham")

scraper_Edinburgh = RightmoveScraper()
city = codes["Edinburgh"]
scraper_Edinburgh.run(city, "Edinburgh")

scraper_Brighton = RightmoveScraper()
city = codes["Brighton"]
scraper_Brighton.run(city, "Brighton")

scraper_Durham = RightmoveScraper()
city = codes["Durham"]
scraper_Durham.run(city, "Durham")
