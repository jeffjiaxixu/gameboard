import csv
import os

from django.contrib.auth.models import User

from gameboardapp.settings import STATIC_ROOT, PROJECT_ROOT, BASE_DIR, APP_ROOT, STATIC_URL, MEDIA_ROOT, MEDIA_URL, \
    REPOSITORY_ROOT
from datetime import datetime
from django.db import IntegrityError
from gameboard.models import Game, GamePlayed, Player, PlayerGroup, DashboardConfiguration


def import_scores_from_csv(f):
    """
    Imports a csv (which is in the right format) into the models. Generates a new group and populates it with the
    appropriate data.

    :param f: The CSV file to import from.
    :return: The group if it was created, otherwise None.
    """
    print(f)
    with open(os.path.join(STATIC_ROOT, 'dataset.csv'), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return None


class ImportScores:
    """
    Imports scores form a custom formatted csv (stored as a static file).
    """
    # The csv file to get data from
    csv_log = os.path.join(STATIC_ROOT, 'dataset.csv')

    # Specific locations of columns within the csv
    day_loc = 0
    game_loc = 1
    first_player_loc = 3
    coop_flag_loc = 16
    total_loc = 17
    end_junk_cnt = 2

    # Storing the player information
    players = []

    def __init__(self):
        """
        Wipes all past data (be careful to only use this in a testing environment!) and then adds data. Adding starts
        with players, then games, then individual games by the date they were played. Assumes the dataset contains all
        games played by a single group, which hasn't been created yet.
        """
        # Wipe the db
        self.wipe_db()

        # Set some global things
        try:
            dashboard_configuration = DashboardConfiguration(type="default")
            dashboard_configuration.save()
        except IntegrityError:
            dashboard_configuration = DashboardConfiguration.objects.filter(type="default").first()

        # Add all players from dataset
        group = self.add_players(dashboard_configuration)

        # Add all games from the dataset
        self.add_games()

        # Create the games played for this group
        self.add_game_played(group)

    def wipe_db(self):
        """
        WARNING: This function wipes all data in the database. Be careful with its use!

        :return: None
        """
        Player.objects.all().delete()
        Game.objects.all().delete()
        GamePlayed.objects.all().delete()

    def add_players(self, dashboard_configuration):
        """
        Adds all the players within the csv to the Player database table.

        Gets the first line of the csv. Loops over all the players in that line (marked by location marks). Adds those
        players as users, with a temporary password (WebAppsIsTheBestCourse) and usernames/first names cooresponding
        to the player name.

        :return: None
        """
        print("BASE_DIR       ", BASE_DIR)
        print("PROJECT_ROOT   ", PROJECT_ROOT)
        print("APP_ROOT       ", APP_ROOT)
        print("STATIC_ROOT    ", STATIC_ROOT)
        print("STATIC_URL     ", STATIC_URL)
        print("MEDIA_ROOT     ", MEDIA_ROOT)
        print("MEDIA_URL      ", MEDIA_URL)
        print("REPOSITORY_ROOT", REPOSITORY_ROOT)
        with open(self.csv_log, newline='') as f:
            # Get the first line
            reader = csv.reader(f)
            people = next(reader)
            self.players = people[self.first_player_loc:-self.end_junk_cnt]
            group = PlayerGroup(name="TAS and Friends")
            group.save()

            # Loop over those players
            for player in self.players:
                try:
                    # Set the user object
                    username = player.replace(" ", "")
                    u = User(first_name=player, last_name="", username=username)
                    u.save()
                    u.set_password("WebAppsIsTheBestCourse")
                    u.save()

                    # Set the player object
                    p = Player(user=u, dashboard_configuration=dashboard_configuration, date_of_birth=datetime.now())
                    p.save()

                    group.players.add(p)
                    group.admins.add(p)
                except IntegrityError:
                    print("Player object exists already.")
                    pass
            return group

    def add_games(self):
        """
        Adds all the games within the csv for later relation with the GamePlayed object.

        Loops through all lines in the sheet, looking at a specific column and pulling all the unique names it finds
        in that column.

        :return: None
        """
        with open(self.csv_log, newline='') as f:
            # Open the csv
            reader = csv.reader(f)
            for line in reader:
                # Get the game data
                game = line[self.game_loc]
                if len(game) > 0:
                    try:
                        # Add it if it is unique
                        g = Game(name=game)
                        g.save()
                    except IntegrityError:
                        pass

    def add_game_played(self, group):
        """
        Adds all games that were played which were recorded, as long as they are properly formatted.

        :return: None
        """
        with open(self.csv_log, newline='') as f:
            # Open the csv, and read through every line (but the header)
            reader = csv.reader(f)
            next(reader)  # skip header line
            for line in reader:
                # Get the game (if it is not there, ignore this line)
                game = line[self.game_loc]
                if len(game) > 0:
                    # Get the date the game was played on
                    date = datetime.strptime(line[self.day_loc], "%A, %m/%d/%y")

                    # Get the players (and their win counts) that played on that day
                    players_wins = line[self.first_player_loc:-self.end_junk_cnt]

                    players = list()
                    win_count = list()
                    # Loop through all the players who played
                    for player_index in range(len(players_wins)):
                        # Get their names, and the wins they had
                        player = self.players[player_index]
                        player_win_count = players_wins[player_index]

                        if player_win_count != "":
                            # Actually played in this game
                            players.append(player)
                            win_count.append(int(player_win_count))

                    # Try to get the number of wins that occurred on that day (for calculating ties)
                    try:
                        total_win_count = int(line[self.total_loc])
                    except ValueError:
                        total_win_count = 0

                    # Check if this was a coop game
                    if line[self.coop_flag_loc] != "":
                        # coop win, ignore
                        pass
                    elif total_win_count > 1:
                        # Add together all the wins which occurred
                        sum = 0
                        for num in players_wins:
                            try:
                                sum += int(num)
                            except ValueError:
                                pass

                        # Check if there were ties
                        if sum != total_win_count:
                            # Some ties occurred, handle this special case manually...
                            print("WARNING: Found a difficult case to handle, please manually enter.")
                            print("    Game: %s" % game)
                            print("    Date: %s" % date)
                            print("    Total wins: %d" % total_win_count)
                            for num_index in range(len(players_wins)):
                                if players_wins[num_index] != "":
                                    print("    %s: %s" % (self.players[num_index], players_wins[num_index]))
                        else:
                            # No ties, so just repeat submission, 1 for every win.
                            winners = []
                            for player_index in range(len(players)):
                                player = players[player_index]
                                win = win_count[player_index]
                                for i in range(win):
                                    winners.append(player)
                            for winner in winners:
                                self.enter_game_played(players, [winner], game, date, group)

                    # Only one win, so assign win to everyone without a zero in their column.
                    elif total_win_count == 1:
                        winners = []
                        for player_index in range(len(players)):
                            player = players[player_index]
                            win = win_count[player_index]
                            if win > 0:
                                winners.append(player)

                        self.enter_game_played(players, winners, game, date, group)

                    else:
                        # Something went wrong, we should check these out manually.
                        print("Not counting %s" % game)

    def enter_game_played(self, players_names, winners_names, game, date, group):
        """
        Actually adds the game played to the database, linking to Player objects and Game objects.

        :param players_names: The names of the players
        :param winners_names: The names of the winners of the game
        :param game: The game that was played (string)
        :param date: A date object to use for when the game was played
        :return: None
        """
        try:
            game_played = GamePlayed()
            game_played.game = Game.objects.get(name__exact=game)
            game_played.date = date
            game_played.group = group
            game_played.save()

            for player in players_names:
                game_played.players.add(Player.objects.get(user__first_name__exact=player))
            for winner in winners_names:
                game_played.winners.add(Player.objects.get(user__first_name__exact=winner))
        except:
            print("Error entering game", game)
            pass

