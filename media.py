import urllib
import json
import logging
from functools import wraps

API_BASE_URL = "https://api.themoviedb.org/3/"
FIND_API_URL = API_BASE_URL + "find/"
MOVIE_API_URL = API_BASE_URL + "movie/"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w300_and_h450_bestv2/"

API_KEY = "e65e9ea6072972e796ddbae4e2bdb8d4"  # Throwaway key
YOUTUBE_BASE_URL = "https://www.youtube.com/watch?v="


def return_none_on_error(f):
    """Wraps a function to capture exceptions and return None instead"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            logging.error("Error occured in func {}. Skipping Movie..."
                          "".format(f.__name__))
            return None
    return decorated_function


class Movie:
    """
    Class to store metadata for movies
    """

    def __init__(self, title, poster_image_url, trailer_youtube_url):
        self.title = title
        self.poster_image_url = poster_image_url
        self.trailer_youtube_url = trailer_youtube_url

    def __repr__(self):
        return str(self.title)


class MovieFactory:
    """Pseudo factory method to generate movie instances."""

    def __init__(self):
        pass

    @staticmethod
    def create_movie(api_query):
        """Creates a new Movie instance based on an imdb id.

        Queries the 'themoviedb' API and returns returns None if the API call
        fails.

        Args:
            api_query (str): imdb id of a movie
        Returns:
            Movie instance with appropriate metadata
            None if the creation process fails

        """
        data = MovieFactory.get_info(api_query)
        if data is not None:
            return Movie(data["title"],
                         data["image_url"],
                         data["trailer_youtube_url"])
        else:
            return None

    @staticmethod
    @return_none_on_error
    def get_info(imdb_id):
        """Queries the 'themoviedb' API for a movie's metadata.

        Args:
            imdb_id (str): imdb id of movie. imdb_id is the string which
                follows /title/ in the url when you open up a movie's imdb
                page.
                eg. 'http://www.imdb.com/title/tt3748528/?ref_=nv_sr_1'
                    => imdb_id=tt3748528
        Returns:
            a dictionary of
                {"trailer_youtube_url": {link} (str),
                 "title": {title} (str),
                 "image_url": {link} (str)}
            If an exception is encountered, None is return instead
        """
        def _parse_find_response(json_response):
            """Parses response from the FIND api.
            """
            r = json.loads(json_response)
            movies = r.get("movie_results", [])
            if len(movies) > 0:
                movie = movies[0]
                movie_id = movie["id"]
                poster_path = movie["poster_path"]
                title = movie["title"]
                return {"success": True,
                        "movie_id": movie_id,
                        "poster_path": IMAGE_BASE_URL + poster_path,
                        "title": title}
            else:
                logging.error("No movie found")
                return {"success": False}

        def _parse_movies_response(json_response):
            r = json.loads(json_response)
            videos = r.get("results", [])
            youtube_vids = [v for v in videos if v["site"] == "YouTube"]
            if len(youtube_vids) > 0:
                vid = youtube_vids[0]
                return {"success": True,
                        "link": YOUTUBE_BASE_URL + vid["key"]}
            else:
                logging.error("No YouTube link found")
                return {"success": False}

        def _get_connection(url, q_params):
            q_string = urllib.urlencode(q_params)
            # print url + "?" + q_string
            connection = urllib.urlopen(url + "?" + q_string)
            return connection

        # Make request to the FIND API. This gets us internal movie_id,
        # image path, and title
        q_params = {"language": "en-US",
                    "external_source": "imdb_id",
                    "api_key": API_KEY}
        url = FIND_API_URL + str(imdb_id)
        connection = _get_connection(url, q_params)
        if connection.code != 200:
            return None  # exit on failure

        movie_info = _parse_find_response(connection.read())
        if movie_info["success"] is not True:
            return None  # exit on failure

        # Using the internal movie_id, make request to the MOVIE API to get
        # a youtube trailer link
        movie_id = movie_info["movie_id"]
        q_params = {"language": "en-US",
                    "api_key": API_KEY}
        url = MOVIE_API_URL + str(movie_id) + "/videos"
        connection = _get_connection(url, q_params)
        if connection.code != 200:
            return None  # exit on failure

        trailer_info = _parse_movies_response(connection.read())
        if trailer_info["success"] is not True:
            return None

        return {"trailer_youtube_url": trailer_info["link"],
                "title": movie_info["title"],
                "image_url": movie_info["poster_path"]}
