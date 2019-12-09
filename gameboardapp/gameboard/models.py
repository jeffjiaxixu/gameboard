from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class DashboardConfiguration(models.Model):
    """
    Has dashboard configuration options, which change how the dashboards look.
    """
    type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.type)


class Player(models.Model):
    """
    The player class stores information about individual players.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dashboard_configuration = models.ForeignKey(DashboardConfiguration, on_delete=models.CASCADE)
    date_of_birth = models.DateField(default=timezone.now().strftime("%Y-%m-%d"))
    profile_image = models.ImageField(upload_to='',blank=True)
    def __str__(self):
        return str(self.user.username)


class Game(models.Model):
    """
    The game class is all of the information about individual games which are played by users. Games will be non-group
    specific. So if one group adds a game, it will then be available for all groups in the future.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=400)
    game_picture = models.ImageField(upload_to='',blank=True)

    def __str__(self):
        return str(self.name)


class PlayerGroup(models.Model):
    """
    A player group is a group which users/players can create and invite other players too. This allows users to keep all
    of the friends the play games with in separate groups, and keep track of scores with those other players.
    """
    name = models.CharField(max_length=50)
    players = models.ManyToManyField(Player, related_name='players')
    admins = models.ManyToManyField(Player, related_name='admins')
    group_picture = models.ImageField(upload_to='',blank=True)

    def __str__(self):
        return str(self.name)


class GamePlayed(models.Model):
    """
    When a group plays a game, they will create a new instance of this class. This stores all of the relevant
    information about who played the game, who won, and the game played.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().strftime("%Y-%m-%d"))
    winners = models.ManyToManyField(Player, related_name='game_winners')
    players = models.ManyToManyField(Player, related_name='game_players')
    group = models.ForeignKey(PlayerGroup, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
