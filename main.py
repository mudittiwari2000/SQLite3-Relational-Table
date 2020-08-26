import xml.etree.ElementTree as ET
import sqlite3

# Connecting to the Database
conn = sqlite3.connect('tracksdb.sqlite')

# Creating a cursor to execute the scripts
curr = conn.cursor()

# Executing the SQLite scripts using the cursor we created through our connect method
# executescript method allows multiple scripts to be passed in it as it's parameter, whereas execute method allows only one script
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

# Checking and retrieving the element using the attribute passed to it
# We check the left sides key's value to return the right side's key's value, since they are a key-value pair of a kind
def retrieve(element, attribute):
    found = False
    for child in element:
        if found:
            return child.text
        if child.tag == 'key' and child.text == attribute:
            found = True
    return None

# Taking input for the file's name from the user
filename = input('Enter the File name: ')
# If the filename variable's length is less than 1, we enter a default value in it, just for convenience's sake
if len(filename) < 1:
    filename = 'Files/Library.xml'

# Parsing the XML using the xml module
xml = ET.parse(filename)
# Finding and retrieving all the dict nodes inside of two parent dict nodes, and storing them in an array(implicitly) to iterate through them later
relevant = xml.findall('dict/dict/dict')
# Iterating through the dict nodes retrieved from the above findall method from the element tree
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

    # A little sanity check, also it did bring a bug to the progam so I added it anyway
    if track is None or artist is None or genre is None:
        continue

    # print(track, artist, album, genre, length, rating, count)
    
    # Inserting genre values we retrieved from the XML in the Genre Table, ignoring the repeated values since we only require unique values
    curr.execute('''
        INSERT OR IGNORE INTO Genre(name) VALUES(?) 
    ''', (genre, ))
    # Selecting the id attribute from the Genre Table where name attribute is equals to the genre value we retrieved from the XML
    curr.execute(' SELECT id FROM Genre WHERE name = ?', (genre, ))
    # Fetching the selecting value in the cursor from our previous select above
    genre_id = curr.fetchone()[0]
    
    
    # Inserting artist values we retrieved from the XML in the Artist Table, ignoring the repeated values since we only require unique values
    curr.execute('''
        INSERT OR IGNORE INTO Artist(name) VALUES(?) 
    ''', (artist, ))
    curr.execute(' SELECT id FROM Artist WHERE name = ?', (artist, ))
    artist_id = curr.fetchone()[0]
    
    
    # Inserting album values we retrieved from the XML in the Album Table, ignoring the repeated values since we only require unique values
    curr.execute('''
        INSERT OR IGNORE INTO Album(title, artist_id) VALUES(?, ?) 
    ''', (album, artist_id))
    curr.execute(' SELECT id FROM Album WHERE title = ?', (album, ))
    album_id = curr.fetchone()[0]

    #rint(genre_id, artist_id, album_id)
    
    # Inserting genre values we retrieved from the XML in the Genre Table, replacing the repeated values since some values
    # such as count(Play count), rating can be different from the previous registry of the same title
    curr.execute('''
        INSERT OR REPLACE INTO Track(title, len, rating, count, genre_id, album_id) VALUES(?, ?, ?, ?, ?, ?) 
    ''', (track, length, rating, count, genre_id, album_id))
    
    # Commiting our changes to the database one at a time, that is slow, but it is simple
    conn.commit()

# Selecting the Track Title, Artist Name, Album Title, Genre Name from the Relational Tables
# Also, limiting the row count to 3 and ordering the names by Artist Names
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
