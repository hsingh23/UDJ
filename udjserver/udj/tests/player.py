import json

from udj.tests.testhelpers import JeffTestCase
from udj.tests.testhelpers import YunYoungTestCase
from udj.tests.testhelpers import KurtisTestCase
from udj.tests.testhelpers import AlejandroTestCase
from udj.tests.testhelpers import EnsureParticipationUpdated
from udj.models import Vote
from udj.models import LibraryEntry
from udj.models import Player
from udj.models import PlayerLocation
from udj.models import PlayerPassword
from udj.models import Participant
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.auth import hashPlayerPassword
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER
from udj.headers import MISSING_RESOURCE_HEADER

from django.test.client import Client

from datetime import datetime



class GetPlayersTests(JeffTestCase):
  def testGetNearbyPlayers(self):
    response = self.doGet('/udj/players/40.11241/-88.222053')
    self.assertEqual(response.status_code, 200, response.content)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])

  def testGetPlayersByName(self):
    response = self.doGet('/udj/players?name=kurtis')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])

class CreatePlayerTests(YunYoungTestCase):
  def testCreatePlayer(self):
    playerName = "Yunyoung Player"
    payload = {'name' : playerName } 
    response = self.doJSONPut('/udj/users/7/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['player_id']
    addedPlayer = Player.objects.get(pk=givenPlayerId)
    self.assertEqual(addedPlayer.name, playerName)
    self.assertEqual(addedPlayer.owning_user.id, 7)
    self.assertFalse(PlayerLocation.objects.filter(player=addedPlayer).exists())
    self.assertFalse(PlayerPassword.objects.filter(player=addedPlayer).exists())

  def testCreatePasswordPlayer(self):
    playerName = "Yunyoung Player"
    password = 'playerpassword'
    passwordHash = hashPlayerPassword(password)
    payload = {'name' : playerName, 'password' : password}
    response = self.doJSONPut('/udj/users/7/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['player_id']
    addedPlayer = Player.objects.get(pk=givenPlayerId)
    self.assertEqual(addedPlayer.name, playerName)
    self.assertEqual(addedPlayer.owning_user.id, 7)
    self.assertFalse(PlayerLocation.objects.filter(player=addedPlayer).exists())

    addedPassword = PlayerPassword.objects.get(player=addedPlayer)
    self.assertEqual(addedPassword.password_hash, passwordHash)

  def testCreateLocationPlayer(self):
    playerName = "Yunyoung Player"
    payload = {'name' : playerName } 
    location = {
        'address' : '201 N Goodwin Ave',
        'city' : 'Urbana',
        'state' : 'IL',
        'zipcode' : 61801
    }
    payload['location'] = location

    response = self.doJSONPut('/udj/users/7/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['player_id']
    addedPlayer = Player.objects.get(pk=givenPlayerId)
    self.assertEqual(addedPlayer.name, playerName)
    self.assertEqual(addedPlayer.owning_user.id, 7)
    self.assertFalse(PlayerPassword.objects.filter(player=addedPlayer).exists())

    createdLocation = PlayerLocation.objects.get(player__id=givenPlayerId)
    self.assertEqual(createdLocation.address, location['address'])
    self.assertEqual(createdLocation.city, location['city'])
    self.assertEqual(createdLocation.state.name, location['state'])
    self.assertEqual(createdLocation.zipcode, location['zipcode'])
    self.assertEqual(createdLocation.point.y, 40.1135372574038)
    self.assertEqual(createdLocation.point.x, -88.2240781569526)


class PlayerModificationTests(KurtisTestCase):

  def testChangeName(self):
    newName = "A Bitchn' name"
    response = self.doPost('/udj/users/2/players/1/name', {'name': newName})
    self.assertEqual(200, response.status_code)
    player = Player.objects.get(pk=1)
    self.assertEqual(player.name, newName)

  def testSetPassword(self):
    newPassword = 'nudepassword'
    response = self.doPost('/udj/users/2/players/1/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.get(player__id=1)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))

  def testSetLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'city' : 'Plymouth',
      'state' : 'MN',
      'zipcode' : 55447
    }

    response = self.doPost('/udj/users/2/players/1/location', newLocation)
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerLocation = PlayerLocation.objects.get(player__id=1)
    self.assertEqual(playerLocation.address, '305 Vicksburg Lane')
    self.assertEqual(playerLocation.city, 'Plymouth')
    self.assertEqual(playerLocation.state.id, 23)
    self.assertEqual(playerLocation.zipcode, 55447)

  def testSetLocationWithNoPreviousLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'city' : 'Plymouth',
      'state' : 'MN',
      'zipcode' : 55447
    }

    response = self.doPost('/udj/users/2/players/4/location', newLocation)
    self.assertEqual(200, response.status_code)
    playerLocation = PlayerLocation.objects.get(player__id=4)
    self.assertEqual(playerLocation.address, '305 Vicksburg Lane')
    self.assertEqual(playerLocation.city, 'Plymouth')
    self.assertEqual(playerLocation.state.id, 23)
    self.assertEqual(playerLocation.zipcode, 55447)

class PlayerModificationTests2(AlejandroTestCase):

  def testChangePassword(self):
    oldTime = PlayerPassword.objects.get(player__id=3).time_set
    newPassword = "nudepassword"
    response = self.doPost('/udj/users/6/players/3/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.get(player__id=3)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))
    self.assertTrue(oldTime < playerPassword.time_set)

  def testDeletePassword(self):
    response = self.doDelete('/udj/users/6/players/3/password')
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.filter(player__id=3)
    self.assertFalse(playerPassword.exists())

class BeginParticipateTests(YunYoungTestCase):
  def testSimplePlayer(self):
    response = self.doPut('/udj/players/1/users/7')
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    newParticipant = Participant.objects.get(user__id=7, player__id=1)

  def testPasswordPlayer(self):
    response = self.doPut('/udj/players/3/users/7', 
        headers={DJANGO_PLAYER_PASSWORD_HEADER : 'alejandro'})
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    newParticipant = Participant.objects.get(user__id=7, player__id=3)

  def testBadPassword(self):
    response = self.doPut('/udj/players/3/users/7', 
        headers={DJANGO_PLAYER_PASSWORD_HEADER : 'wrong password'})
    self.assertEqual(response.status_code, 401, "Error: " + response.content)
    self.assertEqual(response['WWW-Authenticate'], 'player-password')
    newParticipant = Participant.objects.filter(user__id=7, player__id=3)
    self.assertFalse(newParticipant.exists())

  def testBadNoPassword(self):
    response = self.doPut('/udj/players/3/users/7')
    self.assertEqual(response.status_code, 401, "Error: " + response.content)
    self.assertEqual(response['WWW-Authenticate'], 'player-password')
    newParticipant = Participant.objects.filter(user__id=7, player__id=3)
    self.assertFalse(newParticipant.exists())

class PlayerAdminTests(KurtisTestCase):

  def testGetUsers(self):
    participants = Participant.objects.filter(player__id=1).exclude(user__id=7)
    participants.update(time_last_interaction=datetime.now())

    response = self.doGet('/udj/players/1/users')
    self.assertEqual(response.status_code, 200)
    jsonUsers = json.loads(response.content)
    self.assertEquals(len(jsonUsers), 2)
    possibleUsers = ['jeff', 'vilas']
    for user in jsonUsers:
      self.assertTrue(user['username'] in possibleUsers)

  def testGetUsers2(self):
    participants = Participant.objects.filter(player__id=1)
    participants.update(time_last_interaction=datetime.now())

    response = self.doGet('/udj/players/1/users')
    self.assertEqual(response.status_code, 200)
    jsonUsers = json.loads(response.content)
    self.assertEquals(len(jsonUsers), 3)
    possibleUsers = ['jeff', 'vilas', 'yunyoung']
    for user in jsonUsers:
      self.assertTrue(user['username'] in possibleUsers)

  def testSetCurrentSong(self):
    response = self.doPost('/udj/players/1/current_song', {'lib_id' : 1})
    self.assertEqual(response.status_code, 200, response.content)

    self.assertEqual('FN',ActivePlaylistEntry.objects.get(pk=5).state)
    self.assertEqual('PL',ActivePlaylistEntry.objects.get(pk=1).state)
    PlaylistEntryTimePlayed.objects.get(playlist_entry__id=1)

  def testSetPaused(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'paused'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).state, 'PA')

  def testSetInactive(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'inactive'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).state, 'IN')

  def testSetPlaying(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'playing'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).state, 'PL')

  def testBadStateRequest(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'wrong'})
    response = self.assertEqual(response.status_code, 400)

    self.assertEqual(Player.objects.get(pk=1).state, 'PL')

  def testSetVolume(self):
    response = self.doPost('/udj/users/2/players/1/volume', {'volume': '1'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).volume, 1)

  def testBadSetVolume(self):
    response = self.doPost('/udj/users/2/players/1/volume', {'volume': 'a'})
    response = self.assertEqual(response.status_code, 400)

    self.assertEqual(Player.objects.get(pk=1).volume, 5)

  def testBadSetVolume2(self):
    response = self.doPost('/udj/users/2/players/1/volume', {'volume': '11'})
    response = self.assertEqual(response.status_code, 400)

    self.assertEqual(Player.objects.get(pk=1).volume, 5)

  def testSongRemove(self):
    response = self.doDelete('/udj/players/1/active_playlist/songs/2')
    self.assertEqual(response.status_code, 200)

    shouldntBeRemoved = ActivePlaylistEntry.objects.get(pk=2)
    self.assertEqual('RM', shouldntBeRemoved.state)

  def testOtherSongRemove(self):
    response = self.doDelete('/udj/players/1/active_playlist/songs/2')
    self.assertEqual(response.status_code, 200)

    shouldntBeRemoved = ActivePlaylistEntry.objects.get(pk=2)
    self.assertEqual('RM', shouldntBeRemoved.state)

  def testPlaylistMultiMod(self):
    toAdd = [9]
    toRemove = [3]

    response = self.doPost(
      '/udj/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(response.status_code, 200, response.content)
    #make sure song was queued
    addedSong = ActivePlaylistEntry.objects.get(
      song__player__id=1, song__player_lib_song_id=9, state='QE')
    #make sure song was removed
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__player__id=1,
      song__player_lib_song_id=3,
      state='QE').exists())
    self.assertTrue(ActivePlaylistEntry.objects.filter(
      song__player__id=1,
      song__player_lib_song_id=3,
      state='RM').exists())

  def testBadRemoveMultiMod(self):
    toAdd = [9]
    toRemove = [3,6]

    response = self.doPost(
      '/udj/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(response.status_code, 404, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

    responseJSON = json.loads(response.content)
    self.assertEqual([6], responseJSON)

    #ensure 9 wasn't added
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__player__id='1',
      song__player_lib_song_id='9',
      state="QE").exists())

    #ensure 3 is still queued
    ActivePlaylistEntry.objects.get(
      song__player__id='1',
      song__player_lib_song_id='3',
      state="QE")

  def testBadAddMultiMod(self):
    toAdd = [6,9]
    toRemove = [3]
    response = self.doPost(
      '/udj/players/1/active_playlist',
      {'to_add' : json.dumps(toAdd), 'to_remove' : json.dumps(toRemove)}
    )
    self.assertEqual(409, response.status_code, response.content)

    #ensure 9 wasn't added
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__player__id='1',
      song__player_lib_song_id='9',
      state="QE").exists())

    #ensure 3 is still queued
    ActivePlaylistEntry.objects.get(
      song__player__id='1',
      song__player_lib_song_id='3',
      state="QE")





