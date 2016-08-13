# Udacity Blog Project
## A Google App Engine application

This is a blog written on App Engine for my Full Stack nanodegree

### Accessing the demo
An online demo can be seen at (superlinkx-example-blog.appspot.com)[]

### Running a development version
#### Requirements
- Google App Engine SDK for Python [Download and install instructions](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)
- Clone this repository: `git clone https://github.com/superlinkx/udacity-blog`
- Install 3rd-Party components with pip: `pip install -r requirements.txt -t lib`

#### Run a development instance
- Run `dev_appserver.py .` within the source directory
- Go to [http://localhost:8080](http://localhost:8080) in your browser
- Browse the application. Any edits to source files should reload the server automatically.

#### Deploy to an App Engine instance
- Create a new project on cloud.google.com
- Deploy with `appcfg.py -A [YOUR_PROJECT_ID] -V v1 update ./` where `[YOUR_PROJECT_ID]` is the project id for your new project
