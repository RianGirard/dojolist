from django.urls import path
from django.conf.urls import url
from .views import SearchResultsView
from . import views

app_name = 'mainapp'

urlpatterns = [
    path('', views.index),
    path('myaccount', views.myaccount),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('post/new', views.post_new),
    path('post/create_post', views.create_post),
    path('post/destroy/<int:id>',views.destroy_post),
    path('post/<int:id>', views.post_detail),
    path('post/edit/<int:id>', views.post_edit),
    path('post/update_post/<int:id>', views.update_post),
    path('update', views.update),
    url(r'^calendar/$', views.CalendarView.as_view(), name='calendar'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
]