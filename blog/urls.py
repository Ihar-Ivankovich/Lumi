from django.conf.urls import url
from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, \
    PostUpdateView, PostDeleteView, UserPostListView, addcomment, ReactionView

from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('reaction', ReactionView.as_view(), name='reaction'),
    url(r'^post/addcomment/(?P<article_id>[0-9]+)',  views.addcomment, name='addcomment')
]