# puppet manifest

# Make sure the correct directories are in the path:
Exec {
    path => [
    '/usr/local/sbin',
    '/usr/local/bin',
    '/usr/sbin',
    '/usr/bin',
    '/sbin',
    '/bin',
    ],
    logoutput => true,
}

# Refresh the catalog of repositories from which packages can be installed:
exec {'apt-get-update':
    command => 'apt-get update'
}

# make sure we have some basic tools and libraries available

package {'redis-server':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libxslt1-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'build-essential':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'python-dev':
    ensure => installed,
    require => Exec['apt-get-update']
}

package {'python-pip':
    ensure => installed,
    require => Package['python-dev']
}

package {'libaio1':
    ensure => installed,
    require => Exec['apt-get-update']
}

package {'libaio-dev':
    ensure => installed,
    require => Exec['apt-get-update']
}

package {'git':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'unzip':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'curl':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'wget':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libcurl4-openssl-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'openssl':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'zlib1g-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'libsqlite3-dev':
    ensure => latest,
    require => Exec['apt-get-update'],
}

package {'sqlite3':
    ensure => latest,
    require => Exec['apt-get-update'],
}

# Install virtualenv and virtualenvwrapper - depends on pip

package {'virtualenv':
    ensure => latest,
    provider => 'pip',
    require => [ Package['python-pip'], ],
}

package {'virtualenvwrapper':
    ensure => latest,
    provider => 'pip',
    require => [ Package['python-pip'], ],
}

# make sure that virtualenvwrapper is active
file {'/etc/profile.d/venvwrapper.sh':
    ensure => file,
    content => 'source `which virtualenvwrapper.sh`',
    mode => '755',
    require => Package['virtualenvwrapper'],
}

# Install the Oracle instant client

# This is a helper function to retrieve files from URLs:
define download ($uri, $timeout = 300) {
  exec {
      "download $uri":
          command => "wget -q '$uri' -O $name",
          creates => $name,
          timeout => $timeout,
          require => Package['wget'],
  }
}

# Using the helper function above, download the Oracle instantclient zip files:
download {
  "/tmp/instantclient-basiclite-linux.x64-11.2.0.3.0.zip":
      uri => "https://s3.amazonaws.com/icommons-static/oracle/instantclient-basiclite-linux.x64-11.2.0.3.0.zip",
      timeout => 900;
}

download {
  "/tmp/instantclient-sqlplus-linux.x64-11.2.0.3.0.zip":
      uri => "https://s3.amazonaws.com/icommons-static/oracle/instantclient-sqlplus-linux.x64-11.2.0.3.0.zip",
      timeout => 900;
}

download {
  "/tmp/instantclient-sdk-linux.x64-11.2.0.3.0.zip":
      uri => "https://s3.amazonaws.com/icommons-static/oracle/instantclient-sdk-linux.x64-11.2.0.3.0.zip",
      timeout => 900;
}

# Create the directory where the Oracle instantclient will be installed
file {'/opt/oracle':
    ensure => directory,
}

# Unzip the three Oracle zip files that we downloaded earlier:
exec {'instantclient-basiclite':
    require => [ Download['/tmp/instantclient-basiclite-linux.x64-11.2.0.3.0.zip'], File['/opt/oracle'], Package['unzip'] ],
    cwd => '/opt/oracle',
    command => 'unzip /tmp/instantclient-basiclite-linux.x64-11.2.0.3.0.zip',
    creates => '/opt/oracle/instantclient_11_2/BASIC_LITE_README',
}

exec {'instantclient-sqlplus':
    require => [ Download['/tmp/instantclient-sqlplus-linux.x64-11.2.0.3.0.zip'], File['/opt/oracle'], Package['unzip'] ],
    cwd => '/opt/oracle',
    command => 'unzip /tmp/instantclient-sqlplus-linux.x64-11.2.0.3.0.zip',
    creates => '/opt/oracle/instantclient_11_2/sqlplus',
}

