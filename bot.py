#from db import *
#user1 = users
from my import *
from pyrogram import *
import pyrogram
#from pyrogram import Client,Filters
import json
import requests as r
from newsapi import *
import random
import logging as py_log
import schedule
py_log.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=py_log.INFO)
logger = py_log.getLogger()
logger.setLevel(py_log.INFO)
from threading import *
import time
import re

bot = Client("covid19bot") #the bot client
newsapi = NewsApiClient(api_key='6ec89eb5f564973a5cf3e3d14945246') #newsapi setup
userinf = {}
bot.start()
username = "@"+str(bot.get_me().username) #getting bot's username
print(username)
bot.stop()
n = "n" #A variable to be passed if you want to ignore the column in databasse update
admins = [401643149,827414826]
news = {} #For storing all news in dictionary in Title:news pair
news_countries = [] #All the countries that were retrieved via news so that they get updated in autonews like if someone used india news then 'in' will get aded to it as iit was used by a member so al news gets updated every 1.5 hrs with all the countries the user specified and also the used ones!
user_query={}

#news query
def news_q(_,query):
    a = query.data.split(":")
    if a[0] == 'news':
        user_query[str(query.from_user.id)+"_2"] = query.data
        return True
    else:
        return False
#get stats query
def stats_q(_,query):
    a = query.data
    if "stats" in a:
        return True
    else:
        return False

#return news query
def news_r(_,query):
    a = query.data.split(":")
    if a[0] == "get_news":
        return True
    else:
        return False
    
#query to delete a message on pressing exit button
def deletenow(_,query):
    a = query.data
    if "exitnow" in a:
        return True
    else:
        return False

#group auto news query
def group_a_news(_,query):
    a = query.data.split(":")
    if a[0] == 'g':
        return True
    else:
        return False

#user auto news query
def user_a_news(_,query):
    a = query.data.split(":")
    if a[0] == 'u':
        return True
    else:
        return False
    
#add country feature query
def add_a_country(_,query):
    a = query.data.split(":")
    if a[0] == "acountry":
        return True
    else:
        return False
#delete a country query
def del_a_country(_,query):
    a = query.data.split("|") #to add a country it will be added in this format in db eg c = "in:India,us:United States Of America" so we first split with , then again split with : added filters make a query handler now for ad and remove country
    if a[0] == 'delc':
        return True
    else:
        return False

#ok got it button to delete the autonews message query
def autonewsdelete(_,query):
    a= query.data
    if "autonewsdelete" in a:
        return True
    else:
        return False
# for g is group and u is user in callback query handler using split seee add an country callback data
news_filter = Filters.create(news_q)
stats_filter = Filters.create(stats_q)
news_return_filter = Filters.create(news_r)
delete_filter = Filters.create(deletenow)
gauto_filter = Filters.create(group_a_news)
uauto_filter = Filters.create(user_a_news)
add_country_filter = Filters.create(add_a_country)
del_country_filter = Filters.create(del_a_country)
autonewsdelete_filter = Filters.create(autonewsdelete)
#---------------------------------------------------------
#to update the news!
def update_the_news():
    print("\n\n\n\n\n\nStarting to update news\n\n\n\n\n\n\n\n")
    global news
    if news_countries:
        for a in news_countries:
            try:
                data = newsapi.get_top_headlines(q='corona',language='en',country = '{}'.format(a)) #get news using newsapi
                data = data['articles'] #see the articles section
            except:
                #if country not found then skip
                return False
            no = int(news[str(a)]) #the total nnumber of countries in news_countries
            m = 0
            del news[str(a)] #start clearning the dictionary
            while m <= no:
                #clearing everything
                try:
                    del news[str(a)+"_{}_title".format(m)]
                    del news[str(a)+"_{}_desc".format(m)]
                    del news[str(a)+"_{}_url".format(m)]
                except:
                    pass
                m = m+1
            p = len(data) - 1
            news[str(a)] = p
            m = 0
            for d in data:
                #start to update the dictionary
                news["{}_{}_title".format(str(a),str(m))] = d['title']
                news["{}_{}_desc".format(str(a),str(m))] = d['description']
                news["{}_{}_url".format(str(a),str(m))] = d['url']
                m = m+1
    print("\n\n\n\n\n\nCompleted Updating News\n\n\n\n\n\n")


