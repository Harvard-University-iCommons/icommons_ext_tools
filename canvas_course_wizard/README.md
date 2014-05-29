

Dependencies (to build and run locally):

1) VirtualBox 2) Vagrant

Other Project Dependencies:

    See files under the requirements folder (Note some of the dependencies are private repositories that you will not be able to download)

Authentication

You will want to add your own authenication backend in your settings file:

Ex.

AUTHENTICATION_BACKENDS = ( 'some.path.to.your.auth.backend', )

How to install and run the application(s):

1) install VirtualBox for your OS (https://www.virtualbox.org/) 2) install Vagrant for your OS (http://www.vagrantup.com/) 3) checkout the code from git

git clone git@github.com:Harvard-University-iCommons/icommons_ext_tools.git

4) cd into the project directory

cd icommons_ext_tools

5) run vagrant up from the command line:

$vagrant up

6) setup an ssh key to use to login to the vagrant instance:

Ex: on OSX I type
$ssh-add ~/.ssh/id_rsa

You can verfiy the key was added like this:

$ssh-add -L

7) ssh into the vagrant machine:

$vagrant ssh

    The vagrant process created a virtual environment for you, and should automatically place you in the correct directory with the virtual environment activated. Now you just need to get the application dependencies using pip.

8) $pip install -r requirements/local.txt

Now that the environment is setup you can try running the server:

9) python manage.py runserver 0.0.0.0:8000

### Custom 404 exception handling:

Django will catch 404 exceptions by default and handle them by displaying a project-level 404 page.  They provide a mechanism to customize that page per application.  If you want to handle 404s on a per-view basis though, use the Custom404Mixin class:

```
from canvas_course_wizard.mixins import Custom404Mixin

class SchoolListView(Custom404Mixin, generic.ListView):
    template_name_404 = 'path/to/template.html'
```

The *template_name_404* parameter is required and an ImproperlyConfigured exception will be raised if the template is not defined.  Note, however, that the exception will only be raised at the point where a 404 exception is caught, so you'll want to make sure you verify that parameter is present during the testing phase for your application.
