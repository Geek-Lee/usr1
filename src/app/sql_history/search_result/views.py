# -*- coding: utf-8 -*-
from .models import sql_record, match_result, user_info
from django.template import loader, Context
from django.db.models import Count, Max
from django.http import Http404
import datetime
import json
from django.contrib import auth
from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.template.context import RequestContext
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from bootstrap_toolkit.widgets import BootstrapUneditableInput
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
import pandas as pd
from sqlalchemy import create_engine
from sql_history.settings import DATABASES

engine_ht = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(
    DATABASES['default']['USER'],
    DATABASES['default']['PASSWORD'],
    DATABASES['default']['HOST'],
    DATABASES['default']['PORT'],
    DATABASES['default']['NAME'],
), connect_args={"charset": "utf8"})


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render_to_response('login.html', RequestContext(request, {'form': form, }))
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return render_to_response('index.html', RequestContext(request))
            else:
                return render_to_response('login.html',
                                          RequestContext(request, {'form': form, 'password_is_wrong': True}))
        else:
            return render_to_response('login.html', RequestContext(request, {'form': form, 'password_is_wrong': False}))


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/accounts/login/")


def latest_time(sql_record):
    max_date = sql_record[0]['creat_at']
    for record in sql_record:
        if record['creat_at'] > max_date:
            max_date = record['creat_at']
    return max_date


def sum_r(sql_record):
    sum = 0
    for record in sql_record:
        sum = sum + record['rows_sent']
    return sum


def sum_u(sql_record):
    user_list = sql_record.values('user').distinct().order_by('user')
    return len(user_list)


def sum_t(sql_record):
    sum = 0
    for record in sql_record:
        sum = sum + record['query_time']
    return sum


# Create your views here.
@login_required
def home(request):
    data = sql_record.objects.all()  # 使用对象关系映射，因为BlogPost类是django.db.model.Model的子类
    user_list = data.values('user').distinct().order_by('user')
    posts = data.filter(user=user_list[0]['user'])
    latest = latest_time(posts.values('creat_at'))
    posts = posts.filter(creat_at=latest)
    # models = []
    for i in range(1, len(user_list)):
        post = data.filter(user=user_list[i]['user'])
        latest = latest_time(post.values('creat_at'))
        post = post.filter(creat_at=latest)
        # models.append({'post':post,'date':latest.strftime('%Y-%m-%d')})
        posts = posts | post
    posts = posts.order_by('-creat_at', 'user')
    t = loader.get_template("table_SQL_history.html")  # 创建模板对象
    c = Context({'posts': posts})
    # c = Context({'models': models})#模板渲染数据
    return HttpResponse(t.render(c))  # 每个视图函数都会返回HttpRespose对象。render即返回一个字符串。


@login_required
def home_page(request):
    sql = "SELECT *, Count(user_id) as visit_times FROM easy_log GROUP BY user_id"
    df = pd.read_sql(sql, engine_ht)
    posts = df.to_dict(orient="records")
    return render(request, 'table_SQL_history.html', {'posts': posts})


@login_required
def user_detail(request, user):
    try:
        date_now = datetime.datetime.now()
        datetime_now = datetime.datetime(date_now.year, date_now.month, date_now.day, 23, 59, 59)
        start_30 = datetime_now - datetime.timedelta(30)
        post = sql_record.objects.filter(user=user).order_by('-creat_at')
        sum_row = sum_r(post.values('rows_sent'))
        data = post.filter(creat_at__gte=start_30)
        posts1 = [{'date': '1990-01-01', 'sum_rows': 0}] * 30
        posts2 = [{'date': '1990-01-01', 'sum_times': 0}] * 30
        for i in range(0, 30):
            date_current = (datetime_now - datetime.timedelta(i)).strftime("%Y-%m-%d")
            data_current = data.filter(date=date_current)
            data_current_rows = sum_r(data_current.values('rows_sent'))
            posts1[-(i + 1)] = {'date': date_current, 'sum_rows': data_current_rows}
            posts2[-(i + 1)] = {'date': date_current, 'sum_times': int(len(data_current))}
        post_json1 = json.dumps(posts1)
        post_json2 = json.dumps(posts2)
        user = post.values('company').distinct().order_by('company')[0]['company']
        # t = loader.get_template("user_sql_history.html")
        # c = Context({'post':post,'user':user,'sum_raw':sum_raw})
    except sql_record.DoesNotExist:
        raise Http404
    return render_to_response("user_sql_history.html",
                              {'post': post, 'user': user, 'sum_row': sum_row, 'post1': post_json1,
                               'post2': post_json2})


