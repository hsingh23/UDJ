import json
from udj.models import LibraryEntry
from udj.tests.testhelpers import KurtisTestCase

class LibTestCases(KurtisTestCase):

  def verifySongAdded(self, jsonSong):
    addedSong = LibraryEntry.objects.get(player__id=1, player_lib_song_id=jsonSong['id'])
    self.assertEqual(addedSong.title, jsonSong['title'])
    self.assertEqual(addedSong.artist, jsonSong['artist'])
    self.assertEqual(addedSong.album, jsonSong['album'])
    self.assertEqual(addedSong.track, jsonSong['track'])
    self.assertEqual(addedSong.genre, jsonSong['genre'])
    self.assertEqual(addedSong.duration, jsonSong['duration'])

  def testSimpleAdd(self):
    payload = {
      "id" : 11,
      "title" : "Zero",
      "artist" : "The Smashing Pumpkins",
      "album" : "Mellon Collie And The Infinite Sadness",
      "track" : 4,
      "genre" : "Rock",
      "duration" : 160
    }

    response = self.doJSONPut('/udj/users/2/players/1/library/song', json.dumps(payload))
    self.assertEqual(201, response.status_code, response.content)
    self.verifySongAdded(payload)

  def testDuplicateAdd(self):
    payload = {
      "id" : 10,
      "title" : "My Name Is Skrillex",
      "artist" : "Skrillex",
      "album" : "My Name Is Skirllex",
      "track" : 1,
      "genre" : "Dubstep",
      "duration" : 291
    }

    response = self.doJSONPut('/udj/users/2/players/1/library/song', json.dumps(payload))
    self.assertEqual(409, response.status_code, response.content)


"""
import json
from udj.headers import getDjangoUUIDHeader
from udj.tests.testhelpers import User2TestCase
from udj.tests.testhelpers import User3TestCase
from udj.tests.testhelpers import User4TestCase
from udj.models import LibraryEntry

class LibTestCases(User2TestCase):

  def verifySongAdded(self, lib_id, ids, title, artist, album):
    matchedEntries = LibraryEntry.objects.filter(host_lib_song_id=lib_id, 
      owning_user=self.user_id)
    self.assertEqual(len(matchedEntries), 1,
      msg="Couldn't find inserted song.")
    insertedLibEntry = matchedEntries[0]
    self.assertEqual(insertedLibEntry.title, title)
    self.assertEqual(insertedLibEntry.artist, artist)
    self.assertEqual(insertedLibEntry.album, album)

    self.assertTrue(lib_id in ids)


  def testSingleLibAdd(self):

    lib_id = 13
    title = 'Roulette Dares'
    artist = 'The Mars Volta'
    album = 'Deloused in the Comatorium'
    duration = 451

    payload = [{
      'id' : lib_id,
      'title' : title,
      'artist' : artist,
      'album' : album,
      'duration' : duration
    }]


    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, msg=response.content)
    self.verifyJSONResponse(response)
    ids = json.loads(response.content)
    self.verifySongAdded(lib_id, ids, title, artist, album)

  def testMultiLibAdd(self):

    lib_id1 = 13
    title1 = 'Roulette Dares'
    artist1 = 'The Mars Volta'
    album1 = 'Deloused in the Comatorium'
    duration1 = 451

    lib_id2 = 14
    title2 = 'Goliath'
    artist2 = 'The Mars Volta'
    album2 = 'The Bedlam in Goliath'
    duration2 = 435

    payload = [
      {
        'id' : lib_id1,
        'title' : title1,
        'artist' : artist1,
        'album' : album1,
        'duration' : duration1
      },
      {
        'id' : lib_id2,
        'title' : title2,
        'artist' : artist2,
        'album' : album2,
        'duration' : duration2
      }
    ]

    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})

    self.assertEqual(response.status_code, 201, msg=response.content)
    self.verifyJSONResponse(response)
    ids = json.loads(response.content)
    self.verifySongAdded(lib_id1, ids, title1, artist1, album1)
    self.verifySongAdded(lib_id2, ids, title2, artist2, album2)

  def testDupAdd(self):

    dup_lib_id=1

    payload = [{
      "song" : "Never Let You Go", 
      "artist" : "Third Eye Blind",
      "album" : "Blue", 
      "id" : dup_lib_id, 
      "duration" : 237 
    }]
    response = self.doJSONPut(
      '/udj/users/' + self.user_id + '/library/songs', json.dumps(payload),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})

    self.assertEqual(response.status_code, 201, msg=response.content)
    self.verifyJSONResponse(response)
    ids = json.loads(response.content)
    self.assertEqual(ids[0], dup_lib_id)
    onlyOneSong = LibraryEntry.objects.get(
      owning_user__id=2, host_lib_song_id=dup_lib_id)

  def testLibSongDelete(self):
    response = self.doDelete('/udj/users/' + self.user_id + '/library/10',
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 200, msg=response.content)
    deletedEntries = LibraryEntry.objects.filter(
      host_lib_song_id=10, owning_user__id=2, is_deleted=True)
    self.assertEqual(len(deletedEntries), 1)
"""
