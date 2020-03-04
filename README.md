# [Movie Picker app](hhttp://130.204.58.113:3127/)

[Movie Picker](http://startbootstrap.com/template-overviews/freelancer/) is a webapp that recommends movies based on your individual preferences. It uses K-nearest neighbors with some other tricks to accomplish its goal.

## Preview

This was created as a part of my journey in the [Google Front-End Web Dev Challenge Scholarship](https://www.udacity.com/google-scholarships).

**[View Live Preview](http://130.204.58.113:3127/)**

### Updating db
0. Place your existing db in the project's root folder.
1. Run scraper with `docker-compose up`
2. `docker run -it movie-picker_pydocker bash`

Db will be updated with new top 250 movies. Old movies will be kept. Images will be refreshed.
