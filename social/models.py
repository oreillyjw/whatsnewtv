from django.db import models
from django.contrib.auth.models import User
import json
from django.utils import timezone, formats
from .templatetags import *
from django.contrib.humanize.templatetags.humanize import date
from datetime import datetime

# Create your models here.
class MovieDBInfo(models.Model):
    """
        Cached data stored from MovieDB API
        This helps keep the number of requests down and allows
    """
    moviedb_id = models.CharField(max_length = 64)
    type = models.CharField(max_length = 64, blank=True)
    last_synced = models.DateTimeField(blank=True)
    created = models.DateTimeField()
    data = models.TextField(blank=True)
    upcoming_data = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
            extract some of the save values and store it properly
        """
        if type(self.data) is dict:
            if 'next_episode_to_air' in self.data and self.data['next_episode_to_air'] is not None:
                self.upcoming_data = json.dumps(self.data['next_episode_to_air'])
            elif 'next_episode_to_air' in self.data and self.data['next_episode_to_air'] is None:
                self.upcoming_data = None
            elif 'release_date' in self.data and self.data['release_date'] is not None:
                release_date = datetime.strptime(self.data['release_date'], "%Y-%m-%d")
                if release_date > datetime.now():
                    self.upcoming_data = json.dumps({"air_date": f"{self.data['release_date']}"})
                else:
                    self.upcoming_data = None

            self.data = json.dumps(self.data)

        if not self.id:
            self.created = timezone.now()

        self.last_synced = timezone.now()
        super(MovieDBInfo, self).save(*args, **kwargs)

    def __str__(self):
        """
            The display of the object could vary depending on what data is present
        """
        all_data = json.loads(self.data)
        return_info = ""
        if 'title' in all_data:
            return_info = f"{all_data['title']} ({all_data['release_date'].split('-')[0]})"
        elif 'name' in all_data:
            if 'first_air_date' in all_data and all_data['first_air_date'] is not None:
                timerange = all_data['first_air_date'].split("-")[0]
                if 'last_air_date' in all_data and not all_data['in_production']:
                    timerange = f'{timerange} - {all_data["last_air_date"].split("-")[0]}'
                else:
                    timerange += " - Present"
                return_info = f"{all_data['name']} ({timerange})"
            else:
                return_info = f"{all_data['name']}"

        return return_info

class Comment(models.Model):
    """
        Store all the comments that users make on various movie db data
        the approved field allows for comments to be removed
    """
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="comment")
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length = 64, blank=True)
    moviedb = models.ForeignKey(MovieDBInfo,
            related_name="comments",
            on_delete = models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True)
    text = models.TextField(blank=True)
    approved = models.BooleanField(default=True )

    def __str__(self):
        return f"Approved: {self.approved} - {self.user} - {self.text}"


class Favorites(models.Model):
    """
        These are moviedb records that have been favorited
    """
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="favorites")
    moviedb = models.ForeignKey(MovieDBInfo,
                on_delete = models.CASCADE)
    is_favorite = models.BooleanField(default=False )
    def __str__(self):
        return f"Approved: {self.is_favorite} - {self.moviedb} - {self.user}"


class Tags(models.Model):
    """
        When you tags another user, it gets recorded here
    """
    read = models.BooleanField( default=False )
    tagged_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="notifications")
    tagging_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="tags")
    comment = models.ForeignKey(Comment, on_delete = models.CASCADE, related_name="tagged_comment")
