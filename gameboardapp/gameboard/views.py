from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from gameboard.forms import LoginForm, RegisterForm, DataEntryForm, EditForm, EditGroupForm
from gameboard.helpers.import_helper import ImportScores
from gameboard.helpers.queries import *
from gameboard.models import Player, GamePlayed, Game, PlayerGroup, DashboardConfiguration


""" Helper functions """


def get_user_info(request):
    """
    A helper function which uses the user information in the request to get the Player object (which also contains the
    user object).

    :param request: A html request with user data (specifically username)
    :return: None if no user found, otherwise the Player object.
    """
    try:
        user = request.user
        if user.is_anonymous:
            return None
        else:
            return Player.objects.filter(user__username=user.username).first()
    except KeyError:
        return None


def get_user_info_by_username(username):
    """
    A helper function which uses the user information in the request to get the Player object (which also contains the
    user object).

    :param username: A html request with user data (specifically username)
    :return: None if no user found, otherwise the Player object.
    """
    try:
        return Player.objects.filter(user__username=username).first()
    except KeyError:
        return None


def find_recent_games(games):
    """
    Finds 9 of the most recent games, and appends their information into a list.

    :param games: The games to sort through to get information from.
    :return: A list of lists, containing the index and game information.
    """
    recent_games = []
    counter = 0
    index = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    for i in games:
        game = []
        game.append(i)
        game.append(index[counter])
        recent_games.append(game)
        counter += 1
        if counter == 9:
            break
    return recent_games

def is_player_admin(group, player):
    """
    Determines if a player is an admin in a group or not.

    :param group: Thr group object to check
    :param player: The player object to check against
    :return: A boolean value
    """
    admins = group.admins.all()
    for admin in admins:
        if player.user.username == admin.user.username:
            return True
    return False

""" Non login required functions """


def index(request):
    """
    The index page for the game board application. This is a landing page encouraging new users to sign up. If they are
    signed in, redirect them to their dashboard.

    :param request: The user's request.
    :return: A rendering of a web page for the user to interact with. Either a splash page or a redirect.
    """
    if not request.user.is_authenticated:
        return render(request, "index.html", {"data": "data"})
    else:
        return HttpResponseRedirect(reverse(player))


def import_scores(request):
    """
    Requests the user for a CSV file, which is then used to generate a new group and populate it with data. An example
    file that can be used can be found at <project root>/src/gameboardapp/gameboard/static/dataset.csv

    :param request: The user's request.
    :return: A redirect to the index page, once the import is complete.
    """
    ImportScores()

    return HttpResponseRedirect(reverse(index))


def gb_register_login(request):
    """
    A page for registering or logging into the website. Requires a form to be filled out with valid data before the user
    is created.

    :param request: A html request. Must contain a post function to have the page react to the user's input.
    :return: A render template containing the register/login page. On success, a link to the index page.
    """
    # Don't need to render this page if the user is already logged in.
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(player))

    # Setup dictionary with data to be returned with render
    data = dict()

    # Get submit type

    if request.method == "POST":
        submit_type = request.POST.get('submit', None)
    else:
        submit_type = None

    # Setup basic forms
    register_form = RegisterForm(prefix='register')
    login_form = LoginForm(prefix='login')

    # Only do things if the user has submitted data
    if request.method == "POST":
        if submit_type == 'register':
            # Create the form using the request
            register_form = RegisterForm(request.POST, prefix='register')

            profile_image = None
            if "photo" in request.FILES:
                profile_image = request.FILES['photo']

            # Check if the data is valid
            if register_form.is_valid():
                # Get the relevant cleaned data for creating a user
                first_name = register_form.cleaned_data['first_name']
                last_name = register_form.cleaned_data['last_name']
                username = register_form.cleaned_data['username']
                password = register_form.cleaned_data['password']

                # Create the django user object
                u = User(first_name=first_name, last_name=last_name, username=username, password=password)
                u.save()

                # Set it's password (for some reason providing the password doesnt work, have to set it again)
                u.set_password(password)
                u.save()

                # Tie the user to the player user object
                dashboard_configuration = DashboardConfiguration.objects.filter(type="default").first()
                p = Player(user=u, dashboard_configuration=dashboard_configuration)
                if profile_image:
                    p.profile_image = profile_image
                    p.save()
                p.save()
                p.user.save()

                # Login the user, and send them to the index page
                login(request, u)
                return HttpResponseRedirect(reverse(index))

        # Only work with login form if the register form has not been filled out.
        if submit_type == 'login' and not register_form.is_valid():
            login_form = LoginForm(request.POST, prefix='login')

            # Check if the data is valid
            if login_form.is_valid():
                # Get the relevant cleaned data for creating a user
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']

                # Authenticate the user, then log them in.
                user = authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)

                    # Send the user to the index page
                    return HttpResponseRedirect(reverse(index))

    # Set the data to whatever was figured out above
    data['register_form'] = register_form
    data['login_form'] = login_form

    # Render the page
    return render(request, "register_login.html", data)


