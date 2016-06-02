# 说明

此为作者平时工作经验总结,不推荐除作者以外的人员使用,此代码库引起的所有后果,作者概不负责.

(ps: 能看懂就看懂,不能看懂活该!)

# 依赖

1. python >= 3.5
2. flask >= 0.11
3. postgresql >= 9.5
4. 一些flask扩展 (flask-login, flask-wtf, flask-sqlalchemy, flask-restful, WTForms-JSON, ...等等)

# 模型

    from flask_zeus.mixin import (CRUDMixin, DeletedMixin, EntryMixin, EntryColumnMixin, AccountMixin)

1. CRUDMixin

    包括(id, created_at, updated_at, deleted)等字段
    
    包括(create, update, delete, save)等方法
    
2. DeletedMixin

    就有个 deleted 字段
    
3. EntryMixin

4. EntryColumnMixin

5. AccountMixin

    包括(email, password_hash, email_confirmed)等字段
    
    包括(password, token)等属性
    
    包括(verify_password, get_by_token, get_by_account, generate_token, verify_token, load_token, confirm)

简单模型定义

    from flask_zeus import db
    from flask_zeus.mixin import CRUDMixin

    class Post(db.Model, CRUDMixin):
        content = db.Column('content', db.Text, doc='内容')
        
用户模型定义
    
    from flask_zeus import db
    from flask_zues.mixin import CRUDMixin, AccountMixin
    
    class User(db.Model, CRUDMixin, AccountMixin):
        pass_

# 表单

    from flask_zeus import Form
    from wtforms import fields
    from wtforms import validators
    from jinja2 import Markup
    
    class LoginForm(Form):
        email = fields.StringField('邮箱', validators=[
            validators.Email(message='请输入正确的邮箱地址'),
        ], description='')
        password = fields.PasswordField('密码', validators=[
            validators.Length(min=6, message='密码最短6位'),
            validators.Length(max=50, message='密码最长50位'),
        ], description=Markup('<a href="/account/password/forget/">忘记密码?</a>'))
        remember = fields.BooleanField('记住我(一个月内免登陆)', default=True)
        submit = fields.SubmitField('登陆')

# 接口输出字段
    
为接口定义模型的输出格式


    from flask_zeus import fields
    
    user_fields = {
        'id': fields.String('用户id'),
        'email': fields.String('邮箱'),
        'nickname': fields.String('用户昵称'),
        'avatar': fields.String('用户头像'),
        'follower_count': fields.Integer('关注数'),
        'followed_count': fields.Integer('粉丝数'),
        'created_at': fields.DateTime('创建时间'),
        'uri_self': fields.Url('详情链接', endpoint='api_v1.account_detail', absolute=True),
        'uri_follow': fields.Url('关注链接', endpoint='api_v1.follow', absolute=True),
    }
    
    login_user_fields = user_fields.copy()
    login_user_fields['token'] = fields.String('用户token')

# 接口URL参数解析

    from flask_restful import reqparse
    
    page_args = reqparse.RequestParser()
    page_args.add_argument('page', type=int, help='页码', location='args')
    page_args.add_argument('per_page', type=int, help='每页显示个数', location='args')

# REST接口

增删改查接口定义 (get, post, put, delete)

重要属性 model(模型), model_fields(模型输出), create_form(post方法使用的表单类), update_form(put方法使用的表单类)

请求方式有开关可控制 can_read, can_create, can_update, can_delete

##### GET:

如果url中包含id字段,输出详情

否则输出列表

列表中包含分页信息

#### POST:
#### PUT:
#### DELETE:

看源码吧

    from flask_restful import (marshal)
    from flask_zeus.api import RestfulResource
    from flask_zeus.api.error import ZeusBadRequest
    from flask_login import (login_user)
    from .. import api
    from ...models import User
    from .forms import (LoginForm, RegisterForm)
    from .fields import (user_fields, login_user_fields)
    from .parsing import account_list_args
    
    
    @api.resource('/account/', endpoint='account')
    class AccountEntriesResource(RestfulResource):
        model = User
        model_fields = user_fields
        parsing = account_list_args
    
    
    @api.resource('/account/<uuid:id>/', endpoint='account_detail')
    class AccountEntriesResource(RestfulResource):
        model = User
        model_fields = user_fields
    
    
    @api.resource('/account/login/', endpoint='account_login')
    class AccountLoginResource(RestfulResource):
        can_read = False
        can_create = True
        create_form = LoginForm
        model_fields = login_user_fields
    
        def post(self):
            form = self.create_form()
    
            if form.validate_on_submit():
                login_user(form.user, form.remember.data)
                return marshal(form.user, self.model_fields)
    
            raise ZeusBadRequest(details=form.errors)

