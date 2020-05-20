from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page,
                  'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.group_posts.order_by('-pub_date').all()
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page,
                  'paginator': paginator, 'group': group})


@login_required
def new_post(request):
    if request.method == 'POST':
        form_for_new_posts = PostForm(request.POST)
        if form_for_new_posts.is_valid():
            form = form_for_new_posts.save(commit=False)
            form.author_id = request.user.pk
            form.save()
            return redirect('index')

    form = PostForm()
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    username = get_object_or_404(User, username=username)
    count = Post.objects.filter(author=username).count()

    post_list = Post.objects.order_by('-pub_date').filter(author=username)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'posts/profile.html', {'username': username,
                  'count': count, 'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    username = get_object_or_404(User, username=username)
    count = Post.objects.filter(author=username).count()
    post = get_object_or_404(Post, id=post_id)

    return render(request, 'posts/post.html', {'username': username,
                  'count': count, 'post': post})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form_modified_posts = PostForm(request.POST)
        if form_modified_posts.is_valid():
            post.text = form_modified_posts.cleaned_data['text']
            post.group_posts = form_modified_posts.cleaned_data['group']
            post.save()
            return redirect('post', username=username, post_id=post_id)

    if request.user == post.author:
        form = PostForm(instance=post)
        return render(request, 'posts/new.html',
                      {'form': form,
                       'post': post})
    else:
        return redirect('post', username=username, post_id=post_id)
