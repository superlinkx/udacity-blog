from google.appengine.ext import db


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