class PlayerAdminTests2(AlejandroTestCase):
  def testSetCurrentSongWithBlank(self):
    response = self.doPost('/udj/players/3/current_song', {'lib_id' : 1})
    self.assertEqual(response.status_code, 200, response.content)

    self.assertEqual('PL',ActivePlaylistEntry.objects.get(pk=8).state)
    PlaylistEntryTimePlayed.objects.get(playlist_entry__id=8)

  def testGetPlaylistWithBlankCurrent(self):
    response = self.doGet('/udj/players/3/active_playlist')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    current_song = jsonResponse['current_song']
    self.assertEqual(current_song,{})
    plSongs = ActivePlaylistEntry.objects.filter(song__player__id=3, state='QE')
    plSongIds = [x.song.player_lib_song_id for x in plSongs]
    for plSong in jsonResponse['active_playlist']:
      self.assertTrue(plSong['song']['id'] in plSongIds)
    self.assertEqual(len(jsonResponse['active_playlist']), len(plSongIds))


class PlayerReparticipateTest(YunYoungTestCase):

  @EnsureParticipationUpdated(7,1)
  def testReparticipate(self):
    response = self.doPut('/udj/players/1/users/7')
    self.assertEqual(201, response.status_code)


class PlayerQueryTests(YunYoungTestCase):

  @EnsureParticipationUpdated(7, 1)
  def testGetUsers(self):
    response = self.doGet('/udj/players/1/users')
    self.assertEqual(response.status_code, 200)
    jsonUsers = json.loads(response.content)
    self.assertEquals(len(jsonUsers), 1)
    possibleUsers = ['jeff', 'vilas', 'yunyoung']
    for user in jsonUsers:
      self.assertTrue(user['username'] in possibleUsers)

  @EnsureParticipationUpdated(7, 1)
  def testSimpleGetMusic(self):

    response = self.doGet('/udj/players/1/available_music?query=Third+Eye+Blind')
    self.assertEqual(response.status_code, 200)
    songResults = json.loads(response.content)
    self.assertEquals(4, len(songResults))
    expectedLibIds =[1,2,3,5]
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

  @EnsureParticipationUpdated(7, 1)
  def testSimpleGetWithMax(self):
    response = self.doGet('/udj/players/1/available_music?query=Third+Eye+Blind&max_results=2')
    self.assertEqual(response.status_code, 200)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))

  @EnsureParticipationUpdated(7, 1)
  def testAlbumGet(self):

    response = self.doGet('/udj/players/1/available_music?query=Bedlam+in+Goliath')
    self.assertEqual(response.status_code, 200)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    expectedLibIds =[6,7]
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

  @EnsureParticipationUpdated(7, 1)
  def testGetRandom(self):

    response = self.doGet('/udj/players/1/available_music/random_songs?max_randoms=2')
    self.assertEqual(response.status_code, 200)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    for song in songResults:
      self.assertFalse(
          LibraryEntry.objects.get(player__id=1, player_lib_song_id=song['id']).is_deleted)
      self.assertFalse(
          LibraryEntry.objects.get(player__id=1, player_lib_song_id=song['id']).is_banned)


  @EnsureParticipationUpdated(7, 1)
  def testGetPlaylist(self):

    response = self.doGet('/udj/players/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    current_song = jsonResponse['current_song']
    realCurrentSong = ActivePlaylistEntry.objects.get(song__player__id=1, state='PL')
    self.assertEqual(current_song['song']['id'], realCurrentSong.song.player_lib_song_id)
    plSongs = ActivePlaylistEntry.objects.filter(song__player__id=1, state='QE')
    plSongIds = [x.song.player_lib_song_id for x in plSongs]
    for plSong in jsonResponse['active_playlist']:
      self.assertTrue(plSong['song']['id'] in plSongIds)
    self.assertEqual(len(jsonResponse['active_playlist']), len(plSongIds))

    self.assertEqual(jsonResponse['volume'], 5)
    self.assertEqual(jsonResponse['state'], 'playing')

  @EnsureParticipationUpdated(7, 1)
  def testGetArtists(self):
    response = self.doGet('/udj/players/1/available_music/artists')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(3, len(jsonResponse))
    requiredArtists = [u'Skrillex', u'The Mars Volta', u'Third Eye Blind']
    for artist in jsonResponse:
      self.assertTrue(artist in requiredArtists)

  @EnsureParticipationUpdated(7, 1)
  def testSpecificArtistGet(self):
    response = self.doGet('/udj/players/1/available_music/artists/Third Eye Blind')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(4, len(jsonResponse))
    requiredIds = [1, 2, 3, 5]
    for songId in [x['id'] for x in jsonResponse]:
      self.assertTrue(songId in requiredIds)

  @EnsureParticipationUpdated(7, 1)
  def testRecentlyPlayed(self):
    response = self.doGet('/udj/players/1/recently_played')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(2, len(jsonResponse))
    self.assertEqual(7, jsonResponse[0]['song']['id'])
    self.assertEqual(5, jsonResponse[1]['song']['id'])

  @EnsureParticipationUpdated(7, 1)
  def testRecentlyPlayedWithMax(self):
    response = self.doGet('/udj/players/1/recently_played?max_songs=1')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(1, len(jsonResponse))


class PlaylistModTests(JeffTestCase):

  @EnsureParticipationUpdated(3, 1)
  def testSimpleAdd(self):

    response = self.doPut('/udj/players/1/active_playlist/songs/9')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__player__id=1, song__player_lib_song_id=9, state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddRemovedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/10')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__player__id=1, song__player_lib_song_id=10, state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddBannedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/4')
    self.assertEqual(response.status_code, 404)

    self.assertFalse( ActivePlaylistEntry.objects.filter(
      song__player__id=1, song__player_lib_song_id=4, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddDeletedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/8')
    self.assertEqual(response.status_code, 404)

    self.assertFalse( ActivePlaylistEntry.objects.filter(
      song__player__id=1, song__player_lib_song_id=8, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddQueuedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/1')
    self.assertEqual(response.status_code, 409)

  @EnsureParticipationUpdated(3, 1)
  def testAddPlayingSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/6')
    self.assertEqual(response.status_code, 409)

  @EnsureParticipationUpdated(3, 1)
  def testRemoveQueuedSong(self):
    response = self.doDelete('/udj/players/1/active_playlist/songs/3')
    self.assertEqual(response.status_code, 403)

    removedSong = ActivePlaylistEntry.objects.get(pk=3)
    self.assertEqual('QE', removedSong.state)

  @EnsureParticipationUpdated(3, 1)
  def testVoteSongUp(self):
    response = self.doPost('/udj/players/1/active_playlist/songs/1/users/3/upvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=1, weight=1)

  @EnsureParticipationUpdated(3, 1)
  def testVoteDownSong(self):
    response = self.doPost('/udj/players/1/active_playlist/songs/1/users/3/downvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=1, weight=-1)

  @EnsureParticipationUpdated(3, 1)
  def testBadSongVote(self):
    response = self.doPost('/udj/players/1/active_playlist/songs/50/users/3/downvote')
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

  @EnsureParticipationUpdated(3, 1)
  def testDuplicateVote(self):
    response = self.doPost('/udj/players/1/active_playlist/songs/2/users/3/downvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=2, weight=-1)

