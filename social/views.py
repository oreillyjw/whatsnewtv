from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from .models import MovieDBInfo, Comment, Favorites, Tags
from social.forms import SignUpForm
import os, json
from django.utils.html import escape
import tmdbsimple as tmdb
import requests
from decimal import *
from django.utils import timezone, formats
from .helper import *
import re
from datetime import datetime

# API Key for moviedb
tmdb.API_KEY = os.getenv('MOVIEDB_API_KEY_V3')

# Create your views here.
def index(request):
    """
        Render the home page for the website
        and if the user is signed in then display any upcoming shows that they may have
    """
    upcoming = []
    if  request.user.is_authenticated:
        for favorite in request.user.favorites.filter(is_favorite=True).all():
            if favorite.moviedb.upcoming_data is not None and favorite.moviedb.upcoming_data != "":
                upcoming_json = json.loads(favorite.moviedb.upcoming_data)
                if 'air_date' in upcoming_json:
                    upcoming_json['air_date'] = datetime.strptime(upcoming_json['air_date'], "%Y-%m-%d")

                upcoming.append({
                            "data": json.loads(favorite.moviedb.data),
                            "type": favorite.moviedb.type,
                            "upcoming": upcoming_json
                        })


    # fetch the most popular movies and tv shows from tmdb
    movies = tmdb.Movies().popular()
    tvshows = tmdb.TV().popular()

    return render(request, "social/index.html",
                    {
                        "upcoming" : upcoming,
                        "movies": movies['results'][:12],
                        "tvshows": tvshows['results'][:12]
                    }
                 )


def login_view(request):
    """Try to authenticate a user or show them an error message"""
    if  request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    errors = []
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            errors.append("Invalid credentials.")

    return render(request, "social/login.html",
        {
            "errors": errors,
            "type": "Login",
            "post_url": reverse('login'),
            "backlink": {
             "link": reverse('register'),
             "text": "Register"
             }
        })

def register(request):
    """Try and register a user using the extended UserCreationForm"""
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    message = []
    form = SignUpForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            for error in form.errors:
                message.append(form.errors[error])
    else:
        form = SignUpForm()

    return render(request, "social/login.html",
        {
            "errors": message,
            "type": "Register",
            "register" : True,
            "post_url": reverse('register'),
            'form': form,
            "backlink": {
                 "link": reverse('login'),
                 "text": "Login"
             }
        })

def details(request, type, id):
    """
        Fetch Detail page information such as recommendations, internal comments
        favorite information if the user is logged in
        A user can only have one comment on a given moviedb record
    """
    errors = []
    types = {
        'movie': tmdb.Movies,
        'tv' : tmdb.TV
    }
    allData = {}
    try:
        data = types[type](id)
        movieDBInfo = MovieDBInfo.objects.get(moviedb_id=id, type=type)
        time_since_insertion = timezone.now() - movieDBInfo.last_synced
        # store the data for the page visited if it is older
        # than a day or does not exist
        if time_since_insertion.days >= 1 or movieDBInfo.data is None:
            kwargs ={"append_to_response": "recommendations,videos"}
            allData = data.info(**kwargs)
            movieDBInfo.data = allData
            movieDBInfo.save()
        else:
            allData =  json.loads(movieDBInfo.data)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise Http404(f"{type} not found")
        else:
            raise HttpResponseServerError("Looks like something went wrong")

    except MovieDBInfo.DoesNotExist:
        # if the record if does not exist then create it
        kwargs ={"append_to_response": "recommendations,videos"}
        allData = data.info(**kwargs)
        movieDBInfo = MovieDBInfo.objects.create(moviedb_id=id, type=type, data=allData)
        movieDBInfo.save()


    has_comment = True
    favorited = False

    if request.user.is_authenticated:
        has_comment = request.user.comment.filter(moviedb=movieDBInfo).count()
        try:
            # Check to see if the record is favorited
            favorited_info = request.user.favorites.get(moviedb=movieDBInfo)
            favorited = favorited_info.is_favorite if favorited_info.is_favorite else False
        except Favorites.DoesNotExist:
            favorited = False

    if request.method == 'POST' and not has_comment:
        moviedb_id = request.POST['moviedb']
        if moviedb_id != id:
            raise HttpResponseBadRequest("Invalid ${type} page")

        comment = request.POST['comment-text']
        rating = request.POST['new-rating']
        title = request.POST['title']

        if rating and comment:
            # get all tagged user names and unique them
            tagged_users = re.findall('(?:^|\s)@(\w*(?:\w*))', comment, re.IGNORECASE)
            tagged_users_set = set(tagged_users)
            tagged_users = list(tagged_users_set)
            rating = float(rating)
            # add new comment
            new_comment = Comment.objects.create(user=request.user, title=title,
                    moviedb=movieDBInfo, rating=Decimal.from_float(rating), text=comment)
            new_comment.save()
            has_comment= True
            for username in tagged_users:
                try:
                    # Store Tags
                    user = User.objects.get(username=username)
                    new_tag = Tags(tagged_user=user, tagging_user=request.user, comment=new_comment)
                    new_tag.save()
                except User.DoesNotExist:
                    errors.append(f"Could notify everyone you wanted to sorry")
        else:
            errors.append("Please add both a rating and comment for your review")

    recommendations = []
    # get recommendations
    if allData['recommendations'] and allData['recommendations']['results']:
        recommendations = allData['recommendations']['results'][:6]

    videos = allData['videos']
    # get comments
    comments = movieDBInfo.comments.filter(approved=True).all().order_by("-created")
    comments_page = request.GET.get('comments_page', 1)

    comments = setup_paging_controls(comments,comments_page, 5)

    return render(request, "social/details.html",
                {
                    "errors": errors,
                    "data": allData,
                    "recommendations": recommendations,
                    "videos" : videos,
                    "type": type,
                    "comments": comments,
                    "show_comment": not bool(has_comment),
                    "favorited" : favorited
                })


