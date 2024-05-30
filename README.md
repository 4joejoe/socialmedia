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