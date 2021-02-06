FROM python:3.5.9-stretch
COPY . /app
RUN apt-get update

RUN pip install bs4
RUN pip install requests
RUN pip install peewee
RUN pip install selenium
RUN pip install sklearn
RUN pip install certifi
RUN pip install chardet
RUN pip install Click
RUN pip install Flask
RUN pip install gunicorn
RUN pip install idna
RUN pip install itsdangerous
RUN pip install Jinja2
RUN pip install MarkupSafe
RUN pip install numpy
# RUN pip install pkg-resources
RUN pip install scikit-learn
RUN pip install scipy
RUN pip install urllib3
RUN pip install Werkzeug
# chromium and chrome driver must be the same version
RUN apt-get install chromium -y
RUN apt-get install chromedriver -y
# RUN pip install playhouse
WORKDIR /app/
# RUN ls -la
# RUN python3 scrapeTop250.py
CMD bash
