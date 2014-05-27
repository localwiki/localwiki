from django.template import Context, Template

from pages.models import Page


def run(*args, **kwargs):
    print "Populating page card thumbnails & memcached..."

    for p in Page.objects.all():
        print p
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
