# breadboard
An API for the Zwierlein Group

How does it work?
---

Breadboard is a [RESTful Web API](https://en.wikipedia.org/wiki/Representational_state_transfer). In short, it provides a bare-bones web-based interface between a database of experimental parameters, and you. The name 'breadboard' refers to the idea of a configurable platform to build custom devices: you can use breadboard to build your favorite UIs, from websites to analysis tools.

It's powered by the [Django REST framework](https://www.django-rest-framework.org/) and [Postgres](https://www.postgresql.org/). For more information about REST APIs and Django, [click here](https://medium.com/@djstein/modern-django-part-2-rest-apis-apps-and-django-rest-framework-ea0cac5ab104).


Why an API?
---

We typically analyze images. Every experimental run generates parameters and images, while your analysis generates settings, crop regions, and various labels. An API provides a two-way channel for data to be stored and retrieved using the simple and universal language of HTTP and URLs. This allows us to store data without being locked into a language.


What kinds of metadata can we store?
---

Aside from the basic experimental runtime, and imagenames, you can store notes, settings, crop regions, pixel sizes, bad shot labels, datasets, filepaths to image files, and more.


How do I use the API?
---

* If you want to use the API directly, read [the API docs](https://documenter.getpostman.com/view/5261788/RWaHxpKC). This is ideal if you're not using python.
* If you want to use a python client, use [breadboard-python-client](https://github.com/biswaroopmukherjee/breadboard-python-client)
* To write Cicero experimental parameters, use [breadboard-cicero](https://github.com/biswaroopmukherjee/breadboard-cicero).


I don't want to use python. What do I do?
---
I'm still writing documentation for the HTTP endpoints.


How can I host breadboard?
---

This project is currently hosted on google cloud. You can run your own server locally by cloning this repo and running

```sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

The server will run on `localhost:8000` or something similar. Note: you need to connect your own Postgres database in order for this to work. Docs coming soon.
