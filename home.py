import os
import jinja2
import webapp2

#Set up jinja to use the template directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

#Helper functions from the intro to backend course
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class FrontPage(Handler):
	def get(self):
		self.render("frontpage.html", name=self.request.get("name"))

class SignUp(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

class SignIn(Handler):
	def get(self):
		self.render("signin.html")
	def post(self):
		username = self.request.POST.get('username')
		password = self.request.POST.get('password')
		setcookie = self.request.POST.get('setcookie')
		
		self.render("signin.html", username=username, password=password, setcookie=setcookie
		)

class Logout(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

class NewPost(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

class EditPost(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

class DeletePost(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

class ViewPost(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

class Dashboard(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello, webapp world!')

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
