try:
    import flask_sqlalchemy
    from .zeus_model import db, CRUDMixin
except:
    pass

try:
    import celery
    from .zeus_celery import Celery
except:
    pass