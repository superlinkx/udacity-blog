import os
import string
import random
import jinja2
import webapp2
import hashlib
import hmac

from google.appengine.ext import db

#Set up jinja to use the template directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
#TODO: Don't leave this in the actual repo. Should be imported from a non-tracked module
secret = "a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447"

#Helper functions from the intro to backend course
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
		self.user = user and User.get_by_key_name(str(user))
		self.username = str(user)

#TODO: Move models to their own file
#Models
class Post(db.Model):
	title = db.StringProperty(required = True)
	body = db.TextProperty(required = True)
	author = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class User(db.Model):
	name = db.StringProperty(required = True)
	email = db.EmailProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	salt = db.StringProperty(required = True)

#Handlers
class FrontPage(Handler):
	def get(self):
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")

		if self.user:
			name = self.user.name
		else:
			name = None

		self.render("frontpage.html", name = name, posts = posts)

class SignUp(Handler):
	def get(self):
		self.render("signup.html")

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		email = self.request.get('email')
		name = self.request.get('name')
		salt = self.generate_salt()

		if username and password and email and name and salt:
			pw_hash = self.generate_secure_hash(password, salt)
			u = User(key_name = username, pw_hash = pw_hash, email = email, name = name, salt = salt)
			u.put()
			self.redirect('/')

		else:
			error = "Missing required field"
			self.render("signup.html", error = error, username = username, name = name, email = email)

class SignIn(Handler):
	def get(self):
		self.render("signin.html")

	def post(self):
		username = self.request.POST.get('username')
		password = self.request.POST.get('password')
		setcookie = self.request.POST.get('setcookie')

		if username and password:
			user = User.get_by_key_name(username)
			if user:
				if self.check_secure_hash(password, user.salt, user.pw_hash):
					self.set_secure_cookie('user', str(username))
					self.redirect("/")
				else:
					error = "Invalid user/password"
					self.render("signin.html", error = error, username = username, setcookie = setcookie)
			else:
				error = "No user found by that name"
				self.render("signin.html", error = error, username = username, setcookie = setcookie)
		else:
			error = "Missing username/password"
			self.render("signin.html", error = error, username = username, setcookie = setcookie)

class Logout(Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'user=; Path=/')
		self.redirect("/")

class NewPost(Handler):
	def get(self):
		if self.user:
			self.render("createpost.html")
		else:
			self.redirect("/signin")

	def post(self):
		if self.user:
			title = self.request.get("title")
			body = self.request.get("body")
			author = self.username

			if title and body and author:
				p = Post(title = title, body = body, author = author)
				p.put()

				self.redirect("/")
			else:
				error = "Missing title, body, or author id"
				self.render("createpost.html", error = error, title = title, body = body)
		else:
			self.redirect("/signin")

class EditPost(Handler):
	def get(self):
		if self.user:
		 	id = self.request.get("id")
			if id:
				post = Post.get_by_id(int(id))
				if post and post.author == self.username:
					self.render("editpost.html", id = id, title = post.title, body = post.body)
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
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

class Dashboard(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

#App config
app = webapp2.WSGIApplication()
app.router.add((r'/', FrontPage))
app.router.add((r'/signup', SignUp))
app.router.add((r'/signin', SignIn))
app.router.add((r'/logout', Logout))
app.router.add((r'/create', NewPost))
app.router.add((r'/edit', EditPost))
app.router.add((r'/delete', DeletePost))
app.router.add((r'/view', ViewPost))
app.router.add((r'/dashboard', Dashboard))
