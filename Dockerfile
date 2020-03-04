FROM python:3.5.9-stretch
COPY . /app
RUN pip install bs4
RUN pip install requests
RUN pip install peewee
RUN pip install selenium
RUN pip install sklearn
# RUN pip install playhouse
WORKDIR /app/scrape\ imdb/
# RUN ls -la
# RUN python3 scrapeTop250.py
CMD bash
