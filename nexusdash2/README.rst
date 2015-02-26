=========
NexusDash
=========

Program
=======
Nexus Dash

- A Django based monitoring web dashboard for Nexus machines. Simply drop-in the app and go!
(from https://github.com/datacenter/nexus9000 but modified to make it works)

Features
========

- A beautiful web-based dashboard for monitoring Nexus info

- Interactive graphs showing historical data of Nexus

- Live, on-demand monitoring of RAM, CPU, Load, Uptime, Disk Allocation, Interface Throughput and many more system stats

- Make your own Django App Plugin and easily add to this website
  
- Cross platform application (Windows and Unix supported)

- Uses Celery to allow asynchronously polling devices


Installation (Unix)
===================

Make sure to first install necessary libraries: :code:`sudo apt-get install python python-dev libatlas-base-dev gcc gfortran g++` (thanks to Shameer Ali)

1) Install Dependencies using Conda
-----------------------------------

Follow these CLI commands to install all dependencies::

    $ # No need to sudo
    $ cd /tmp/
    $ # Install Miniconda
    $ wget http://repo.continuum.io/miniconda/Miniconda-3.5.5-Linux-x86_64.sh
    $ chmod +x Miniconda-3.5.5-Linux-x86_64.sh
    $ ./Miniconda-3.5.5-Linux-x86_64.sh
    $ 
    $ # Create a Python env
    $ conda create --name nexusdash python
    $ source activate nexusdash
    $ conda install pip
    $ 
    $ # Download ./requirements.txt from source
    $ ## Use following args for pip if server doesn't allow SSL: --index-url http://pypi.gocept.com/simple/ --allow-all-external --timeout 60
    $ pip install -r requirements.txt


If some packages are not installed via :code:`pip install -r ./requirements.txt`, please try :code:`conda install <package>`

2) Start the Django Server
--------------------------

Follow these CLI commands to run the Django Server::

    $ source activate nexusdash
    $ # Key can be any string
    $ export SECRET_KEY=asdaduy7683ybhby
    $ 
    $ # Set Django Setting, to run in production env, use nexusdash.settings.production
    $ export DJANGO_SETTINGS_MODULE=nexusdash.settings.local
    $ 
    $ # Sync Database and create root admin account
    $ python manage.py syncdb
    $
    $ # If you have a message that says tables are not synced and need to be migrate execute theses following commands 
    $ # (because of a bug, you need to make a fake migrate before the real migrate)
    $ # For example for celery: python manage.py migrate djcelery 0001 --fake
    $ # python manage.py migrate djcelery
    $
    $
    $ 
    $ # To run in Development env
    $ python manage.py runserver 0.0.0.0:5555 --noreload
    $ 

To run in Production env (DO NOT USE PREVIOUS COMMAND IN PRODUCTION)
Deploying Django with `Apache and mod_wsgi <https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/modwsgi/#how-to-use-django-with-apache-and-mod-wsgi>`_
    
    


3) Start Celery for polling
---------------------------

Follow these CLI commands to start Celery::

    $ source activate nexusdash
    $ # Key can be any string
    $ export SECRET_KEY=asdaduy7683ybhby
    $ 
    $ # Set Django Setting, to run in production env, use nexusdash.settings.production
    $ export DJANGO_SETTINGS_MODULE=nexusdash.settings.local
    $ 
    $ cd /path/to/nexusdash-with-manage.py
    $ 
    $ # Start Periodic polling
    $ celery -A nexusdash beat
    $ 
    $ # Start celery
    $ celery -A nexusdash worker -l info
    $ 
    
In production, you may want to `run celery as a deamon <http://celery.readthedocs.org/en/latest/tutorials/daemonizing.html>`_


    
    
4) Navigate to website
----------------------

Enjoy!!


Installation (Windows)
======================

Similar to Unix installation except the following changes:

- Install Miniconda for Windows from here: http://conda.pydata.org/miniconda.html and follow steps as described in Unix

	- Installing python-nvd3 requires Visual Studio. To install Visual Studio, follow steps from here: http://akbintel.com/mediawiki/index.php/Python/Conda#Installing_Visual_Studio

- Use :code:`set` instead of :code:`export` to set env variable
    


Installation (Mac)
==================

Similar to Unix installation except the following changes:

- Install Miniconda for Mac from here: http://conda.pydata.org/miniconda.html and follow steps as described in Unix

- TODO
    

Settings
========

1) Polling Interval
-------------------

- To change the interval at which the devices get polled periodically, change the variable CELERYBEAT_SCHEDULE in ./nexusdash/settings/base.py

- Default value is every 30 minutes (e.i: '*/30')



Contributing and How to add a new Widget
========================================

Take a look at the app called :code:`foo` and copy-n-modify as per your need

1) Step1
---------

- Create a Django app called :code:`foo`

	- Create a model in :code:`foo.models` called :code:`FooStats` with following attributes:

		- polling_timestamp as FloatField,
		
		- hostname for many-to-one relationship with hostnames.HostNames model,
		
		- other attributes for your need.

	- Create file :code:`foo.admin` to register the model to admin page.

	- Create file :code:`foo.tasks` to add a celery task to poll device. Create function :code:`poll_foostats` that actually polls the device (:code:`utils.fetchcliout.get_foostats`) and updates DB
	
	- Create file and dir :code:`foo\templates\foo\foo.html` which correct div ID and content that you wish to by populated by jQuery call

2) Step2
---------

- Modify :code:`nexusdash.views` starting from :code:`# This is a sample example` line
	
	- This piece of code gets called when user navigates to dash page per device (or user clicks refresh button) that in-turn triggers a jquery call that does a GET request to :code:`http://nexusdash.com/1.1.1.1/dash/query/?module=foostats`)
	
	- What this code does:
	
		- Polls device by calling function :code:`poll_foostats`
		
		- Queries the database with latest polling timestamp and saves it in a dictionary :code:`context`
		
		- This dictionary :code:`context` will be returned as JSON data to the frontend which will be parsed (:code:`$.getJSON(module_url + module) // in nexusdash/static/js/dashboard.common.js`)

3) Step3
--------
		
- Modify :code:`nexusdash/static/js/dashboard.perdevice.js` starting from :code:`dashboard.getFooStats = function () {` line

	- This piece of code gets called when a HTTP GET request is made to :code:`http://nexusdash.com/1.1.1.1/dash/query/?module=foostats`
	
	- What this code does:
	
		- AJAX display of the content. For table, this uses jquery dataTable
		
		- Make sure to update the selectors (e.i :code:`("table-foostats")`)
		
		- Make sure that HTML div id :code:`<div id="widget-foostats"` (in :code:`foo\templates\foo\foo.html`), where :code:`foostats` matches the attr name in :code:`dashboard.fnMap`
		
		- Make sure that module name from URL parameter (e.i foostats in :code:`?module=foostats`) matches attr name in :code:`dashboard.fnMap`
		 