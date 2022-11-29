from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
import operator
from django.urls import reverse_lazy
from django.contrib.staticfiles.views import serve
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db.models import Q
import structlog
logger = structlog.get_logger('base')


def home(request):
    logger.info("Browsing posts", action="browsing_posts", user=request.user.pk)
    return render(request, 'blog/base.html')

@login_required
def search(request):
    template='blog/home.html'

    query=request.GET.get('q')

    result=Post.objects.filter(Q(title__icontains=query) | Q(author__username__icontains=query) | Q(content__icontains=query))
    paginate_by=2
    context={ 'posts':result }
    logger.info("Searching", action="searching", user=request.user.pk, query=query)
    return render(request,template,context)

@login_required
def getfile(request):
   return serve(request, 'File')


class PostListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 2

    def dispatch(self, request, *args, **kwargs):
        logger.info('Listing posts', action='post_list', user=request.user.pk)
        return super(PostListView, self).dispatch(request, *args, **kwargs)

class UserPostListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def dispatch(self, request, *args, **kwargs):
        logger.info('Listing posts of user', action='post_user_list', user=request.user.pk)
        return super(UserPostListView, self).dispatch(request, *args, **kwargs)

class PostDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    template_name = 'blog/post_detail.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        logger.info('Post details', action='post_details', user=request.user.pk)
        return super(PostDetailView, self).dispatch(request, *args, **kwargs)

class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        logger.info('Creating post', action='post_create', user=request.user.pk)
        response = super(PostCreateView, self).dispatch(request, *args, **kwargs)
        logger.info('Post created', action='post_create', user=request.user.pk)
        return response


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user == post.author or request.user.is_superuser:
            logger.info('Updating post', action='post_update', user=request.user.pk)
            response = super(PostUpdateView, self).dispatch(request, *args, **kwargs)
            logger.info('Post updated', action='post_update', user=request.user.pk)
            return response

        logger.warning('Updating post permission denied', action='post_delete', user=request.user.pk)
        raise PermissionDenied


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user == post.author or request.user.is_superuser:
            logger.info('Deleting post', action='post_delete', user=request.user.pk)
            response = super(PostDeleteView, self).delete(request, *args, **kwargs)
            logger.info('Post deleted', action='post_delete', user=request.user.pk)
            return response

        logger.warning('Deleting post permission denied', action='post_delete', user=request.user.pk)
        raise PermissionDenied

@login_required
def about(request):
    logger.info("Reading about", action="about", user=request.user.pk)
    return render(request, 'blog/about.html', {'title': 'About'})
