from flask import Flask, request, redirect, render_template, session, flash
import cgi
from app import app, db
from models import Blog, User
from hashutils import make_pw_hash, check_pw_hash

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


@app.route('/')
def index():
    return redirect('/blog')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash(email + ', is not a valid email')
            return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()

        if email_db_count > 0:
            flash(email + 'already has an existing account')
            return redirect('/signup')
        if password != verify:
            flash('oops! it looks like your passwords did not match!')
            return redirect('/signup')
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
        if users.count() == 1:
            user = users.first()
            if check_pw_hash(password, user.pw_hash):
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect('/newpost')
        flash('bad username or password')
        return redirect('/login')

@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['user']
    return redirect('/')


@app.route('/blog')
def blog():

    blog_posts = Blog.query.all()
    if request.args.get('id'):
        post_id = request.args.get('id')
        #post_id = int(post_id)
        print(post_id)
        single_post = Blog.query.filter_by(id=post_id).first()
        print(single_post.title)


        return render_template('singlepost.html',single_post=single_post)

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