""" Login required functions """


@login_required
def gb_logout(request):
    """
    A simple logout function.

    :param request: A html request, which contains the user's info.
    :return: A link to the index page.
    """
    logout(request)
    return HttpResponseRedirect(reverse(index))


@login_required
def player(request, player=None, message=None):
    """
    The player's main page, to be shown upon login.

    :param request: A html request.
    :type player: String
    :param player: A player's username (for looking at other players, not yourself)
    :param message: A message to display on the page in the case of an error.
    :return: A rendering of a web page for the user to interact with.
    """
    # Get game board user
    gb_user = get_user_info(request)

    # Setup dictionary with data to be returned with render
    data = dict()

    # Check if we are looking at another user, or ourselves
    if not player:
        # TODO show error message
        player = gb_user
    else:
        player = get_user_info_by_username(player)

    # Get user stats
    win_percentage = round(find_win_percentage(player), 4)
    num_played = num_games_played(player)
    num_wins = find_wins(player)
    num_losses = find_losses(player)
    games_played = find_games_played(player)
    fav_game = find_favorite_game(player)
    games_played_by_date = games_played_by_player_by_day(player)
    if games_played_by_date == False:
        games_played_by_date = "sample, data, play, more, games, 7, 8, 10, 2, 5"
    wins_by_game = wins_by_player_by_game(player)
    if wins_by_game == False:
        wins_by_game = "sample, data, play, more, games, 12, 7, 7, 5, 2"
    top_5_games = top_5_games_by_player(player)
    if top_5_games == False:
        top_5_games = "sample, data, play, more, games, 12, 7, 7, 5, 2"

    player_stats = {"win_percentage": win_percentage, 'num_played': num_played,
                    'num_wins': num_wins, 'num_losses': num_losses,
                    'games_played': games_played, 'fav_game': fav_game,
                    'games_played_by_date': games_played_by_date,
                    'wins_by_game': wins_by_game,
                    'top_5_games': top_5_games}

    found_groups = find_groups(player)
    groups = []
    for group in found_groups:
        group_json = {}
        group_json["name"] = group.name
        group_json["players"] = find_players_in_group(group)
        group_json["admins"] = find_admins_in_group(group)
        groups.append(group_json)

    # Return stats with page
    data["stats"] = player_stats
    data["groups"] = groups
    data["player"] = player
    data["message"] = message
    return render(request, "profile.html", data)


