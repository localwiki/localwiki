import copy

from django import template
from django.core.cache import get_cache
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models.signals import post_save

from pages.models import Page
from maps.widgets import InfoMap

register = template.Library()

# Remove the PanZoom on normal page views.
olwidget_options = copy.deepcopy(getattr(settings,
    'OLWIDGET_DEFAULT_OPTIONS', {}))
map_opts = olwidget_options.get('map_options', {})
map_controls = map_opts.get('controls', [])
if 'PanZoom' in map_controls:
    map_controls.remove('PanZoom')
if 'PanZoomBar' in map_controls:
    map_controls.remove('PanZoomBar')
if 'KeyboardDefaults' in map_controls:
    map_controls.remove('KeyboardDefaults')
if 'Navigation' in map_controls:
    map_controls.remove('Navigation')

olwidget_options['map_options'] = map_opts
olwidget_options['map_div_class'] = 'mapwidget'


@register.simple_tag(takes_context=True)
def page_card(context, page):
    from maps.widgets import map_options_for_region
    cache = get_cache('long-living')
    request = context['request']
    host = request.META['HTTP_HOST']

    card = cache.get('card:%s,%s' % (page.id, host))
    if card:
        return card

    _file, _map = None, None

    # Try and get a useful image
    _file = page.get_highlight_image() 

    # Otherwise, try and get a map
    if not _file and hasattr(page, 'mapdata'):
        olwidget_options.update(map_options_for_region(page.region))
        _map = InfoMap(
            [(page.mapdata.geom, '')],
            options=olwidget_options
        ).render(None, None, {'id': 'map_page_id_%s' % page.id})

    card = render_to_string('pages/card.html', {
        'page': page,
        'file': _file,
        'map': _map,
    })
    cache.set('card:%s,%s' % (page.id, host), card)
    return card

def _clear_card(sender, instance, *args, **kwargs):
    cache = get_cache('long-living')
    cache.delete('card:%s' % instance.id)

post_save.connect(_clear_card, sender=Page)
