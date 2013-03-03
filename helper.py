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

class ShoppingmallSpider(BaseSpider):
    def mySelect(self, hxs, string):
        s = hxs.select(string)
        if len(s) == 0:
            return ""
        else:
            return s.extract()[0].encode("utf-8")


class ElevenStSpider(ShoppingmallSpider):
    """ Spider for www.11st.co.kr """

    name = "11st spider"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # get data
        name = self.mySelect(hxs, '//p[@class="pro_tit_v2"]/text()')
        price = self.mySelect(hxs, '//*[@id="addAllSelPrc"]/@value')
        disPrice = self.mySelect(hxs, '//*[@name="discountPrc"]/@value')
        diff = str(int(price) - int(disPrice))

        # each product has different type of delivery charge
        deliveryCharge = hxs.select('//*[@id="dlvCstInfo3"]').extract()[0]
        if(deliveryCharge.find("<span") == 0): # always same value
            deliveryCharge = self.mySelect(hxs, '//*[@id="dlvCstInfo3"]/text()')
        else: # changed by dropdown box
            deliveryCharge = self.mySelect(hxs, '//*[@id="dlvCstInfo3"]/span/text()')

        sellerId = self.mySelect(hxs, '//*[@id="prodetail_ns4"]/div[1]/div[2]/p[1]/a/text()')
        companyName = self.mySelect(hxs, '//*[@id="dvPrdInfoWrap"]/table[4]/tr[1]/td[2]/text()')
        registerNo = self.mySelect(hxs, '//*[@id="dvPrdInfoWrap"]/table[4]/tr[2]/td[1]/span/text()')
        
        # render template
        html = gmarketHtml.format(name, price, disPrice, diff, deliveryCharge, sellerId, companyName, registerNo)
    
        # return html string
        self.request.write(html)
        self.request.finish()

class GmartketSpider(ShoppingmallSpider):
    """ Spider for item.gmarket.co.kr """

    name = "Gmarket spider"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # get data
        name = self.mySelect(hxs, '//*[@class="tit-goodsnum"]/p/text()')
        price = self.mySelect(hxs, '//*[@id="order_price"]/@value')

        # disPrice in Gmarket contains ','
        disPrice = self.mySelect(hxs, '//span[@id="dc_price"]/text()').replace(",", "").replace(",", "")

        diff = str(int(price) - int(disPrice))

        deliveryCharge = self.mySelect(hxs, '//*[@id="delivery_fee_tr"]/td/div/strong/text()')

        # following filed are encoded. use orignal javascript code to decode field
        sellerNameCode = self.mySelect(hxs, '//*[@class="goods-info"][2]/tbody/tr[1]/td[1]/script')
        companyNameCode = self.mySelect(hxs, '//*[@class="goods-info"][2]/tbody/tr[1]/td[2]/script')
        registerNoCode = self.mySelect(hxs, '//*[@class="goods-info"][2]/tbody/tr[4]/td[1]/script')

        # render template
        html = gmarketHtml.format(name, price, disPrice, diff, deliveryCharge, sellerNameCode, companyNameCode, registerNoCode)
    
        # return html string
        self.request.write(html)
        self.request.finish()

class BrandonSpider(ShoppingmallSpider):
    """ Spider for brandon.gmarket.co.kr """

    name = "Gmarket(BrandOn) spider"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # get data
        name = self.mySelect(hxs, '//*[@id="brand-container"]/div[1]/div[1]/div[2]/div/h2/text()')
        price = self.mySelect(hxs, '//*[@id="order_price"]/@value')

        # disPrice in Gmarket contains ','
        disPrice = self.mySelect(hxs, '//span[@id="dc_price"]/script')

        diff = "Can't calculated"

        deliveryCharge = self.mySelect(hxs, '//*[@id="delivery_fee_tr"]/td/div/strong/text()')

        # following filed are encoded. use orignal javascript code to decode field
        sellerNameCode = self.mySelect(hxs, '//*[@id="brand-container"]/div[3]/div[7]/table/tbody/tr[1]/td[1]/script')
        companyNameCode = self.mySelect(hxs, '//*[@id="brand-container"]/div[3]/div[7]/table/tbody/tr[1]/td[2]/script')
        registerNoCode = self.mySelect(hxs, '//*[@id="brand-container"]/div[3]/div[7]/table/tbody/tr[3]/td[1]/script')

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
        elif(url[0].find("brandon.gmarket.co.kr") >= 0):
            spider = BrandonSpider()
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
