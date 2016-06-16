# 说明

此为作者平时工作经验总结


# 安装
    
    git clone https://github.com/nanlong/flask_zeus.git
    cd flask_zeus
    python setup.py install
            
    
或者
    
    pip install flask-zeus

# 依赖

1. python >= 3.5
2. flask >= 0.11
3. postgresql >= 9.5
4. 一些flask扩展 (flask-login, flask-wtf, flask-sqlalchemy, flask-restful, WTForms-JSON, ...等等)


# Example:

    from app.models import Post
    from app.forms import PostCreateForm, PostUpdateForm
    from app.model_fields import post_fields

    @api.resource('/posts/', '/posts/<int:id>/')
    class PostAPI(RestfulApi):
        model = Post
        create_form = PostCreateForm
        update_form = PostUpdateForm
        model_fields = post_fields
        can_create = True
        can_update = True
        can_delete = True

说明:

api1 /posts/ 为资源列表

api2 /posts/<int:id>/为资源详情

两个接口都支持GET方法

两个接口都支持OPTIONS方法,用来查看接口说明.包括支持的method头部信息,不同method的请求数据说明和返回的数据说明.

对api1使用POST方法,用来创建资源

对api2使用PUT方法,用来更新资源

对api2使用DELETE方法,用来删除资源