@login_required
def group_page(request, message=None):
    """
    The group page, which contains statistics, graphs, and players within a group.

    :param request: A html request.
    :param message: A message to display on the page in the case of an error.
    :return:
    """
    gb_user = get_user_info(request)
    group = find_first_group(gb_user)
    if not group:
        print("go back to group")
        return player(request, gb_user, "You are not in a group")
    group_name = group.name

    players = group.players.all()
    admins = group.admins.all()

    # Generate grou
    games = find_games_by_group(group)
    recent_games = find_recent_games(games)
    num_games_played = len(games)
    (best_player, best_player_win_rate) = find_best_player_in_group(group)
    best_player_win_rate = round(best_player_win_rate, 2)
    (longest_win_streak_player, longest_win_streak) = find_longest_win_streak_in_group(group)
    if longest_win_streak_player == None:
        longest_win_streak_player = ''
        longest_win_streak = 'No Win Streak Yet!'
    (most_active_player, most_active_played) = find_most_active_player_in_group(group)
    (favorite_game, favorite_game_played) = find_favorite_game_in_group(group)
    num_players = find_num_player_in_group(group)
    games_played_by_date = games_played_by_group_by_day(group)
    if games_played_by_date == False:
        games_played_by_date = "sample, data, play, more, games, to, view, your, game, stats, 0, 4, 5, 1, 3, 7, 8, 10, 2, 5"
    top_5_winners = top_5_winners_by_group(group)
    top_5_winners = top_5_winners_by_group(group)
    if top_5_winners == False:
        top_5_winners = "sample, data, play, more, games, 5, 8, 9, 10, 15"
    top_5_games = top_5_games_by_group(group)
    if top_5_games == False:
        top_5_games = "sample, data, play, more, games, 2, 5, 7, 8, 12"

    data = {'group_name': group_name, 'players': players, 'admins': admins,
            'recent_games': recent_games, 'best_player': best_player,
            'best_player_win_rate': best_player_win_rate,
            'num_games_played': num_games_played,
            'longest_win_streak_player': longest_win_streak_player,
            'longest_win_streak': longest_win_streak,
            'most_active_player': most_active_player,
            'most_active_played': most_active_played,
            'favorite_game': favorite_game,
            'favorite_game_played': favorite_game_played,
            'num_players': num_players,
            'games_played_by_date': games_played_by_date,
            'games_played_by_date': games_played_by_date,
            'top_5_winners': top_5_winners,
            'top_5_games': top_5_games,
            'message': message}

    return render(request, "group_page.html", {"data": data})


def game_page(request):
    """
    Display information about the specific game.

    :param request: A html request.
    :return:
    """
    if request.method == "POST":
        return render(request, "data_entry.html", {"data": "data"})
    return render(request, "game_page.html", {"data": "data"})


def edit_group(request):
    """
    Edit group information like what players and admins there are, as well as name.

    :param request:
    :return:
    """
    gb_user = get_user_info(request)
    group = find_first_group(gb_user)
    if is_player_admin(group, gb_user) == False:
        print("user is not admin")
        return group_page(request, "You are not an admin, only admins can access that page")

    group_players = find_players_in_group(find_first_group(gb_user))
    group_admins = find_admins_in_group(find_first_group(gb_user))
    all_players = Player.objects.all()

    # this gets a list of all players in the group (admins + players)
    all_group_players_list = []
    all_player_group_set = set()
    for i in range(len(group_players)):
        if gb_user.user.username != group_players[i].user.username:  # cant remove self
            all_player_group_set.add(group_players[i].user.username)
            tpl = (group_players[i].user.username, group_players[i].user.first_name)
            all_group_players_list.append(tpl)

    # gets a list of only admins
    group_admins_list = []
    all_admins = set()
    for i in range(len(group_admins)):
        if gb_user.user.username != group_admins[i].user.username:
            tpl = (group_admins[i].user.username, group_admins[i].user.first_name)
            group_admins_list.append(tpl)
            all_admins.add(group_admins[i].user.username)

    # gets a list of only players that are not admins
    group_players_list = []
    for i in range(len(group_players)):
        if (gb_user.user.username != group_players[i].user.username) and (
                group_players[i].user.username not in all_admins):
            tpl = (group_players[i].user.username, group_players[i].user.first_name)
            group_players_list.append(tpl)

    # players that are not in this group
    not_in_group_list = []
    for i in range(len(all_players)):
        if gb_user.user.username != all_players[i].user.username:
            username = all_players[i].user.username
            if username not in all_player_group_set:
                tpl = (all_players[i].user.username, all_players[i].user.first_name)
                not_in_group_list.append(tpl)
                # remove_player,         make_admin,         add_player,     make_player
    edit_group_form = EditGroupForm(all_group_players_list, group_players_list, not_in_group_list, group_admins_list)

    if request.method == "POST":
        if "group_name" in request.POST and request.POST["group_name"] != "":
            group.name = request.POST["group_name"]
            group.save()
        if "make_admin" in request.POST:
            make_admin_list = request.POST.getlist('make_admin')
            for username in make_admin_list:
                player_obj = Player.objects.filter(user__username__exact=username).first()
                group.admins.add(player_obj)

        if "make_player" in request.POST:
            make_player_list = request.POST.getlist('make_player')
            for username in make_player_list:
                player_obj = Player.objects.filter(user__username__exact=username).first()
                group.admins.remove(player_obj)
                # currgroup = PlayerGroup.objects.filter(players__user__username__exact =  username).first()
                # group.players.add(player_obj)

        if "remove_player" in request.POST:
            remove_list = request.POST.getlist('remove_player')
            for username in remove_list:
                player_obj = Player.objects.filter(user__username__exact=username).first()
                # currgroup = PlayerGroup.objects.filter(players__user__username__exact =  username).first()
                group.players.remove(player_obj)
                group.admins.remove(player_obj)

        if "add_player" in request.POST:
            add_list = request.POST.getlist('add_player')
            for username in add_list:
                player_obj = Player.objects.filter(user__username__exact=username).first()
                group.players.add(player_obj)

        # form = EditGroupForm(group_players_list, add_players_list)

        return HttpResponseRedirect(reverse(group_page))
    return render(request, "edit_group.html", {"form": edit_group_form, "player": gb_user})