exec {'instantclient-sdk':
    require => [ Download['/tmp/instantclient-sdk-linux.x64-11.2.0.3.0.zip'], File['/opt/oracle'], Package['unzip'] ],
    cwd => '/opt/oracle',
    command => 'unzip /tmp/instantclient-sdk-linux.x64-11.2.0.3.0.zip',
    creates => '/opt/oracle/instantclient_11_2/sdk',
}

# Create some symlinks that are missing:
file {'/opt/oracle/instantclient_11_2/libclntsh.so':
    ensure => link,
    target => 'libclntsh.so.11.1',
    require => Exec['instantclient-basiclite'],
}

file {'/opt/oracle/instantclient_11_2/libocci.so':
    ensure => link,
    target => 'libocci.so.11.1',
    require => Exec['instantclient-basiclite'],
}

# Make sure that the ORACLE_HOME, PATH, and LD_LIBRARY_PATH environment variables are set properly:
file {'/etc/profile.d/oracle.sh':
    ensure => file,
    content => 'export ORACLE_HOME=/opt/oracle/instantclient_11_2; export PATH=$ORACLE_HOME:$PATH; export LD_LIBRARY_PATH=$ORACLE_HOME',
    mode => '755',
    require => Exec['instantclient-basiclite'],
}

# Ensure github.com ssh public key is in the .ssh/known_hosts file so
# pip won't try to prompt on the terminal to accept it
file {'/home/vagrant/.ssh':
    ensure => directory,
    mode => 0700,
}

exec {'known_hosts':
    provider => 'shell',
    user => 'vagrant',
    group => 'vagrant',
    command => 'ssh-keyscan github.com >> /home/vagrant/.ssh/known_hosts',
    unless => 'grep -sq github.com /home/vagrant/.ssh/known_hosts',
    require => [ File['/home/vagrant/.ssh'], ],
}

file {'/home/vagrant/.ssh/known_hosts':
    ensure => file,
    mode => 0744,
    require => [ Exec['known_hosts'], ],
}

# Create a symlink from ~/icommons_ext_tools to /vagrant as a convenience for the developer
file {'/home/vagrant/icommons_ext_tools':
    ensure => link,
    target => '/vagrant',
}

# Create a virtualenv 
exec {'create-virtualenv':
    provider => 'shell',
    user => 'vagrant',
    group => 'vagrant',
    require => [ Package['virtualenvwrapper'], File['/home/vagrant/icommons_ext_tools'], File['/etc/profile.d/oracle.sh'],
		 Exec['known_hosts'], ],
    environment => ["ORACLE_HOME=/opt/oracle/instantclient_11_2", "LD_LIBRARY_PATH=$ORACLE_HOME",
		    "HOME=/home/vagrant", "WORKON_HOME=/home/vagrant/.virtualenvs"],
    command => '/vagrant/vagrant/venv_bootstrap.sh',
    creates => '/home/vagrant/.virtualenvs/icommons_ext_tools',
}

# set the DJANGO_SETTINGS_MODULE environment variable
file_line {'add DJANGO_SETTINGS_MODULE env to postactivate':
    ensure => present,
    line => 'export DJANGO_SETTINGS_MODULE=icommons_ext_tools.settings.local',
    path => '/home/vagrant/.virtualenvs/icommons_ext_tools/bin/postactivate',
    require => Exec['create-virtualenv'],
}

file_line {'add DJANGO_SETTINGS_MODULE env to postdeactivate':
    ensure => present,
    line => 'unset DJANGO_SETTINGS_MODULE',
    path => '/home/vagrant/.virtualenvs/icommons_ext_tools/bin/postdeactivate',
    require => Exec['create-virtualenv'],
}

# change into the project directory and activate the virtual env upon login
file {'/home/vagrant/.bash_profile':
    owner => 'vagrant',
    content => 'cd icommons_ext_tools; workon icommons_ext_tools',
    require => Exec['create-virtualenv'],
}



