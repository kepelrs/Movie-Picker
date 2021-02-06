import bs4 as bs
import requests
import database_model as d
from selenium import webdriver as w
from time import sleep
from selenium.webdriver.chrome.options import Options

# start DB
d.initialize_db()


def download_and_save(url, target_filename=False):
    ''' downloads and saves target url '''

    # request page
    pg = requests.get(url)
    # confirm it was properly saved
    pg.raise_for_status()
    # save it as a file on current folder
    if target_filename:
        with open(target_filename, mode="wb") as f:
            for chunk in pg.iter_content(100000):
                f.write(chunk)

    soup = bs.BeautifulSoup(pg.content, "html.parser")

    return soup


def scrape_top250(pg):
    ''' opens saved html file and returns dict movienames:info '''

    # select table with all movies
    table = pg.find("tbody", class_="lister-list")
    # get all rows
    rows = table.find_all("tr")
    # get td for the names
    titles = [i.find("td", class_="titleColumn") for i in rows]
    # get names
    stripped_names = [i.text.split("\n")[2].strip() for i in titles]
    # get links
    hrefs = [i.find("a")["href"] for i in titles]
    # get ratings
    ratingsCol = [i.find("td", class_="ratingColumn imdbRating") for i in rows]
    ratings = [i.text.replace("\n", "") for i in ratingsCol]
    # get sinopses and posters
    sinopses = []
    posters = []
    counter = len(hrefs)
    for i in hrefs:
        print("Downloading info from:", i)
        print(counter, "movies left")
        counter -= 1
        sinopse, poster = scrape_movie_info(i)
        sinopses.append(sinopse)
        posters.append(poster)

    # reasign posters to high definition version
    posters = get_high_def_posters(posters)

    # assert data integrity
    data_size = len(hrefs)
    assert all(map(lambda x: len(x) == data_size, [sinopses, posters,
               stripped_names, ratings])), "DATA SIZES ARE NOT EQUAL"
    # return zip object
    return zip(stripped_names, hrefs, ratings, sinopses, posters)


def get_high_def_posters(array):
    # higher def links
    posters = []
    # use Selenium, because pages are rendered by JS
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = w.Chrome(chrome_options=chrome_options)
    browser.get("http://www.google.com")
    sleep(3)
    # iterate over all url's in the array
    for linkIndex, link in enumerate(array):
        print('Fetching poster ' + str(linkIndex + 1) + ' of ' + str(len(array)))

        url = "http://www.imdb.com" + link
        # get page and sleep in order for JS to load
        browser.get(url)
        sleep(3)
        # get HTML of rendered page
        html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        pg = bs.BeautifulSoup(html, "html.parser")
        # get img elements
        # matches = pg.find_all(class_="pswp__img")
        matches = pg.find_all("img")
        # get only the ones that have an "alt" attribute
        filtered_matches = []
        for i in matches:
            try:
                i["alt"]
            except:
                continue
            filtered_matches.append(i)
        # select only the main img element if there are multiple matches
        try:
            poster = filtered_matches[0]["src"]
        except:
            poster = filtered_matches[1]["src"]
        # store in posters array
        posters.append(poster)

    # close browser
    browser.quit()

    return posters


def add_movies_to_db(zip_obj):
    for i in zip_obj:
        movie_status, movie = check_if_movie_up_to_date(i)
        if movie_status == "Not in database":
            d.Movie.create(name=i[0],
                           grade=i[2],
                           sinopse=i[3],
                           imdb_link=i[1],
                           poster_link=i[4],
                           )
        elif movie_status == "Not up to date":
            movie.grade = i[2]
            movie.sinopse = i[3]
            movie.imdb_link = i[1]
            movie.poster_link = i[4]
            movie.save()
        print(i[0], movie_status)


def check_if_movie_up_to_date(movie_info_array):
    # reasing (for semantics only)
    i = movie_info_array
    # select movies a given name
    selection = d.Movie.select().where(d.Movie.name == i[0])
    movies = selection.where(d.Movie.archived == False)
    # sanity check number of matches
    number_of_matches = len(movies)
    if number_of_matches > 1:
        raise IndexError("Too many movies matched for", i[0])
    elif number_of_matches == 1:
        movie = movies[0]
    else:
        movie = False

    # check status of information for a given movie
    if movie:
        if (movie.grade == float(i[2]) and movie.sinopse == i[3] and
            movie.imdb_link == i[1] and movie.poster_link == i[4]):
            return "Up to date", movie
        return "Not up to date", movie
    return "Not in database", False


def scrape_movie_info(link):
    url = "http://www.imdb.com" + link
    pg = download_and_save(url)

    # get sinopse:
    sinopse = pg.find("div", class_="summary_text").text.strip()
    # get poster
    poster = pg.find("div", class_="poster").find("a")["href"]
    return sinopse, poster


top250 = download_and_save("http://www.imdb.com/chart/top", "CurrentPage.html")
all_movies = scrape_top250(top250)

add_movies_to_db(all_movies)

print("SCRAPING DONE")
