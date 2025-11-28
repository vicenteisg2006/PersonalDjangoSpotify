from django.db import models

#                                                  ====================
#                                                  ====  Tabla ALBUM ====
#                                                  ====================

class Album(models.Model):
    title = models.CharField(max_length=200, unique=True)
    release_date = models.DateField(null=True, blank=True)
    cover_art_url = models.URLField(max_length=500, blank=True, null=True, default='/static/images/default_2.jpg')

    artist = models.ForeignKey(
        'PERFIL',
        on_delete=models.CASCADE,
        related_name='albums'
    )

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

#                                                  ====================
#                                                  ====  Tabla SONG =====
#                                                  ====================

class Song(models.Model):
    artist = models.ForeignKey(
        'PERFIL',
        on_delete=models.CASCADE,
        related_name='songs'
    )

    album = models.ForeignKey(
        'Album',
        on_delete=models.SET_NULL,
        related_name='Tracks',
        null=True,
        blank=True
    )
    
    song_text = models.CharField(max_length=300, unique=True)
    img_src = models.URLField(max_length=500, blank=True, null=True, default='/static/images/default_1.jpg')
    duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Duracion de la cancion (ej. HH:MM:SS o MM:SS)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.song_text
    
    class Meta:
        ordering = ['song_text']

#                                                  ====================
#                                                  =Tabla STREAMS_X_MES= 
#                                                  ====================

class MonthlyStreamRecord(models.Model):
    song = models.ForeignKey(
        'Song', 
        on_delete=models.CASCADE, 
        related_name='monthly_streams'
    )
    
    date = models.DateField()
    
    streams = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('song', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.song.song_text} streams for {self.date.strftime('%Y-%m')}"

#                                                  ====================
#                                                 Tabla Streams_x_Cancion 
#                                                  ====================

class CANCION_REPRODUCCION(models.Model):
    song = models.ForeignKey(
        'Song', 
        on_delete=models.CASCADE, 
        related_name='reproductions'
    )

    listener = models.ForeignKey(
        'PERFIL', 
        on_delete=models.SET_NULL, 
        related_name='reproductions_made',
        null=True
    )
    
    fecha_reproduccion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.song.song_text} - {self.listener.username}"
    
    class Meta:
        ordering = ['-fecha_reproduccion']
















































class Playlist(models.Model):
    name = models.CharField(max_length=150)
    img_src = models.URLField(max_length=500, default='https://picsum.photos/seed/playlist/300')
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True, through='PlaylistSong')
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        'PERFIL',
        on_delete=models.CASCADE,
        related_name='created_playlists'
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('playlist', 'song')
        ordering = ['order', 'added_at']
    
    def __str__(self):
        return f"{self.song.song_text} en {self.playlist.name}"



#                                                  ====================
#                                                  ===  Tabla PERFIL ====
#                                                  ====================

class PERFIL(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    nombre = models.CharField(max_length=50)
    rol = models.CharField(max_length=15, choices= 
        [('user', 'User'), 
         ('artist', 'Artist'), 
         ('administrator', 'Administrator'), 
         ('moderator', 'Moderator')
        ])
    
    ubicacion = models.CharField(max_length=15, choices=
        [('Asia', 'Asia'),
         ('Africa', 'Africa'),
         ('America', 'America'),
         ('Europa', 'Europa'),
         ('Oceania', 'Oceania')
        ],
        default='America')
    
    estado_moderacion = models.CharField(max_length=15, choices=
    [('ok', 'OK'),
     ('alert', 'ALERT'),
     ('ban', 'BAN'),
     ('en_espera', 'En_espera')
    ],
    default='OK')
    

#                                                  ====================
#                                                Tabla REGISTRO MODERADOR
#                                                  ====================


class REGISTRO_MODERADOR(models.Model):
    perfil_afectado = models.ForeignKey(
        'PERFIL', 
        on_delete=models.CASCADE, 
        related_name='moderation_history', 
        verbose_name='Perfil Afectado'
    )

    moderador_emisor = models.ForeignKey(
        'PERFIL',
        on_delete=models.SET_NULL,
        related_name='action_taken',
        verbose_name='Moderador Emisor',
        null=True,
        blank=True
    )

    reason = models.CharField(max_length=100, default='Reporte de Usuario')

    action_status = models.CharField(
        max_length=15,
        choices=
        [('ok', 'OK'),
         ('alert', 'ALERT'),
         ('ban', 'BAN'),
         ('en_espera', 'En_espera')   
        ],
        default='En_espera'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.action_status.upper()}] - {self.perfil_afectado.username}"
    
    class Meta:
        verbose_name = 'Registro de Moderación'
        verbose_name_plural = 'Registros de Moderación'
        ordering = ['-fecha']



#                                                  ====================
#                                              Tabla COORDENADAS GEOGRAFICAS
#                                                  ====================

class UbicacionGeo(models.Model):
    continente = models.CharField(max_length=15, unique=True) 
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.continente

    class Meta:
        verbose_name_plural = "Ubicaciones Geográficas"
