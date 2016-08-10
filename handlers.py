import models
import time
from slugify import slugify
from handler import Handler


# Handlers
class FrontPage(Handler):
    def get(self):
        posts = models.Post.get_all()

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
            pw_hash = self.generate_secure_hash(password, salt)
            u = models.User.register(username, email, name, salt, pw_hash)
            if u is False:
                error = "That username already exists. Please choose another."
            else:
                u.put()
                self.set_secure_cookie('user', str(username))
                time.sleep(0.1)  # Hack to fix inconsistency
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
        error = None
        if self.user:
            title = self.request.get("title")
            body = self.request.get("body")
            author = self.username

            if title and body and author:
                slug = slugify(title)
                p = models.Post.create(slug=slug, title=title,
                                       body=body, author=author)
                if p is False:
                    error = "Title already used. Try a different one."
                else:
                    p.put()
                    time.sleep(0.1)  # Fix for eventual consistency
                    self.redirect("/")
            else:
                error = "Missing title, body, or author id"
        else:
            self.redirect("/signin")

        self.render("createpost.html", error=error, signedin=True,
                    title=title, body=body)


class EditPost(Handler):
    def get(self, slug):
        if self.user:
            if slug:
                post = models.Post.by_slug(slug)
                if post and post.author == self.username:
                    self.render("editpost.html", slug=slug,
                                title=post.title, body=post.body)
                    return
                else:
                    self.render("editpost.html", slug=slug,
                                title=post.title, body=post.body)
                    return
            self.redirect(self.request.referrer or "/")

        self.redirect("/signin")

    def post(self, slug):
        if self.user:
            if slug:
                title = self.request.get("title")
                body = self.request.get("body")
                if title and body:
                    post = models.Post.edit(slug=slug, title=title, body=body,
                                            user=self.username)
                    if post is False:
                        self.render("editpost.html", slug=slug,
                                    title=post.title, body=post.body)
                        return

                self.redirect("viewpost/"+slug)

            self.redirect("/")

        else:
            self.redirect("/signin")


class DeletePost(Handler):
    def post(self, slug):
        if self.user:
            if slug:
                post = models.Post.delete(slug=slug, user=self.username)
                if post is False:
                    self.redirect(self.request.referrer or "/")
                self.redirect("/")
            else:
                self.redirect(self.request.referrer or "/")

        else:
            self.redirect("/signin")


class ViewPost(Handler):
    def get(self, slug):
        post = models.Post.by_slug(slug)

        if post is not None:
            error = None
            comments = models.Comment.get_all(slug)
            self.render("viewpost.html", slug=slug, error=error, post=post,
                        comments=comments, currentuser=self.username)
        else:
            self.error_404()


class CreateComment(Handler):
    def post(self):
        if self.user:
            body = self.request.get("comment")
            post = self.request.get("post-id")
            author = self.username

            if body and author and post:
                comment = models.Comment.create(author=author, body=body,
                                                post=post)
                comment.put()
                time.sleep(0.1)  # Fix for eventual consistency
                self.redirect(self.request.referrer or "/")
            else:
                self.redirect(self.request.referrer or "/")
        else:
            self.redirect("/signin")


class EditComment(Handler):
    def get(self, slug, cid):
        cid = int(cid)
        if self.user:
            if cid and slug:
                parent_key = models.Post.key_by_slug(slug)
                comment = models.Comment.by_id(cid=cid, parent=parent_key)
                if self.username == comment.author:
                    self.render("editcomment.html", cid=cid, slug=slug,
                                body=comment.body, error=None)
                    return
            self.redirect(self.request.referrer or "/")
        self.redirect("/signin")

    def post(self, slug, cid):
        cid = int(cid)
        if self.user:
            body = self.request.get("body")

            if body and cid and slug:
                print(slug)
                parent_key = models.Post.key_by_slug(slug)
                comment = models.Comment.update(cid=cid, body=body,
                                                user=self.username,
                                                parent=parent_key)
                if comment is False:
                    self.redirect(self.request.referrer or "/")
                else:
                    time.sleep(0.1)  # Fix for eventual consistency
                    self.redirect("/viewpost/"+slug or "/")
            else:
                self.redirect(self.request.referrer or "/")
        else:
            self.redirect("/signin")


class DeleteComment(Handler):
    def post(self, slug, cid):
        cid = int(cid)
        if self.user:
            if cid and slug:
                parent_key = models.Post.key_by_slug(slug)
                comment = models.Comment.delete(cid=cid,
                                                user=self.username,
                                                parent=parent_key)
                if comment is False:
                    self.redirect(self.request.referrer or "/")
                else:
                    time.sleep(0.1)  # Fix for eventual consistency
                    self.redirect(self.request.referrer or "/")
            else:
                self.redirect(self.request.referrer or "/")
        else:
            self.redirect("/signin")
