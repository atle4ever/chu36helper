# html templates
elevenStHtml = """
<!DOCTYPE html>

<html>
    <head>
        <script language="javascript" type="text/javascript" src="jsFlashEncode.js"></script>
    </head>

    <body>
        name: {0} <br />
        price: {1} <br />
        disPrice: {2} <br />
        diff: {3} <br />
        deliveryCharge: {4} <br />
        sellerId: {5} <br />
        companyName: {6} <br />
        registerNo: {7} <br />
    </body>
</html>
"""

gmarketHtml = """
<!DOCTYPE html>

<html>
    <head>
        <script language="javascript" type="text/javascript" src="jsFlashEncode.js"></script>
    </head>

    <body>
        name: {0} <br />
        price: {1} <br />
        disPrice: {2} <br />
        diff: {3} <br />
        deliveryCharge: {4} <br />
        sellerName: {5} <br />
        companyName: {6} <br />
        registerNo: {7} <br />
    </body>
</html>
"""

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

class ElevenStSpider(BaseSpider):
    """ Spider for www.11st.co.kr """

    name = "11st spider"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # get data
        name = hxs.select('//p[@class="pro_tit_v2"]/text()').extract()[0].encode("utf-8")
        price = hxs.select('//*[@id="addAllSelPrc"]/@value').extract()[0].encode("utf-8")
        disPrice = hxs.select('//*[@name="discountPrc"]/@value').extract()[0].encode("utf-8")
        diff = str(int(price) - int(disPrice))

        # each product has different type of delivery charge
        deliveryCharge = hxs.select('//*[@id="dlvCstInfo3"]').extract()[0]
        if(deliveryCharge.find("<span") == 0): # always same value
            deliveryCharge = hxs.select('//*[@id="dlvCstInfo3"]/text()').extract()[0].encode("utf-8")
        else: # changed by dropdown box
            deliveryCharge = hxs.select('//*[@id="dlvCstInfo3"]/span/text()').extract()[0].encode("utf-8")

        sellerId = hxs.select('//*[@id="prodetail_ns4"]/div[1]/div[2]/p[1]/a/text()').extract()[0].encode("utf-8")
        companyName = hxs.select('//*[@id="dvPrdInfoWrap"]/table[4]/tr[1]/td[2]/text()').extract()[0].encode("utf-8")
        registerNo = hxs.select('//*[@id="dvPrdInfoWrap"]/table[4]/tr[2]/td[1]/span/text()').extract()[0].encode("utf-8")
        
        # render template
        html = gmarketHtml.format(name, price, disPrice, diff, deliveryCharge, sellerId, companyName, registerNo)
    
        # return html string
        self.request.write(html)
        self.request.finish()

class GmartketSpider(BaseSpider):
    """ Spider for www.gmarket.co.kr """

    name = "Gmaret spider"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # get data
        name = hxs.select('//*[@class="tit-goodsnum"]/p/text()').extract()[0].encode("utf-8")
        price = hxs.select('//*[@id="order_price"]/@value').extract()[0].encode("utf-8")

        # disPrice in Gmarket contains ','
        disPrice = hxs.select('//span[@id="dc_price"]/text()').extract()[0].encode("utf-8")
        disPrice = disPrice.replace(",", "")

        diff = str(int(price) - int(disPrice))

        deliveryCharge = hxs.select('//*[@id="delivery_fee_tr"]/td/div/strong/text()').extract()[0].encode("utf-8")

        sellerNameCode = hxs.select('//*[@class="goods-info"]/tbody')[1].select('tr[1]/td[1]/script').extract()[0]
        companyNameCode = hxs.select('//*[@class="goods-info"]/tbody')[1].select('tr[1]/td[2]/script').extract()[0]
        registerNoCode = hxs.select('//*[@class="goods-info"]/tbody')[1].select('tr[4]/td[1]/script').extract()[0]

        # render template
        html = gmarketHtml.format(name, price, disPrice, diff, deliveryCharge, sellerNameCode, companyNameCode, registerNoCode)
    
        # return html string
        self.request.write(html)
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

        if(url[0].find("www.11st.co.kr") >= 0):
            spider = ElevenStSpider()
        elif(url[0].find("item.gmarket.co.kr") >= 0):
            spider = GmartketSpider()
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

# static pages
root.putChild("",                   static.File("./index.html"))
root.putChild("jsFlashEncode.js",   static.File("./jsFlashEncode.js"))

# dynamic pages
root.putChild("parser", Parser())

factory = server.Site(root)
reactor.listenTCP(8080, factory)
reactor.run()
