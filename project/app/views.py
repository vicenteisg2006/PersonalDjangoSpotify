#Imports generales
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta, date
import json

#Imports model y form para mensajes moderador
from .models import PERFIL, REGISTRO_MODERADOR
from .forms import alertaMODERADORForm, RegistroModeradorForm

#Imports modelos para playlist
from .models import Playlist, Song, PlaylistSong, Album, MonthlyStreamRecord, CANCION_REPRODUCCION, UbicacionGeo



#                                                   ==========================
#                                                   ========== LOGIN ==========
#                                                   ==========================

def loginPage(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")

            try:
                perfil = PERFIL.objects.get(username=username, password=password)

                if perfil.estado_moderacion == 'ban':
                    error_msg = "Acceso denegado, su cuenta ha sido baneada"
                    return render(request, "0_login/login.html", {"error": error_msg})

                if perfil.rol == "user":
                    return redirect("userV", perfil_id = perfil.id)
                elif perfil.rol == "artist":
                    return redirect("artistV", perfil_id = perfil.id)
                elif perfil.rol == "administrator":
                    return redirect("dashboard",)
                elif perfil.rol == "moderator":
                    return redirect("moder", perfil_id = perfil.id)
                
            except PERFIL.DoesNotExist:
                error_msg = "Invalid credentials, please try again."
                return render(request, "0_login/login.html", {"error": error_msg})

        elif form_type == "register":
            new_username = request.POST.get("new_username")
            new_password = request.POST.get("new_password")
            new_name = request.POST.get('new_name')
            new_rol = request.POST.get("new_rol")
            new_ubicacion = request.POST.get("new_ubicacion")

            if PERFIL.objects.filter(username=new_username).exists():
                error_msg = "Username already exists. Please choose a different one."
                return render(request, "0_login/login.html", {"error": error_msg})
            else:
                PERFIL.objects.create(username=new_username, password=new_password, rol=new_rol, nombre=new_name, ubicacion = new_ubicacion)
                success_msg = "Registration successful! You can now log in."
                return render(request, "0_login/login.html", {"success": success_msg})
    return render(request, '0_login/login.html')







#                                                   ==========================
#                                                   ========= ARTISTA =========
#                                                   ==========================

def artistV(request, perfil_id): #Variante artista -> usando BaseKA
    listeners_chart = {'labels': ['Jan', 'Feb', 'Mar'], 'values': [18000, 22500, 25500]}
    continental_data = {'Jan': {'Asia': 10000, 'Africa': 10000, 'America': 35000, 'Europa': 40000, 'Oceania': 25000}}
    continental_listeners_data = {'Jan': {'Asia': 1500, 'Africa': 1500, 'America': 5250, 'Europa': 6000, 'Oceania': 3750}}

    perfil = get_object_or_404(PERFIL, id=perfil_id, rol='artist')

    all_artist_reproductions = CANCION_REPRODUCCION.objects.filter(song__artist=perfil)
    
    total_streams_count = all_artist_reproductions.count() 
    
    top_songs_data = Song.objects.filter(artist=perfil).annotate(
        streams=Count('reproductions') 
    ).order_by('-streams')[:5]
    
    monthly_streams_data = all_artist_reproductions.annotate(
        month=TruncMonth('fecha_reproduccion') 
    ).values('month').annotate(total_streams=Count('id')).order_by('month')

    streams_chart = {
        'labels': [record['month'].strftime('%b') for record in monthly_streams_data], 
        'values': [record['total_streams'] for record in monthly_streams_data],
    }

    album_streams_data = Song.objects.filter(artist=perfil).values('album__title').annotate(
        total_album_streams=Count('reproductions') 
    ).order_by('-total_album_streams')
    
    albums_chart = {
        'labels': [item['album__title'] for item in album_streams_data if item['album__title']],
        'data': [item['total_album_streams'] for item in album_streams_data if item['album__title']],
        'backgroundColor': ['#FF6B9D', '#4ECDC4', '#FFD93D', '#95E1D3', '#C77DFF', '#00F5FF'], 
    }

    context = {
        'perfil': perfil,
        'perfil_id': perfil_id,
        'artist_name': perfil.nombre, 
        
        'total_streams': total_streams_count,
        'top_songs': top_songs_data, 
        
        'streams_chart': json.dumps(streams_chart),
        'albums_chart': json.dumps(albums_chart),
        
        'monthly_listeners': 456789,
        'followers': 123456,
        'top_viewers': [{'name': 'User1', 'streams': 15000}, {'name': 'User2', 'streams': 12000}], 
        'listeners_chart': json.dumps(listeners_chart),
        'continental_data': json.dumps(continental_data), 
        'continental_listeners_data': json.dumps(continental_listeners_data), 
    }
    
    return render(request, '2_artista/1_artist_v.html', context)




#                                                   ==========================
#                                                   ====  CANCIONES ARTISTA ====
#                                                   ==========================

def artist_songs(request, perfil_id): 
    perfil = get_object_or_404(PERFIL, id=perfil_id, rol='artist')
    
    songs_data_for_table = Song.objects.filter(artist=perfil).annotate(
        streams=Count('reproductions')
    ).order_by('-streams')

    total_songs = songs_data_for_table.count()
    total_streams = songs_data_for_table.aggregate(Sum('streams'))['streams__sum'] or 0

    artist_albums = Album.objects.filter(artist=perfil).order_by('title')
    
    chart_songs = []
    for song in songs_data_for_table:

        total_seconds = int(song.duration.total_seconds()) if song.duration else 0
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        duration_str = f"{minutes:02d}:{seconds:02d}"

        chart_songs.append({
            "name": song.song_text,
            "album": song.album.title if song.album else 'Single',
            "duration": duration_str, 
            "streams": song.streams,
            "release_date": song.created_at.strftime("%Y-%m-%d") 
        })
    
    context = {
        'artist_name': perfil.nombre,
        'perfil_id': perfil.id,
        'total_songs': total_songs,
        'total_streams': total_streams,
        'songs': songs_data_for_table, 
        'albums': artist_albums,        
        'songsDataJson': json.dumps(chart_songs), 
    }
    return render(request, '2_artista/artist_songs.html', context)



#                                                   ==========================
#                                                   ==  SUBIR CANCION ARTISTA ==
#                                                   ==========================

def upload_song(request, perfil_id):

    REDIRECT_SUCCESS_URL = 'artist_songs'
    
    if request.method == 'POST':
        try:

            artist_perfil = PERFIL.objects.get(id=perfil_id, rol='artist') 
        except PERFIL.DoesNotExist:
            return redirect('loginPage') 

        song_text = request.POST.get('song_text')
        img_src = request.POST.get('img_src')
        album_id = request.POST.get('album_id')
        
        duration_text = request.POST.get('duration')
        
        song_duration = None
        if duration_text and ':' in duration_text:
            try:
                minutes, seconds = map(int, duration_text.split(':'))
                song_duration = timedelta(minutes=minutes, seconds=seconds)
            except ValueError:
                pass 
        
        try:
            selected_album = Album.objects.get(id=album_id, artist=artist_perfil)
        except Album.DoesNotExist:
            return redirect(REDIRECT_SUCCESS_URL, perfil_id=perfil_id) 

        try:
            Song.objects.create(
                song_text=song_text,
                img_src=img_src,
                album=selected_album,
                artist=artist_perfil, 
                duration=song_duration, 
            )
        except Exception as e:
            print(f"ERROR: Fallo al crear canción: {e}")
            return redirect(REDIRECT_SUCCESS_URL, perfil_id=perfil_id) 

        return redirect(REDIRECT_SUCCESS_URL, perfil_id=perfil_id) 
        
    return redirect(REDIRECT_SUCCESS_URL, perfil_id=perfil_id)



#                                                   ==========================
#                                                   === SUBIR ALBUM ARTISTA ====
#                                                   ==========================

def create_album(request, perfil_id): 
    REDIRECT_URL = 'artist_songs' 
    
    if request.method == 'POST':
        try:
            artist_perfil = PERFIL.objects.get(id=perfil_id, rol='artist')
        except PERFIL.DoesNotExist:
            return redirect('loginPage') 

        title = request.POST.get('title')
        release_date_str = request.POST.get('release_date')
        cover_art_url = request.POST.get('cover_art_url')

        release_date = date.fromisoformat(release_date_str) if release_date_str else None
        
        try:
            Album.objects.create(
                title=title,
                release_date=release_date,
                cover_art_url=cover_art_url,
                artist=artist_perfil 
            )
        except Exception as e:
            print(f"ERROR: Fallo al crear álbum: {e}")
            return redirect(REDIRECT_URL, perfil_id=perfil_id)

        return redirect(REDIRECT_URL, perfil_id=perfil_id) 
        
    return redirect(REDIRECT_URL, perfil_id=perfil_id)




#                                                   ==========================
#                                                   ========= USUARIO =========
#                                                   ==========================

def userV(request, perfil_id): #Variante -> usando BaseK
    perfil = PERFIL.objects.get(id=perfil_id)
    mensajes = REGISTRO_MODERADOR.objects.filter(perfil_afectado=perfil).order_by('-fecha')
    context = {
        'perfil': perfil,
        'mensajes': mensajes,
    }

    return render(request, '1_usuario/1_user_v.html', context)







# ========== COMPLEMENTOS USUARIOS ==========

def playlistV(request, perfil_id): #Variante playlist -> usando BaseK
    perfil = PERFIL.objects.get(id=perfil_id)

    load_playlist_id = request.GET.get('playlist_id')
    
    if load_playlist_id:
        request.session['active_playlist_id'] = int(load_playlist_id)
    
    playlist_id = request.session.get('active_playlist_id')
    playlist_obj = None
    songs_list = []
    
    if playlist_id:
        try:
            playlist_obj = Playlist.objects.get(id=playlist_id)
            songs_list = list(playlist_obj.songs.values('id', 'song_text', 'img_src'))
        except Playlist.DoesNotExist:
            request.session.pop('active_playlist_id', None)
    
    all_playlists = Playlist.objects.all()
    
    context = {
        'placeholder_text': 'Ingresa el nombre de tu playlist',
        'playlist_name': playlist_obj.name if playlist_obj else None,
        'songs': json.dumps(songs_list),
        'all_playlists': all_playlists,
        'perfil': perfil,
    }
    return render(request, '1_usuario/2_funcionPlaylist_v.html', context)

def userStatsV(request, perfil_id):
    perfil = get_object_or_404(PERFIL, id=perfil_id)
    mensajes = REGISTRO_MODERADOR.objects.filter(perfil_afectado=perfil).order_by('-fecha')

    return render(request, "1_usuario/dashboardUser.html", {
        'perfil': perfil,
        'mensajes': mensajes
    })








#                                                   ==========================
#                                                   ====== ADMINISTRADOR ======
#                                                   ==========================
def admin(request): #Administrador
    return render(request, '3_admin/admin.html')

def moder(request, perfil_id): #Moderador
    perfil = get_object_or_404(PERFIL, id=perfil_id, rol='moderator')

    moderated_statuses = Q(estado_moderacion='alerta') | Q(estado_moderacion = 'ban')

    n_alertas = PERFIL.objects.filter(estado_moderacion = 'alerta').count()
    n_baneos = PERFIL.objects.filter(estado_moderacion = 'ban').count()
    all_moderated_profiles = PERFIL.objects.filter(moderated_statuses)
    u_moderados = all_moderated_profiles.filter(rol='user').count()
    a_moderados = all_moderated_profiles.filter(rol='artist').count()
    n_pendientes = PERFIL.objects.filter(estado_moderacion = 'en_espera').count()
    n_finalizados = all_moderated_profiles.count()

    context = {
        'perfil': perfil,
        'n_alertas': n_alertas,
        'n_baneos': n_baneos,
        'u_moderados': u_moderados,
        'a_moderados': a_moderados,
        'n_pendientes': n_pendientes,
        'n_finalizados': n_finalizados,
    }

    return render(request, '4_moderador/1_moderHome.html', context)


# ========== COMPLEMENTOS ADMINISTRADOR ==========
CONTINENT_MAP = {
    'America': (54.52, -105.25, 'América Global'), 
    'Europa': (54.52, 15.25, 'Europa'),
    'Asia': (34.04, 100.61, 'Asia'),
    'Africa': (-0.02, 17.15, 'África'),
    'Oceania': (-25.27, 133.77, 'Oceanía'),
}

def get_monthly_trend_data(status_values, target_role=None):
    six_months_ago = date.today() - timedelta(days=180)

    query = REGISTRO_MODERADOR.objects.filter(
        action_status__in=status_values,
        fecha__gte=six_months_ago
    )
    
    if target_role:
        query = query.filter(perfil_afectado__rol=target_role)
    
    monthly_data = REGISTRO_MODERADOR.objects.filter(
        action_status__in=status_values,
        fecha__gte=six_months_ago
    ).annotate(
        month_start=TruncMonth('fecha')
    ).values('month_start').annotate(
        total=Count('id')
    ).order_by('month_start')

    labels = [m['month_start'].strftime('%b') for m in monthly_data]
    data_values = [m['total'] for m in monthly_data]
    
    return labels, data_values


def get_globe_data(status_values, target_role=None):
    q_filter = Q(estado_moderacion__in=status_values)
    
    if target_role:
        q_filter &= Q(rol=target_role)

    continent_counts = PERFIL.objects.filter(q_filter).values('ubicacion').annotate(
        value=Count('id')
    )
    
    globe_data = []
    for count_item in continent_counts:
        ubicacion_db = count_item['ubicacion']
        count_value = count_item['value']
        coords = CONTINENT_MAP.get(ubicacion_db)
        
        if coords:
            lat, lon, title = coords
            
            globe_data.append({
                'title': title,
                'lat': lat,
                'lon': lon,
                'value': count_value
            })
            
    return globe_data


STATUS_ALERTA = ['ALERT']
STATUS_BAN = ['BAN']
STATUS_MODERADO = ['ALERT', 'BAN']
STATUS_PENDIENTE = ['En_espera']


def get_moder_data(request, chart_id): 
    

    if chart_id == 'graph-card-1':
        status = STATUS_ALERTA
        role = None
        color = '#8EFAB4'
        title_g1 = 'Alertas por Continente'
        title_g2 = 'Alertas en los últimos 6 meses'
        
    elif chart_id == 'graph-card-2': 
        status = STATUS_BAN
        role = None
        color = '#FF6384'
        title_g1 = 'Baneos por Continente'
        title_g2 = 'Baneos en los últimos 6 meses'

    elif chart_id == 'graph-card-3':
        status = STATUS_MODERADO
        role = 'user'
        color = '#36A2EB'
        title_g1 = 'Usuarios Moderados por Continente'
        title_g2 = 'Usuarios Moderados en los últimos 6 meses'
        
    elif chart_id == 'graph-card-4': 
        status = STATUS_MODERADO
        role = 'artist'
        color = '#FFCE56'
        title_g1 = 'Artistas Moderados por Continente'
        title_g2 = 'Artistas Moderados en los últimos 6 meses'

        globe_data = get_globe_data(status, target_role=role) 
        labels, data_values = get_monthly_trend_data(status, target_role=role)

    elif chart_id == 'graph-card-5':
        status = STATUS_PENDIENTE
        role = None
        color = '#FFCE56'
        title_g1 = 'Alertas Pendientes por Continente'
        title_g2 = 'Detalle Alertas Pendientes'

        globe_data = get_globe_data(status, target_role=role)
        
        grafico_1_data = get_globe_data(status, target_role=role)
        return JsonResponse({
            'grafico_1_data': grafico_1_data,
            'grafico_2_data': {
                'title': title_g2,
                'type': 'bar',
                'labels': ['Mal Uso', 'Hackeo', 'Pirateo', 'Cont. Inapropiado'],
                'options': { 'scales': { 'x': { 'stacked': True }, 'y': { 'stacked': True } } },
                'datasets': [
                    {'label': 'Reportes de Usuario', 'data': [12, 19, 3, 5], 'backgroundColor': '#36A2EB'},
                    {'label': 'Reportes de Artista', 'data': [8, 10, 2, 4], 'backgroundColor': '#FFCE56'},
                ]
            }
        })

    elif chart_id == 'graph-card-6': 
        status = STATUS_MODERADO
        role = None
        color = '#36A2EB'
        title_g1 = 'Alertas Realizadas por Continente'
        title_g2 = 'Detalle Alertas Finalizadas'
        
        grafico_1_data = get_globe_data(status, target_role=role)
        return JsonResponse({
            'grafico_1_data': grafico_1_data,
            'grafico_2_data': {
                'title': title_g2,
                'type': 'bar',
                'labels': ['Mal Uso', 'Hackeo', 'Pirateo', 'Cont. Inapropiado'],
                'options': { 'scales': { 'x': { 'stacked': True }, 'y': { 'stacked': True } } },
                'datasets': [
                    {'label': 'Reportes de Usuario', 'data': [120, 190, 30, 50], 'backgroundColor': '#36A2EB'},
                    {'label': 'Reportes de Artista', 'data': [80, 100, 20, 40], 'backgroundColor': '#FFCE56'},
                ]
            }
        })
    
    globe_data = get_globe_data(status, target_role=role)
    labels, data_values = get_monthly_trend_data(status)
    
    grafico_1_data = {'title': title_g1, 'type': 'globe', 'data': globe_data}
    grafico_2_data = {
        'title': title_g2,
        'type': 'line', 
        'labels': labels,
        'datasets': [{'label': 'Total', 'data': data_values, 'borderColor': color, 'tension': 0.2}]
    }

    data = {'grafico_1_data': grafico_1_data, 'grafico_2_data': grafico_2_data}
    return JsonResponse(data)


def moderate(request, perfil_id): #banear
    perfil = get_object_or_404(PERFIL, id=perfil_id, rol='moderator')
    
    target_profiles = PERFIL.objects.filter(
        Q(rol='user') | Q(rol='artist')
    ).order_by('username')
    
    form = RegistroModeradorForm()
    
    
    context = {
        'perfil': perfil,
        'perfil_moderador': perfil,
        'target_profiles': target_profiles, 
        'form': form, 
    }

    return render(request, '4_moderador/2_funcionBan.html', context)

def update_moderation_status(request, moderator_perfil_id):
    REDIRECT_URL = 'moder' 
    
    if request.method == 'POST':
        try:
            moderator_perfil = PERFIL.objects.get(id=moderator_perfil_id, rol='moderator')
        except PERFIL.DoesNotExist:
            return redirect('loginPage') 

        target_perfil_id = request.POST.get('target_perfil_id')
        new_status = request.POST.get('new_status')
        reason_text = request.POST.get('reason') 

        if not target_perfil_id or not new_status:
            return redirect(REDIRECT_URL, perfil_id=moderator_perfil_id) 

        try:
            target_perfil = PERFIL.objects.get(id=target_perfil_id)
            
            target_perfil.estado_moderacion = new_status
            target_perfil.save() 
            
            REGISTRO_MODERADOR.objects.create(
                perfil_afectado=target_perfil,
                moderador_emisor=moderator_perfil,
                action_status=new_status,
                reason=reason_text
            )

        except PERFIL.DoesNotExist:
            print(f"Error: Perfil objetivo {target_perfil_id} no encontrado.")
        except Exception as e:
            print(f"Error al guardar el registro de moderación: {e}")
        
        return redirect(REDIRECT_URL, perfil_id=moderator_perfil_id)

    return redirect('moder', perfil_id=moderator_perfil_id)






#                                                   ==========================
#                                                   ========  PLAYLIST  ========
#                                                   ==========================

def playlistV(request, perfil_id): 
    perfil = get_object_or_404(PERFIL, id=perfil_id, rol='user') 

    all_artists = PERFIL.objects.filter(rol='artist').order_by('nombre')
    
    all_playlists = Playlist.objects.filter(owner=perfil).order_by('-created_at')

    DEFAULT_PLAYLIST_IMG = '/static/images/playlist1.jpg'

    for playlist in all_playlists:
        if not playlist.img_src:
            playlist.img_src = DEFAULT_PLAYLIST_IMG

    playlist_obj = None
    songs_list = []
    
    load_playlist_id = request.GET.get('playlist_id')
    
    if load_playlist_id:
        try:
            playlist_obj = Playlist.objects.get(id=int(load_playlist_id), owner=perfil)
            songs_list = list(playlist_obj.songs.values('id', 'song_text', 'img_src'))
        except Playlist.DoesNotExist:
            pass

    if playlist_obj and not playlist_obj.img_src:
        playlist_obj.img_src = DEFAULT_PLAYLIST_IMG
    
    if not playlist_obj and all_playlists.exists():
        playlist_obj = all_playlists.first() 
        songs_list = list(playlist_obj.songs.values('id', 'song_text', 'img_src'))

    context = {
        'placeholder_text': 'Ingresa el nombre de tu playlist',
        'playlist_name': playlist_obj.name if playlist_obj else None,
        'playlist_id': playlist_obj.id if playlist_obj else 0, 
        'songs': json.dumps(songs_list), 
        'all_playlists': all_playlists,
        'perfil': perfil,
        'all_artists': all_artists, 
    }
    return render(request, '1_usuario/2_funcionPlaylist_v.html', context)


#                                                   ==========================
#                                                   = FUNCIONES CREAR PLAYLIST =
#                                                   ==========================

def create_playlist(request, perfil_id): 
    
    if request.method == 'POST':
        try:
            user_perfil = PERFIL.objects.get(id=perfil_id, rol='user')
        except PERFIL.DoesNotExist:
            return redirect('loginPage') 

        playlist_name = request.POST.get('playlist_name')
        img_src = request.POST.get('img_src')
        
        if playlist_name:
            Playlist.objects.create(
                name=playlist_name,
                img_src=img_src,
                owner=user_perfil
            )
            
            return redirect('playlistV', perfil_id=user_perfil.id) 
        
        return redirect('playlistV', perfil_id=user_perfil.id) 

    return redirect('loginPage')


def get_artist_songs(request):
    artist_id = request.GET.get('artist_id')
    
    if not artist_id:
        return JsonResponse({'error': 'No artist ID provided'}, status=400)
    
    try:
        songs_queryset = Song.objects.filter(artist_id=artist_id)
        
        songs_list = []
        for song in songs_queryset:
            img_url = song.img_src if song.img_src else '/static/images/default_1.jpg' 
        
            songs_list.append({
                'id': song.id,
                'song_text': song.song_text,
                'img_src': img_url, 
            })
        
        return JsonResponse({'songs': songs_list})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def listen_playlist(request):
    perfil_id = request.POST.get('perfil_id')
    playlist_id = request.POST.get('playlist_id')
    
    if not perfil_id or not playlist_id:
        return redirect('loginPage') 

    try:
        user_perfil = PERFIL.objects.get(id=perfil_id, rol='user') 
        playlist = Playlist.objects.get(id=playlist_id, owner=user_perfil)
    
        for song in playlist.songs.all():
            CANCION_REPRODUCCION.objects.create(
                song=song,
                listener=user_perfil,
            )
        
        return redirect('playlistV', perfil_id=user_perfil.id)
        
    except (PERFIL.DoesNotExist, Playlist.DoesNotExist):
        return redirect('loginPage')
        
    except Exception as e:
        print(f"Error al registrar reproducción: {e}")
        return redirect('loginPage')
    

def add_song(request):
    if request.method == 'POST':
        perfil_id = request.POST.get('perfil_id') 
        playlist_id = request.POST.get('playlist_id')
        song_id = request.POST.get('song_id')

        if not perfil_id or not playlist_id or not song_id:
            return JsonResponse({'success': False, 'error': 'Missing required IDs'}, status=400)

        try:
            user_perfil = PERFIL.objects.get(id=perfil_id)
            playlist = Playlist.objects.get(id=playlist_id, owner=user_perfil) 
            song = Song.objects.get(id=song_id)
            
            PlaylistSong.objects.get_or_create(playlist=playlist, song=song)
            
            return JsonResponse({
                'success': True, 
                'song_id': song_id, 
                'song_text': song.song_text, 
                'img_src': song.img_src
            })

        except (PERFIL.DoesNotExist, Playlist.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Playlist not found or does not belong to user.'}, status=403)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


def remove_song(request):
    if request.method == "POST":
        playlist_id = request.POST.get('playlist_id') 
        perfil_id = request.POST.get('perfil_id') 
        song_id = request.POST.get('song_id')
        
        if not playlist_id or not perfil_id or not song_id:
            return JsonResponse({'error': 'Missing required IDs'}, status=400)
        
        try:
            user_perfil = PERFIL.objects.get(id=perfil_id)
            playlist_obj = Playlist.objects.get(id=playlist_id, owner=user_perfil) 
            
            PlaylistSong.objects.filter(playlist=playlist_obj, song_id=song_id).delete()
            
            return JsonResponse({'success': True})
        except (PERFIL.DoesNotExist, Playlist.DoesNotExist, Exception):
            return JsonResponse({'error': 'No se pudo eliminar (Acceso denegado o no existe)'}, status=403)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

