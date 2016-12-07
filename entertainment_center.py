#!/usr/bin/env python
"""Main script to create an static movie trailer site with a list of movies
identified by their imdb_id.

Usage:
    Add your favourite movies by imdb_id to the global variable FAV_MOVIE_IDS
    imdb_id is the string which follows /title/ in the url when you open up
    a movie's imdb page.
    eg. 'http://www.imdb.com/title/tt3748528/?ref_=nv_sr_1'
        => imdb_id=tt3748528
    If there are issues retrieving metadata for the specified movie, errors
    will be logged to stdout and the movie will be skipped.
"""
from fresh_tomatoes import open_movies_page
from media import MovieFactory

FAV_MOVIE_IDS = ["tt2543164", "tt1211837", "tt0357413", "tt0266543",
                 "tt0829482", "tt0365830", "tt3521164", "tt3183660"]


def main():
    movies = []
    for imdb_id in FAV_MOVIE_IDS:
        movie = MovieFactory.create_movie(imdb_id)
        if movie is not None:
            movies.append(movie)
    open_movies_page(movies)


if __name__ == "__main__":
    main()
