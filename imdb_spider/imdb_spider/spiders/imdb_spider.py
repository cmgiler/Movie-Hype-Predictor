import scrapy
import pickle


class IMDBSpider(scrapy.Spider):
    name = 'imdb_spider'

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 3,
        "HTTPCACHE_ENABLED": True
    }

    with open("../my_data.pkl", 'rb') as picklefile:
        links = list(pickle.load(picklefile))

    start_urls = [
        'http://www.imdb.com/title/%s/' % l for l in links
    ]

    def parse(self, response):
        # Extract the links to the individual festival pages
        if 'Box Office' in response.xpath('//h3[@class="subheading"]/text()').extract():
            title_id = response.url.split('/')[-2]

            # response.url()
            title = response.xpath('//h1[@itemprop="name"]/text()').extract()[0].replace('\xa0','')
            release = response.xpath('//div[@class="subtext"]/a/text()').extract()[0].replace('\n','')
            try:
                rating = response.xpath('//meta[@itemprop="contentRating"]/@content').extract()[0]
            except:
                rating = ''

            try:
                director = response.xpath('//span[@itemprop="director"]/a/span[@itemprop="name"]/text()').extract()[0]
            except:
                director = ''

            try:
                studio = response.xpath('//span[@itemprop="creator"][@itemtype="http://schema.org/Organization"]/a/span[@itemprop="name"]/text()').extract()[0]
            except:
                studio = ''

            moneys = response.xpath('//h3[@class="subheading"]')[0].xpath('following-sibling::div/text()').re(r'\$[0-9,]+')
            money_labels = response.xpath('//h3[@class="subheading"]')[0].xpath('following-sibling::div/h4/text()').extract()
            moneys = [i.replace(',','').replace('$','') for i in moneys]

            budget = ''
            opening = ''
            gross = ''
            worldwide_gross = ''
            try:
                for m, l in zip(moneys, money_labels[:len(moneys)]):
                    if 'budget' in l.lower():
                        budget = m
                    elif 'opening' in l.lower():
                        opening = m
                    elif 'worldwide' in l.lower():
                        worldwide_gross = m
                    elif 'gross' in l.lower():
                        gross = m
                    else:
                        continue
            except:
                pass

            try:
                metacritic_score = response.xpath('//div[@class="titleReviewBarItem"]/a/div/span/text()').extract()[0]
            except:
                metacritic_score = ''

            yield {
                    'title_id': title_id,
                    'title': title,
                    'release': release,
                    'director': director,
                    'studio': studio,
                    'budget': budget,
                    'opening': opening,
                    'gross': gross,
                    'worldwide_gross': worldwide_gross,
                    'metacritic_score': metacritic_score,
                    'mpaa_rating': rating
                }

        # Follow pagination links and repeat