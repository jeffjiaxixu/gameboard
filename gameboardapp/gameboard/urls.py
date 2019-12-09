from django.urls import path
from gameboard.views import index, import_scores, game_page, group_page, data_entry, player, gb_logout, \
    gb_register_login, edit_player, group_page_graph,edit_group
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # Main page reference
    path('', index, name="index"),

    # Sets up database
    path('import', import_scores, name="import"),

    # Player specific pages
    path('player', player, name="player"),
    path('player/<slug:player>', player, name="player"),
    path('edit_player', edit_player, name="edit_player"),

    # Group Pages
    path('group_page', group_page, name="group_page"),
    path('game_page', game_page, name="game_page"),
    path('group_page_graph', group_page, name="group_page_graph"),
    path('edit_group', edit_group, name="edit_group"),

    # Site functionality
    path('logout', gb_logout, name="logout"),
    path('register_login', gb_register_login, name="register_login"),
    path('data_entry', data_entry, name="data_entry")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)