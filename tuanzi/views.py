from datetime import datetime
from email.mime import application
import imp
import random
from urllib import response
from bs4 import BeautifulSoup
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from django.urls import reverse
from tuanzi.Myforms import AvatarForm, UserForm, ChangePasswordForm
from tuanzi.models import Applications, Post, Post2Tag, Tag, UserInfo, following
from tuanzi.utils import validCode
from tuanzi import models
import json
from django.http import JsonResponse
from django.db.models import F, Count
from django.db.models.functions import TruncMonth
from django.db import transaction
from django.contrib.auth.decorators import login_required
import os
from xiaotuan import settings
from django.core.paginator import Paginator
import random
from datetime import datetime
from django.db.models import Q


def login(request):
    """
    登录视图函数:
       get请求响应页面
       post(Ajax)请求响应字典
    :param request:
    :return:
    """

    if request.method == "POST":

        response = {"user": None, "msg": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")

        valid_code_str = request.session.get("valid_code_str")
        if valid_code.upper() == valid_code_str.upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)  # request.user== 当前登录对象
                response["user"] = user.username
            else:
                response["msg"] = "用户名或者密码错误!"

        else:
            response["msg"] = "验证码错误!"

        return JsonResponse(response)

    return render(request, "login.html")


def get_valid_code_img(request):
    """
    基于PIL模块动态生成响应状态码图片
    :param request:
    :return:
    """
    img_data = validCode.get_valid_code_img(request)

    return HttpResponse(img_data)


def logout(request):
    """
    注销视图
    :param request:
    :return:
    """
    auth.logout(request)  # request.session.flush()

    return redirect("/login/")


def index(request, x, pindex=1):
    """
    系统首页
    :param request:
    :return:
    """
    mywhere = ""
    # searchtag = request.GET.get("keywordtag",None)
    search = request.GET.get("keyword", None)

    countpost = 2

    if x == 2:
        k = x
        if search is not None:
            taglist = models.Tag.objects.filter(title__icontains=search).all()
            allp2tlist = []
            allpost_list = []
            for tag in taglist:
                p2tlist = models.Post2Tag.objects.filter(tag=tag)
                allp2tlist += p2tlist

            for p2t in allp2tlist:
                p_list = models.Post.objects.filter(nid=p2t.post.nid)
                allpost_list += p_list
            mywhere = "keyword=" + (search)

            countpost = len(allp2tlist)


        else:
            allpost_list = models.Post.objects.all()
            countpost = len(allpost_list)

    elif x == 1:
        k = x
        if search is not None:
            allpost_list = models.Post.objects.filter(title__icontains=search).all()
            mywhere = "keyword=" + (search)
            countpost = len(allpost_list)
        else:
            allpost_list = models.Post.objects.all()
            countpost = len(allpost_list)


    else:
        allpost_list = models.Post.objects.all()
        countpost = len(models.Post.objects.all())

    allpost_list = list(reversed(allpost_list))

    p = Paginator(allpost_list, 5)

    if pindex < 1:
        pindex = 1

    if pindex > p.num_pages:
        pindex = p.num_pages

    pagerange = p.page_range

    post_list = p.page(pindex)
    op = []
    while not op:
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost + 2)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]
    status = UserInfo.objects.get(nid=request.session.get('_auth_user_id')).status
    if status == 3:
        status3 = 1
    else:
        status3 = 0
    return render(request, "index.html", locals())


def searchtag(request):
    allpost_list = models.Post.objects.all()
    p = Paginator(allpost_list, 5)

    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]

    tag_list = models.Tag.objects.all()
    return render(request, 'searchtag.html', locals())


