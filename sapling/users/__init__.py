from django.contrib import auth
from django.contrib import messages
from django.utils.translation import ugettext as _

def logged_out_msg(sender, request, user, **kwargs):
    messages.add_message(request, messages.SUCCESS,
        _("You are now logged out."))

auth.signals.user_logged_out.connect(logged_out_msg,
    dispatch_uid='user_logged_out_msg')
