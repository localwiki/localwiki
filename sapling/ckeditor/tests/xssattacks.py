import urllib2
from lxml import etree

def load_url(url):
    req = urllib2.Request(url)
    return urllib2.urlopen(req)

def xss_attacks():
    return #disabled for now, needs manually constructed documents
    attacks_url = 'http://ha.ckers.org/xssAttacks.xml'
    doc = etree.parse(load_url(attacks_url))
    for attack in doc.iter("attack"):
        name = attack.find("name").text
        code = attack.find("code").text
        desc = attack.find("desc").text
        label = attack.find("label").text
        browser = attack.find("browser").text
        print browser
        print desc
        yield make_document(code)
        
def make_document(snippet):
    return '<html><head><title>Lorem</title></head><body>%s</body></html>' % (snippet,)
