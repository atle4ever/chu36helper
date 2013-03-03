from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class ElevenStSpider(BaseSpider):
    name = "shopping"
    start_urls = [ "http://www.11st.co.kr/product/SellerProductDetail.tmall?method=getSellerProductDetail&xfrom=search^prd&prdNo=31719542&trTypeCd=20&trCtgrNo=585021&lCtgrNo=14594&mCtgrNo=15858" ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        price = hxs.select('//*[@id="addAllSelPrc"]/@value').extract()[0].encode("utf-8")
        disPrice = hxs.select('//*[@name="discountPrc"]/@value').extract()[0].encode("utf-8")
        
        self.request.write(price + "," + disPrice)
        self.request.finish()

from twisted.web import server, resource
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings

class HelloResource(resource.Resource):
    isLeaf = True
    numberRequests = 0
    
    def render_GET(self, request):
        spider = ElevenStSpider()
        spider.request = request
        crawler = Crawler(Settings())
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()

        return server.NOT_DONE_YET

reactor.listenTCP(8080, server.Site(HelloResource()))
reactor.run()