def auto_news():
    print("Starting Auto News")
    global news_countries
    global news
    a = db.query("Select * from autonews where ison = 1")
    r = a.fetchall()
    print("Fetched Everything")
    keyboard =[]
    keyboard.append([InlineKeyboardButton("Ok got it !",callback_data= "autonewsdelete")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    for a in r:
        chat_id = a[1]
        c = a[3]
        print("cc :",c)
        if c and ((c!='') or (c!=None)):
            d = c.split(",")
            print("d: ",d)
            if (d!= '') or (d!= []) or (d!=None):
                for coun in d:
                    if coun != '':
                        e = coun.split(":")
                        print("E: ",e)
                        country = e[0]
                        name = e[1]
                        text = '**News of {}**\n\n'.format(name)
                        if country in news_countries:
                            print("Country: ",country)
                            no = int(news[str(country)])
                            m = 0
                            while m <= no:
                                n = m+1
                                title = news["{}_{}_title".format(str(country),str(m))]
                                url = news["{}_{}_url".format(str(country),str(m))]
                                text = text+"{}. [{}]({})\n".format(n,title,url)
                                m = m+1
                            print("The while Part")
                            bot.send_message(chat_id = chat_id,text = text,reply_markup = reply_markup)
                        else:
                            try:
                                print("Try Part")
                                data = newsapi.get_top_headlines(q='corona',language='en',country = '{}'.format(country))
                                data = data['articles']
                                p = len(data) - 1
                                news[str(country)] = p
                                m = 0
                                for d in data:
                                    n = m+1
                                    news["{}_{}_title".format(str(country),str(m))] = d['title']
                                    news["{}_{}_desc".format(str(country),str(m))] = d['description']
                                    news["{}_{}_url".format(str(country),str(m))] = d['url']
                                    text = text+"{}. [{}]({})\n".format(str(n),str(d['title']),str(d['url']))
                                    m = m+1
                                news_countries.append(country)
                                bot.send_message(chat_id = chat_id,text= text,reply_markup = reply_markup)
                            except:
                                print("Except Part")
                                text = text+"**Sorry No news updates available for {} right now!".format(country)
                                bot.send_message(chat_id = chat_id,text= text,reply_markup = reply_markup)
def start_schedule():
    import time
    schedule.every(83).minutes.do(update_the_news)
    schedule.every(90).minutes.do(auto_news)
    while True:
        schedule.run_pending()
        time.sleep(1)

def spam_less(b):
    chat_id = b.chat.id
    c = b.message_id
    time.sleep(7)
    bot.delete_messages(chat_id = chat_id,message_ids = c)
#-----------------------------------------------------------
@bot.on_message(Filters.command(["start{}".format(username), "start"], prefixes="/"))
def start(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id  = message.from_user.id
    chat_id = message.chat['id']
    user = check_user(user_id)
    if user:
        pass
    else:
        new_user(user_id)
    message.reply('I am Corona Virus Updates Bot  you can check and get informmation regarding corona virus with my help! \n\nTo know how to use me see /help .')

@bot.on_message(Filters.command(["help","help{}".format(username)], prefixes='/'))
def help(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id  = message.from_user.id
    chat_id = message.chat['id']
    message.reply("Hello ,\nI am The Corona Update Bot \n/stats : See stats of corona globally or just pass the country name \nFor example: ```/stats india``` will return stats of India\n/news countryname : To see news related to corona of that country \n/autonews : To toggle Auto news updates on or off\n/addcountry : Pass a country name to add it in the news updates list\n/delcountry : Remove a country from news updates list\n\n\nIf you feel symptoms like **COUGH,FEVER,CHEST PAIN,BREADTH PROBLEMS** visit a Doctor and get your desired mesidcines and test's done!and if necessary quarantine yourself at home\n\n")

#to get stats!
@bot.on_message(Filters.command(["stats","stats{}".format(username),"info","info{}".format(username)],prefixes = '/'))
def info(client,message):
    chat_id = message.chat.id
    try:
        #this is to see if a country is passed in the command or not!
        country = message.text.split(" ",1)[1]
    except:
        #if no country is passed it sets to False
        country = False
    if country:
        #If country is passed part
        a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country))) #Visit the api and get the list of countries with the matching name
        if a.status_code == 200:
            a = json.loads(a.text) #the result is in json format we use json.loads() to convert it to dictionary
            keyboard = []
            for b in a:
                name = b['name'] #Name of the country
                code = b['alpha2Code'] #country code
                keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "stats:{}".format(code))]) #now check line 41 then line 92 to see the callback response and then go to line 577 to see  how this query works!
            keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")]) #shows a exiit button to delete the message see line 53 and 94
            reply_markup = InlineKeyboardMarkup(keyboard)
            user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
            message.reply("Please choose your desired country!",reply_markup = reply_markup)
        else:
            b = message.reply("No countries with that name found make sure you are passing the right country name that exists!")
            m = b.message_id
            time.sleep(10)
            bot.delete_messages(chat_id = chat_id,message_ids = m)
    else:
        chat_id = message.chat['id']
        b = message.reply("Processing!")
        b = b.message_id
        a = r.get("https://api.thevirustracker.com/free-api?global=stats")
        total_cases = re.search('"total_cases":(.+?),',a.text)[1]
        total_recovered = re.search('"total_recovered":(.+?),',a.text)[1]
        total_unresolved = re.search('"total_unresolved":(.+?),',a.text)[1]
        total_deaths = re.search('"total_deaths":(.+?),',a.text)[1]
        new_cases_today = re.search('"total_new_cases_today":(.+?),',a.text)[1]
        deaths_today = re.search('"total_new_deaths_today":(.+?),',a.text)[1]
        text = "**Global Report**\n\n**Total Cases**: {}\n**Total Recovered**: {}\n**Total Unresolved**: {}\n**Total Deaths**: {}\n**New Cases Today**: {}\n**Deaths Today**: {}".format(total_cases,total_recovered,total_unresolved,total_deaths,new_cases_today,deaths_today)
        keyboard = []
        keyboard.append([InlineKeyboardButton("Delete",callback_data="exitnow")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id = chat_id,text = text,message_id = b,reply_markup=reply_markup)


@bot.on_message(Filters.command(['news','news{}'.format(username)],prefixes='/'))
def get_news(client,message):
    try:
        country = message.text.split(" ",1)[1] #check for country passed
    except:
        country = False
    print(country)
    if country:
        a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country))) #the same sees for the common country names and returns the shoort codes with user to choose the countries
        if a.status_code == 200:
            a = json.loads(a.text)
            keyboard = []
            for b in a:
                name = b['name'] #Name to be shown to the user
                code = b['alpha2Code'] #Short code to be used of the country
                keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "news:{}".format(code))]) #see line 35 and 105 for defining the query catching and 497 to see the working!
            keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
            message.reply("Please choose your desired country!",reply_markup = reply_markup)
        else:
            message.reply("No countries with that name found make sure you are passing the right country name that exists!")
    else:
        message.reply("Pass a country name to get News about it\nLike : ```/news india```")


