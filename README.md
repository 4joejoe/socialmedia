# Social Media

API endpoint is live on 


[SocialMedia](https://socialmedia-ajee.onrender.com) <br>

https://socialmedia-ajee.onrender.com


**Setup Instruction**

```bash
# install packages
pip install -r requirements.txt
```

```bash
# setup local environment
python3 -m venv env
```

```bash
# setup models and db
# this project uses sqlite
python3 manage.py makemigrations
# in some cases might need to run this also
python3 manage.py makemigrations authapp

# finally migrate
python3 manage.py migrate
```

```bash
# run app
python3 manage.py runserver
```

or

```bash
# for linux
./setup.sh
```

Setup Postman collection by importing provided postman json
> Change base url in Postman variable to appropriate host 

> Request body is provided with postman file

> Generate two or more user to test friend request functionality 