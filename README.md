# [Movie Picker app](hhttp://130.204.58.113:3127/)

[Movie Picker](http://startbootstrap.com/template-overviews/freelancer/) is a webapp that recommends movies based on your individual preferences. It uses K-nearest neighbors with some other tricks to accomplish its goal.

## Preview

This was created as a part of my journey in the [Google Front-End Web Dev Challenge Scholarship](https://www.udacity.com/google-scholarships).

**[Demo](https://movie.arockhub.com/)**

## Updating db
0. Place your existing db in the scrape folder.
1. Start container with `docker-compose up`
2. `docker container ls` to find container id (fda47af889c5 in this case)
2. `docker container exec -it fda47af889c5 bash`
3. `cd scrape\ imdb/ && python3 scrapeTop250.py`.

You can edit files within the container as needed (will update outside files as well)

Db will be updated with new top 250 movies. Old movies will be kept. Outdated data (eg. images) will be refreshed.
