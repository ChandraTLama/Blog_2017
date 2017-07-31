from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, CommentForm
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator




def post_list(request):
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
        tone_analyzer = ToneAnalyzerV3(
            username='ddd11ad5-76b3-4e2f-8618-0dc241ed0f32',
            password='ALfKFtrDGslF',
            version='2016-05-19 ')
        language_translator = LanguageTranslator(
            username='5556fa8f-1a8b-4380-8c92-ebb9e3fa19d6',
            password='G6GqvjRrxgWP')
        # print(json.dumps(translation, indent=2, ensure_ascii=False))
        for post in posts:
            data = json.dumps(tone_analyzer.tone(text=post.text), indent=1)  # converting to string and storing in the data
            j = json.loads(data);
            post.info = j['document_tone']['tone_categories'][0]['tones']
            # post.info = json.dumps(post.info);
            post.angerScore = post.info[0]['score']
            post.disgustScore = post.info[1]['score']
            post.fearScore = post.info[2]['score']
            post.joyScore = post.info[3]['score']
            post.sadScore = post.info[4]['score']
        # print(post.info[0]['tone_name'])
            translation = language_translator.translate(
                text=post.text,
                source='en',
                target='fr')
            post.translatedText = json.dumps(translation, indent=2, ensure_ascii=False)

        return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            ##post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
               ## post.published_date = timezone.now()
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_remove(request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect('post_list')

@login_required
def post_draft_list(request):
        posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
        tone_analyzer = ToneAnalyzerV3(
            username='ddd11ad5-76b3-4e2f-8618-0dc241ed0f32',
            password='ALfKFtrDGslF',
            version='2016-05-19 ')
        language_translator = LanguageTranslator(
            username='5556fa8f-1a8b-4380-8c92-ebb9e3fa19d6',
            password='G6GqvjRrxgWP')
        # print(json.dumps(translation, indent=2, ensure_ascii=False))
        for post in posts:
            data = json.dumps(tone_analyzer.tone(text=post.text),
                              indent=1)  # converting to string and storing in the data
            j = json.loads(data);
            post.info = j['document_tone']['tone_categories'][0]['tones']
            # post.info = json.dumps(post.info);
            post.angerScore = post.info[0]['score']
            post.disgustScore = post.info[1]['score']
            post.fearScore = post.info[2]['score']
            post.joyScore = post.info[3]['score']
            post.sadScore = post.info[4]['score']
            # print(post.info[0]['tone_name'])
            translation = language_translator.translate(
                text=post.text,
                source='en',
                target='fr')
            post.translatedText = json.dumps(translation, indent=2, ensure_ascii=False)
        return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.publish()
        return redirect('post_detail', pk=pk)

def add_comment_to_post(request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = CommentForm()
        return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.approve()
        return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        return redirect('post_detail', pk=comment.post.pk)

# Create your views here.