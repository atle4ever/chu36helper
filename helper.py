from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class ElevenStSpider(BaseSpider):
    """ Spider for www.11st.co.kr """

    name = "shopping"
    start_urls = [ "http://www.11st.co.kr/product/SellerProductDetail.tmall?method=getSellerProductDetail&xfrom=search^prd&prdNo=31719542&trTypeCd=20&trCtgrNo=585021&lCtgrNo=14594&mCtgrNo=15858" ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        name = hxs.select('//p[@class="pro_tit_v2"]/text()').extract()[0].encode("utf-8")
        price = hxs.select('//*[@id="addAllSelPrc"]/@value').extract()[0].encode("utf-8")
        disPrice = hxs.select('//*[@name="discountPrc"]/@value').extract()[0].encode("utf-8")

        # each product has different type of delivery charge
        deliveryCharge = hxs.select('//*[@id="dlvCstInfo3"]').extract()[0]
        if(deliveryCharge.find("<span") == 0): # always same value
            deliveryCharge = hxs.select('//*[@id="dlvCstInfo3"]/text()').extract()[0].encode("utf-8")
        else: # changed by dropdown box
            deliveryCharge = hxs.select('//*[@id="dlvCstInfo3"]/span/text()').extract()[0].encode("utf-8")

        sellerId = hxs.select('//*[@id="prodetail_ns4"]/div[1]/div[2]/p[1]/a/text()').extract()[0].encode("utf-8")
        sellerName = hxs.select('//*[@id="dvPrdInfoWrap"]/table[4]/tr[1]/td[2]/text()').extract()[0].encode("utf-8")
        registerNo = hxs.select('//*[@id="dvPrdInfoWrap"]/table[4]/tr[2]/td[1]/span/text()').extract()[0].encode("utf-8")
        
        self.request.write("name: " + name + "<br />")
        self.request.write("price: " + price + "<br / >")
        self.request.write("disPrice: " + disPrice + "<br />")
        self.request.write("diff: " + str(int(price) - int(disPrice)) + "<br />")
        self.request.write("deliveryCharge: " + deliveryCharge + "<br />")
        self.request.write("sellerId: " + sellerId + "<br />")
        self.request.write("sellerName: " + sellerName + "<br />")
        self.request.write("registerNo: " + registerNo + "<br />")
        self.request.finish()

from twisted.web import server, resource, static
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings

class Parser(resource.Resource):
    """ Transfer url to proper spider """

    isLeaf = True
    numberRequests = 0
    
    def render_GET(self, request):
        url = request.args['url']

        if(url[0].find("http://www.11st.co.kr") == 0):
            spider = ElevenStSpider()
        else:
            return "Invalid URL. Please check again<br />" + url[0]

        spider.request = request
        spider.start_urls = request.args['url']
        crawler = Crawler(Settings())
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()

        return server.NOT_DONE_YET

root = resource.Resource()
root.putChild("", static.File("./index.html"))
root.putChild("parser", Parser())
factory = server.Site(root)
reactor.listenTCP(8080, factory)
reactor.run()
