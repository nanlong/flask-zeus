# 模型

    from flask_zeus.mixin import (CRUDMixin, DeletedMixin, EntryMixin, EntryColumnMixin, AccountMixin)

1. CRUDMixin
2. DeletedMixin
3. EntryMixin
4. EntryColumnMixin
5. AccountMixin

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

    from flask_zeus.api import ToggleResource_

# 列表视图

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


    
