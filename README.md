# Stakeholder Mapping Tool

The stakeholder mapping tool guides you through a series of steps to identify potential collaborators to begin to experiment with. It suggests ways to both leverage your existing networks and to craft new relationships.

## Installation

The mapper is built on top of [Django](https://djangoproject.com) web framework and requires [Python 3](https://www.python.org/). 

Easiest way to install the mapper is to clone it using `git`:

```
$ git clone git@github.com:onurmatik/oep.git  
```

And installing the requirements via `pip` into a `virtual environment`. 

```
$ cd oep/  
$ python3 -m venv env  
$ . env/bin/activate  
(env) $ pip3 install -r requirements.txt
```

Create the database and initialize with data.

```
$ python manage.py migrate
$ python manage.py loaddata mapper.json
```

Run the Django development server.

```
$ python manage.py runserver
```

Visit the local application page: [http://localhost:8000/mapper/](http://localhost:8000/mapper/)
