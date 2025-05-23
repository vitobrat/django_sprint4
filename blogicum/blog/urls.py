from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'blog'

urlpatterns = [
    # View posts.
    path('',
         views.PostIndexListView.as_view(), name='index'),
    path('category/<slug:category_slug>/',
         views.PostCategoryListView.as_view(), name='category_posts'),
    path('posts/<int:post_id>/',
         views.PostDetailView.as_view(), name='post_detail'),

    # Edit posts.
    path('posts/create/',
         views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/',
         views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),

    # Profile.
    path('profile/<str:username>/',
         views.ProfileListView.as_view(), name='profile'),
    path('edit_profile/',
         views.ProfileUpdateView.as_view(), name='edit_profile'),

    # Comments.
    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
