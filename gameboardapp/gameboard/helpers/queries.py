from gameboard.models import Player, GamePlayed, PlayerGroup, Game
from operator import itemgetter, attrgetter
from collections import Counter
from datetime import datetime


def num_games_played(player):
    """
    Get the number of games a single player has played, across all groups.

    :param player: A Player object, which contains the user info
    :return: The number of games played.
    """
    num_played = 0
    if player:
        games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.first_name)
        num_played = len(games_played)
    return num_played


def find_wins(player):
    """
    Calculate the number of wins that player has to their name, across all games played (and all groups).

    :param player: A Player object, which contains the user info
    :return: The number of wins for a player.
    """
    num_wins = 0
    if player:
        games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.first_name)
        wins = GamePlayed.objects.all().filter(winners__user__username__exact=player.user.first_name)
        num_wins = len(wins)
    return num_wins


def find_losses(player):
    """
    Find the number of losses that a player has across all games played (and all groups).

    :param player: A Player object, which contains the user info
    :return: The number of losses for a player.
    """
    num_losses = 0
    if player:
        games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.first_name)
        wins = GamePlayed.objects.all().filter(winners__user__username__exact=player.user.first_name)
        num_losses = len(games_played) - len(wins)
    return num_losses


def find_win_percentage(player):
    """
    Calculate the win percentage for a player.

    :param player: A Player object, which contains the user info
    :return: The player's win percentage across all games played (and all groups)
    """

    percentage = 0
    if player:
        games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.first_name)
        wins = GamePlayed.objects.all().filter(winners__user__username__exact=player.user.first_name)
        if len(games_played) > 0:
            percentage = (len(wins)/len(games_played)) * 100
    return percentage


def find_win_percentage_for_game(player, game_name):
    """
    Calculate the win percentage for a player for a specific game.

    :param player: A Player object, which contains the user info
    :param game_name: The name of a game to be looking for TODO switch this to game object
    :return: The win percentage for a player playing a specific game
    """
    percentage = 0
    if player:
        #print("Found user " + player.user.first_name)
        games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.first_name)
        #print("Games played: " + str(len(games_played)))
        wins = GamePlayed.objects.all().filter(winners__user__username__exact=player.user.first_name, game__name__exact=game_name)
        #print("Wins: " + str(len(wins)))
        if len(games_played) > 0:
            percentage = (len(wins)/len(games_played)) * 100
            #print("Percentage won: " + str(percentage))
    return percentage


def find_games_played(player):
    """
    Calculate the number of games a single player has played, across all groups.

    :param player: A Player object, which contains the user info
    :return: The number of games played.
    """
    played = set()
    if player:
        games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.username)
        for g in games_played:
            played.add(g.game.name)
    return played


def find_favorite_game(player):
    """
    Find the favorite game for a given player. Uses all game data to find what game they play the most.

    :param player: A Player object, which contains the user info
    :return: The player's favorite game (as an object).
    """
    fav_game = ''
    if player:
        games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.username)
        game_dict = dict()
        for g in games_played:
            if g.game.name not in game_dict:
                game_dict[g.game.name] = 0
            game_dict[g.game.name] += 1

        max_count = 0 
        for name in game_dict:
            if game_dict[name] > max_count:
                max_count = game_dict[name]
                fav_game = name
    return fav_game
# TODO something similar to find_favorite_game for find_best_game, where wins are factored at a higher weight


def find_players_in_game(game_id):
    """
    Find the players who have played a game.

    :param game_id: TODO switch this to game object
    :return:
    """
    players = Player.objects.filter(id=game_id)
    return players


def find_best_player_in_group(group):
    """
    Find the best player in a given group.

    :param group: The group object to look through for the best player
    :return:
    """
    players = group.players.all()
    max_win_rate = 0
    best_player = None
    percentage = 0
    for player in players:
        if player:
            games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.username)
            wins = GamePlayed.objects.all().filter(winners__user__username__exact=player.user.username)
            if len(games_played) > 0:
                percentage = (len(wins)/len(games_played)) * 100
                if percentage > max_win_rate:
                    max_win_rate = percentage
                    best_player = player
    return best_player, percentage


def get_date(game_played):
    """
    Gets the date from within the game object.
    TODO is this necessary?

    :param game_played: A game_played object to use.
    :return: The date of the game played.
    """
    return game_played.date


def find_longest_win_streak_in_group(group):
    """
    Find the longest win streak and player in a given group

    :param group: A Group object, which contains the group info
    :return: the longest streak player and the longest streaks
    """
    group_id = group.id
    games_played = GamePlayed.objects.all().filter(group__id=group_id)
    games_played = list(games_played)
    games_played = sorted(games_played, key=attrgetter('date'))

    longest_streak = 0
    longest_streak_player = None
    curr_streak = 0
    curr_player = None

    for i in range(len(games_played)-1):
        if games_played[i].winners == games_played[i+1].winners:
            curr_player = games_played[i].winners
            curr_streak += 1
        else:
            longest_streak_player = curr_player
            longest_streak = curr_streak

    return longest_streak_player, longest_streak


