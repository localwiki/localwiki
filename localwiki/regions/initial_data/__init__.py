"""
We don't use a fixture here because:

    1. Each set of pages needs to point to a different region.  Not sure how
       to do this using fixtures.
    2. Translations are easier.
"""

from django.utils.translation import ugettext as _

from pages.models import Page, slugify

def populate_region(region):
    Page(
        name="Templates",
        slug="templates",
        # Translators: Please fix the links here to point to "Place," "Business", "Disambiguation", "Restaurant" as translated in your language.  But leave the "Templates/" part of the page link.  "Templates/" in a URL is currently hard-coded and must remain in English for now.
        content=_("""<p>
    	Templates are special pages that serve as a starting point when creating a new page. &nbsp;Using a common template for related topics gives those pages a common structure. &nbsp;To use one of the templates, simply select the template when creating a new page. &nbsp;</p>
    <p>
    	Below is a list of the available templates. To add a new template, create a page whose title starts with &quot;Templates/&quot;, as in <a href="Templates%2FBusiness">Templates/Business</a>. &nbsp;When you create a new template, add it to this list so it&#39;s easier to find.</p>
    <h3>
    	<span>List of templates</span></h3>
    <ul>
    	<li>
    		<a href="Templates%2FPlace">Templates/Place</a></li>
    	<li>
    		<a href="Templates%2FBusiness">Templates/Business</a></li>
    	<li>
    		<a href="Templates%2FDisambiguation">Templates/Disambiguation</a></li>
    	<li>
    		<a href="Templates%2FRestaurant">Templates/Restaurant</a></li>
    </ul>"""),
        region=region
    ).save()
  
    # Translators: This is for "Templates/Page" - a template page
    template_type = _("Place")
    Page(
        name="Templates/%s" % template_type,
        slug="templates/%s" % slugify(template_type),
        content=_("""<table>
    	<tbody>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Location</strong></td>
    		</tr>
    		<tr>
    			<td>
    				address</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Contact</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(555) 555 5555</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Website</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Add link here</td>
    		</tr>
    	</tbody>
    </table>
    <p>
    	The <strong>Thing I&#39;m Talking About</strong> should have a blurb here with links to relevant things, like the <a href="Front%20Page">Front Page</a>.</p>
    <h2>
    	Section Title</h2>
    <p>
    	Text goes here.</p>"""),
        region=region
    ).save()
   
    # Translators: This is for "Templates/Restaurant" - a template page
    template_type = _("Restaurant")
    Page(
        name="Templates/%s" % template_type,
        slug="templates/%s" % slugify(template_type),
        content=_("""<table>
    	<tbody>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Location</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Please fill in address</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Hours</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(Please fill in hours)</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Phone</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(415) 555-5555</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Website</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Add link here</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Established</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(Date, i.e. YYYY-MM-DD)</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Price range</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(Prices for &quot;average&quot; entrees)</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Payment Methods</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(Cash, check, credit cards, other?)</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Wheelchair accessibility</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(notes on stairs, bathroom access, handrails, aisle width)</td>
    		</tr>
    	</tbody>
    </table>
    <p>
    	Then, put&nbsp;<em>whatever</em>&nbsp;you want down here! Note that&nbsp;<a href="http://local.google.com">http://local.google.com</a>&nbsp;is sometimes a good and easy place to find times/phone. Better yet, look them up in the phone book, and ask them.</p>
    <p>
    	Remember to add this restaurant to the neighborhood&nbsp;<a href="restaurants">restaurants</a>&nbsp;page.</p>
    <h3>
    	Related Links</h3>
    <ul>
    	<li>
    		<a href="Restaurants">Restaurants</a></li>
    </ul>
    <p>
    	&nbsp;</p>"""),
        region=region
    ).save()
    
    # Translators: This is for "Templates/Business" - a template page
    template_type = _("Business")
    Page(
        name="Templates/%s" % template_type,
        slug="templates/%s" % slugify(template_type),
        content=_("""
    <table>
    	<tbody>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Location</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Please fill in address</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Hours</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Please fill in hours</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Phone</strong></td>
    		</tr>
    		<tr>
    			<td>
    				(415) 555-5555</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Website</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Add link here</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>E-mail</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Email address</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Owner(s)</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Names of owners/proprietors here</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Established</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Date, i.e. YYYY-MM-DD</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Payment Method</strong></td>
    		</tr>
    		<tr>
    			<td>
    				Type of payment</td>
    		</tr>
    		<tr>
    			<td style="background-color: rgb(232, 236, 239);">
    				<strong>Wheelchair accessibility</strong></td>
    		</tr>
    		<tr>
    			<td>
    				stairs, bathrooms, handrails, aisle width?</td>
    		</tr>
    	</tbody>
    </table>
    <p>
    	Then, put&nbsp;<em>whatever</em>&nbsp;you want down here! Note that&nbsp;<a href="http://local.google.com">http://local.google.com</a>&nbsp;is sometimes a good and easy place to find times/phone. Better yet, look them up in the phone book, and ask them. Remove the fields you don&#39;t fill out &mdash; or even better, look up or call them for the missing information!</p>
    <h3>
    	Related Links</h3>
    <ul>
    	<li>
    		<a href="Shopping">Shopping</a></li>
    </ul>
    <p>
    	&nbsp;</p>"""),
        region=region
    ).save()
    
    # Translators: This is for "Templates/Disambiguation" - a template page
    template_type = _("Disambiguation")
    Page(
        name="Templates/%s" % template_type,
        slug="templates/%s" % slugify(template_type),
        content=_("""<p>
    	This has multiple meanings. You are probably looking for information on one of the following:</p>
    <ul>
    	<li>
    		<a href="ItemOne">ItemOne</a>&nbsp;- A brief summary of ItemOne</li>
    	<li>
    		<a href="ItemTwo">ItemTwo</a>&nbsp;- A brief summary of ItemTwo</li>
    </ul>
    <p>
    	&nbsp;</p>
    <p>
    	This is a&nbsp;<em>disambiguation</em> page&nbsp;&mdash; a navigational aid which lists other pages that might otherwise share the same title. If an page link referred you here, you might want to go back and fix it to point directly to the intended page.</p>"""),
        region=region
    ).save()
    
    Page(
        name="Front Page",
        slug="front page",
        content=(_("""<p>
    	Welcome to the new LocalWiki region for %(region)s! There are currently just a handful of pages in it, to get you started.
    <p>
    	Click on <strong>Explore</strong> at the top to see what's here now.</p>
    <p>
    	You can edit this and any other page by clicking the <strong>Edit</strong> button.</p>
    <p>Need <strong>help</strong>? Please see the <a href="http://localwiki.net/main/Help">help page</a> on the <a href="http://localwiki.net/main/">LocalWiki Guide</a>!</p>""") % {'region': region.full_name}),
        region=region
    ).save()
