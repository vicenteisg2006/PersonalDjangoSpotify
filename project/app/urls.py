from django.urls import path
from . import views

#urls que reconoce la app
urlpatterns = [
    #principal
    path('', views.loginPage, name='login'),        

    #genericos
    path('dashboard/', views.admin, name='dashboard'),

    #Variantes (Usan alguna base)
    path('userV/<int:perfil_id>', views.userV, name='userV'),      ##
    path('playlistV/<int:perfil_id>', views.playlistV, name='playlistV'),

    path('api/artist/songs/', views.get_artist_songs, name='get_artist_songs'),
    path('playlist/listen/', views.listen_playlist, name='listen_playlist'),

    path('artistV/<int:perfil_id>', views.artistV, name='artistV'),
    path('artist-songs/<int:perfil_id>', views.artist_songs, name='artist_songs'),
    path('upload/song/<int:perfil_id>', views.upload_song, name='upload_song'),
    path('create/album/<int:perfil_id>', views.create_album, name='create_album'),

    path('moder/<int:perfil_id>', views.moder, name='moder'),
    path('funcionBan/<int:perfil_id>', views.moderate, name='moderate'),
    path('moderador/data/<str:chart_id>/', views.get_moder_data, name='moder_data'),
    path('moder/update_status/<int:moderator_perfil_id>', views.update_moderation_status, name='update_moderation_status'),



    #playlist
    # path('playlist/', views.playlist, name='playlist'),

    #prototipos

    # crear playlist
    path('create-playlist/<int:perfil_id>', views.create_playlist, name='create_playlist'),
    path('add-song/', views.add_song, name='add_song'),
    path('remove-song/', views.remove_song, name='remove_song'),

    path('userStatsV/<int:perfil_id>', views.userStatsV, name='userStatsV'),

]