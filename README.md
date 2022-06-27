# 🌐 RecorderPlayer WebApp 
<hr>
This is source code of RecorderPlayer Web.

## ⚠️ Prerequisites
<a href="https://www.python.org/downloads/release/python-3100/">Python 3.10.0</a>
<a href="https://www.djangoproject.com/download/">Djanog 4.0.5</a>
<a href="https://www.postgresql.org/download/">PostgreSQL 14.1</a>

## 🛠 Build
1. Create a venv environment `python -m venv ./venv` and activate it `source venv/bin/activate`
2. Create `.env` file in main direction and insert values from `.env.example`
  ```
  # DEBAG MODE of WebApp. If it's true, all exception will show you.
  DEBUG_MODE=
  
  # Secret key for django app. Random sybols which sould starts with `django-insecure`. Example: `django-insecure-adfasdfwer123rasdv~2123!!@#$ASfd-asdfasf323423radfa`
  SECRET_KEY=
  
  # Values from postgres database
  DB_NAME=
  DB_USER=
  DB_USER_PASSWORD=
  DB_HOST=
  DP_PORT=
  ```
 3. Download all needest requirements from `requirements.txt` - `pip3 install -r requirements.txt`
 4. Go to recorder direct by command `cd recorder`
 5. Create supperuser `python3 manage.py createsuperuser` after enter all needest values.
 6. Start the website `python3 manage.py runserver`
 7. Go to http://127.0.0.1:8000/
 
 ## 📄 license
 Copyright ©2022 RecorderPlayer. Released under the MIT license.
