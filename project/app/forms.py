from django.db.models import Q
from django import forms
from .models import Playlist, Song
from .models import PERFIL, REGISTRO_MODERADOR

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'img_src']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la playlist...'
            }),
            'img_src': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la imagen de la playlist'
            })
        }
        labels = {
            'name': '',
            'img_src': ''
        }

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['song_text', 'img_src']
        widgets = {
            'song_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la canción - Artista'
            }),
            'img_src': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la imagen'
            })
        }
        labels = {
            'song_text': 'Canción',
            'img_src': 'Imagen'
        }

# ========== formularios Vicente ==========
class alertaMODERADORForm(forms.ModelForm):
    perfil_afectado = forms.ModelChoiceField(
        queryset=PERFIL.objects.filter(Q(rol='user') | Q(rol='artist')),
        label="Perfil a Moderar"
    )

    class Meta:
        model = REGISTRO_MODERADOR
        fields = [
            'perfil_afectado',
            'reason'
        ]


class RegistroModeradorForm(forms.ModelForm):
    class Meta:
        model = REGISTRO_MODERADOR
        # Solo necesitamos el campo 'reason' del modelo
        fields = ['reason'] 
        
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 3,
                'placeholder': 'Describa la razón del cambio de estado (ej: Uso de lenguaje inapropiado, contenido plagiado).'
            }),
        }