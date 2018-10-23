from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:archana@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_post = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title_arg,blog_post_arg,owner):
        self.title = title_arg
        self.blog_post = blog_post_arg
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique = True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/login',methods=['POST','GET'])
def login():
    error_msg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif existing_user and existing_user.password != password:
            error_msg = "Password is incorrect"
            flash(error_msg,'error')
            return redirect('/login')
        elif not existing_user:
            error_msg = "Username does not exist."
            flash(error_msg,'error')
            return redirect('/login')

    return render_template('login.html')


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypwd = request.form['verify']
        error = validate_signup(username,password,verifypwd)
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and not error:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        elif existing_user:
            flash("Username already exists.","error")

    return render_template('signup.html')


def validate_signup(username,password,verifypwd):
   
    error_msg = ""
    if not username.strip() or not password.strip() or not verifypwd.strip():    
        error_msg = "one or more fields are blank."
        flash(error_msg,'error')    
    elif password != verifypwd:
        error_msg = "Passwords do not match."
        flash(error_msg,'error')
    elif len(username)<3 :
        error_msg = "Invalid username"
        flash(error_msg,'error')
    elif len(password)<3 :
        error_msg = "Invalid password"
        flash(error_msg,'error')
    return error_msg



@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/')


@app.route('/')
def homepage():
    return redirect('/blog')
    
@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.args.get('id') is not None:
        id_value = int(request.args.get('id'))
        singleblog = Blog.query.filter_by(id = id_value).one()
        return render_template('singleblog.html',title="Build-a-blog",eachblog=singleblog)
    else:
        blog_list = Blog.query.all()
        return render_template('blogs.html',title="Build-a-blog", blogs = blog_list)

@app.route('/newpost')
def new_post():
    return render_template('newpost.html',title="Build-a-blog")

@app.route('/newpost',methods=['POST'])
def submitform():
    title_name_form = request.form['form-title']
    error_titlename = validatetitlename(title_name_form)

    blog_post_form = request.form['form-blog']
    error_blogpost = validateblogpost(blog_post_form)

    if len(error_titlename) == 0 and len(error_blogpost)== 0:
        new_blog = Blog(title_name_form,blog_post_form)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id={0}'.format(new_blog.id))
    else:
        return render_template('newpost.html',title="Build-a-blog!",
            title_error=error_titlename,blog_error=error_blogpost,
            title_namefield=title_name_form,blog_postfield=blog_post_form)

def validatetitlename(title_name_form):
    if len (title_name_form ) == 0:
        return "Title cannot be Empty!"
    elif len(title_name_form)>120:
        return "Title cannot be longer than 120 characters!"
    else:
        return ""

def validateblogpost(blog_post_form):
    if len (blog_post_form ) == 0:
        return "Blog cannot be Empty!"
    elif len(blog_post_form)>500:
        return "Blog cannot be longer than 500 characters!"
    else:
        return ""




#@app.route('/delete-task', methods=['POST'])
#def delete_task():

#    task_id = int(request.form['task-id'])
#    task = Task.query.get(task_id)
#   task.completed = True
#  db.session.add(task)
#   db.session.commit()

#   return redirect('/')


if __name__ == '__main__':
    app.run()