@login_required
def data_entry(request):
    """
    A data entry page, which allows the user to enter a new game played.

    :param request: The user's request.
    :return: A rendering of a web page for the user to interact with.
    """
    # Get user
    gb_user = get_user_info(request)

    # Get ready with the data to send to the front end
    data = dict()

    data_entry_form = DataEntryForm()
    # Only do things if the user has submitted data
    if request.method == "POST":
        # Create the form using the request
        data_entry_form = DataEntryForm(request.POST)

        # Check if the data is valid
        if data_entry_form.is_valid():
            group = find_groups(gb_user).first()
            game = data_entry_form.cleaned_data.get('game')
            date = data_entry_form.cleaned_data.get('date')
            players = data_entry_form.cleaned_data.get('players').split(",")
            winners = data_entry_form.cleaned_data.get('winners').split(",")

            # Valid, so add the new game played object
            game_played = GamePlayed()
            game_played.game = Game.objects.get(name__exact=game)
            game_played.date = date
            game_played.group = group
            game_played.save()

            for player in players:
                game_played.players.add(Player.objects.get(user__username__exact=player))
            for winner in winners:
                game_played.winners.add(Player.objects.get(user__username__exact=winner))

            response = JsonResponse({})
            response.status_code = 200
            return response
        else:
            # Non valid form, render it on the page
            response = JsonResponse({"error": data_entry_form.errors})
            response.status_code = 400
            return response

    # Store the data and send to the view.
    data['data_entry_form'] = data_entry_form
    data['all_games'] = find_games()
    data['all_players'] = find_players_in_group(find_groups(gb_user).first())
    return render(request, "data_entry.html", data)


@login_required
def edit_player(request):
    """
    Edit player information, like username, name, password, and upload profile images.

    :param request: A html request, that needs a post request to submit data.
    :return: A rendering of the edit player page.
    """
    # Get user
    gb_user = get_user_info(request)

    # Get ready with the data to send to the front end
    data = dict()

    edit_form = EditForm(gb_user.user.username)
    # Only do things if the user has submitted data
    if request.method == "POST":
        # Create the form using the request
        edit_form = EditForm(gb_user.user.username, request.POST)

        profile_image = None
        if "photo" in request.FILES:
            profile_image = request.FILES['photo']
        # profile_image = request.FILES['profile_image']
        # Check if the data is valid
        if edit_form.is_valid():
            # Get the relevant cleaned data for creating a user
            username = edit_form.cleaned_data['username']
            first_name = edit_form.cleaned_data['first_name']
            last_name = edit_form.cleaned_data['last_name']
            password = edit_form.cleaned_data['password']

            # print("profile image is ",username, profile_image)

            if username:
                gb_user.user.username = username
            if first_name:
                gb_user.user.first_name = first_name
            if last_name:
                gb_user.user.last_name = last_name
            if password:
                gb_user.user.set_password(password)
            if profile_image:
                gb_user.profile_image = profile_image
                gb_user.save()
            gb_user.user.save()
            # print("users are ",account.objects.get(username="Keegan"))
            login(request, gb_user.user)
            return HttpResponseRedirect(reverse(index))

    data['edit_player_form'] = edit_form
    return render(request, "edit_player.html", data)


def group_page_graph(request):
    """
    Displays graphs from the group page.

    :param request: A html request.
    :return: Json data for the graphs
    """
    gb_user = get_user_info(request)
    group = find_first_group(gb_user)
    games_played_by_date = games_played_by_group_by_day(group)

    data = {"games_played_by_date": games_played_by_date}
    return JsonResponse(data)
