from django.views.generic import ListView
from django.contrib.auth.models import User

from pages.models import Page
from follow.models import Follow
from users.views import get_user_page


class FollowedPagesListView(ListView):
    model = Follow
    context_object_name = 'follows'
    template_name = 'stars/page_stars_for_user.html'

    def get_queryset(self):
        username = self.kwargs.get('username')
        self.user = User.objects.get(username__iexact=username)
        qs = super(FollowedPagesListView, self).get_queryset()
        qs = qs.exclude(target_page=None).filter(user=self.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super(FollowedPagesListView, self).get_context_data(**kwargs)
        context['user_for_page'] = self.user
        context['page'] = get_user_page(self.user, self.request)
        return context


class FollowedUsersListView(ListView):
    model = Follow
    context_object_name = 'follows'
    template_name = 'stars/user_stars_for_user.html'

    def get_queryset(self):
        username = self.kwargs.get('username')
        self.user = User.objects.get(username__iexact=username)
        qs = super(FollowedUsersListView, self).get_queryset()
        return qs.exclude(target_user=None).exclude(target_user=self.user).filter(user=self.user)

    def get_context_data(self, **kwargs):
        context = super(FollowedUsersListView, self).get_context_data(**kwargs)
        context['user_for_page'] = self.user
        context['page'] = get_user_page(self.user, self.request)
        return context
