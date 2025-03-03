from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager  # Import login_manager from app
from models import User, Post, Comment
from forms import RegistrationForm, LoginForm, PostForm, CommentForm
from werkzeug.security import generate_password_hash, check_password_hash

# Remove the following lines (they are now in app.py):
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page – list posts and search
@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('q')
    if search_query:
        posts = Post.query.filter(Post.title.contains(search_query) | Post.content.contains(search_query)).order_by(Post.timestamp.desc()).all()
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Create a new post
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            tags=form.tags.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully.')
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form)

# Post detail with comments
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.')
        return redirect(url_for('post_detail', post_id=post_id))
    return render_template('post_detail.html', post=post, form=form)

# API endpoint to like a post
@app.route('/api/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

# (Optional) API endpoint to fetch posts (for frontend AJAX use)
@app.route('/api/posts', methods=['GET'])
def api_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_data = [{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'likes': post.likes,
        'tags': post.tags,
        'timestamp': post.timestamp.isoformat()
    } for post in posts]
    return jsonify(posts_data)