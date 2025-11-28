from django.contrib import admin
from .models import PERFIL
from .models import Playlist, Song, PlaylistSong

# Register your models here.
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['song_text', 'img_src', 'created_at', 'get_playlists_count']
    search_fields = ['song_text']
    list_filter = ['created_at']
    
    def get_playlists_count(self, obj):
        return obj.playlists.count()
    get_playlists_count.short_description = 'Playlists'

class PlaylistSongInline(admin.TabularInline):
    model = PlaylistSong
    extra = 1
    autocomplete_fields = ['song']

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'get_songs_count']
    search_fields = ['name']
    list_filter = ['created_at']
    inlines = [PlaylistSongInline]
    
    def get_songs_count(self, obj):
        return obj.songs.count()
    get_songs_count.short_description = 'Canciones'

@admin.register(PlaylistSong)
class PlaylistSongAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'song', 'added_at', 'order']
    list_filter = ['playlist', 'added_at']
    search_fields = ['playlist__name', 'song__song_text']
    ordering = ['playlist', 'order', 'added_at']

admin.site.register(PERFIL)
