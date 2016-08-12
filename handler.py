import os
import string
import random
import jinja2
import webapp2
import hashlib
import hmac
import json
import models


# Helper functions from the intro to backend course
class Handler(webapp2.RequestHandler):
    # TODO: Don't leave this in the actual repo.
    #       Should be imported from a non-tracked module
    secret = "a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447"

    # Set up jinja to use the template directory
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(
                    template_dir),
                autoescape=True)

    # Generic method for writing to response
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # Generic method for writing to a specific jinja template
    def render_str(self, template, **params):
        t = self.jinja_env.get_template(template)
        return t.render(params)

    # Generic method for rendering a jinja template to the response body
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # Generic method for rendering JSON into a response
    def render_json(self, data):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(data))

    # Method to generate a random salt (using 10 chars)
    def generate_salt(self):
        return ''.join(random.choice(string.letters) for x in xrange(10))

    # Method to generate a secure hash using a password and a salt
    def generate_secure_hash(self, password, salt):
        return hmac.new(str(salt), str(password), hashlib.sha256).hexdigest()

    # Method for verifying a secure hash by comparing a new password/salt hash
    # to the stored hash
    def check_secure_hash(self, password, salt, dbhash):
        if self.generate_secure_hash(password, salt) == dbhash:
            return True
        else:
            return False

    # Method to create a secure value using the global server secret
    def generate_secure_val(self, val):
        return '%s|%s' % (val, self.generate_secure_hash(val, self.secret))

    # Method to check a secure value's integrity
    def check_secure_val(self, secure_val):
        val = secure_val.split('|')[0]
        if secure_val == self.generate_secure_val(val):
            return val
        else:
            return False

    # Method to set a secure cookie
    def set_secure_cookie(self, name, val):
        cookie_val = self.generate_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    # Method to read in a secure cookie and check its validity
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and self.check_secure_val(cookie_val)

    # Method to render a 404 page
    def error_404(self, errmsg="Page Not Found"):
        self.error(404)
        error = "Not Found"
        self.render("error.html", error=error, errmsg=errmsg, code=404)

    # Method to initialize requests to the server
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user = self.read_secure_cookie('user')
        self.user = user and models.User.by_name(str(user))
        self.username = str(user)
