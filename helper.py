# html templates
HtmlHeader = """
<!DOCTYPE html>

<html>
    <head>
        <script language="javascript" type="text/javascript" src="jsFlashEncode.js"></script>
        <script language="javascript" type="text/javascript" src="common.js"></script>
    </head>

    <body>
"""

HtmlTail = """
    </body>
</html>
"""

elevenStHtmlBody = """
        no: {0} <br />
        name: {1} <br />
        price: {2} <br />
        disPrice: {3} <br />
        diff: {4} <br />
        deliveryCharge: {5} <br />
        sellerId: {6} <br />
        companyName: {7} <br />
        registerNo: {8} <br />
        link: {9} <br />
        <br />
"""

gmarketHtmlBody = """
        no: {0} <br />
        name: {1} <br />
        price: {2} <br />
        disPrice: {3} <br />
        diff: {4} <br />
        deliveryCharge: {5} <br />
        sellerName: {6} <br />
        companyName: {7} <br />
        registerNo: {8} <br />
        link: {9} <br />
        <br />
"""

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

class ShoppingmallSpider(BaseSpider):
    name = "Shoppingmall spider"

    def start_requests(self):
        order = 0
        for url in self.start_urls:
            yield Request(url, self.parse, meta={'order':order})
            order = order+1

    def mySelect(self, hxs, string):
        s = hxs.select(string)
        if len(s) == 0:
            return ""
        else:
            return s.extract()[0].encode("utf-8")

    def elevenStParse(self, response):
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
        return gmarketHtmlBody.format(str(response.meta['order']+1), name, price, disPrice, diff, deliveryCharge, sellerId, companyName, registerNo, self.getLink(response))

    def gmarketParse(self, response):
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
        return gmarketHtmlBody.format(str(response.meta['order']+1), name, price, disPrice, diff, deliveryCharge, sellerNameCode, companyNameCode, registerNoCode, self.getLink(response))

    def brandonParse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # get data
        name = self.mySelect(hxs, '//*[@id="brand-container"]/div[1]/div[1]/div[2]/div/h2/text()')
        price = self.mySelect(hxs, '//*[@id="order_price"]/@value')
        disPrice = self.mySelect(hxs, '//span[@id="dc_price"]/script')
        diff = "Can't calculated"

        deliveryCharge = self.mySelect(hxs, '//*[@id="delivery_fee_tr"]/td/div/strong/text()')

        # following filed are encoded. use orignal javascript code to decode field
        sellerNameCode = self.mySelect(hxs, '//*[@id="brand-container"]/div[3]/div[7]/table/tbody/tr[1]/td[1]/script')
        companyNameCode = self.mySelect(hxs, '//*[@id="brand-container"]/div[3]/div[7]/table/tbody/tr[1]/td[2]/script')
        registerNoCode = self.mySelect(hxs, '//*[@id="brand-container"]/div[3]/div[7]/table/tbody/tr[3]/td[1]/script')

        # render template
        return gmarketHtmlBody.format(str(response.meta['order']+1), name, price, disPrice, diff, deliveryCharge, sellerNameCode, companyNameCode, registerNoCode, self.getLink(response))

    def auctionParse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # get data
        name = self.mySelect(hxs, '////h2[@id="hdivItemTitle"]/text()[1]')
        price = self.mySelect(hxs, '//input[@id="hddnSellingPrice"]/@value')
        if(len(price) == 0):
            price = "0"
        disPrice = self.mySelect(hxs, '//input[@id="hddnDiscountSellingPrice"]/@value')
        if(len(disPrice) == 0 or int(disPrice) == 0):
            disPrice = price
        diff = str(int(price) - int(disPrice))

        deliveryCharge = self.mySelect(hxs, '//*[@id="st1"]/span/text()')

        # following filed are encoded. use orignal javascript code to decode field
        sellerNameCode = self.mySelect(hxs, '//*[@id="htblCorpMemberInfo"]/tr[1]/td[1]/script')
        companyNameCode = self.mySelect(hxs, '//*[@id="htblCorpMemberInfo"]/tr[2]/td[1]/script')
        registerNoCode = self.mySelect(hxs, '//*[@id="htblCorpMemberInfo"]/tr[2]/td[2]/script')

        # render template
        return gmarketHtmlBody.format(str(response.meta['order']+1), name, price, disPrice, diff, deliveryCharge, sellerNameCode, companyNameCode, registerNoCode, self.getLink(response))

    def parse(self, response):
        url = response._url

        if(url.find("www.11st.co.kr") >= 0):
            self.bodies[response.meta['order']] = self.elevenStParse(response)
        elif(url.find("item.gmarket.co.kr") >= 0):
            self.bodies[response.meta['order']] = self.gmarketParse(response)
        elif(url.find("brandon.gmarket.co.kr") >= 0):
            self.bodies[response.meta['order']] = self.brandonParse(response)
        elif(url.find("http://itempage3.auction.co.kr") >= 0):
            self.bodies[response.meta['order']] = self.auctionParse(response)
        else:
            return "Invalid URL. Please check again<br />" + url

    def getLink(self, response):
        return "<a href={0}>click</a>".format(response._url)

