import numpy as np
import urllib2
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import sys
from itertools import cycle, islice

%matplotlib inline

#plt.rcParams['backend'] = "Qt4Agg"
#set unicode for error 'UnicodeEncodeError"
reload(sys)
sys.setdefaultencoding('utf-8')

#create User-Agent (solve 404 error)
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

#compile urls into matrix 
url_list = [['http://www.foxsports.com/soccer/team-stats?competition=1&season=20160&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=1&season=20150&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=1&season=20140&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=1&season=20130&category=standard&sort=1'],
            ['http://www.foxsports.com/soccer/team-stats?competition=2&season=20160&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=2&season=20150&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=2&season=20140&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=2&season=20130&category=standard&sort=1'],
            ['http://www.foxsports.com/soccer/team-stats?competition=3&season=20160&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=3&season=20150&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=3&season=20140&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=3&season=20130&category=standard&sort=1'],
            ['http://www.foxsports.com/soccer/team-stats?competition=4&season=20160&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=4&season=20150&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=4&season=20140&category=standard&sort=1',
           'http://www.foxsports.com/soccer/team-stats?competition=4&season=20130&category=standard&sort=1']]

#inputing url for scraping
url_header = opener.open('http://www.foxsports.com/soccer/team-stats?competition=1&season=20160&category=standard&sort=1')

#parse url into soup
soup = BeautifulSoup(url_header, "html.parser")


#find desire table
table = soup.find("table", attrs = {'class' : 'wisbb_standardTable'})


#find headers
table_rows = table.findAll('th')
table_headers =[th.text for th in table_rows]
#remove spacing symbols
table_headers = [headers.replace('\r\n','') for headers in table_headers]
table_headers = [headers.replace('\t','') for headers in table_headers]
#adding "SEASON" and "LEAGUE" columns into table header
table_headers.append('SEASON')
table_headers.append('LEAGUE')

#skip header and find data row


#create empty list for data rows
Data = []

#for each table row
for url_league in url_list:
    for url in url_league:
        url_rows = opener.open(url)

        #parse url into soup
        soup = BeautifulSoup(url_rows, "html.parser")

        #find table
        table = soup.find("table", attrs = {'class' : 'wisbb_standardTable'})
    
        data_rows = table.findAll('tr')[1:]
        #find all <tr> tag
        for i in range(len(data_rows)):
            team_rows = [] #create an emptly list for each team's record


        #for each table data element from each table row
            for td in data_rows[i].findAll('td'):
                textrow = td.getText()

                if td == data_rows[i].find('td'):
                    td = data_rows[i].findAll('span')[1]
                    textrow = td.getText() #set found string to variable 
                
                #extract extra chracters
                if '\n\n\n' in textrow:
                    textrow = textrow.replace('\n\n\n','')
                if '\n' in textrow:
                    textrow = textrow.replace('\n','')
                team_rows.append(textrow)
            

            #Fill 'SEASON' value   
            if '20160' in url:
                team_rows.append('2016')
            elif '20150' in url:
                team_rows.append('2015')
            elif '20140' in url:
                team_rows.append('2014')
            else:
                team_rows.append('2013')
                
            #Fill 'LEAGUE' value
            if 'competition=1' in url:
                team_rows.append('Premier League')
            elif 'competition=2' in url:
                team_rows.append('La Liga')
            elif 'competition=3' in url:
                team_rows.append('Serie A')
            else:
                team_rows.append('Bundesliga I')
                    
        #Append each team matrix
            Data.append(team_rows)
           
    #put the rows and headers into a dataframe
        df = pd.DataFrame(Data, columns = table_headers)

#change first column's name to 'Team'
df.rename(columns = {u'STANDARD' : 'TEAM'}, inplace = True)

#convert records type from object to numeric (integer)
df[['GF', 
     'A','SOG',
     'S','HG','KG',
     'YC','RC','F','OFF','SEASON']] = df[['GF', 
     'A','SOG',
     'S','HG','KG',
     'YC','RC','F','OFF', 'SEASON']].apply(pd.to_numeric, downcast = 'integer')


##METRIC Calculation 

#group by Team and Season for aggergation 
dfGrouped = df.groupby(['TEAM','SEASON'])

#Add 'Goals Per Game' calculation to each team record
df['GPG'] = df[df["LEAGUE"] == "Bundesliga I"]["GF"]/34
df['GPG'][df["LEAGUE"] <> "Bundesliga I"] = df[df["LEAGUE"] <> "Bundesliga I"]["GF"]/38

