import os
import re
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


directoryPath = os.path.dirname(os.path.abspath(__file__)) + "//songs"
destForNewHebrewSongs = directoryPath + "//SortedSongs//Hebrew"
destForNewEnglishSongs = directoryPath + "//SortedSongs//English"



def uploadDF():
    df = pd.read_csv('singersCSV.csv')
    df = pd.DataFrame(df, columns=['Title', 'Artist'])
    df['Title'] = df['Title'].str.lower()
    df['Artist'] = df['Artist'].str.lower()
    df.dropna(inplace=True)
    return df


def spotifyConnection():
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="FILL_HERE",
                                                               client_secret="FILL_HERE"))
    return sp


def searchSingerInSpotify(singerName, sp):
    results = sp.search(q=singerName, limit=20)
    for idx, track in enumerate(results['tracks']['items']):
        print(idx, track['name'])


def searchSongInSpotify(name, sp):
    results = sp.search(name, type='track', market=None)
    for track in results['tracks']['items']:
        trackName = track['name'].lower()
        if name in trackName:
            return True
    return False


#it will be a tuple of 2, if it hadn't split it will be tuple of 1
def splitOriginalString(currTrimmed):
    trimmed = currTrimmed.split('-', 1)
    # the strip is for spaces, the split is for removing another unnecessary '-' in the name of song/singer
    #remove everything within () and []
    result = [re.sub("[\\(\\[].*?[\\)\\]]", "", currWord).strip().split('-', 1)[0] for currWord in trimmed]
    return tuple(result)


#return [original string, separated string to song and singer ]
def getAllFilesNames():
    dir_list = os.listdir(directoryPath)
    result = list()
    for currFile in dir_list:
        if ".mp3" in currFile:
            currTrimmed = currFile[:-4]     #removes the "mp3"
            currTrimmed = currTrimmed.replace("_", " ")                      #switches _ with " " -> hey_jude = hey jude
            currTrimmed = ''.join([i for i in currTrimmed if not (i.isdigit() or i == '.')])    #remove numbers and dots
            result.append([currFile, splitOriginalString(currTrimmed)])
    return result


#Checks database first, if not found checks spotify
def checkIfSong(name, df, sp):
    if df['Title'].str.contains(name).any():
        return True
    return searchSongInSpotify(name, sp)


def searchSingerSingingThisSong(name):
    results = sp.search(name, type='track', market=None)
    singersList = list()
    for track in results['tracks']['items']:
        for currArtist in track['artists']:
            singersList.append(currArtist['name'])

    #lists all the singers for this song, currently assuming it's the first one
    return singersList[0]


def decideIfSingerOrSong(curr, df, sp):
    if len(curr) == 1:
        return curr[0], searchSingerSingingThisSong(curr)
    if checkIfSong(curr[0].lower(), df, sp):        #check if first section is song
        return curr[0], curr[1]
    if checkIfSong(curr[1].lower(), df, sp):        #check if second section is song
        return curr[1], curr[0]
    return "", ""


def getSortedSongsNames(dest):
    dir_list = os.listdir(dest)
    result = list()
    for curr in dir_list:
        result.append([currWord.strip().replace(".mp3", "") for currWord in curr.split('-', 1)])
    return result


def isEnglish(songName):
    return songName.isascii()


def loadSortedSongsNames():
    result = list()
    result += getSortedSongsNames(destForNewHebrewSongs)
    result += getSortedSongsNames(destForNewEnglishSongs)
    return result


def sortingSongs(fileNames, df, sp):
    foundSongs = loadSortedSongsNames()

    for original, curr in fileNames:
        song, singer = decideIfSingerOrSong(curr, df, sp)
        if len(song) == 0 or len(singer) == 0:
            continue        #problem with this file

        finalName = song + " - " + singer + ".mp3"
        oldName = directoryPath + "//" + original
        if [song, singer] in foundSongs:   #or os.path.isfile(destForNewEnglishSongs) or os.path.isfile(destForNewHebrewSongs):
            print(f"The song {finalName} already exists")
        else:
            #english songs and hebrew songs are in different folders
            if isEnglish(finalName):
                newName = destForNewEnglishSongs + "//" + finalName
            else:
                newName = destForNewHebrewSongs + "//" + finalName
            os.rename(oldName, newName)
            foundSongs.append([song, singer])


def checkDirectoryExists():
    if not os.path.exists(directoryPath):
        os.makedirs(directoryPath)
    if not os.path.exists(destForNewHebrewSongs):
        os.makedirs(destForNewHebrewSongs)
    if not os.path.exists(destForNewEnglishSongs):
        os.makedirs(destForNewEnglishSongs)



if __name__ == '__main__':

    checkDirectoryExists()
    sp = spotifyConnection()
    df = uploadDF()
    fileNames = getAllFilesNames()
    sortingSongs(fileNames, df, sp)
