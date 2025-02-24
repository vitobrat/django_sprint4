from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin

from blog.models import Post, Category
from blog.forms import PostForm, CommentForm

POSTS_PER_PAGE = 10


class PostMixin:
    """Set default model for post views."""

    model = Post


class PostEditMixin(PostMixin):
    """Set default template for post-edit views."""

    template_name = 'blog/create.html'


class PostIndexListView(PostMixin, ListView):
    """Show latest POSTS_PER_PAGE posts.

    1. Publication date must be earlier than current;
    2. Post & category must be published.
    """

    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return self.model.objects.filter(
            category__is_published__exact=True, is_published__exact=True,
            pub_date__lte=timezone.now()
        ).order_by(
            '-pub_date'
        ).annotate(comment_count=Count("comment"))


class PostCategoryListView(PostMixin, ListView):
    """Show latest POSTS_PER_PAGE posts in category.

    1. Publication date must be earlier than current;
    2. Post & category must be published.
    3. Posts must belong to selected category.
    """

    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE
    _category = None

    def get_category(self) -> Category:
        """Fetch and cache the category object."""
        if not self._category:
            self._category = get_object_or_404(
                Category,
                slug=self.kwargs['category_slug'],
                is_published=True
            )
        return self._category

    def get_queryset(self, **kwargs):
        """Return posts for <category_slug> category."""
        category = self.get_category()
        return self.model.objects.filter(
            category__exact=category,
            is_published__exact=True, pub_date__lte=timezone.now()
        ).order_by('-pub_date').annotate(comment_count=Count("comment"))

    def get_context_data(self, **kwargs):
        """Add category to the context."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class PostDetailView(PostMixin, DetailView):
    """Show a single post by ID.

    1. Publication date must be earlier than current;
    2. Post & category must be published.
    """

    template_name = 'blog/detail.html'

    def get_object(self, **kwargs):
        """Return Post or Http404 by post ID."""
        post = get_object_or_404(
            self.model.objects.filter(pk=self.kwargs['post_id'])
        )

        # Allow access: user is the author.
        if post.author == self.request.user:
            return post

        # Deny access: user is not the author, post isn't published.
        is_denied = (not post.is_published
                     or post.pub_date > timezone.now()
                     or not post.category.is_published)
        if is_denied:
            raise Http404

        # Allow access: user is not the author, post is published.
        return post

    def get_context_data(self, **kwargs):
        """Add form and comments to the context."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class PostCreateView(PostEditMixin, LoginRequiredMixin, CreateView):
    """Create a new post."""

    form_class = PostForm

    def form_valid(self, form):
        """Save model instance."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to user's page (blog:profile)."""
        return reverse("blog:profile", args=[self.request.user])


class PostUpdateView(PostEditMixin, LoginRequiredMixin, UpdateView):
    """Edit an existing post."""

    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Check if the current user is the author of the post."""
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Redirect to post detail page (blog:post_detail)."""
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostEditMixin, LoginRequiredMixin, DeleteView):
    """Delete an existing post."""

    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """Check if the current user is the author of the post."""
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add form to the context."""
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        """Return user's page (blog:profile)."""
        return reverse('blog:profile', args=[self.request.user])
