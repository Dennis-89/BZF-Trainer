# BZF-Trainer
To learn the exam questions and calculate the heading

Let's go:
You just have to install Flask:

https://pypi.org/project/Flask/

https://flask.palletsprojects.com/en/2.2.x/

After installed Flask, you can create a local test-server by tipping "flask run" and browsering the BZF-Trainer.
For that just open your Browser and open die URL 

```
localhost:5000
``` 

and have fun.

For using under production conditionals you have to install also a server, something like "gunicorn".

https://pypi.org/project/gunicorn/

https://docs.gunicorn.org/en/stable/install.html

Start "gunicorn" like this:

```
gunicorn --bind <SERVER-IP> <path>.<to>.Question_Trainer.app:app
```

For example:

```
gunicorn --bind 198.160.0.35:5000 home.user.Question_Trainer.app:app
```

You can visit the BZF-Trainer in the browser by entering this URL:
```
http://<SERVER-IP>:5000
```

Have fun!
