from peewee import *
from sklearn.neighbors import KNeighborsClassifier
from playhouse.shortcuts import model_to_dict
from collections import Counter
import datetime

db = SqliteDatabase('movie_ratings.db')


class User(Model):

    id = PrimaryKeyField()
    ip_address = CharField()
    grades = TextField(default="1" * 1)
    date_added = DateTimeField(default=datetime.datetime.now)
    archived = BooleanField(default=False)

    class Meta:
        database = db


class Movie(Model):

    id = PrimaryKeyField()
    name = CharField(default="asd")
    grade = FloatField(default=1)
    sinopse = TextField(default="asd")
    imdb_link = TextField(default="asd")
    poster_link = TextField(default="asd")
    date_added = DateTimeField(default=datetime.datetime.now)
    archived = BooleanField(default=False)

    class Meta:
        database = db


class DBHandler():
    ''' this class contains the utility functions for the model '''

    def update_ratings_length():
        ''' make sure len(User.grades) == number of movies in database '''
        number_of_movies = len(DBHandler.all_movies_)
        ratings = User.select().where(User.archived == False)
        for i in ratings:
            vote_number = len(i.grades)
            if vote_number <= number_of_movies:
                i.grades += "1" * (number_of_movies + 1 - vote_number)
                i.save()

    def handle_request(request):
        ''' takes request from user, returns dict for adding_new_rating '''
        ip = request.remote_addr
        rated_ids = [i for i in request.form if i[:3] == "Mid"]
        grades = [request.form[i] for i in rated_ids]
        indexes = [int(i[3:]) for i in rated_ids]

        return ip, indexes, grades

    def add_new_rating(ip, indexes, grades):
        ''' add retrieved data to database
            returns new user object '''

        # archive previous rating (if any)
        selection = User.select().where(User.ip_address == ip)
        selection = selection.where(User.archived == False)
        # archive older rating logs (if available)
        if len(selection) > 0:
            target = selection.order_by(User.id)[0]
            target.archived = True
            target.save()

        # add new rating log
        new_user = User.create(ip_address=ip,
                               grades="1" * (DBHandler.db_movie_size_ + 1))

        # edit grades
        new_string = [i for i in new_user.grades]
        for (i, v) in zip(indexes, grades):
            new_string[i] = v

        new_user.grades = "".join(new_string)
        new_user.save()
        return new_user

    def query_ratings(indexes, exclude=False):
        ''' query all User.grades for the [indexes] movies '''
        selection = User.select().where(User.archived == False)

        # grab what grades all users have given to these movies
        grades = []
        user_ids = []
        for i in selection:
            # ignore current user
            if i.id == exclude:
                continue

            grade = [int(i.grades[index]) for index in indexes]
            grades.append(grade)
            user_ids.append(i.id)
        return grades, user_ids

    def get_closest_fit(grades, labels, my_grades):
        ''' input:
                grades is an array where each element is a string/array
                containing all the grades a given user gave to the movies
                being queried.

                labels is an array where each element is the id of the user
                who's grades are in the grades array

                my_grades is a string/array containing the user's votes/grades
                for the movies in question

            ouput: id of the Users that most closely match my_grades '''

        # fit the model
        my_classifier = KNeighborsClassifier(n_neighbors=1)
        my_classifier.fit(grades, labels)

        # get top 20% closest matches
        n = DBHandler.db_user_size_ * 0.2
        n = int(n) if n > 1 else 1
        my_grades_int = [int(i) for i in my_grades]
        selection = my_classifier.kneighbors([my_grades_int], n, False)

        # get id of selected users
        closest_people = [labels[int(i)] for i in selection[0]]
        return closest_people

    def extract_recomendations(user_object, closest_people):
        ''' input:
                closest_people (array):
                    array of users that have similar tastes
                user_object (User instance):
                    current user's instance

            output:
                array of Movie.id of recommended movies '''

        # select users that have the closest movie opinions
        selection = User.select().where(User.id << closest_people)
        # get all their votings, and the current user's voting
        similar_grades = [i.grades for i in selection]
        user_grades = user_object.grades
        # create (close_person_votes, my_votes) tuples for zipping
        zips = [zip(user_grades, similar) for similar in similar_grades]

        # add to array whenever close person has watched and liked a movie
        # but current_user still has not watched it
        recommendations = []
        for zipped in zips:
            for (index, (user_grade, recommender_grade)) in enumerate(zipped):
                if user_grade == "1" and recommender_grade == "2":
                    recommendations.append(index)

        return recommendations

    def sort_recomendations(array):
        ''' input array of movie.ids that close_matched people have watched
            output sorted recommendations by highest imdb grade '''
        recommended = Counter(array).most_common()
        sorted_recommended = [k for k, v in recommended if
                              k in DBHandler.all_movies_ids_]

        # when list ends, start recommending from highest unwatched movie
        sorted_rest = []
        for i in DBHandler.all_movies_:
            movie_id = i.id
            if movie_id not in array:
                sorted_rest.append(movie_id)

        # full list:
        all_recomendations_ids = sorted_recommended + sorted_rest

        return all_recomendations_ids

    def load_all_movies():
        ''' load all movies, in order not to query again '''
        all_movies = Movie.select()
        unarchived = all_movies.where(Movie.archived == False)
        ordered_movies = unarchived.order_by(Movie.grade.desc())

        # all movies that are not archived, ordered by rating:
        DBHandler.db_movie_size_ = len(all_movies)
        DBHandler.all_movies_ = ordered_movies

        # and their ids
        DBHandler.all_movies_ids_ = [i.id for i in DBHandler.all_movies_]

        # how many active users
        DBHandler.db_user_size_ = len(User.select().where(User.archived == False))

    def retireve_movie_info(movie_ids):
        # only search for id of non-archived movies
        filtered_ids = [i for i in movie_ids if i in DBHandler.all_movies_ids_]
        # find and keep movie order
        selection = Movie.select().where(Movie.id << filtered_ids)
        ordered = []
        for i in filtered_ids:
            for obj in selection:
                if obj.id == i:
                    ordered.append(obj)
                    break
        # return array, where i is a dict of the movie info
        return [model_to_dict(i) for i in ordered]

    # TODO
    # add possibilities to filter by categories


def setup_db():
    DBHandler.load_all_movies()
    DBHandler.update_ratings_length()


def initialize_db():
    db.connect()
    db.create_tables([User, Movie], safe=True)