@bot.on_message(Filters.command(['autonews','autonews{}'.format(username)],prefixes='/'))
def set_auto_news(client,message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    data = check_news(chat_id)
    if data:
        pass
    else:
        data = create_auto_news(chat_id)
        data = check_news(chat_id)
    keyboard = []
    if (supergroup) or (groups):
        if data[3]:
            keyboard.append([InlineKeyboardButton("Turn On Updates",callback_data="g:{}:1".format(chat_id,user_id))])
            keyboard.append([InlineKeyboardButton("Turn Off Updates",callback_data="g:{}:0".format(chat_id,user_id))])
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply("Please Choose an action:",reply_markup = reply_markup)
        else:
            b = message.reply("You havent added any countries From which you wana receive news of!\nAdd one using ```/addcountry countryname```")
            spam_less(b)
        
    else:
        if data[3]:
            keyboard.append([InlineKeyboardButton("Turn On Updates",callback_data="u:1".format(user_id))])
            keyboard.append([InlineKeyboardButton("Turn Off Updates",callback_data="u:0".format(user_id))])
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply("Please Choose an action:",reply_markup = reply_markup)
        else:
            b = message.reply("You havent added any countries From which you wana receive news of!\nAdd one using ```/addcountry countryname```")
            
@bot.on_message(Filters.command(["addcountry","addcountry{}".format(username)],prefixes='/'))
def add_country(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    try:
        country = message.text.split(" ",1)[1]
    except:
        country = False
    if country:
        print('hii')
        user_id = message.from_user.id
        chat_id = message.chat.id
        if groups or supergroup:
            check = bot.get_chat_member(chat_id,user_id).status 
            if (check == 'administrator') or (check == 'creator'):
                print("admin")
                data = check_news(chat_id)
                if data:
                    pass
                else:
                    create_auto_news(chat_id)
                a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country)))
                if a.status_code == 200:
                    a = json.loads(a.text)
                    keyboard = []
                    for b in a:
                        name = b['name']
                        code = b['alpha2Code']
                        keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "acountry:g:{}:{}".format(code,name))])
                    keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
                    message.reply("Please choose your desired country you wish to receive updates for!",reply_markup = reply_markup)
                else:
                    message.reply("Wrong Country Name Provided!")
            else:
                b = message.reply("You need to be an admin to perform that action!!!!")
                b = b.message_id
                time.sleep(7)
                bot.delete_messages(chat_id = chat_id,message_ids= b)
        else:

            a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country)))
            if a.status_code == 200:
                a = json.loads(a.text)
                keyboard = []
                for b in a:
                    name = b['name']
                    code = b['alpha2Code']
                    keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "acountry:u:{}:{}".format(code,name))])
                keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
                message.reply("Please choose your desired country you wish to receive updates for!",reply_markup = reply_markup)
    elif country == False:
        if (groups) or (supergroup):
            b = message.reply("Pass a country Name like  ```/addcountry countryname```")
            spam_less(b)
        else:
            message.reply("Pass a country Name like  ```/addcountry countryname```")
        
