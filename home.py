import webapp2
import handlers

# App config
app = webapp2.WSGIApplication()
app.router.add((r'/', handlers.FrontPage))
app.router.add((r'/signup', handlers.SignUp))
app.router.add((r'/signin', handlers.SignIn))
app.router.add((r'/logout', handlers.Logout))
app.router.add((r'/createpost', handlers.NewPost))
app.router.add((r'/editpost', handlers.EditPost))
app.router.add((r'/deletepost', handlers.DeletePost))
app.router.add((r'/viewpost', handlers.ViewPost))
