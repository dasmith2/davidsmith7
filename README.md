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
1. You can delete the example app entirely

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

# CSS, Javascript, and Django templates

OK, so some ideas apply to all sites. Some ideas apply only to the specific site you're on. Some ideas apply only to a particular section of the site, and some ideas apply only to a specific page. For each level of idea, there is an appropriate place to put your CSS, Javascript, and tempplates.

## All sites

Some styles apply to all websites. For instance, djaveForm.fields render
problems like <div style="problem">This field is required</div>. It's most
helpful to just color all "problem" text red by default. so .problem { color:
#f00; } belongs in main/templates/main_css.html, which gets copied around to
all the websites. main_css.html should stay pretty small.

I like to start with margins and padding 0, and add them back in again as
necessary. When it comes to vertical spacing, by convention, I use margin-top.
This is like saying, "Everybody drive on the left hand side of the road." It
doesn't matter which side of the road everybody drives on as long as it's the
same side of the road. So anyway, this top-margins-only approach gets set up in
main_css.html too.

main/templates/main.html is for HTML that applies to all sites. As you can
imagine, this too should be kept small. It includes 3 libraries: jQuery,
Handlebars for Javascript templates, and Roboto, a nice font from Google.

## Specific site

Now, davebase does provide this_site_css.html, but it's empty. This file is meant to be overwritten by the specific sites. The reason davebase provides this_site_css.html is so that this_site.html can come pre-loaded with the correct css link.

## Specific section on a site

## Only a single page
