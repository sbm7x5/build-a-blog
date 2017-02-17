
import webapp2
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

#create blog post database
class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    post = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

def get_posts(limit, offset):
    # TODO: query the database for posts, and return them
    blog_posts = db.GqlQuery("""Select * FROM BlogPost ORDER BY created DESC LIMIT """
    +limit+""" OFFSET """ +offset)


class Index(webapp2.RequestHandler):
    def get(self):
        self.redirect("/blog")

class Blog(webapp2.RequestHandler):
    def get(self):
        #pull existing blog posts from database
        blog_posts = db.GqlQuery("""SELECT * FROM BlogPost ORDER BY created DESC
        LIMIT 5""")

        t = jinja_env.get_template("blog.html")
        content = t.render(blog_posts = blog_posts)
        self.response.write(content)

class NewPost(webapp2.RequestHandler):
    def get(self):

        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)

    def post(self):
        title = self.request.get("blog-title")
        post = self.request.get("blog-post")

        if title and post:
            blog = BlogPost(title = title, post = post)
            blog.put()
            blog_id = blog.key().id()
            self.redirect("/blog/%s"% blog_id)
        else:
            error = "You must enter both a title and post content."
            t = jinja_env.get_template("newpost.html")
            content = t.render(error = error)
            self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = BlogPost.get_by_id(int(id))
        title = post.title
        body = post.post

        if not post:
            self.renderError(400)
            return

        t = jinja_env.get_template("singlepost.html")
        content = t.render(title = title, body = body)
        self.response.write(content)

app = webapp2.WSGIApplication([
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/', Index),
    ('/blog', Blog),
    ('/newpost', NewPost)
], debug=True)
