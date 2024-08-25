
from django.contrib import admin
from django.urls import path,include
from . import views,user_login,intern_views
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base',views.BASE,name='base'),
    path('',views.HOME,name='home'),
    path('404',views.PAGE_NOT_FOUND,name='404'),
    path('courses',views.SINGLE_COURSE,name='single_course'),
    path('course/filter-data',views.filter_data,name="filter-data"),
    path('contact',views.CONTACT,name='contact_us'),
    path('about',views.ABOUT,name='about_us'),
    path('doLogin',user_login.DO_LOGIN,name='doLogin'),
    path('accounts/register',user_login.REGISTER,name='register'),
    path('search',views.SEARCH_COURSE,name='search_course'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile',user_login.PROFILE,name='profile'),
    path('accounts/profile/update',user_login.PROFILE_UPDATE,name='profile_update'),
    path('course/<slug:slug>',views.COURSE_DETAILS,name="course_details"),
    path('my-course',views.MY_COURSE,name='mycourse'),
    path('checkout/<slug:slug>',views.CHECKOUT,name='checkout'),
    path('course/watch-course/<slug:slug>',views.WATCH_COURSE,name='watch_course'),
    path('internship/register',intern_views.REGISTER,name='intern_register'),
    path('verify_payment',views.VERIFY_PAYMENT,name='verify_payment'),
    path('page/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('pages',views.PAGES_ALL,name='blog_list'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

urlpatterns+= static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)