@login_required
def date_detail(request, date):
    try:
        post = sql_record.objects.filter(date=date).order_by('-creat_at', 'user')
        user_list = post.values('user').distinct().order_by('user')
        sum_user = len(user_list)
        posts1 = [{'user': 'lalalalala', 'sum_rows': 0}] * sum_user
        posts2 = [{'user': 'lalalalala', 'sum_times': 0}] * sum_user
        posts3 = [{'user': 'lalalalala', 'sum_time': 0}] * sum_user
        for i in range(0, sum_user):
            data_current = post.filter(user=user_list[i]['user'])
            data_current_rows = sum_r(data_current.values('rows_sent'))
            # query_time_list = data_current.values('query_time')
            qurey_time_sum = sum_t(data_current.values('query_time'))
            user_current = data_current.values('company').distinct().order_by('company')[0]['company']
            posts1[i] = {'user': user_current, 'sum_rows': data_current_rows}
            posts2[i] = {'user': user_current, 'sum_times': int(len(data_current))}
            posts3[i] = {'user': user_current, 'sum_time': qurey_time_sum}
        post_json1 = json.dumps(posts1)
        post_json2 = json.dumps(posts2)
        post_json3 = json.dumps(posts3)
        # t = loader.get_template("date_sql_history.html")
        # c = Context({'post':post,'date':date,'sum_user':sum_user})
    except sql_record.DoesNotExist:
        raise Http404
    return render_to_response("date_sql_history.html",
                              {'post': post, 'date': date, 'sum_user': sum_user, 'post1': post_json1,
                               'post2': post_json2, 'post3': post_json3})


@login_required
def user_date(request, date, user):
    try:
        date_time = datetime.datetime.strptime(date, "%Y-%m-%d")
        post = sql_record.objects.filter(date=date).filter(user=user).order_by('-creat_at', 'user')
        sum_times = len(post)
        posts1 = [{'datetime': '1990-01-01 00:00', 'sum_rows': 0}] * 24
        for i in range(0, 24):
            start_time = datetime.datetime(date_time.year, date_time.month, date_time.day, i, 0)
            end_time = datetime.datetime(date_time.year, date_time.month, date_time.day, i, 59)
            data_current = post.filter(creat_at__gte=start_time).filter(creat_at__lt=end_time)
            data_current_rows = sum_r(data_current.values('rows_sent'))
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M")
            posts1[i] = {'datetime': start_time_str, 'sum_rows': data_current_rows}
        post_json1 = json.dumps(posts1)
        company = post.values('company').distinct().order_by('company')[0]['company']
    except sql_record.DoesNotExist:
        raise Http404
    return render_to_response("user_date_sql_history.html",
                              {'user_code': user, 'posts': post, 'date': date, 'user': company, 'sum_times': sum_times,
                               'post1': post_json1})


@login_required
def date_static(request):
    date_now = datetime.datetime.now()
    datetime_now = datetime.datetime(date_now.year, date_now.month, date_now.day, 23, 59, 59)
    start_30 = datetime_now - datetime.timedelta(30)
    data = sql_record.objects.filter(creat_at__gte=start_30)
    # sum = [0]*30
    # sum_user = [0]*30
    # date_list = ["1990-01-01"]*30
    posts1 = [{'date': '1990-01-01', 'sum_user': 0}] * 30
    posts2 = [{'date': '1990-01-01', 'sum_times': 0}] * 30
    posts3 = []
    for i in range(0, 30):
        date_current = (datetime_now - datetime.timedelta(i)).strftime("%Y-%m-%d")
        # date_list[-(i+1)] = date_current
        data_current = data.filter(date=date_current)
        # sum[-(i+1)] = len(data_current)
        user_list = data_current.values('user').distinct().order_by('user')
        # sum_user[-(i+1)] = len(user_list)
        posts1[-(i + 1)] = {'date': date_current, 'sum_user': int(len(user_list))}
        posts2[-(i + 1)] = {'date': date_current, 'sum_times': int(len(data_current))}
    date_list = data.values('date').distinct().order_by('-date')
    for day in date_list:
        data_current = data.filter(date=day['date'])
        user_list = data_current.values('user').distinct().order_by('user')
        posts3.append({'date': day['date'], 'sum_user': len(user_list), 'sum_times': len(data_current)})
    # df = pd.DataFrame({'date':date_list,'sum_user':sum_user,'sum':sum})
    post_json1 = json.dumps(posts1)
    post_json2 = json.dumps(posts2)
    return render_to_response("date_static.html", {'posts': posts3, 'post1': post_json1, 'post2': post_json2})
    # t = loader.get_template("date_static.html")
    # c = Context({'post': post_json})
    # return HttpResponse(t.render(c))


