from flask import Flask,request,redirect,url_for,render_template,flash
from flask_sqlalchemy import SQLAlchemy
from os import path
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from flask_login import login_user,logout_user,current_user,login_required
from flask_login import LoginManager
from PIL import Image
import os
import glob
db=SQLAlchemy()
DB_NAME='web_app'
app=Flask(__name__)
app.config['SECRET_KEY']='heythisisasecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']=f'mysql://root:root@localhost/{DB_NAME}'
db.init_app(app)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=True)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    notes=db.relationship('Notes')
class Notes(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    notes=db.Column(db.Text(5000000))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
class Posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    posts=db.Column(db.String(500))


def create(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('created database')
create(app)
login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html',user=current_user)
@app.route('/posts',methods=['POST','GET'])
def posts():
    if request.method=='POST':
        posts=request.form.get('title')
        new_posts=Posts(posts=posts)
        db.session.add(new_posts)
        db.session.commit()
    return render_template('posts.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        user=User.query.filter_by(email=email).first()
        if user:
            flash('Mail id already exists!',category='error')
        elif len(email)<4:
            flash('Mail id is too short!',category='error')
        elif len(name)<2:
            flash('Username is too short!',category='error')
        elif len(password1)<5:
            flash('Your password is too short!',category='error')
        elif password1!=password2:
            flash('Password don\'t match!',category='error')
        else:
            new_user=User(name=name,email=email,password=generate_password_hash(password1,method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user,remember=False)
            flash('Account created!',category='success')
            return redirect(url_for('home'))
    return render_template('register.html',title='register page',user=current_user)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password1')
        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user,remember=False)
                flash('Logged in sucessfully!',category='success')
                return redirect(url_for('home'))
            else:
                flash('Invalid password!',category='error')
        else:
            flash('Invalid mailid!',category='error')
    return render_template('login.html',title='login page',user=current_user)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/notes',methods=['POST','GET'])
def notes():
    if request.method=='POST':
        notes=request.form.get('notes')
        new_notes = Notes(notes=notes,user_id=current_user.id)
        db.session.add(new_notes)
        db.session.commit()
        flash('Note added successfully',category='success')
    return render_template('notes.html',title='notes',user=current_user)
@app.route('/delete/<int:id>',methods=['GET','POST'])
def delete(id):
    if request.method=='POST':
        delete_notes=Notes.query.get(id)
        db.session.delete(delete_notes)
        db.session.commit()
        return redirect(url_for('notes'))
    else:
        return redirect(url_for('notes'))
@app.route('/gallery')
def gallery():
    named= os.path.dirname(__file__)
    folder = os.path.join(named, "static//images")
    return render_template('gallery.html',path=os.listdir(folder),user=current_user)

@app.route('/cgpa',methods=['GET','POST'])
def cgpa():
    return render_template('calculator.html')
if __name__=='__main__':
    app.run(debug=True)
    