
Dependenceis (to build and run localy):

1) VirtualBox
2) Vagrant

Other Project Dependencies:

* See files under the requirements folder (Note some of the dependencies are private repositories that you will not be able to download)

Authentication

You will want to add your own authenication backend in your settings file:

Ex.

AUTHENTICATION_BACKENDS = (
    'some.path.to.your.auth.backend',
)

How to install and run the application(s):

* install VirtualBox for your OS (https://www.virtualbox.org/)
* install Vagrant for your OS (http://www.vagrantup.com/)
* checkout the code from git

	git clone git@github.com:Harvard-University-iCommons/icommons_ext_tools.git

* cd into the project directory

	cd icommons_ext_tools
   
* run vagrant up from the command line:
	
	$vagrant up
    
* setup an ssh key to use to login to the vagrant instance:
	
	Ex: on OSX I type
	$ssh-add ~/.ssh/id_rsa

	You can verfiy the key was added like this:

	$ssh-add -L

* ssh into the vagrant machine:

	$vagrant ssh

* The vagrant process created a virtual environment for you, and should automatically place you in the
  correct directory with the virtual environment activated. Now you just need to get the application dependencies using pip.
  
  $pip install -r requirements/local.txt