@bot.on_message(Filters.command(["delcountry","delcountry{}".format(username)],prefixes='/'))
def delete_country(client,message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    keyboard = []
    if supergroup or groups:
        data = check_news(chat_id)
        if data:
            c = data[3]
            if c:
                d = c.split(",")
                print("d :",d)
                m = 0
                if (d!=[]) or (d!= '') or (d!=None):
                    for e in d:
                        if e != '':
                            print("e:",e)
                            f = e.split(":")
                            print("f:",f)
                            cshort = f[0]
                            cfull = f[1]
                            keyboard.append([InlineKeyboardButton("{}".format(cfull),callback_data="delc|g|{}".format(e))])
                            m = 1
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply("Please choose the country you wish to remove from auto alerts:",reply_markup=reply_markup)
                else:
                    b = message.reply("You havent added any countries to be deleted!!")
                    b = b.message_id
                    time.sleep(7)
                    bot.delete_messages(chat_id = chat_id,message_ids= b)
            else:
                b = message.reply("You havent added any countries to be deleted!!")
                b = b.message_id
                time.sleep(7)
                bot.delete_messages(chat_id = chat_id,message_ids= b)
        else:
            create_auto_news(chat_id)
            b = message.reply("You havent added any countries to be deleted!!")
            b = b.message_id
            time.sleep(7)
            bot.delete_messages(chat_id = chat_id,message_ids= b)
    else:
        data = check_news(chat_id)
        if data:
            c = data[3]
            if c:
                d = c.split(",")
                print("d :",d)
                m = 0
                if (d!=[]) or (d!= '') or (d!=None):
                    for e in d:
                        if e != '':
                            print("e :",e)
                            f = e.split(":")
                            print("f :",f)
                            cshort = f[0]
                            cfull = f[1]
                            keyboard.append([InlineKeyboardButton("{}".format(cfull),callback_data="delc|u|{}".format(e))])
                            m = 1
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply("Please choose the country you wish to remove from auto alerts:",reply_markup=reply_markup)
                else:
                    b = message.reply("You havent added any countries to be deleted!!")
                    b = b.message_id
                    time.sleep(7)
                    bot.delete_messages(chat_id = chat_id,message_ids= b)
            else:
                b = message.reply("You havent added any countries to be deleted!!")
                b = b.message_id
                time.sleep(7)
                bot.delete_messages(chat_id = chat_id,message_ids= b)
        else:
            create_auto_news(chat_id)
            b = message.reply("You havent added any countries to be deleted!!")
            b = b.message_id
            time.sleep(7)
            bot.delete_messages(chat_id = chat_id,message_ids= b)
        
@bot.on_callback_query(news_filter)
def get_news(_,query):
    country = query.data.split(":")[1]
    country = str(country)
    country = country.lower()
    keyboard = []
    try:
        n = news[str(country)]
        m = 0
        while m <= n:
            title = news["{}_{}_title".format(str(country),str(m))]
            desc = news["{}_{}_desc".format(str(country),str(m))]
            url = news["{}_{}_url".format(str(country),str(m))]
            keyboard.append([InlineKeyboardButton("{}".format(title),callback_data = "get_news:{}:{}".format(str(country),str(m)))])
            m = m+1
        #keyboard.append([InlineKeyboardButton("🔙 Back", callback_data= user_query[str(query.from_user.id)+"_1"])])
        keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
        reply_markup = InlineKeyboardMarkup(keyboard)    
        query.edit_message_text("Choose the news you wana read: ",reply_markup=reply_markup)
    except:
        try:
            data = newsapi.get_top_headlines(q='corona',language='en',country = '{}'.format(country))
            data = data['articles']
        except:
            query.answer("Sorry No news available for that country Thanks!")
            return False
        a = data
        p = len(data) - 1
        news[str(country)] = p
        m = 0
        for d in a:
            news["{}_{}_title".format(str(country),str(m))] = d['title']
            news["{}_{}_desc".format(str(country),str(m))] = d['description']
            news["{}_{}_url".format(str(country),str(m))] = d['url']
            m+=1
        news_countries.append(str(country))
        m = 0
        while m <= p:
            title = news["{}_{}_title".format(str(country),str(m))]
            desc = news["{}_{}_desc".format(str(country),str(m))]
            url = news["{}_{}_url".format(str(country),str(m))]
            keyboard.append([InlineKeyboardButton("{}".format(title),callback_data = "get_news:{}:{}".format(str(country),str(m)))])
            m = m+1
        #keyboard.append([InlineKeyboardButton("🔙 Back", callback_data= user_query[str(query.from_user.id)+"_1"])])
        keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])    
        reply_markup = InlineKeyboardMarkup(keyboard)    
        query.edit_message_text("Choose the news you wana read: ",reply_markup=reply_markup)

