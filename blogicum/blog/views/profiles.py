from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from blog.models import Post
from blog.views.posts import POSTS_PER_PAGE
from blog.forms import ProfileEditForm

User = get_user_model()


class ProfileListView(ListView):
    """Show user's page with posts."""

    model = Post
    paginate_by = POSTS_PER_PAGE  # Defined in 'blog/views/posts.py'
    template_name = 'blog/profile.html'

    def get_queryset(self):
        """Return posts for <username> author."""
        filters = {'author__username': self.kwargs['username']}
        if self.request.user.username != self.kwargs['username']:
            # Hide unpublished posts for other users.
            filters.update({
                'is_published__exact': True,
                'pub_date__lte': timezone.now()
            })
        return (self.model.objects.select_related('author')
                .filter(**filters).order_by('-pub_date')
                .annotate(comment_count=Count("comment")))

    def get_context_data(self, **kwargs):
        """Add profile to the context."""
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Show user data editing form."""

    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        """Return User object."""
        return self.request.user

    def get_success_url(self):
        """Redirect to user's page (blog:profile)."""
        return reverse('blog:profile', args=[self.request.user])
