from django.template import Context, Template
from django.utils.encoding import smart_str

from pages.models import Page


def run(*args, **kwargs):
    print "Populating page card thumbnails & memcached..."

    for p in Page.objects.all().defer('content'):
        print smart_str(p)
        try:
            t = Template("""{% load thumbnail %}
{% load cards_tags %}

{% page_card page as card %}
  
{% if card.file %}
  {% thumbnail card.file.file "200x200" crop="center" as im %}
    <img src="{{ im.url }}"/>
  {% endthumbnail %}
{% endif %}
""")
            t.render(Context({'page': p}))
        except:
            print "ERROR on", smart_str(p)
