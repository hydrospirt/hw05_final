from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings

from posts.models import Group, Post, Follow, User
from posts.forms import PostForm, CommentForm


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts_lists = Post.objects.all()
    paginator = Paginator(posts_lists, settings.NUMBER_SHOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_lists = group.posts.all()
    paginator = Paginator(posts_lists, settings.NUMBER_SHOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts_lists = author.posts.select_related('author')
    post_count = posts_lists.count()
    paginator = Paginator(posts_lists, settings.NUMBER_SHOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Профиль пользователя {username}'
    following = (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()
    )
    followers = Follow.objects.filter(author=author).count()
    context = {
        'post_count': post_count,
        'author': author,
        'title': title,
        'page_obj': page_obj,
        'following': following,
        'followers': followers
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    post_count = post.author.posts.count()
    followers = post.author.following.count()
    title = f'Публикация {post}'
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'title': title,
        'post': post,
        'post_count': post_count,
        'form': form,
        'comments': comments,
        'followers': followers
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    title = 'Создание новой публикации'
    if request.method != 'POST':
        form = PostForm()
        context = {'form': form, 'title': title}
        return render(request, template, context)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{post.author}/')
    context = {'form': form, 'title': title}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    title = 'Редактирование публикации'
    post = Post.objects.get(pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method != 'POST':
        form = PostForm(instance=post)
        context = {'form': form, 'title': title, 'is_edit': True}
        return render(request, template, context)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'title': title, 'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    posts = Post.objects.filter(author__id__in=authors)
    paginator = Paginator(posts, settings.NUMBER_SHOW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('posts:profile', username=username)
    following = get_object_or_404(User, username=username)
    already_follow = Follow.objects.filter(
        user=request.user,
        author=following
    ).exists()
    if not already_follow:
        Follow.objects.create(user=request.user, author=following)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(Follow, author=following, user=request.user)
    follower.delete()
    return redirect('posts:profile', username=username)