def find_longest_win_streak_in_game(game_name):
    """
    Find the longest win streak and player in a given group

    :param game_name: The name of the game to find TODO this should be a game object
    :return: the longest streak player and the longest streaks
    """
    games_played = GamePlayed.objects.all().filter(game__name__exact=game_name)
    games_played = list(games_played)
    games_played = sorted(games_played, key=attrgetter('date'))

    longest_streak = 0
    longest_streak_player = None
    curr_streak = 0
    curr_player = None

    for i in range(len(games_played)-1):
        if games_played[i].winners == games_played[i+1].winners:
            curr_player = games_played[i].winners
            curr_streak += 1
        else:
            longest_streak_player = curr_player
            longest_streak = curr_streak

    return (longest_streak_player, longest_streak)


def find_players_in_group(group):
    """
    Find the players who have played a game.

    :param group: A Group object, which contains the group info
    :return: All players who have played a game in a group
    """
    group_id = group.id
    players_ids = PlayerGroup.objects.filter(id=group_id).values('players')
    players = []
    for item in players_ids:
        players.append(Player.objects.filter(id=item["players"]).first())
    return players


def find_admins_in_group(group):
    """
    Find the players who have played a game.

    :param group: A Group object, which contains the group info
    :return: The admins in a given group
    """
    group_id = group.id
    admins_ids = PlayerGroup.objects.filter(id=group_id).values('admins')
    admins = []
    for item in admins_ids:
        admins.append(Player.objects.filter(id=item["admins"]).first())
    return admins


def find_games():
    """
    Get all games
    TODO is this necessary?

    :return: All games as an queryset of objects
    """
    games = Game.objects.all()
    return games


def find_groups(player):
    """
    Finds all groups that a player is a part of

    :param player: A Player object, which contains the user info
    :return: A queryset of group objects the player belongs to
    """
    group = PlayerGroup.objects.filter(players__user__username=player.user.username)

    return group


def find_first_group(player):
    """
    Finds the first group from a set of groups.

    :param player: A Player object, which contains the user info
    :return: A single group object the player belongs to if they belong to one, otherwise None
    """
    group = find_groups(player)
    if group:
        return group.first()
    else:
        return None


def find_games_by_group(group):
    """
    Finds all games within a group.

    :param group: A Group object, which contains the group info
    :return: A queryset of games that are played by a group
    """
    games = set()
    if group:
        games = GamePlayed.objects.filter(group__id=group.id).order_by('-date')
    return games


def find_rival_in_group(group, player):
    """
    find the rival player in a group (the player that the current player
    has lost most games against)

    :param group: a Group object
           player: a Player object
    :return: A tuple of the max wins against current player and the username
    of that player
    """

    group_players = group.players.all()
    games_played = GamePlayed.objects.all().filter(group__name__exact=group.name)

    max_win = 0
    max_player = None
    for p in group_players:
        if player.user.username != p.user.username:
            p_games_won = 0
            for g in games_played:
                if p in g.winners.all():
                    p_games_won += 1
            if p_games_won > max_win:
                max_win = p_games_won
                max_player = player.user.username
    return (max_win, max_player)


def find_most_active_player_in_group(group):
    """
    find the most active player in a group (most games played)

    :param group: A Group object
    :return: a tuple of the most active player and the number of games they played
    """

    games_played = GamePlayed.objects.all().filter(group__name__exact=group.name)

    played = []
    for game in games_played:
        players = list(game.players.all())
        played += players

    (most_active, num_most_active) = Counter(played).most_common(1)[0]

    return (most_active, num_most_active)


def find_favorite_game_in_group(group):
    """
    find the favorite game in a group (most played)

    :param group: A Group object
    :return: a tuple of favorite game and number of times the game is played
    """

    games_played = GamePlayed.objects.all().filter(group__name__exact=group.name)

    played = []
    for g in games_played:
        played.append(g.game.name)

    (favorite_game, favorite_played) = Counter(played).most_common(1)[0]

    return (favorite_game, favorite_played)


def find_num_player_in_group(group):
    """
    find the number of players in a group

    :param group: A Group object
    :return: number of players in the group
    """
    
    players = group.players.all()

    return (len(players))


def games_played_by_group_by_day(group):
    """
    find the number of games played by group each date sorted in ascending order

    :param group: A group object
    :return: csv of date, date, date..., played, played, played... sorted by 
    date in ascending order limit 10
    """

    games_played = GamePlayed.objects.all().filter(group__name__exact=group.name)

    dateDict = dict()
    for game in games_played:
        date = str(game.date)
        if date not in dateDict:
            dateDict[date] = 0
        dateDict[date] += 1

    dateList = list()
    for date in dateDict:
        dateList.append([date, dateDict[date]])
    dateList = sorted(dateList, key=lambda x: (x[0]))
    if len(dateList) < 10:
        return False
    else:
        dateList = dateList[-10:]

    result = str()
    for i in range(10):
        result += (str(dateList[i][0]) + ", ")
    for j in range(9):
        result += (str(dateList[j][1]) + ", ")
    result += str(dateList[9][1])

    return result


