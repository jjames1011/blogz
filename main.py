from flask import Flask, request, redirect, render_template, session, flash
import cgi
from app import app, db
from models import Blog #,User
#from hashutils import make_pw_hash, check_pw_hash

app.secret_key = 'y337kGcys&zP3B'


@app.route('/')
def index():
    return redirect('/blog')



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


        blogpost = Blog(title, body)
        db.session.add(blogpost)
        db.session.commit()
        single_post = Blog.query.filter_by(title=blogpost.title).first()




        return render_template('singlepost.html',single_post=single_post)



    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()