class GmarketBestSpider(ShoppingmallSpider):
    """ Spider for gmarket best """

    name = "Gmarket best spider"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        items = hxs.select('//*[@id="gBestWrap"]/div[3]/div/ul/li')

        for i in range(0, 100):
            if(i%10 == 0):
                self.request.write("<br />")

            item = items[i]
            url = self.mySelect(item, 'a/@href')
            self.request.write(url + "<br />")
        
        # return html string
        self.request.finish()

class AuctionBestSpider(ShoppingmallSpider):
    """ Spider for auction best """

    name = "Auction best spider"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        items = hxs.select('//*[@id="contents"]/div[2]/div[2]/ul')

        item = items[0]
        subItems = item.select('li')
        for subItem in subItems:
            url = self.mySelect(subItem, 'div/div[3]/em/a/@href')
            self.request.write(url + "<br />")
        
        for i in range(1, 20):
            if(i%2 == 0):
                self.request.write("<br />")

            item = items[i]
            subItems = item.select('li')

            for subItem in subItems:
                url = self.mySelect(subItem, 'div/div[2]/em/a/@href')
                self.request.write(url + "<br />")
        
        # return html string
        self.request.finish()



from twisted.web import server, resource, static
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy import signals

class Parser(resource.Resource):
    """ Transfer url to proper spider """

    isLeaf = True
    numberRequests = 0
    
    def render_POST(self, request):
        url = request.args['url']

        spider = ShoppingmallSpider()
        spider.request = request
        spider.start_urls = url[0].splitlines()
        spider.html = HtmlHeader
        spider.bodies = [""] * len(spider.start_urls)

        crawler = Crawler(Settings())
        crawler.configure()
        crawler.crawl(spider)

        crawler.signals.connect(self.spider_closed, signals.spider_closed)

        crawler.start()

        return server.NOT_DONE_YET
    
    def spider_closed(self, spider):
        spider.html = spider.html + " ".join(spider.bodies)
        spider.html = spider.html + HtmlTail
        spider.request.write(spider.html)
        spider.request.finish()

class BestParserGmarket(resource.Resource):
    """ Transfer url to proper spider """

    isLeaf = True
    numberRequests = 0
    
    def render_GET(self, request):
        spider = GmarketBestSpider()
        spider.request = request
        spider.start_urls = ["http://promotion.gmarket.co.kr/bestseller/BestSellerList.asp?group_kind=G&group_cd=G04&groupSub_kind=GS&groupsub_cd=S076"]
        crawler = Crawler(Settings())
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()

        return server.NOT_DONE_YET

class BestParserAuction(resource.Resource):
    """ Transfer url to proper spider """

    isLeaf = True
    numberRequests = 0
    
    def render_GET(self, request):
        spider = AuctionBestSpider()
        spider.request = request
        spider.start_urls = ["http://corners.auction.co.kr/corner/CategoryBest.aspx?category=20000000"]
        crawler = Crawler(Settings())
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()

        return server.NOT_DONE_YET


root = resource.Resource()

# static pages
root.putChild("",                   static.File("./index.html"))
root.putChild("jsFlashEncode.js",   static.File("./jsFlashEncode.js"))
root.putChild("common.js",          static.File("./common.js"))

# dynamic pages
root.putChild("parser", Parser())
root.putChild("bestparserg", BestParserGmarket())
root.putChild("bestparsera", BestParserAuction())

factory = server.Site(root)
reactor.listenTCP(8080, factory)
reactor.run()