@login_required
def fofeasy_home(request):
    data = match_result.objects.all().exclude(company='私募云通')
    posts = data.values('ip_address').annotate(sum_api=Count('api')).annotate(date=Max('action_time')).values(
        'ip_address', 'company', 'date', 'sum_api', 'user_id', 'address').order_by('-date')
    posts4 = user_info.objects.exclude(company='私募云通').filter(GeoCoordX__isnull=False, GeoCoordY__isnull=False).values(
        'location').distinct().annotate(sum_user=Count('ip_address')).values('location', 'sum_user', 'GeoCoordX',
                                                                             'GeoCoordY').order_by('-sum_user')
    post_data = []
    post_geoc = {}
    for post in posts4:
        post_data.append({'name': post['location'], 'value': post['sum_user']})
        post_geoc[post['location']] = [post['GeoCoordX'], post['GeoCoordY']]
    province_data = user_info.objects.exclude(company='私募云通').filter(GeoCoordX__isnull=False, GeoCoordY__isnull=False).values(
        'province').distinct().annotate(sum_user=Count('ip_address')).values('province', 'sum_user').order_by('-sum_user')
    post_province = []
    for post in province_data:
        post_province.append({'name': post['province'], 'value': post['sum_user']})
    post4 = {'data': post_data, 'geo': post_geoc, 'province': post_province}
    post4 = json.dumps(post4)
    date_now = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    start_date = date_now - datetime.timedelta(30)
    d_data = data.filter(action_time__gte=start_date)
    posts1 = [{'date': '1990-01-01', 'sum_user': 0}] * 30
    posts2 = [{'date': '1990-01-01', 'sum_api': 0}] * 30
    for i in range(30):
        date_end = date_now - datetime.timedelta(i - 1)
        date_start = date_now - datetime.timedelta(i)
        data_current = d_data.filter(action_time__gte=date_start, action_time__lt=date_end)
        ip_num = data_current.values('ip_address').distinct().count()
        api_num = data_current.count()
        posts1[-(i + 1)] = {'date': date_start.strftime('%Y-%m-%d'), 'sum_ip': ip_num}
        posts2[-(i + 1)] = {'date': date_start.strftime('%Y-%m-%d'), 'sum_api': api_num}
    posts1 = json.dumps(posts1)
    posts2 = json.dumps(posts2)
    api_data = d_data.values('user_action').annotate(sum_api=Count('api')).values('user_action', 'sum_api').order_by(
        '-sum_api')
    posts3 = []
    for post in api_data:
        posts3.append(post)
    posts3 = json.dumps(posts3)
    # x
    sql = "SELECT *, Count(user_id) as visit_times FROM easy_log GROUP BY user_id"
    df = pd.read_sql(sql, engine_ht)
    posts5 = df.to_dict(orient="records")
    sum_user = df['user_id'].count()
    return render_to_response("fofeasy_home.html",
                              {'posts': posts, 'post1': posts1, 'post2': posts2, 'post3': posts3, 'sum_user': sum_user, 'post4': post4, 'post5': posts5})

@login_required
def fofeasy_home(request, user_id):
    sql = "SELECT *, Count(user_id) as visit_times FROM easy_log GROUP BY user_id={}".format(int(user_id))
    df = pd.read_sql(sql, engine_ht)
    sum_user = df['user_id'].count()
    return render_to_response("")


