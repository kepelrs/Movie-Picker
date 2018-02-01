// valid movie ids in random order
let shuffled = [];
// cached objects for voting
let vote_cache = [];
// user voted values
let user_votes = {};

// recommendations array
let rec_array = [];
// cached for recommending
let rec_cache = [];

// jquery targets
let movie_info = $("#movie_info");
let movie_poster = $("#movie_poster");
let movie_title = $("#movie_title");
let likeButton = $("#likeBtn");
let dislikeButton = $("#disikeBtn");
let notWatched = $("#notWatched");
let recommendDiv = $("#recommend-div");
let recommendButton = $("#recommend-btn");
let recPoster = $("#rec-poster");
let recPosterParent = recPoster.parent();
let recInfoDiv = $("#rec-info");
let recNextBtn = $("#next-rec");
let recRow = $("#rec-row");
let recTitle = $("#rec-title");
let recSinopse = $("#rec-sinopse");
let recLink = $("#rec-link");

// dummy posters elements
let dummy_vote_poster = movie_poster.clone().attr("src", "");
let dummy_rec_poster = recPoster.clone().attr("src", "").css("display", "block");

// turn movie JSON into [posterImgDummy, JSON]
function preformatData(data, datatype){
    let returnArray = [];

    // select appropriate dummy type
    let dummy = datatype == "voting" ? dummy_vote_poster : dummy_rec_poster;

    // create elements and add to array
    for(let i = 0; i < data.length; i++){
        let targetMovie = data[i];
        let movie_poster = dummy.clone().attr("src", targetMovie.poster_link);
        returnArray.push([movie_poster, targetMovie]);
    }
    return returnArray;
}

// cache movie information
function getMovieInfo(array, first_call){
    form = {};
    form.movie = "";
    // get first 5 items in array
    for(let i = 0; i < 8; i++) {
        form.movie += array.shift().toString();
        form.movie += ",";
    }
    // get info and cache it
    $.post("/movie_info", form, function(data){
        // cache appropriately
        if(array == shuffled){
            data = preformatData(data, "voting");
            vote_cache = vote_cache.concat(data);
            // populate fields after first load
            if(first_call === "yes"){
                populateVoting();
            }
        } else {
            data = preformatData(data, "recommending");
            rec_cache = rec_cache.concat(data);
            // setup and populate fields after first load
            if(first_call === "yes"){
                setupRecommending();
                populateRecommending();
            }
        }
    });
}

// make sure cache keeps updating
function keepCacheAlive(cache){
    let target_array  = cache == vote_cache ? shuffled : rec_array;
    if(cache.length < 4){
        getMovieInfo(target_array, "not");
    }
}

// place information from cache onto voting div
function populateVoting(){
    let data = vote_cache.shift();
    let poster = data[0];
    let movie = data[1];

    keepCacheAlive(vote_cache);

    movie_poster.fadeOut(function(){
        movie_poster.remove();
        movie_info.prepend(poster);
        movie_poster = poster;
        movie_title.html(movie.name);
        movie_title.attr("movieid", movie.id);
        movie_poster.fadeIn();
    });
    displayRecommendDiv();
}

// populate recommendations
function populateRecommending(){
    let data = rec_cache.shift();
    let poster = data[0];
    let movie = data[1];

    keepCacheAlive(rec_cache);

    recRow.fadeOut(function(){
        recPoster.remove();
        recPosterParent.append(poster);
        recPoster = poster;
        recLink.attr("href", "https://imdb.com" + movie.imdb_link);
        recSinopse.html(movie.sinopse);
        recTitle.html(movie.name);
        recRow.fadeIn();
    });
}

// save user opinion about a movie on user_votes
function voteMovie(num){
    let movieId = movie_title.attr("movieid");
    user_votes[movieId] = num;
}

// display recommend button when enough votes
function displayRecommendDiv(){
    if(Object.keys(user_votes).length >= 10){
        if(recommendDiv.css("display") == "none"){
            recommendDiv.fadeIn();
        }
    }
}

// send user votes to server and retrieve recommendations
function getRecommendations(){
    $.post("/process_votes", user_votes, function(data){
        rec_array = data;
        getMovieInfo(rec_array, "yes");
    });
}

// setup recommendation div
function setupRecommending(){
    // animate out
    let target = $("#recommendations");
    target.fadeOut(function() {
        // remove paragraphs
        $("#para1").css("display", "none");
        $("#para2").css("display", "none");
        // display movie fields
        recPoster.css("display", "block");
        recInfoDiv.css("display", "block");
        // change button text
        recNextBtn.html("Give me another one...");
        // animate in
        target.fadeIn();
    });

    // change button behavior
    recNextBtn.toggleClass("js-scroll-trigger");
    recNextBtn.attr("target", "_blank");
    recNextBtn.unbind();
    recNextBtn.click(function(e){
        e.preventDefault();
        populateRecommending();
    });
}

// like button behaviour
likeButton.click(function(){
    voteMovie(2);
    populateVoting();
});

// dislike button behaviour
dislikeButton.click(function(){
    voteMovie(0);
    populateVoting();
});

// not watched button behaviour
notWatched.click(populateVoting);

// get recommendations button
recommendButton.click(getRecommendations);

// load random data on page load
$.post("/shuffled_movies", function(data){
    shuffled = data;
    getMovieInfo(shuffled, "yes");
});
