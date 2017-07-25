from flask import Flask, request, redirect, render_template, session, flash
import cgi
from app import app, db
from models import Blog, User
from hashutils import make_pw_hash, check_pw_hash
from sqlalchemy import desc

app.secret_key = 'y337kGcys&zP3B'


def logged_in_user():
    owner = User.query.filter_by(email=session['user']).first()
    return owner

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.before_request
def require_login():
    endpoints_without_login = ['blog','login','signup', 'index']
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect('login')
@app.route('/')
def index():
    list_users = User.query.all()


    return render_template('index.html', list_users=list_users)

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if email == '':
            flash('Please fill out the email form.')
            return render_template('signup.html')
        if len(email)<3:
            flash('hmm, your email seems to be too short. ')
            return render_template('signup.html')
        if len(password)<3:
            flash('hmm, your password seems to be too short. Passwords must be longer than 3 characters.')
            return render_template('signup.html', email=email)

        if password == '':
            flash('Please fill out the password form.')
            return render_template('signup.html', email=email)
        if verify == '':
            flash('Please verify your password.')
            return render_template('signup.html', email=email)
        #email errors
        if not is_email(email):
            flash(email + ', is not a valid email')
            return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()

        if email_db_count > 0:
            flash(email + 'already has an existing account')
            return redirect('/signup')
        if password != verify:
            flash('oops! it looks like your passwords did not match!')
            return render_template('signup.html', email=email)
        user = User(email,password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        flash('Welcome, '+ email)
        return redirect('/newpost')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if not is_email(email):
            flash('Please enter a valid email')
            return render_template('login.html',email=email)
        if users.count() == 1:
            user = users.first()
        else:
            flash(email + ' does not have an account. Feel free to create one by clicking the link below!')
            return render_template('login.html',email=email)
        if check_pw_hash(password, user.pw_hash):
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect('/newpost')
        elif password == '':
            flash('Please enter a password.')
            return render_template('login.html',email=email)
        elif not check_pw_hash(password,user.pw_hash):
            flash('opps, it looks like you have provided a wrong password. Please try again.')
            return render_template('login.html', email=email)
    return render_template('login.html', email=email)

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')


@app.route('/blog')
def blog():

    blog_posts = Blog.query.order_by(desc(Blog.id)).all()
    # if there is a query parameter
    if request.args.get('id'):
        post_id = request.args.get('id')
        single_post = Blog.query.filter_by(id=post_id).first()
        return render_template('singlepost.html',single_post=single_post)
    if request.args.get('user_id'):
        user_id = request.args.get('user_id')
        user_posts = Blog.query.filter_by(owner_id=user_id).all()
        user = User.query.filter_by(id=user_id).first()
        if len(user_posts) == 0:
            flash(user.email + ' has not posted anything yet! :(')
        return render_template('singleuser.html', user_id=user_id,user=user)
    return render_template('blog.html', blog_posts=blog_posts)

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        #if fields are not filled out
        if not title:
            flash('Please fill out the title')
            return render_template('newpost.html',title=title,body=body)
        if not body:
            flash('Please fill out the body')
            return render_template('newpost.html',title=title,body=body)
#note that I haven't implemented a log in route handler yet so there is no session thus logged_in_user function will break
        blogpost = Blog(title, body, logged_in_user())
        db.session.add(blogpost)
        db.session.commit()
        single_post = Blog.query.filter_by(title=blogpost.title).first()
        return render_template('singlepost.html',single_post=single_post)
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