#Add 'Shots on Goal Per Game' calculation to each team record
df['SOGPG'] = df[df["LEAGUE"] == "Bundesliga I"]["SOG"]/34
df['SOGPG'][df["LEAGUE"] <> "Bundesliga I"] = df[df["LEAGUE"] <> "Bundesliga I"]["SOG"]/38

#Add 'Fouls Per Game' calculation to each team record
df['FPG'] = df[df["LEAGUE"] == "Bundesliga I"]["F"]/34
df['FPG'][df["LEAGUE"] <> "Bundesliga I"] = df[df["LEAGUE"] <> "Bundesliga I"]["F"]/38

#Add 'Red Cards Per Game' calculation to each team record
df['RCPG'] = df[df["LEAGUE"] == "Bundesliga I"]["RC"]/34
df['RCPG'][df["LEAGUE"] <> "Bundesliga I"] = df[df["LEAGUE"] <> "Bundesliga I"]["RC"]/38

#Add 'Yellow Cards Per Game' calculation to each team record
df['YCPG'] = df[df["LEAGUE"] == "Bundesliga I"]["YC"]/34
df['YCPG'][df["LEAGUE"] <> "Bundesliga I"] = df[df["LEAGUE"] <> "Bundesliga I"]["YC"]/38


#Round up calculation by 2 decimal points
df = df.round({'GPG': 2, 'SOGPG': 2, 'FPG': 2, 'RCPG': 2, 'YCPG': 2})


#VISUALIZATION 
#Set colors
my_colors = list(islice(cycle(['#d78b8b', '#efb583', '#8aaec6', '#9ac59a']), None, len(df)))

#Set aggergration by LEAUGE 
dfGrouped = df.groupby(['LEAGUE'])
 
#FPG Calculation 
Fouls_Viz = dfGrouped['FPG'].mean()
#Plot bar chart for FPG by league 
BarChart = Fouls_Viz.plot(kind = 'bar', color = my_colors).set_ylabel('Average Fouls Per Game')
#Plot frenquency distribution of FPG by league - broken down by color
plt.hist(df[df["LEAGUE"]=="Premier League"]["FPG"].reset_index(drop=True), alpha=0.6, label="Premier League")
plt.hist(df[df["LEAGUE"]=="La Liga"]["FPG"].reset_index(drop=True), alpha=0.6, label="La Liga")
plt.hist(df[df["LEAGUE"]=="Serie A"]["FPG"].reset_index(drop=True), alpha=0.6, label="Serie A")
plt.hist(df[df["LEAGUE"]=="Bundesliga I"]["FPG"].reset_index(drop=True), alpha=0.6, label="Bundesliga I")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
plt.show()
#Plot a normal distribution 
df.hist('FPG')



#GPG Calculation 
Fouls_Viz = dfGrouped['GPG'].mean()
#Plot bar chart for GPG by league 
BarChart = Fouls_Viz.plot(kind = 'bar', color = my_colors).set_ylabel('Average Goals Per Game')
#Plot frenquency distribution of FPG by league - broken down by color
plt.hist(df[df["LEAGUE"]=="Premier League"]["GPG"].reset_index(drop=True), alpha=0.6, label="Premier League")
plt.hist(df[df["LEAGUE"]=="La Liga"]["GPG"].reset_index(drop=True), alpha=0.6, label="La Liga")
plt.hist(df[df["LEAGUE"]=="Serie A"]["GPG"].reset_index(drop=True), alpha=0.6, label="Serie A")
plt.hist(df[df["LEAGUE"]=="Bundesliga I"]["GPG"].reset_index(drop=True), alpha=0.6, label="Bundesliga I")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
plt.show()
#Plot a normal distribution 
df.hist('GPG')

#SOGPG Calculation 
Fouls_Viz = dfGrouped['SOGPG'].mean()
#Plot bar chart for SOGPG by league 
BarChart = Fouls_Viz.plot(kind = 'bar', color = my_colors).set_ylabel('Average Shots on Goal Per Game')
#Plot frenquency distribution of FPG by league - broken down by color
plt.hist(df[df["LEAGUE"]=="Premier League"]["SOGPG"].reset_index(drop=True), alpha=0.6, label="Premier League")
plt.hist(df[df["LEAGUE"]=="La Liga"]["SOGPG"].reset_index(drop=True), alpha=0.6, label="La Liga")
plt.hist(df[df["LEAGUE"]=="Serie A"]["SOGPG"].reset_index(drop=True), alpha=0.6, label="Serie A")
plt.hist(df[df["LEAGUE"]=="Bundesliga I"]["SOGPG"].reset_index(drop=True), alpha=0.6, label="Bundesliga I")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
plt.show()
#Plot a normal distribution 
df.hist('SOGPG')

