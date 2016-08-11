import webapp2
import handlers

# App config
app = webapp2.WSGIApplication()
app.router.add((r'/', handlers.FrontPage))
app.router.add((r'/signup', handlers.SignUp))
app.router.add((r'/signin', handlers.SignIn))
app.router.add((r'/logout', handlers.Logout))
app.router.add((r'/post/create', handlers.NewPost))
app.router.add((r'/post/edit/(.*)', handlers.EditPost))
app.router.add((r'/post/delete/(.*)', handlers.DeletePost))
app.router.add((r'/post/like/(.*)', handlers.LikePost))
app.router.add((r'/post/view/(.*)', handlers.ViewPost))
app.router.add((r'/comment/create', handlers.CreateComment))
app.router.add((r'/comment/edit/(.*)/([0-9]+)', handlers.EditComment))
app.router.add((r'/comment/delete(.*)/([0-9]+)', handlers.DeleteComment))