@bot.on_callback_query(news_return_filter)
def return_news(_,query):
    print("Received")
    data = query.data.split(":")
    country = data[1]
    m = data[2]
    title = "**"+str(news["{}_{}_title".format(str(country),str(m))])+"**"
    desc = news["{}_{}_desc".format(str(country),str(m))]
    url = news["{}_{}_url".format(str(country),str(m))]
    text = "{}\n\n{}".format(title,desc)
    keyboard = [[InlineKeyboardButton("Read Full news", url = "{}".format(url))],[InlineKeyboardButton("🔙 Back", callback_data= user_query[str(query.from_user.id)+"_2"])],[InlineKeyboardButton("Exit",callback_data="exitnow")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text,reply_markup = reply_markup)


@bot.on_callback_query(delete_filter)
def delete_now(_,query):
    data = query.data.split(":")
    messageid = query.message.message_id
    try:
        userid = data[1]
        ison = 1
    except:
        ison = False
    if ison :
        user_id = query.from_user.id
        if user_id == userid:
            bot.delete_messages(chat_id = query.message.chat['id'], message_ids=messageid)
        else:
            query.answer("You are not meant to Press this!")
    else:    
        messageid = query.message.message_id
        bot.delete_messages(chat_id = query.message.chat['id'], message_ids=messageid)


@bot.on_callback_query(stats_filter)
def show_stats(_,query):
    country = query.data.split(":")[1]
    if country:
        query.edit_message_text("Processing!")
        a = r.get("https://api.thevirustracker.com/free-api?countryTotal={}".format(country)) #got the country abbrevation now request for the corona data using the api
        #a = a.text
        #a = a.replace("<br />\n<b>Warning</b>:  session_start(): open(/var/cpanel/php/sessions/ea-php72/sess_9c962023b9e3054cc3977e038435b451, O_RDWR) failed: No space left on device (28) in <b>/home/thevirustracker/api.thevirustracker.com/connections.php</b> on line <b>1</b><br />\n<br />\n<b>Warning</b>:  session_start(): Failed to read session data: files (path: /var/cpanel/php/sessions/ea-php72) in <b>/home/thevirustracker/api.thevirustracker.com/connections.php</b> on line <b>1</b><br />\n","")
        #a = json.loads(a)
        keyboard = []
        keyboard.append([InlineKeyboardButton("Delete",callback_data="exitnow")])
        reply_markup= InlineKeyboardMarkup(keyboard)
        try:
            data = re.search('"data":"(.+?)"',a.text)[1] == 'none'
        except:
            data = 0
        if data:
            query.edit_message_text("Currently no stats Available for that country",reply_markup = reply_markup)
        else:
            cn = re.search('"title":"(.+?)",',a.text)[1]
            total_cases = re.search('"total_cases":(.+?),',a.text)[1]
            total_recovered = re.search('"total_recovered":(.+?),',a.text)[1]
            total_unresolved = re.search('"total_unresolved":(.+?),',a.text)[1]
            total_deaths = re.search('"total_deaths":(.+?),',a.text)[1]
            new_cases_today = re.search('"total_new_cases_today":(.+?),',a.text)[1]
            deaths_today = re.search('"total_new_deaths_today":(.+?),',a.text)[1]
            text = "**{} Report**\n\n**Total Cases**: {}\n**Total Recovered**: {}\n**Total Unresolved**: {}\n**Total Deaths**: {}\n**New Cases Today**: {}\n**Deaths Today**: {}".format(cn,total_cases,total_recovered,total_unresolved,total_deaths,new_cases_today,deaths_today)
            query.edit_message_text(text,reply_markup=reply_markup)

@bot.on_callback_query(gauto_filter)
def group_auto_news(_,query):
    data = query.data.split(":")
    user = query.from_user.id
    chat = int(data[1])
    check = bot.get_chat_member(chat,user).status
    ison = int(data[2])
    if (check == 'administrator') or (check == 'creator'):
        update_news(chat,ison,'n')
        if ison:
            b = query.edit_message_text("Updates turned on Successfully\nThis group will receive news updates every 1.5 hrs")
            b = b.message_id
        else:
            b = query.edit_message_text("Updates turned off this group wont receive news updates anymore!")
            b = b.message_id
        time.sleep(7)
        bot.delete_messages(chat_id = chat, message_ids=b)
    else:
        query.answer("You aint allowed to touch it!!!")

@bot.on_callback_query(uauto_filter)
def user_auto_news(_,query):
    data = query.data.split(":")
    ison = int(data[1])
    user_id = query.from_user.id
    update_news(user_id,ison,'n')
    if ison:
        query.edit_message_text("Auto News Turned On\nYou will receive news updates every 1.5 hour")
    else:
        query.edit_message_text("Auto News Turned Off you wont receive news updates")

@bot.on_callback_query(add_country_filter)
def add_country_now(_,query):
    data = query.data.split(":")
    ctype = data[1]
    code = str(data[2]).lower()
    name = data[3]
    if ctype == 'g':
        chat_id = query.message.chat.id
        user = query.from_user.id
        try:
            a = check_news(chat_id)
        except:
            create_auto_news(chat_id)
            a = check_news(chat_id)
        c = a[3]
        if c and (c!= ''):
            a = "{}:{}".format(code,name)
            b = str(a) in str(c)
            if b:
                z = query.answer("{} is already added in countries list!".format(name))
                return ''
            else:
                c = c+"{}:{},".format(code,name)
        else:
            c = '{}:{},'.format(code,name)
        update_news(chat_id,'n',c)
        b = query.edit_message_text("Done {} added in auto updates countries!".format(name))
        time.sleep(7)
        b = b.message_id
        bot.delete_messages(chat_id = chat_id,message_ids=b)
    else:
        chat_id = query.message.chat.id
        user = query.from_user.id
        try:
            a = check_news(chat_id)
        except:
            create_auto_news(chat_id)
            a = check_news(chat_id)
        c = a[3]
        if c and (c!= ''):
            a = "{}:{}".format(code,name)
            b = str(a) in str(c)
            if b:
                query.answer("{} is already added in countries list!".format(name))
                return ''
            else:
                c = c+"{}:{},".format(code,name)
        else:
            c = '{}:{},'.format(code,name)
        update_news(chat_id,'n',c)
        query.edit_message_text("Done {} added in auto updates countries!".format(name))

@bot.on_callback_query(del_country_filter)
def del_country_now(_,query):
    data = query.data.split("|")
    chat_id = query.message.chat.id
    ctype = data[1]
    country= str(data[2])
    name = country.split(":")[1]
    if ctype == 'g':
        user = query.from_user.id
        try:
            a = check_news(chat_id)
        except:
            create_auto_news(chat_id)
            a = check_news(chat_id)
        c = a[3]
        if c and (c!= ''):
            if str(country) in c:
                d = country+","
                c = c.replace(d,"")
                update_news(chat_id,'n',c)
            else:
                pass
            b = query.edit_message_text("Done {} removed from auto updates countries!".format(name))
            print("\n\n\n\n{}\n\n\n\n".format(b))
            time.sleep(7)
            b = b.message_id
            bot.delete_messages(chat_id = chat_id,message_ids=b)
    else:
        try:
            a = check_news(chat_id)
        except:
            create_auto_news(chat_id)
            a = check_news(chat_id)
        c = a[3]
        if c and (c!= ''):
            if str(country) in c:
                d = country+","
                c = c.replace(d,"")
                update_news(chat_id,'n',c)
            else:
                pass
            query.edit_message_text("Done {} removed from auto updates countries!".format(name))

@bot.on_callback_query(autonewsdelete_filter)
def autodeletemnewsnow(_,query): 
    supergroup = query.message.chat.type == 'supergroup'
    groups = query.message.chat.type == 'group'
    chat_id = query.message.chat.id
    user = query.from_user.id
    if (supergroup) or (groups):
        messageid = query.message.message_id
        bot.delete_messages(chat_id = chat_id, message_ids=messageid)
    else:
        messageid = query.message.message_id
        bot.delete_messages(chat_id = chat_id, message_ids=messageid)
t1 = Thread(target = start_schedule)
t1.start()
bot.run()
print("Bot shutting Down")

print("Cursor Closed")
db.commit()
print("Commited Db")

print("Db conn closed")

'''
#🦠🦠🦠🦠🦠🦠'''