def register(request):
    """
    注册视图函数:
       get请求响应注册页面
       post(Ajax)请求,校验字段,响应字典
    :param request:
    :return:
    """

    if request.is_ajax():
        # print(request.POST)
        form = UserForm(request.POST)

        response = {"user": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")

            # 生成一条用户纪录
            user = form.cleaned_data.get("user")
            # print("user", user)
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar_obj = request.FILES.get("avatar")

            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj

            user_obj = UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
            user_obj.save()

        else:
            # print(form.cleaned_data)
            # print(form.errors)
            response["msg"] = form.errors

        return JsonResponse(response)

    form = UserForm()
    return render(request, "register.html", {"form": form})


def createpost(request):
    # if request.method == "POST":
    #     ob=Post()
    #     response = {"user": None, "msg": "Sorry there has something wrong"}
    #     ob.title = request.POST.get("title")
    #     ob.content = request.POST.get("content")
    #     nid=request.session.get('_auth_user_id')
    #     user=UserInfo.objects.get(pk=nid)
    #     ob.user=user
    #     ob.save()

    #     return JsonResponse(response)
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():

            print(tag.name)
            if tag.name == "script":
                tag.decompose()

        ob = models.Post.objects.create(title=title, content=str(soup), user=request.user)

        tagtitle = request.POST.get("tag")
        if not models.Tag.objects.filter(title=tagtitle).all():
            currenttag = Tag()
            currenttag.title = tagtitle
            currenttag.save()
        else:
            currenttag = models.Tag.objects.filter(title=tagtitle).all()[0]
            currenttag.save()

        newp2t = Post2Tag()
        newp2t.tag = currenttag
        newp2t.post = ob
        newp2t.save()

        return redirect("/index/1/1")
    return render(request, "createpost.html")


def post_detail(request, username, post_id):
    """
    文章详情页
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    post_obj = models.Post.objects.filter(pk=post_id).first()
    page = post_id
    comment_list = models.Comment.objects.filter(post_id=post_id)

    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]
    return render(request, "post_detail.html", locals())


def digg(request):
    """
    点赞功能
    :param request:
    :return:
    """

    post_id = request.POST.get("post_id")
    is_up = json.loads(request.POST.get("is_up"))  # "true"
    # 点赞人即当前登录人
    user_id = request.user.pk
    obj = models.PostUpDown.objects.filter(user_id=user_id, post_id=post_id).first()

    response = {"state": True}
    if not obj:
        ard = models.PostUpDown.objects.create(user_id=user_id, post_id=post_id, is_up=is_up)

        queryset = models.Post.objects.filter(pk=post_id)
        if is_up:
            queryset.update(up_count=F("up_count") + 1)
        else:
            queryset.update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
        response["handled"] = obj.is_up

    return JsonResponse(response)


def comment(request):
    """
    提交评论视图函数
    功能:
    1 保存评论
    2 创建事务
    3 发送邮件
    :param request:
    :return:
    """
    post_id = request.POST.get("post_id")
    pid = request.POST.get("pid")
    content = request.POST.get("content")
    user_id = request.user.pk

    post_obj = models.Post.objects.filter(pk=post_id).first()

    # 事务操作
    with transaction.atomic():
        comment_obj = models.Comment.objects.create(user_id=user_id, post_id=post_id, content=content,
                                                    parent_comment_id=pid)
        models.Post.objects.filter(pk=post_id).update(comment_count=F("comment_count") + 1)

    response = {}

    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["username"] = request.user.username
    response["content"] = content

    # from django.core.mail import send_mail
    # from xiaotuan import settings

    #     # send_mail(
    #     #     "您的文章%s新增了一条评论内容"%article_obj.title,
    #     #     content,
    #     #     settings.EMAIL_HOST_USER,
    #     #     ["916852314@qq.com"]
    #     # )

    # import threading

    # t = threading.Thread(target=send_mail, args=("您的文章%s新增了一条评论内容" % post_obj.title,
    #                                                 content,
    #                                                 settings.EMAIL_HOST_USER,
    #                                                 ["1171030447@qq.com"])
    #                          )
    # t.start()
    return JsonResponse(response)


def get_comment_tree(request):
    post_id = request.GET.get("post_id")
    response = list(models.Comment.objects.filter(post_id=post_id).order_by("pk").values("pk", "content",
                                                                                         "parent_comment_id"))

    return JsonResponse(response, safe=False)


def modifya(request):
    if request.is_ajax():
        form = AvatarForm(request.POST, user=request.user)

        response = {"msg": None}

        if form.is_valid():
            user = request.user
            avatar_obj = request.FILES.get("avatar")
            print("1")

            if avatar_obj:
                print("1")
                user.avatar = avatar_obj
                user.save()

        else:
            response["msg"] = form.errors

        return JsonResponse(response)
    else:
        form = UserForm()

    allpost_list = models.Post.objects.all()
    p = Paginator(allpost_list, 5)

    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]
    return render(request, "modifya.html", locals())


def cgpwd(request):
    # redirect_to = reverse('login')

    if request.is_ajax():
        form = ChangePasswordForm(request.POST, user=request.user)  # 获取form表单
        response = {"msg": None}

        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            # return redirect("/login/")

        else:
            response["msg"] = form.errors

        return JsonResponse(response)

    else:
        form = ChangePasswordForm()

    allpost_list = models.Post.objects.all()
    p = Paginator(allpost_list, 5)

    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]

    # context = {}
    # context['page_title'] = '修改密码'
    # context['form_title'] = '修改密码'
    # context['submit_text'] = '修改'
    # context['form'] = form
    # context['return_back_url'] = redirect_to
    return render(request, 'cgpwd.html', locals())


def createp2t(request):
    if request.method == "POST":
        posttitle = request.POST.get("title")
        ob = models.Post.objects.filter(title=posttitle).all()[0]

        tagtitle = request.POST.get("tag")

        currenttag = Tag()
        currenttag.title = tagtitle
        currenttag.save()

        newp2t = Post2Tag()
        newp2t.tag = currenttag
        newp2t.post = ob
        newp2t.save()
        response = {"msg": "i"}
        return JsonResponse(response)

    return render(request, "createp2t.html")


def clubinfo(request, username):
    userid = request.session.get('_auth_user_id')
    xisfollow = models.following.objects.filter(Q(club__username=username) & Q(fan__nid=userid)).first()
    currentclub = models.UserInfo.objects.filter(username=username).first()
    post_list = models.Post.objects.filter(user__username=username).all()

    allpost_list = models.Post.objects.all()
    p = Paginator(allpost_list, 5)

    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]
    return render(request, "clubinfo.html", locals())


def followta(request, clubid):
    userid = request.session.get('_auth_user_id')
    currentfan = models.UserInfo.objects.filter(nid=userid).first()
    currentidol = models.UserInfo.objects.filter(nid=clubid).first()
    currentidolusername = currentidol.username
    ob = following()
    ob.club = currentidol
    ob.fan = currentfan
    ob.save()

    return redirect('/clubinfo/%s' % (currentidolusername))


def myidol(request):
    userid = request.session.get('_auth_user_id')
    followinglist = models.following.objects.filter(fan__nid=userid).all()
    idollist = []
    for ifollowing in followinglist:
        idollist.append(ifollowing.club)

    allpost_list = models.Post.objects.all()
    p = Paginator(allpost_list, 5)

    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]
    return render(request, "myidol.html", locals())


def createapplication(request):
    if request.method == "POST":
        ob = Applications()
        # response = {"user": None, "msg": "Sorry there has something wrong"}
        content = request.POST.get("content")
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():

            print(tag.name)
            if tag.name == "script":
                tag.decompose()
        ob.content = str(soup)
        nid = request.session.get('_auth_user_id')
        user = UserInfo.objects.get(pk=nid)
        user.status = 2
        user.save()
        ob.user = user
        ob.save()
        # return JsonResponse(response)
        return redirect("/index/1/1")

    nid = request.session.get('_auth_user_id')
    user = UserInfo.objects.get(pk=nid)
    status = user.status
    statuslist = [0, 0, 0, 0]
    statuslist[status - 1] = 1
    status1 = statuslist[0]
    status2 = statuslist[1]
    status3 = statuslist[2]
    status4 = statuslist[3]

    allpost_list = models.Post.objects.all()
    p = Paginator(allpost_list, 5)

    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]

    return render(request, "createapplication.html", locals())


def hotrank(request, pindex=1):
    allpost_list = models.Post.objects.all().order_by('-up_count')
    p = Paginator(allpost_list, 5)

    if pindex < 1:
        pindex = 1

    if pindex > p.num_pages:
        pindex = p.num_pages

    countpost = len(models.Post.objects.all())

    post_list = p.page(pindex)
    op = []
    while not op:
        countpost = len(models.Post.objects.all())
        random.seed(datetime.now())
        rangepost_id = random.randint(1, countpost)
        op = models.Post.objects.filter(nid=rangepost_id)
    op = op[0]
    status = UserInfo.objects.get(nid=request.session.get('_auth_user_id')).status
    if status == 3:
        status3 = 1
    else:
        status3 = 0

    return render(request, "hotrank.html", locals())


def upload(request):
    print(request.FILES)
    img_obj = request.FILES.get("upload_img")
    print(img_obj.name)

    path = os.path.join(settings.MEDIA_ROOT, "add_post_img", img_obj.name)

    with open(path, "wb") as f:
        for line in img_obj:
            f.write(line)

    response = {
        "error": 0,
        "url": "/media/add_post_img/%s" % img_obj.name,
    }

    return HttpResponse(json.dumps(response))