def favorite(request):
    """
        Add a favorite or alter the status of the is favorite value
        This is an ajax request
    """
    dump_data = {}

    if request.user.is_authenticated and request.method == 'POST':
        formData = json.loads(request.body)
        try:
            moviedb = MovieDBInfo.objects.get(moviedb_id=formData['id'])
            favorite = Favorites.objects.filter(user=request.user).filter(moviedb=moviedb).all()
            if favorite.count() == 1:
                record = favorite[0]
                record.is_favorite = bool(formData['favorited'])
                record.save()
                favorite_info = record
            else:
                favorite_info = Favorites.objects.create(is_favorite=bool(formData['favorited']),
                            moviedb=moviedb, user=request.user)

            dump_data = {
                "favorited" : "true" if favorite_info.is_favorite else "false"
            }
        except:
            raise HttpResponseBadRequest("Invalid information")

    else:
        return HttpResponseForbidden("You do no have permission to this content")

    return HttpResponse(json.dumps(dump_data), content_type='application/json')

def search(request):
    """
        Paging controls and search for records against the MovieDB API
    """
    page = 1
    query = None
    num_per_page = 20
    results = []
    if request.method == 'POST':
        query = request.POST['search-term']
    elif request.method == "GET":
        page = int(request.GET.get('page', 1))
        query = request.GET.get('query', None)

    if query is not None and query != "":
        data = tmdb.Search().multi(query=escape(query),page=page)
        # pad the results for the paging controls setup
        pre_padded_data= ["{:02d}".format(x) for x in list(range(num_per_page*(page-1)))]
        remaining_size = data['total_results'] - (len(pre_padded_data)+len(data['results']))
        post_padded_data = ["{:02d}".format(x) for x in list(range(remaining_size))]
        results = pre_padded_data + data['results'] + post_padded_data
    else:
        query = "Searching for nothing "

    results = setup_paging_controls(results,page)

    return render(request, "social/search.html",
        {
            "results": results,
            "search_term": query,
            "data" : results,
            "query_param" : f"&query={query}"
        })

def logout_view(request):
    """
        Sign the user out
    """
    logout(request)
    return render(request, "social/login.html",
        {
            "errors": ["Logged out."],
            "type": "Login",
            "post_url": reverse('login'),
            "backlink": {
                "link": reverse('register'),
                "text": "Register"
            }
        })

def account_index(request):
    """
        Get information about all the comments and favorites for a
        given user
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    comments_page = request.GET.get('comments_page', 1)
    favorites_page = request.GET.get('favorites_page', 1)

    comments = request.user.comment.all().order_by("-created")

    comments = setup_paging_controls(comments,comments_page, 5)

    favorites = request.user.favorites.filter(is_favorite=True).all()

    favorites = setup_paging_controls(favorites,favorites_page, 5)

    return render(request, "social/account_index.html",
        {
            "comments" : comments,
            "favorites": favorites,
            "include_comment_info":True
        })


def get_followers(request):
    """
        Get all users for the autocomplete
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You do no have permission to this content")

    all_users = []
    if request.method == 'POST':
        userSearch = json.loads(request.body)

        if userSearch['query']:
            all_users = User.objects.filter(username__icontains=userSearch['query']).exclude(id=request.user.id).all()
        else:
            all_users = User.objects.exclude(id=request.user.id).all()

    dump_data = [ {"username": user.username, "id": user.id } for user in all_users]

    data = json.dumps(dump_data)

    return HttpResponse(data, content_type='application/json')


def get_notifications_count(request):
    """
        Get the number of unread notifications
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You do no have permission to this content")

    data = json.dumps({"count": request.user.notifications.filter(read=False).count()})

    return HttpResponse(data, content_type='application/json')

def get_notifications(request):
    """
        Get the actual notification data are return to client
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You do no have permission to this content")

    notifications = []
    if request.method == 'GET':
        notifications = request.user.notifications.filter(read=False).all()
        dump_data = [
            {
                "from": notification.tagging_user.username,
                "url": reverse("details", kwargs={
                                            'type': notification.comment.moviedb.type,
                                            "id": notification.comment.moviedb.moviedb_id
                                        }),
                "moviedb_data":json.loads(notification.comment.moviedb.data)
            } for notification in notifications]
        # Update all unread notifications at this point to read
        request.user.notifications.filter(read=False).all().update(read=True)

    data = json.dumps(dump_data)

    return HttpResponse(data, content_type='application/json')
