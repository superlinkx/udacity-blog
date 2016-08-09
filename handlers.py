import models
from slugify import slugify
import models
from handler import Handler


# Handlers
class FrontPage(Handler):
    def get(self):
        posts = models.Post.get_five()

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
            u = models.User.by_name(username)
            if u:
                error = "That username already exists. Please choose another."
            else:
                pw_hash = self.generate_secure_hash(password, salt)
                u = models.User.register(username, email, name, salt, pw_hash)
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
            user = models.User.by_name(username)
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
                post = models.Post.get_by_id(int(id))
                if post and post.author == self.username:
                    self.render("editpost.html", signedin=True, id=id,
                                title=post.title, body=post.body)
        else:
            self.redirect("/signin")

    def post(self):
        if self.user:
            id = self.request.get("id")
            if id:
                post = models.Post.get_by_id(int(id))
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
                post = models.Post.get_by_id(int(id))
                if post and post.author == self.username:
                    db.delete(post.key())

            self.redirect("/")

        else:
            self.redirect("/signin")


class ViewPost(Handler):
    def get(self):
        slug = self.request.get("slug")
        post = models.Post.by_slug(slug)

        if post is not None:
            error = None
        else:
            error = "Post not found!"
        self.render("viewpost.html", post=post, error=error)
