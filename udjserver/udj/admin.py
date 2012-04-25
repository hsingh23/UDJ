from udj.models import *
from django.contrib import admin

def removeSongFromActivePlaylist(modeladmin, request, queryset):
  queryset.update(state='RM')

removeSongFromActivePlaylist.short_description = "Remove song(s) from playlist"

class ParticipantAdmin(admin.ModelAdmin):
  list_display=('user', 'player', 'time_joined', 'time_last_interaction')
  list_filters=('player', 'user',)

class ActivePlaylistEntryAdmin(admin.ModelAdmin):
  list_display = ('song', 'time_added', 'adder', 'state')
  list_filter = ('state','player',)
  actions = [removeSongFromActivePlaylist]

class TicketAdmin(admin.ModelAdmin):
  list_display = ('user', 'ticket_hash', 'time_issued')
  
class LibraryAdmin(admin.ModelAdmin):
  list_display = (
    'player',
    'player_lib_song_id', 
    'title', 
    'artist', 
    'album', 
    'track', 
    'genre', 
    'duration', 
    'is_banned', 
    'is_deleted')
  list_filter = ('owning_user', 'is_deleted', 'is_banned')


admin.site.register(Ticket)
admin.site.register(Player)
admin.site.register(PlayerPassword)
admin.site.register(PlayerLocation)
admin.site.register(LibraryEntry, LibraryAdmin)
admin.site.register(ActivePlaylistEntry, ActivePlaylistEntryAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Vote)
admin.site.register(PlaylistEntryTimePlayed)
