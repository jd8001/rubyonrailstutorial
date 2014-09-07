import urllib
import MySQLdb
from bs4 import BeautifulSoup
import time
import argparse
import datetime
import sys
import MFI

#standard development arg string: -s 0 -e 1 -a "localhost" -u "hector" -p "#BEck59187" -d "stocks"

#Parsing Args
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start", type=int,
                    help="Starting Percentage of analysis")
parser.add_argument("-e", "--end", type=int,
                    help="Ending Percentage of analysis")
parser.add_argument("-a", "--host",
                    help="Database host address")
parser.add_argument("-u", "--username",
                    help="Database User Name")
parser.add_argument("-p", "--password",
                    help="Database Password")
parser.add_argument("-d", "--database",
                    help="Using Database")
args = parser.parse_args()


#Connect to the database server
db = MySQLdb.connect(args.host, args.username, args.password, args.database)
c=db.cursor()

c.execute("SELECT ticker, reteq FROM current ORDER BY reteq;")

results = c.fetchall()

i=0
for string in results:
    ActionString = "UPDATE current SET ReteqRank='" + str(i) + "' WHERE ticker='" + string[0] + "';"
    try:
        c.execute(ActionString)
        db.commit()
    except:
        print "Error ranking ", string[0]
    i = i + 1


c.execute("SELECT ticker, earnyield FROM current ORDER BY earnyield;")

results = c.fetchall()

i=0
for string in results:
    ActionString = "UPDATE current SET EarnYieldRank='" + str(i) + "' WHERE ticker='" + string[0] + "';"
    try:
        c.execute(ActionString)
        db.commit()
    except:
        print "Error ranking ", string[0]
    i = i + 1


c.execute("SELECT ticker, EarnYieldRank, ReteqRank FROM current;")

results = c.fetchall()

i=0
for string in results:
    Rank = int(string[1]) + int(string[2])
    ActionString = "UPDATE current SET Rank='" + str(Rank) + "' WHERE ticker='" + string[0] + "';"
    try:
        c.execute(ActionString)
        db.commit()
    except:
        print "Error ranking ", string[0]
    i = i + 1