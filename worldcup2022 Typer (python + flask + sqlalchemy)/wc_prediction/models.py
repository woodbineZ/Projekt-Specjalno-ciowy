from wc_prediction import db, login_manager
from flask_sqlalchemy import SQLAlchemy
from wc_prediction import bcrypt
from flask_login import UserMixin, current_user

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
    advance_f = db.Column(db.Integer(), nullable=False)   # 1 = Currently not advanced       2 = Advanced

    def adding(self):
        self.advance_f = 2
        db.session.commit()

    def changing(self):
        self.advance_f = 1
        db.session.commit()
        
    def __repr__(self):
       return f'Parameters of the teams object id: {self.id} \n group: {self.group} \n Name(qualified_teams): {self.qualified_teams} \n owner: {self.owner} \n advance_f: {self.advance_f}'

db.create_all()
db.session.commit()

