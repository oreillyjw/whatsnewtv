# Final Project

Web Programming with Python and JavaScript
## Description

Everyone loves watching TV and Movies, So I created a website to search, favorite
and tag your friends about all the best television that you watch. Also see what is coming
up and when that you follow.

This website is backed by [The MovieDB API](https://www.themoviedb.org/documentation/api).

### SuperUser credentials:

* Superuser
  * Username: web50
  * Password: summer18

## Files

### Python
* views.py
  - index
    - Render the home page for the website and if the user is signed in then display any upcoming shows that they may have
  - login_view
    - Try to authenticate the user
  - register
    - Extends the UserCreationForm to create a form and if the form is
      valid then it will login in the user and redirect them to the menu
  - logout_view
    - Logs the user out and sends them to the sign in page
  - details
    - Renders the individual details of a particular tv show/movie
    - If you are logged in
      - Allows users to favorite a movie
      - Add a comment only once on a give tv show/movie
      - Tag users in your comments
  - favorite
    - Ajax endpoint to add/remove a favorite for a user
  - search
    - Allow for searching the moviedb for tv show, movies, people, etc.
  - account_index
    - Allows for a signed in user to view their favorites and all comments they have made
  - get_followers
    - Get all users for tagging purposes
    - Ajax endpoint
  - get_notifications_count
    - Gets a count of pending/unread notifications
  - get_notifications
    - Details of all pending notifications
* models.py
  - MovieDBInfo
    - Cached data stored from MovieDB API. This helps keep the number of
    requests down and allows. This is how I bridge the API and the internally stored data
  - Comment
    - Stored internal comments made by users for tv shows/movies
  - Favorites
    - Stored favorites of users
  - Tags
    - How notifications are stored when a user is mentioned in a comment
* forms.py
  - I found that there is a User Creation form, So I curtailed this to suite my need by adding required fields of first name, last name, and email. I also added some init overrides to style the form
  - Citations are below that I used for this form
* helper.py
  - setup_paging_controls
    - Very useful function to compute paging controls for a given object
    - Found in Paginator external resource below
* templatetags/utils.py
  - This is where all my Custom Django template filters live


### Javascript
* details.js
  - configure the star rating jquery plugin I found, resource below
  - favoriting Ajax call
  - And the textcomplete jquery plugin I found and
    documentation on how to implement it
  - resources below
* nav.js
  - Controls the search bar
  - Calls out to get the number of pending notifications
  - When the notifications are clicked then fetch then and display them

# Future Improvements
* TravisCI integration and tests
* Push Notification via Socket.io of being tagged
* Expand to include
  - People
  - TV Seasons
* Add Daily Jobs to update stored information
* Move MovieDBInfo to have a JSONField Object (Only available in Postgres)
* Make Product pages more detailed
  - Figure out what to do when there is no poster or backdrop image
  - Add Network Data or Production Company data
  - Rotten Tomatoes and IMDB integration


# External Resources:
* Index page
  - https://getbootstrap.com/docs/4.0/examples/album/
* Read More
  - https://codepen.io/joserick/pen/ooVPwR
* Custom Django Template Filters
  - https://docs.djangoproject.com/en/2.0/howto/custom-template-tags/
* Star Rating
  - https://github.com/kartik-v/bootstrap-star-rating
* Paginator
  - https://simpleisbetterthancomplex.com/tutorial/2016/08/03/how-to-paginate-with-django.html
* Autocomplete
  - https://www.algolia.com/doc/tutorials/search-ui/autocomplete/autocomplete-textarea/
  - https://github.com/yuku/jquery-textcomplete/tree/master/packages/jquery-textcomplete
* Added concept of followers/friends for tagging restrictions
