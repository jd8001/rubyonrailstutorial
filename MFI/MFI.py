import urllib
import MySQLdb
from bs4 import BeautifulSoup
import time
import argparse
import datetime
import sys

def Generate_Stock_URL(TickerSymbol):
    """This function will return the appropiate URL from google finance for the TickerSymbol provided"""
    front_string = "http://www.google.com/finance?q="
    back_string = "&fstype=ii"
    result = front_string + TickerSymbol + back_string
    return result

def Get_Page(URL):
    """This funaction will return the html file"""
    html = urllib.urlopen(URL).read()
    return html

def Get_Data(DataString, ParentID, Soup):
    """Pulls the data indicated by DataString from the annual statement in Soup"""
    Initials = Soup.find_all("td", text=DataString)
    
    #itterate through Initials looking for annual data
    for string in Initials:
        substring = string.find_parent("div")
        if substring['id'] == ParentID:
            #found the appropiate data, parse the row for return value
            value = string.find_next_sibling("td")

            #some values are set to '-' for zero, return 0 insteadt of -
            if value.string == "-":
                return 0.0
            
            #determine if in millions, throusands, etc
            power = substring.find_next("th")

            exp = 1
            if "Millions" in power.string:
                exp = 1e6
            elif "Thousands" in power.string:
                exp = 1e3
            elif "Billions" in power.string:
                exp = 1e9
            else:
                print "No exponent found"
            return float(value.string.replace(',', '')) * exp

    #print "Error, no data was found for %s with Parent %s", DataString, ParentID
    return 0.0

x=[]
def Get_Price(Ticker):
    url = "http://www.google.com/finance/historical?q=" + Ticker
    html = Get_Page(url)
    soup = BeautifulSoup(html) 
    tag = soup.find("div", id='prices')
    i = 0
    for dec in tag.descendants:
        if i == 28:
            return float(dec.string.replace(',', ''))
        i = i + 1
    
    
            
    
    
    
    
    

def Compute_Return_On_Capital(Soup):
    """Returns the Net Working Capital Calculation from the page loaded into the Soup"""

    #Compute the numerator of the returned value
    Numerator = Get_Data("Total Revenue\n", "incannualdiv", Soup) -  Get_Data("Total Operating Expense\n", "incannualdiv", Soup)
    
    #Compute the denominator
    Denominator = Get_Data("Total Current Assets\n", "balannualdiv", Soup) - Get_Data("Total Current Liabilities\n", "balannualdiv", Soup) + Get_Data("Property/Plant/Equipment, Total - Gross\n", "balannualdiv", Soup) + Get_Data("Accumulated Depreciation, Total\n", "balannualdiv", Soup)

    if Denominator == 0:
        return 0.0

    return Numerator/Denominator

def Compute_Earnings_Yield(Soup,Price):
    """Returns the Earnings Yield Calculation from the page loaded into the Soup and the current share Price"""

    #Compute the numerator of the returned value
    Numerator = Get_Data("Total Revenue\n", "incannualdiv", Soup) -  Get_Data("Total Operating Expense\n", "incannualdiv", Soup)

    #Compute the Denominator - Multiple steps for code readibility
    Denominator = (Price * Get_Data("Total Common Shares Outstanding\n", "balannualdiv", Soup)) + Get_Data("Notes Payable/Short Term Debt\n", "balannualdiv", Soup)
    Denominator = Denominator + Get_Data("Accounts Payable\n", "balannualdiv", Soup) + Get_Data("Total Long Term Debt\n", "balannualdiv", Soup)
    Denominator = Denominator + Get_Data("Redeemable Preferred Stock, Total\n", "balannualdiv", Soup) + Get_Data("Preferred Stock - Non Redeemable, Net\n", "balannualdiv", Soup)
    Denominator = Denominator + Get_Data("Minority Interest\n", "balannualdiv", Soup) - Get_Data("Cash and Short Term Investments\n", "balannualdiv", Soup)

    if Denominator == 0:
        return 0.0

    return Numerator/Denominator

def Format_Stock_Symbol_String(Ticker):
    value = Ticker.replace(' ', '')
    value = value.replace('(', '')
    value = value.replace(')', '')
    value = value.replace(',', '')
    value = value.replace('\n', '')
    value = value.replace('\r', '')
    return value

def Populate_Stock_Symbols(Database, Table, FilePath):
    cursor = Database.cursor()
    Infile = open(FilePath, 'r')

    count = 0
    string = "x"
    while string != "":
        string = Infile.readline()
        string = Format_Stock_Symbol_String(string)
        Action = "INSERT INTO " + Table + " (sym) VALUES ('" + string + "');"
        try:
            cursor.execute(Action)
            Database.commit()
            count = count + 1
        except:
            Database.rollback()
            
        
    Infile.close()
    print count, " records updated in table ", Table


def Check_For_Existing_Entry(DataBase, Ticker):
    """Returns 1 if Database.current has an entry for Ticker"""
    action = DataBase.cursor()
    ActionString = "SELECT * FROM CURRENT WHERE TICKER='" + Ticker + "';"
    action.execute(ActionString)
    CheckResults = action.fetchall();
    for CheckString in CheckResults:
            if CheckString[0] == Ticker:
                print "Found Exisintg Entry For ", Ticker
                return 1

    return 0
    

          









