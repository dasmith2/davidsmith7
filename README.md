# Setting up a new website

This is my starting point for new Django projects on Heroku

Now, Github doesn't allow you to fork your own repositories so easily. So to
create a new project forked from this project, first create a new EMPTY
repository on Github, so make sure you DON'T check "Initialize this repository
with a README". Then clone your new repository locally and cd into it. Next,
add an upstream remote to this repository like so

    git clone git@github.com:dasmith2/my-new-repo.git
    cd my-new-repo
    git remote add upstream git@github.com:dasmith2/davebase.git
    git pull upstream master  # Any time you want to pull from davebase
    git push  # Any time you want to push to my-new-repo

You'll need to make some changes.

1. Update the name, description, and repository in app.json
1. Create a main/local_settings.py file

You'll need to set up a database.

    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    # OK, I admit I'm a bit hazy on the details of users in Postgres. I think
    # by default it tries to use a database user with the same username as the
    # Linux user, so in my case, it made sense to create a database user named
    # dave and grant it permission on everything and use it to create the
    # databases.

Then go create a main/local_settings.py file and put something like this in it

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'davebase',
            'USER': 'dave',
            'PASSWORD': 'asdf1234',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

## Heroku

    heroku apps:create whatever-stage
    heroku addons:create heroku-postgresql:hobby-dev -a whatever-stage
    # Now go to heroku.com and set this app up to automatically deploy from
    # github. At first though, you'll have to manually deploy. There's a button
    # for that somewhere. Then you can...
    heroku run python manage.py createsuperuser -a whatever-stage

# Developing libraries

The libraries will ideally stabilize and just sit on PyPI. But while I'm still
actively developing them I don't want to push to PyPI as part of local
development. So for now I'm removing djaveS3, say, from requirements.txt and
simply checking the djaveS3 source directly into my projects thusly:

    cd davidsmith7
    mkdir djaveS3
    sudo mount --bind ../djaveS3/djaveS3 djaveS3

Then when everything stabilizes, you deploy djaveS3 to PyPI, add djaveS3 to
requirements.txt, and

    umount djaveS3

I found out about this technique from

https://stackoverflow.com/questions/86402/how-can-i-get-git-to-follow-symlinks

# CSS, Javascript, and Django templates

## How NOT to do it

I've been on so many projects where there's, like, a single monstrous CSS file
and a single monstrous Javascript file. So now any time you want to change
anything, you have to paw through thousands of lines of CSS. There's very
little hope of ever figuring out which styles are no longer necessary and
removing them. The styles become unmaintainable over time.

I think this tended to happen because back when bandwidth was a concern we used
to think it was important to separate CSS and Javascript into their own files
so they could get cached.

Then they tended to end up in a single monolith file because that's the obvious
way to guarantee what order the Javascript and CSS run in. Javascript that's
in, like, <script src="whatever.js"></script> tags is a bit complicated. When
Javascript in these script tags runs depends on whether the script tag is in
the HEAD or in the BODY, and it depends on the order that the Javascript files
arrive at the client.

## A simple system for organizing

Some ideas apply to all sites. Some ideas apply only to the specific site
you're on. Some ideas apply only to a particular section of the site, some
ideas apply only to a specific page, and some ideas apply only to a specific
widget. For each level of idea, there is an appropriate place to put your CSS,
Javascript, and templates.

I use Django template inheritance to describe the hierarchy.

### All sites

djaveForm.fields renders problems like <div style="problem">This field is
required</div>. It's most helpful to just color all "problem" text red by
default. So .problem { color: #f00; } belongs in
main/templates/css/all_sites.css, which gets copied around to all the
websites.

I like to start with margins and padding 0, and add them back in again as
necessary. When it comes to vertical spacing, by convention, I use margin-top.
This is like saying, "Everybody drive on the left hand side of the road." It
doesn't matter which side of the road everybody drives on as long as it's the
same side of the road. So anyway, this top-margins-only approach gets set up in
all_sites.css too.

main/templates/all_sites.html is for HTML that applies to all sites. It
includes 4 libraries: jQuery, Handlebars for Javascript templates, Roboto which
is a nice font from Google, and last but not least, all_sites.js which includes
global utility kinds of things such as helper functions for ajax that go well
with tables.

### Specific site

Now, davebase does provide this_site.css, but it's empty. This file is
meant to be overwritten by the specific sites. The reason davebase provides
this_site.css is so that this_site.html can come pre-loaded with the
correct css link. Obviously you can modify this_site.html to your heart's
content as well.

this_site.html inherits from all_sites.html

### Specific section on a site

You'll create my_specific_section.html which inherits from this_site.html
You'll probably do this for Django Apps. Section specific navigation is an
example.

### Only a single page

If it only applies to a specific page, then only put it on that page.
my_specific_page.html should inherit from my_specific_section.html

### A widget

If the css is specifically for a particular widget, just inline the styles
immediately above the widget in the template for the widget.