def top_5_winners_by_group(group):
    """
    get the top 5 winners in a group

    :param group: A group object
    :return: csv of username, username..., wins, wins... sorted by wins in 
    descending order limit 5
    """

    games_played = GamePlayed.objects.all().filter(group__name__exact=group.name)

    winDict = dict()
    for game in games_played:
        for winner in game.winners.all():
            if winner.user.username not in winDict:
                winDict[winner.user.username] = 0
            winDict[winner.user.username] += 1

    winList = list()
    for winner in winDict:
        winList.append([winner, winDict[winner]])
    winList = sorted(winList, key=lambda x: (x[1]))
    if len(winList) < 5:
        return False
    else:
        winList = winList[-5:]
    winList = sorted(winList, key=lambda x: (-x[1]))

    result = str()
    for i in range(5):
        result += (str(winList[i][0]) + ", ")
    for j in range(4):
        result += (str(winList[j][1]) + ", ")
    result += str(winList[4][1])

    return result


def top_5_games_by_group(group):
    """
    find the top 5 games played by a group

    :param group: A group object
    :return: a csv of game name, game name..., times played, times played...
    sorted by times played in descending order limit 5
    """

    games_played = GamePlayed.objects.all().filter(group__name__exact=group.name)

    gameDict = dict()
    for game in games_played:
        if game.game.name not in gameDict:
            gameDict[game.game.name] = 0
        gameDict[game.game.name] += 1

    gameList = list()
    for game in gameDict:
        gameList.append([game, gameDict[game]])
    gameList = sorted(gameList, key=lambda x: (x[1]))

    if len(gameList) < 5:
        return False
    else:
        gameList = gameList[-5:]

    result = str()
    for i in range(5):
        result += (str(gameList[i][0]) + ", ")
    for j in range(4):
        result += (str(gameList[j][1]) + ", ")
    result += str(gameList[4][1])

    return result


def games_played_by_player_by_day(player):
    """
    find the number of games played by player each date sorted in ascending order

    :param player: A Player object
    :return: csv of date, date, date..., played, played, played... sorted by 
    date in ascending order limit 5
    """

    games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.username)

    dateDict = dict()
    for game in games_played:
        date = str(game.date)
        if date not in dateDict:
            dateDict[date] = 0
        dateDict[date] += 1

    dateList = list()
    for date in dateDict:
        dateList.append([date, dateDict[date]])
    dateList = sorted(dateList, key=lambda x: (x[0]))
    if len(dateList) < 5:
        return False
    else:
        dateList = dateList[-5:]

    result = str()
    for i in range(5):
        result += (str(dateList[i][0]) + ", ")
    for j in range(4):
        result += (str(dateList[j][1]) + ", ")
    result += str(dateList[4][1])

    return result


def wins_by_player_by_game(player):
    """
    find the top 5 games that the player wins

    :param player: A Player object
    :return: csv of game name, game name..., wins, wins... sorted by wins in
    descending order limit 5
    """

    games_played = GamePlayed.objects.all().filter(winners__user__username__exact=player.user.username)

    winDict = dict()
    for game in games_played:
        if game.game.name not in winDict:
            winDict[game.game.name] = 0
        winDict[game.game.name] += 1

    winList = list()
    for game in winDict:
        winList.append([game, winDict[game]])
    winList = sorted(winList, key=lambda x: (x[1]))

    if len(winList) < 5:
        return False
    else:
        winList = winList[-5:]
    winList = sorted(winList, key=lambda x: (-x[1]))

    result = str()
    for i in range(5):
        result += (str(winList[i][0]) + ", ")
    for j in range(4):
        result += (str(winList[j][1]) + ", ")
    result += str(winList[4][1])

    return result


def top_5_games_by_player(player):
    """
    find the top 5 game that the player plays

    :param player: A Player object
    :return: csv of game name, game name..., times played, times played... 
    sorted by times played in ascending order limit 5
    """

    games_played = GamePlayed.objects.all().filter(players__user__username__exact=player.user.username)

    gameDict = dict()
    for game in games_played:
        if game.game.name not in gameDict:
            gameDict[game.game.name] = 0
        gameDict[game.game.name] += 1

    gameList = list()
    for game in gameDict:
        gameList.append([game, gameDict[game]])
    gameList = sorted(gameList, key=lambda x: (x[1]))

    if len(gameList) < 5:
        return False
    else:
        gameList = gameList[-5:]

    result = str()
    for i in range(5):
        result += (str(gameList[i][0]) + ", ")
    for j in range(4):
        result += (str(gameList[j][1]) + ", ")
    result += str(gameList[4][1])

    return result



