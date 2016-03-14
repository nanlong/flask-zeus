# flask_zeus

## Model
    from flask import Flask
    from flask.ext.zeus import db, CRUDMixin
    
    app = Flask(__name__)
    db.init_app(app)
    
    class User(db.Model, CRUDMixin):
        username = db.Column('username', db.CHAR(255), index=True, unique=True)
        password_hash = db.Column('password', db.CHAR(512))
        
        
    user = User.create(username='', password_hash='')
    # or
    user = User.get(user_id)
    
    user.as_dict()
    user.update()
    user.delete()
    
    
