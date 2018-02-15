#This tool will give you the champion played of a player
#over different accounts from the last 7 days
import requests
import sys
import time
import operator
import math
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

from AccountIDs import *
from time import gmtime, strftime
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('ChampionLastPlayed.json', scope)
client = gspread.authorize(creds)



pp = pprint.PrettyPrinter()




#Returns the matchhistory of accound ID from the BeginTime
def requestMatchHistory(region, AccountID, BeginTime, APIKey):
    #Here is how I make my URL.  
    ID=(str)(AccountID)
    URL = "https://" + region + ".api.riotgames.com/lol/match/v3/matchlists/by-account/"+ ID + "?beginTime="+ BeginTime+ "&api_key=" + APIKey
    #print(URL)
    response = requests.get(URL)
    return response.json()

#Generates a List of Champions + their ID
def requestChampionList(APIKey):
    URL = "https://euw1.api.riotgames.com/lol/static-data/v3/champions?locale=en_US&dataById=false&api_key=" + APIKey
    #print(URL)
    response = requests.get(URL)
    return response.json()

#Adds up the Amount of times a Champion was played
def addMatchListToLastPlayed7(PlayedMap, responseJSON, ChampionList):
    if responseJSON.get('matches'):
        for f in responseJSON['matches']:
            for x in ChampionList['data']:
               if ChampionList['data'][x]['id'] == f['champion']:
                   if x not in PlayedMap:
                      PlayedMap[x]=1
                   else:
                      PlayedMap[x]=PlayedMap[x]+1
    return PlayedMap

#Update Teamsheet
def getChampsbyTeam(Team, TeamsPlayer, AllAccountIDs, region, BeginTime, APIKey, ChampionList):
        sht = client.open('ChampionLastPlayed')
        sheet = sht.worksheet(Team)
        sheet.update_cell(1, 5, time.ctime())
        numplayer=1
        for Player in TeamsPlayer[Team]:
            sheet.update_cell(3, numplayer*2-1, Player )
            print('\nChampions played by: ' + Player)
            PlayedMap = {}
            if Player in AllAccountIDs:
                for accountID in AllAccountIDs.get(Player):
                    responseJSON  = requestMatchHistory(region, accountID, BeginTime, APIKey)
                    PlayedMap = addMatchListToLastPlayed7(PlayedMap, responseJSON, ChampionList)
            else:
                print('No Accounts in Database')
                sheet.update_cell(5, numplayer*2, 'No Accounts in Database' )
            PlayedMap = sorted(PlayedMap.items(), key=operator.itemgetter(1),  reverse=True)
            i=5
            for champ in PlayedMap:
               
                print(champ[0]+ ': ' + (str)(champ[1]))
                sheet.update_cell(i, numplayer*2-1, champ[0] )
                sheet.update_cell(i, numplayer*2, (str)(champ[1]) )
                i+=1
              
            numplayer += 1



def getChampsbyAllTeams(TeamsPlayer, AllAccountIDs, region, BeginTime, APIKey, ChampionList):
         PlayedMap={}
         for Player in AllAccountIDs:
            for accountID in AllAccountIDs[Player]:
                responseJSON  = requestMatchHistory(region, accountID, BeginTime, APIKey)
                PlayedMap = addMatchListToLastPlayed7(PlayedMap, responseJSON, ChampionList)
         PlayedMap = sorted(PlayedMap.items(), key=operator.itemgetter(1),  reverse=True)
        
         print('\nChampions played in '+region+ ':\n' )
         sht = client.open('ChampionLastPlayed')
         sheet = sht.worksheet(region)
         sheet.update_cell(1, 5, time.ctime())
         i=4
         for champ in PlayedMap:
            sheet.update_cell(i, 1, champ[0])
            sheet.update_cell(i, 2, (str)(champ[1]))
            i += 1

def main():
   
    APIKey=(str)('RGAPI-802fea01-2575-4780-ba9d-beb373b1c491')
        #get Champion IDs
    ChampionList = requestChampionList(APIKey)
    #print(ChampionList)
    
    if('status' in ChampionList):
        print('wrong API Key')
        sys.exit()
        
    #calculate current time and time 7 days ago (-604800000)
    Time=(int)(time.time()*1000)
    BeginTime=(str)(Time-604800000)
   
    
    #Check what the user is looking for and start function accordingly
    job = input("Please enter 'KR'/'EUW' for region or team tags like 'FNC'/'SKT' or to Update all 'ALL': \n")
    #Champions played last 7 days
    if job=='ALL':
        region="KR"
        getChampsbyAllTeams(LCKTeamsPlayer, LCKAllAccountIDs, region, BeginTime, APIKey, ChampionList)
        for team in LCKTeamsPlayer.keys():
            print(team)
            getChampsbyTeam(team, LCKTeamsPlayer, LCKAllAccountIDs, region, BeginTime, APIKey, ChampionList)
        region="EUW1"
        getChampsbyAllTeams(EUTeamsPlayer, EUAllAccountIDs, region, BeginTime, APIKey, ChampionList)
        for team in EUTeamsPlayer.keys():
            getChampsbyTeam(team, EUTeamsPlayer, EUAllAccountIDs, region, BeginTime, APIKey, ChampionList)
    
    if(job =="KR"):
        region="KR"
        getChampsbyAllTeams(LCKTeamsPlayer, LCKAllAccountIDs, region, BeginTime, APIKey, ChampionList)
    if(job=="EUW"):
        region="EUW1"
        getChampsbyAllTeams(EUTeamsPlayer, EUAllAccountIDs, region, BeginTime, APIKey, ChampionList)
    if(job in EUTeamsPlayer.keys()):
        region="EUW1"
        getChampsbyTeam(job, EUTeamsPlayer, EUAllAccountIDs, region, BeginTime, APIKey, ChampionList)
    if(job in LCKTeamsPlayer.keys()):
        region="KR"
        getChampsbyTeam(job, LCKTeamsPlayer, LCKAllAccountIDs, region, BeginTime, APIKey, ChampionList)
       
#This starts my program!
if __name__ == "__main__":
    main()
