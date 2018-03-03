from flask import Flask, render_template, request, jsonify, redirect, url_for
import database_model as d
from random import shuffle
import logging
from datetime import datetime as dt

# setup Flask app
app = Flask(__name__)

# start db model
d.setup_db()


# Ensure responses aren't cached on your browser.
# Useful to see the changes you have made to your front end.
# You can delete this block once the project is finished.
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# When someone accesses "/" returns the index.html file in the teamplate folder
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/<path:path>")
def path_to_files(path):
    return redirect(url_for("static", filename=path))


@app.route("/movie_info", methods=["POST"])
def movie_info():

    # form["movie"] should be a coma separated string containing movie ids
    movie_ids = [int(i) for i in request.form["movie"].split(",") if i]

    # prevent user from crashing server by sending long query (max 10)
    limited = movie_ids[:10]

    # response is a dictionary {index: movie_object}
    selection = d.DBHandler.retireve_movie_info(limited)
    return jsonify(selection)


@app.route("/process_votes", methods=["POST"])
def process_votes():

    # get user ip, movie ids and vote values
    ip = request.remote_addr
    movie_ids = [i for i in request.form]
    votes_values = [request.form[i] for i in movie_ids]
    # convert ids to ints
    movie_ids = [int(i) for i in movie_ids]

    # add votes to db
    usr = d.DBHandler.add_new_rating(ip, movie_ids, votes_values)

    # get array of movie.ids recommendations
    recommeded = find_recomendations(usr, movie_ids, votes_values)

    # return recomendations
    return jsonify(recommeded)


@app.route("/shuffled_movies", methods=["POST"])
def shuffled_movies():
    '''returns valid(unarchived) movies in random order'''

    movies = d.DBHandler.all_movies_ids_[:]
    shuffle(movies)
    return jsonify(movies)


def find_recomendations(user, target_movies, current_votes):

    # get what users are saying about target movies (excluding current user)
    grades, ids = d.DBHandler.query_ratings(target_movies, exclude=user.id)

    # get closest people
    closest_people = d.DBHandler.get_closest_fit(grades, ids, current_votes)

    # get and sort recomendations from closest people
    recommend = d.DBHandler.extract_recomendations(user, closest_people)
    sorted_list = d.DBHandler.sort_recomendations(recommend)

    # remove already watched movies from recommendations
    cleaned_up = [i for i in sorted_list if i not in target_movies]
    print(cleaned_up)

    return cleaned_up


# Run the program
if __name__ == "__main__":
    logfile = 'access' + str(dt.now().day) + '.log'
    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler(logfile)
    logger.addHandler(handler)
    app.logger.addHandler(handler)
    app.run(host="0.0.0.0", port=2020, threaded=True, debug=False)
