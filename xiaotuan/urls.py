"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path

from django.views.static import serve
from tuanzi import views
from xiaotuan import  settings
from django.urls import include
from django.conf.urls import url
from dailyreport import viewss

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('createp2t/', views.createp2t, name='createp2t'),
    path('logout/', views.logout),
    path('myidol/', views.myidol, name='myidol'),
    path('followta/<int:clubid>', views.followta, name='followta'),
    path('index/<int:x>/<int:pindex>', views.index, name='index'),
    # path('logout/', views.logout),
    
    path('get_validCode_img/', views.get_valid_code_img),
    path('register/', views.register),

    url(r'^myreport/$', viewss.MyReportView.as_view(), name='myreport'),
    # url(r'^watchreport/$', viewss.MyReportView.as_view(), name='watchreport'),
    url(r'^myreport/create$', viewss.ReportCreateView.as_view(), name='myreport-create'),
    url(r'^myreport/detail$', viewss.ReportDetailView.as_view(), name='myreport-detail'),
    # url(r'^watchreport/detail$', viewss.ReportDetailView.as_view(), name='watchreport-detail'),
    #re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.clubinfo), 
    # home_site(reqeust,username="yuan",condition="tag",param="python")
    # 个人站点url
    # re_path('^(?P<username>\w+)/$', views.clubinfo),

    # path('clubinfo/<index:clubid>',views.clubinfo),
    path('clubinfo/<str:username>/',views.clubinfo),

    re_path(r"media(?P<path>.*)$",serve,{"document_root":settings.MEDIA_ROOT}),

    re_path('^(?P<username>\w+)/posts/(?P<post_id>\d+)$', views.post_detail),
    
    path('createpost/', views.createpost, name='createpost'),

    path("digg/",views.digg),
    path("comment/",views.comment),
    path("get_comment_tree/",views.get_comment_tree),

    path("cgpwd/", views.cgpwd, name='cgpwd'),
    path("modifya/", views.modifya, name='modifya'),
    path("createapplication/", views.createapplication, name='createapplication'),
    path("searchtag/", views.searchtag, name='searchtag'),
    
    path("hotrank/<int:pindex>",views.hotrank,name='hotrank'),

    path("upload/",views.upload),

    re_path('^$', views.login)

]
