import xml.etree.ElementTree as ET
import sqlite3

# COnnecting to the Database
conn = sqlite3.connect('tracksdb.sqlite')

# Creating a cursor to execute the scripts
curr = conn.cursor()

curr.executescript('''
    DROP TABLE IF EXISTS Track;
    DROP TABLE IF EXISTS Album;
    DROP TABLE IF EXISTS Artist;
    DROP TABLE IF EXISTS Genre;

    CREATE TABLE Genre (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE
    );

    CREATE TABLE Artist (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE
    );

    CREATE TABLE Album (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        title TEXT UNIQUE,
        artist_id INTEGER
    );
    CREATE TABLE Track (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        title TEXT UNIQUE,
        genre_id INTEGER,
        album_id INTEGER,
        len INTEGER,
        rating INTEGER,
        count INTEGER
    );
''')


def retrieve(element, attribute):
    found = False
    for child in element:
        if found:
            return child.text
        if child.tag == 'key' and child.text == attribute:
            found = True
    return None


filename = input('Enter the File name: ')
if len(filename) < 1:
    filename = '../../Files/Library.xml'

# Parsing the XML
xml = ET.parse(filename)
relevant = xml.findall('dict/dict/dict')
for entry in relevant:
    if retrieve(entry, 'Track ID') is None:
        continue

    track = retrieve(entry, 'Name')
    artist = retrieve(entry, 'Artist')
    album = retrieve(entry, 'Album')
    genre = retrieve(entry, 'Genre')
    length = retrieve(entry, 'Total Time')
    rating = retrieve(entry, 'Rating')
    count = retrieve(entry, 'Play Count')

    if track is None or artist is None or genre is None:
        continue

    # print(track, artist, album, genre, length, rating, count)

    curr.execute('''
        INSERT OR IGNORE INTO Genre(name) VALUES(?) 
    ''', (genre, ))
    curr.execute(' SELECT id FROM Genre WHERE name = ?', (genre, ))
    genre_id = curr.fetchone()[0]

    curr.execute('''
        INSERT OR IGNORE INTO Artist(name) VALUES(?) 
    ''', (artist, ))
    curr.execute(' SELECT id FROM Artist WHERE name = ?', (artist, ))
    artist_id = curr.fetchone()[0]

    curr.execute('''
        INSERT OR IGNORE INTO Album(title, artist_id) VALUES(?, ?) 
    ''', (album, artist_id))
    curr.execute(' SELECT id FROM Album WHERE title = ?', (album, ))
    album_id = curr.fetchone()[0]

    print(genre_id, artist_id, album_id)

    curr.execute('''
        INSERT OR REPLACE INTO Track(title, len, rating, count, genre_id, album_id) VALUES(?, ?, ?, ?, ?, ?) 
    ''', (track, length, rating, count, genre_id, album_id))

    conn.commit()

sqlstr = curr.execute('''
    SELECT Track.title, Artist.name, Album.title, Genre.name 
    FROM Track JOIN Genre JOIN Album JOIN Artist 
    ON Track.genre_id = Genre.ID and Track.album_id = Album.id 
        AND Album.artist_id = Artist.id
    ORDER BY Artist.name LIMIT 3
''')
print('Track \t Artist \t Album \t Genre')
for row in sqlstr:
    print(f'{row[0]} \t {row[1]} \t {row[2]} \t {row[3]}')