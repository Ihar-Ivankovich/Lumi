from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Case, IntegerField
from django.db.models import Count
from django.db.models import When
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from blog.forms import CommentForm, ReactionForm
from django_project.settings import PAGE_NUMBER
from .models import Post, Comment, RecipeReaction


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGE_NUMBER
    queryset = Post.objects.all().order_by('-created_at')
    url_name = 'blog-home'

    def get_queryset(self):
        annotate_kwargs = {
            'likes_count': Count(
                Case(
                    When(
                        reactions__status='like',
                        then=1,
                    ),
                    output_field=IntegerField()
                )
            ),
            'dislikes_count': Count(
                Case(
                    When(
                        reactions__status='dislike',
                        then=1,
                    ),
                    output_field=IntegerField()
                )
            )
        }
        if self.request.user.is_authenticated:
            annotate_kwargs['liked'] = Count(
                Case(
                    When(
                        reactions__status='like',
                        reactions__user=self.request.user,
                        then=1,
                    ),
                    output_field=IntegerField()
                )
            )
            annotate_kwargs['disliked'] = Count(
                Case(
                    When(
                        reactions__status='dislike',
                        reactions__user=self.request.user,
                        then=1,
                    ),
                    output_field=IntegerField()
                )
            )

        queryset = super().get_queryset().annotate(**annotate_kwargs)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(
            object_list=object_list, **kwargs
        )
        if self.request.GET.get('exception'):
            raise Exception("Smth bad")
        context['feed_url'] = reverse(self.url_name)
        context['Top'] = Post.objects.filter()
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = PAGE_NUMBER

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(
            object_list=object_list, **kwargs
        )
        if self.request.GET.get('exception'):
            raise Exception("Smth bad")
        context['Top'] = Post.objects.filter()
        return context

class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(
            object_list=object_list, **kwargs
        )
        if self.request.GET.get('exception'):
            raise Exception("Smth bad")
        context['comment_text'] = Comment.objects.filter(recipe_id=self.get_object().id)
        context['form'] = CommentForm()
        context['Top'] = Post.objects.filter()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def addcomment(request, article_id):
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.recipe_id = article_id
            # comment.text = Post.objects.get(id=article_id)
            form.save()
    return HttpResponseRedirect('/post/%s/' % article_id)

class ReactionView(LoginRequiredMixin, CreateView):
    template_name = ''
    form_class = ReactionForm
    http_method_names = ['post']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER') or reverse('blog-home')

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})