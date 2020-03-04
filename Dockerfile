FROM python:3.5.9-stretch
COPY . /app
RUN pip install bs4
RUN pip install requests
RUN pip install peewee
RUN pip install selenium
RUN pip install sklearn
RUN apt-get update
# chromium and chrome driver must be the same version
RUN apt-get install chromium -y
RUN apt-get install chromedriver -y
# RUN pip install playhouse
WORKDIR /app/scrape\ imdb/
# RUN ls -la
# RUN python3 scrapeTop250.py
CMD bash
