from wc_prediction import db, login_manager
from flask_sqlalchemy import SQLAlchemy
from wc_prediction import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=40), nullable=False, unique=True)
    email_address = db.Column(db.String(length=60), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    winning_path = db.relationship('Teams', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


    # to do: relation attribute to assign full tournament prediction to a user

    def __repr__(self):
        return f'User: {self.username}'

class Teams(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    group = db.Column(db.String(1), nullable=False)
    qualified_teams = db.Column(db.String(30), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    advance_f = db.Column(db.String(1), nullable=False)

    def adding(self, user):
        #mistakes here unfortunately, although advance_f is changing for object on self, but later it cant query, like it didnt commit changes
        self.owner = user.id
        print(self.advance_f)
        self.advance_f = "A"
        print(self, "    ")
        print(self.advance_f)
        Teams.advance_f = "A"
        db.session.commit()
    def changing(self, user):
        self.owner = user.id
        self.advance_f = "N"
        db.session.commit()
        


    def __repr__(self):
       return f'Team: {self.qualified_teams}'

db.create_all()
db.session.commit()

