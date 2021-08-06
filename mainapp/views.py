from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic import ListView
from django.db.models import Q
from django.utils.safestring import mark_safe
import calendar

from .models import *
from .utils import Calendar

def index(request):
    posts = Post.objects.all()
    today = datetime.today()
    forsaleposts = Post.objects.filter(type='forsale').filter(archive=False)
    housingposts = Post.objects.filter(type='housing').filter(archive=False)
    eventposts = Post.objects.filter(type='events').filter(archive=False)
    jobsposts = Post.objects.filter(type='jobs').filter(archive=False)
    community = 'seattle'
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        community = user.community
    context = {
        "posts": posts,
        "today": today,
        "forsaleposts": forsaleposts,
        "housingposts": housingposts,
        "eventposts": eventposts,
        "jobsposts": jobsposts,
        "community": community,
    }
    return render(request, 'mainapp/index.html', context)

def myaccount(request):
    if 'user_id' not in request.session:
        return render(request, "mainapp/login_registration.html")
    user = User.objects.get(id=request.session['user_id'])
    postscurrent = Post.objects.filter(publisher=user).filter(archive=False).order_by('-updated_at')
    postsarchived = Post.objects.filter(publisher=user).filter(archive=True).order_by('-updated_at')
    context = {
        "user": user,
        "currentposts": postscurrent,
        "archivedposts": postsarchived,
        "community": user.community,
    }
    return render(request, "mainapp/welcome.html", context)


# registering a user
def register(request):
    if request.method == 'GET':
        return redirect('/')
    errors = User.objects.validate(request.POST)
    if errors:
        for e in errors.values():
            messages.error(request, e)
        return redirect('/myaccount')
    else:
        new_user = User.objects.register(request.POST)
        request.session['user_id'] = new_user.id
        messages.success(request, "You have successfully registered!")
        return redirect('/myaccount')

def login(request):
    if request.method == "GET":
        return redirect('/')
    if not User.objects.authenticate(request.POST['email'], request.POST['password']):
        messages.error(request, 'Invalid Email/Password')
        return redirect('/myaccount')
    user = User.objects.get(email=request.POST['email'])
    request.session['user_id'] = user.id
    return redirect('/myaccount')

def logout(request):
    request.session.flush()
    messages.success(request, 'you have successfully logout')
    return redirect('/')

def post_new(request):
    if 'user_id' not in request.session:
        return render(request, "mainapp/login_registration.html")
    user = User.objects.get(id=request.session['user_id'])
    context = {
        "community": user.community
    }
    return render(request, "mainapp/create_post.html", context)

def create_post(request):
    if 'user_id' not in request.session:
        return redirect('/')
    if request.method != "POST":
        return redirect('/myaccount')
    user = User.objects.get(id=request.session["user_id"])
    Post.objects.create(title=request.POST['title'], description=request.POST['description'], type=request.POST['type'], zipcode=request.POST['zipcode'], community=request.POST['community'], date=request.POST['date'], publisher=user)
    return redirect('/myaccount')

def post_detail(request, id):
    post = Post.objects.get(id=id)
    user = 0
    community_var = 0
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        community_var = user.community
    context = {
        "user": user,
        "post": post,
        "community": community_var
    }
    return render(request, "mainapp/detail_post.html", context)

def post_edit(request, id):
    if 'user_id' not in request.session:
        return redirect('/')
    post = Post.objects.get(id=id)
    user = User.objects.get(id=request.session['user_id'])
    context = {
        "post": post,
        "user": user,
    }
    return render(request, "mainapp/edit_post.html", context)

def update_post(request, id):
    if 'user_id' not in request.session:
        return redirect('/')
    if request.method != "POST":
        return redirect('/myaccount')
    post = Post.objects.get(id=id)
    post.type = request.POST['type']
    post.community = request.POST['community']
    post.title = request.POST['title']
    post.description = request.POST['description']
    post.date = request.POST['date']
    archive = request.POST.get('archive', False)
    if archive == "on":
        post.archive = True
    else: 
        post.archive = False
    post.save()
    return redirect('/myaccount')


def destroy_post(request,id):
    if 'user_id' not in request.session:
        return redirect('/')
    if request.method != "POST":
        return redirect('/myaccount')
    destroyed_item = Post.objects.filter(id = id)
    destroyed_item.delete()
    return redirect('/myaccount')


def update(request):
    if 'user_id' not in request.session:
        return redirect('/myaccount')
    if request.method != "POST":
        return redirect('/myaccount')
    user = User.objects.get(id=request.session['user_id'])
    user.community = request.POST['community']
    user.save()
    return redirect('/')

class CalendarView(generic.ListView):
    model = Post
    template_name = 'mainapp/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

class SearchResultsView(ListView):
    model = Post
    template_name = 'mainapp/search_results.html'
    # queryset = Post.objects.filter(title__icontains='rifle')

    def get_queryset(self):             # overriding the default queryset method
        query = self.request.GET.get('q')
        if query == '':
            object_list = Post.objects.exclude(title__icontains=query)
        else:
            object_list = Post.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return object_list




# Create your views here.
