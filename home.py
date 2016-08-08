import os
import string
import random
import jinja2
import webapp2
import hashlib
import hmac
from slugify import slugify

from google.appengine.ext import db

# Set up jinja to use the template directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# TODO: Don't leave this in the actual repo.
#       Should be imported from a non-tracked module
secret = "a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447"


# Helper functions from the intro to backend course
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def generate_salt(self):
        return ''.join(random.choice(string.letters) for x in xrange(10))

    def generate_secure_hash(self, password, salt):
        return hmac.new(str(salt), str(password), hashlib.sha256).hexdigest()

    def check_secure_hash(self, password, salt, dbhash):
        if self.generate_secure_hash(password, salt) == dbhash:
            return True
        else:
            return False

    def generate_secure_val(self, val):
        return '%s|%s' % (val, self.generate_secure_hash(val, secret))

    def check_secure_val(self, secure_val):
        val = secure_val.split('|')[0]
        if secure_val == self.generate_secure_val(val):
            return val
        else:
            return False

    def set_secure_cookie(self, name, val):
        cookie_val = self.generate_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and self.check_secure_val(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user = self.read_secure_cookie('user')
        self.user = user and User.by_name(str(user))
        self.username = str(user)


# TODO: Move models to their own file
# Models
class Post(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_slug(cls, slug):
        return Post.all().filter('slug = ', slug).get()

    @classmethod
    def get_five(cls):
        return Post.all().fetch(limit=5)


class Comment(db.Model):
    body = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class User(db.Model):
    username = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    salt = db.StringProperty(required=True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        return User.all().filter('username = ', name).get()

    @classmethod
    def by_email(cls, email):
        return User.all().filter('email = ', email).get()

    @classmethod
    def register(cls, username, email, name, salt, pw_hash):
        return User(username=username,
                    name=name,
                    salt=salt,
                    pw_hash=pw_hash,
                    email=email)


# Handlers
class FrontPage(Handler):
    def get(self):
        posts = Post.get_five()

        if self.user:
            name = self.user.name
            signedin = True
        else:
            name = None
            signedin = False

        self.render("frontpage.html", error=None, signedin=signedin, name=name,
                    posts=posts)


class SignUp(Handler):
    def get(self):
        if self.user:
            self.redirect("/")

        self.render("signup.html", error=None, signedin=False)

    def post(self):
        if self.user:
            signedin = True
            self.redirect("/")

        error = None
        username = self.request.get('username')
        password = self.request.get('password')
        email = self.request.get('email')
        name = self.request.get('name')
        salt = self.generate_salt()

        if username and password and email and name and salt:
            u = User.by_name(username)
            if u:
                error = "That username already exists. Please choose another."
            else:
                pw_hash = self.generate_secure_hash(password, salt)
                u = User.register(username, email, name, salt, pw_hash)
                u.put()
                self.redirect('/')

        error = "Missing required field"
        self.render("signup.html", error=error, signedin=False,
                    username=username, name=name, email=email)


class SignIn(Handler):
    def get(self):
        if self.user:
            self.redirect("/")

        self.render("signin.html")

    def post(self):
        if self.user:
            self.redirect("/")

        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        setcookie = self.request.POST.get('setcookie')

        if username and password:
            user = User.by_name(username)
            if user:
                if self.check_secure_hash(password, user.salt, user.pw_hash):
                    self.set_secure_cookie('user', str(username))
                    self.redirect("/")
                else:
                    error = "Invalid user/password"
                    self.render("signin.html", error=error, signedin=False,
                                username=username, setcookie=setcookie)
            else:
                error = "No user found by that name"
                self.render("signin.html", error=error, signedin=False,
                            username=username, setcookie=setcookie)
        else:
            error = "Missing username/password"
            self.render("signin.html", error=error, signedin=False,
                        username=username, setcookie=setcookie)


class Logout(Handler):
    def post(self):
        self.response.headers.add_header('Set-Cookie', 'user=; Path=/')
        self.redirect("/")


class NewPost(Handler):
    def get(self):
        if self.user:
            self.render("createpost.html", error=None, signedin=True)
        else:
            self.redirect("/signin")

    def post(self):
        if self.user:
            title = self.request.get("title")
            body = self.request.get("body")
            author = self.username

            if title and body and author:
                slug = slugify(title)
                p = Post(slug=slug, title=title, body=body, author=author)
                p.put()

                self.redirect("/")
            else:
                error = "Missing title, body, or author id"
                self.render("createpost.html", error=error, signedin=True,
                            title=title, body=body)
        else:
            self.redirect("/signin")


class EditPost(Handler):
    def get(self):
        if self.user:
            id = self.request.get("id")
            if id:
                post = Post.get_by_id(int(id))
                if post and post.author == self.username:
                    self.render("editpost.html", signedin=True, id=id,
                                title=post.title, body=post.body)
        else:
            self.redirect("/signin")

    def post(self):
        if self.user:
            id = self.request.get("id")
            if id:
                post = Post.get_by_id(int(id))
                if post and post.author == self.username:
                    title = self.request.get("title")
                    body = self.request.get("body")

                    post.title = title
                    post.body = body
                    post.put()

            self.redirect("/")

        else:
            self.redirect("/signin")


class DeletePost(Handler):
    def post(self):
        if self.user:
            id = self.request.get("id")
            if id:
                post = Post.get_by_id(int(id))
                if post and post.author == self.username:
                    db.delete(post.key())

            self.redirect("/")

        else:
            self.redirect("/signin")


class ViewPost(Handler):
    def get(self):
        slug = self.request.get("slug")
        post = Post.by_slug(slug)

        if post is not None:
            error = None
        else:
            error = "Post not found!"
        self.render("viewpost.html", post=post, error=error)

# App config
app = webapp2.WSGIApplication()
app.router.add((r'/', FrontPage))
app.router.add((r'/signup', SignUp))
app.router.add((r'/signin', SignIn))
app.router.add((r'/logout', Logout))
app.router.add((r'/createpost', NewPost))
app.router.add((r'/editpost', EditPost))
app.router.add((r'/deletepost', DeletePost))
app.router.add((r'/viewpost', ViewPost))