@login_required
def fofeasy_user_detail(request, user_id):
    try:
        data = match_result.objects.filter(user_id=user_id).order_by("-action_time")
        ip = data.values('ip_address').first()['ip_address']
        company = data.values('company').first()['company']
        date_s = datetime.datetime.strptime(data.values('action_time').last()['action_time'].strftime('%Y-%m-%d'),
                                            '%Y-%m-%d')
        date_e = datetime.datetime.strptime(
            (data.values('action_time').first()['action_time'] + datetime.timedelta(1)).strftime('%Y-%m-%d'),
            '%Y-%m-%d')
        post = []
        while date_s < date_e:
            sum_api = data.filter(action_time__gte=date_s, action_time__lt=date_s + datetime.timedelta(1)).count()
            if sum_api != 0:
                post.append({'company': company, 'ip': ip, 'date': date_s.strftime('%Y-%m-%d'), 'sum_api': sum_api,
                             'user_id': user_id})
            date_s = date_s + datetime.timedelta(1)
        post = sorted(post, key=lambda x: x['date'], reverse=True)
        sum_days = len(post)
        date_now = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
        start_date = date_now - datetime.timedelta(30)
        d_data = data.filter(action_time__gte=start_date)
        posts1 = [{'date': '1990-01-01', 'sum_api': 0}] * 30
        for i in range(30):
            date_end = date_now - datetime.timedelta(i - 1)
            date_start = date_now - datetime.timedelta(i)
            data_current = d_data.filter(action_time__gte=date_start, action_time__lt=date_end)
            api_num = data_current.count()
            posts1[-(i + 1)] = {'date': date_start.strftime('%Y-%m-%d'), 'sum_api': api_num}
        api_data = d_data.values('user_action').annotate(sum_api=Count('api')).values('user_action',
                                                                                      'sum_api').order_by(
            '-sum_api')
        posts2 = []
        for post2 in api_data:
            posts2.append(post2)
        posts1 = json.dumps(posts1)
        posts2 = json.dumps(posts2)
    except match_result.DoesNotExist:
        raise Http404
    return render_to_response("user_api_history.html",
                              {'post': post, 'post1': posts1, 'post2': posts2, 'user_id': user_id, 'sum_days': sum_days,
                               'company': company})


@login_required
def fofeasy_date_detail(request, date):
    try:
        date_start = datetime.datetime.strptime(date, '%Y-%m-%d')
        date_end = date_start + datetime.timedelta(1)
        data = match_result.objects.exclude(company='私募云通').filter(action_time__gte=date_start, action_time__lt=date_end)
        posts = data.values('ip_address').annotate(sum_api=Count('api')).annotate(date=Max('action_time')).values(
            'ip_address', 'company', 'date', 'sum_api', 'user_id').order_by('-sum_api')
        com_api_data = data.values('company').annotate(sum_api=Count('api')).values('company', 'sum_api').order_by(
            '-sum_api')
        posts1 = []
        for post1 in com_api_data:
            posts1.append(post1)
        api_data = data.values('user_action').annotate(sum_api=Count('api')).values('user_action',
                                                                                    'sum_api').order_by(
            '-sum_api')
        posts2 = []
        for post2 in api_data:
            posts2.append(post2)
        posts1 = json.dumps(posts1)
        posts2 = json.dumps(posts2)
    except match_result.DoesNotExist:
        raise Http404
    return render_to_response("date_api_history.html",
                              {'post': posts, 'post1': posts1, 'post2': posts2, 'date': date, 'sum_user': len(posts)})


@login_required
def fofeasy_user_date_detail(request, date, user_id):
    try:
        date_start = datetime.datetime.strptime(date, '%Y-%m-%d')
        date_end = date_start + datetime.timedelta(1)
        data = match_result.objects.filter(action_time__gte=date_start, action_time__lt=date_end,
                                           user_id=user_id).order_by('-action_time')
        posts = data
        company = data.values('company').first()['company']

        api_data = data.values('user_action').annotate(sum_api=Count('api')).values('user_action', 'sum_api').order_by(
            '-sum_api')
        post1 = []
        for post in api_data:
            post1.append(post)
        post1 = json.dumps(post1)
    except match_result.DoesNotExist:
        raise Http404
    return render_to_response("user_date_api_history.html",
                              {'posts': posts, 'post1': post1, 'date': date, 'user': user_id, 'company': company,
                               'sum_api': len(posts)})
