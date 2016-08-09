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
    def key_by_slug(cls, slug):
        return Post.all(keys_only=True).filter('slug = ', slug).get()

    @classmethod
    def get_all(cls):
        return Post.all()

    @classmethod
    def get_five(cls):
        return Post.all().fetch(limit=5)

    @classmethod
    def create(cls, slug, title, body, author):
        if Post.key_by_slug(slug):
            return False
        else:
            return Post(
                        slug=slug,
                        title=title,
                        body=body,
                        author=author
                        )


class Comment(db.Model):
    body = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_all(cls, post):
        return Comment.all().ancestor(Post.key_by_slug(post))

    @classmethod
    def create(cls, body, author, post):
        parent = Post.key_by_slug(post)
        return Comment(parent=parent,
                       body=body,
                       author=author,
                       )


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
        if User.by_name(username):
            return False
        else:
            return User(
                        username=username,
                        name=name,
                        salt=salt,
                        pw_hash=pw_hash,
                        email=email
                        )