所有接口都可以使用options方法查看接口情况, 比如 /account/login/ 接口

headers:

    Allow →POST
    Connection →keep-alive
    Content-Length →1068
    Content-Type →application/json
    Date →Thu, 02 Jun 2016 08:31:48 GMT
    Server →gunicorn/19.6.0
    
body:

    {
      "POST": [
        {
          "name": "email",
          "text": "邮箱",
          "type": "str",
          "validators": [
            "Email regex:^.+@([^.@][^@]+)$"
          ]
        },
        {
          "description": "<a href=\"/account/password/forget/\">忘记密码?</a>",
          "name": "password",
          "text": "密码",
          "type": "str",
          "validators": [
            "Length min:6 max:-1",
            "Length min:-1 max:50"
          ]
        },
        {
          "default": true,
          "name": "remember",
          "text": "记住我(一个月内免登陆)",
          "type": "bool"
        }
      ],
      "return": {
        "avatar": "用户头像",
        "created_at": "创建时间",
        "email": "邮箱",
        "followed_count": "粉丝数",
        "follower_count": "关注数",
        "id": "用户id",
        "nickname": "用户昵称",
        "token": "用户token",
        "uri_follow": "关注链接",
        "uri_self": "详情链接"
      }
    }
    

# Toggle接口

    from flask_zeus.api import ToggleResource

    # 有一种接口类型是开关形式的,比如点赞,关注. 
    # 请求发过来,如果数据存在就把数据删除(取消点赞,取消关注), 否则就创建数据(点赞,关注)
    # 这个时候使用ToggleResource, 只支持POST方法

# 列表视图

用于pc端html页面

    from . import square as app
    from app.models import (Post, Comment, Praise, Follow)
    from app.api_v1.comment.forms import (CommentForm)
    from app.api_v1.square.forms import (PostForm)
    from flask_zeus.view import (ListView, DetailView)
    
    
    @app.route('/', endpoint='entries')
    class PostListView(ListView):
        model = Post
        template = 'square/entries.html'
        order_by = (model.created_at.desc(),)
    
        def get_context(self):
            context = super(PostListView, self).get_context()
            context['square_form'] = PostForm()
            return context
    
        def merge_data(self, items):
            return Praise.for_entries(items)

# 详情视图

用于pc端html页面

    from . import square as app
    from app.models import (Post, Comment, Praise, Follow)
    from app.api_v1.comment.forms import (CommentForm)
    from app.api_v1.square.forms import (PostForm)
    from flask_zeus.view import (ListView, DetailView)
    
    
    @app.route('/<data_id>/', endpoint='entry')
    class PostDetailView(DetailView):
        model = Post
        template = 'square/entry.html'
    
        def get_context(self):
            context = super(PostDetailView, self).get_context()
            context['Comment'] = Comment
            context['comment_form'] = CommentForm()
            return context


# 表单提交视图

用于pc端html页面
    
    @app.route('/shop/create/', endpoint='shop_create')
    class ShopCreateView(CreateView):
        model = Shop
        form = ShopForm
        template = 'sell/shop_create.html'


    @app.route('/shop/update/', endpoint='shop_update')
    class ShopUpdateView(UpdateView):
        model = Shop
        form = ShopForm
        template = 'sell/shop_update.html'
    
        def get_query_filter(self):
            return {'user_id': current_user.id}


# 逻辑解耦
    
如果希望在数据创建前 或者 创建后做一些操作,该怎么办呢?
    
1. SQLAlchemy event (伟大的SQLAlchemy带来的神器)

比如我们在每次模型update操作的时候,更新模型的updated_at值:

    from sqlalchemy import event
    from sqlalchemy.orm import mapper
    
    def mapper_update(mapper, connection, target):
        if target.has_property('updated_at'):
            target.updated_at = datetime.datetime.now()
    
    event.listen(mapper, 'before_update', mapper_update)
    

2. blinker signal (信号,相当强大)

在很多第三方扩展中,都有提供信号.比如flask-login中的(user_logged_in, user_logged_out, user_loaded_from_cookie, user_loaded_from_header, user_loaded_from_request, user_login_confirmed, user_unauthorized, user_needs_refresh, user_accessed, session_protected)

1个信号就代表一个动作,通过订阅信号,来实现动作触发后的后续操作