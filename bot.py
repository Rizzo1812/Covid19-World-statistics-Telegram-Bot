import requests
import json
import time
import os
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

countries = list()
country_keyboard = None

# Header of the requests
headers = {
    'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
    'x-rapidapi-key': os.environ['RAPIDAPIKEY']
    }

#divide list of countries in chuncks of 2
def divide_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

# Create the list containing all countries 
def create_country_list():
    global country_keyboard
    jsonfile = open('ISO3166.json',encoding='UTF-8')
    data = json.load(jsonfile)
    for country in data:
        countries.append("{} {} ({})".format(country['emojiFlag'], country['country'], country['isoCode']))
    country_keyboard = list(divide_chunks(countries, 2))

# Get iso code of a country 
def get_iso(country_string):
    return country_string[country_string.find("(")+1:country_string.find(")")]

# Build the message to send to user with statistics
def build_response_message(response, country="World"):
    response = response.json()[0]
    if country != "World" and response["lastUpdate"] is None:
        return "Data not available for " + response["country"]

    if country == "World":
        message = "🌎 World:\n\n"
    else:
        message = country[0:2] + " " + response["country"] + ":\n\n"
    message += "🦠  Positive cases: "+str(f'{response["confirmed"]:,}') + "\n" +\
    "❤️‍🩹 Recovered: "+str(f'{response["recovered"]:,}') + "\n" +\
    "🏥  Critical cases: "+str(f'{response["critical"]:,}') + "\n" +\
    "☠️  Deaths: "+str(f'{response["deaths"]:,}') + "\n"
    
    return message

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Handle /start command
def start(update, context):
    """Send a welcome message when the command /start is issued."""
    welcome_message = ("Welcome to Covid-19 World Statistics 👋\n"
        "This is a simple telegram BOT that allows you to get statistics about the Covid-19 pandemic 😷\n\n"
        "Use the following commands:\n"
        "/worldstats  - Get latest Covid-19 worldwide statistics\n"
        "/countrystats - Get latest Covid-19 statistic of a specific country\n"
        "/info - More info and credits")
    update.message.reply_text(welcome_message)

def info(update, contex):
    """Send a message with more info about the BOT when the command /info is issued."""
    info_message = ("Welcome to Covid-19 World Statistics 👋\n"
        "This is a simple telegram BOT that allows you to get statistics about the Covid-19 pandemic 😷\n\n"
        "Use the following commands:\n"
        "/worldstats  - Get latest Covid-19 worldwide statistics\n"
        "/countrystats - Get latest Covid-19 statistic of a specific country\n"
        "/info - More info and credits\n\n\n"
        "ℹ️ MORE INFO ℹ️\n"
        "This BOT uses free APIs provided by RapidAPI\n"
        "https://rapidapi.com/\n\n"
        "The code of this BOT is open source\n"
        "Source code is on GitHub: https://github.com/Rizzo1812/Covid19-daily-report-Telegram-Bot\n\n"
        "©️ Credits ©️\n"
        "This BOT uses a list of all countries made by selimata (GitHub user)\n"
        "https://gist.github.com/selimata")
    update.message.reply_text(info_message)

# Handle /worldstats command (send Covid19 global statistics)
def countrystats(update, context):
    update.message.reply_text(
        'Now select country',
        reply_markup=ReplyKeyboardMarkup(
            country_keyboard, one_time_keyboard=True, input_field_placeholder='Select country'
        ),
    )
    return 1

# Handle /countrystats command
def worldstats(update, context):
    response = requests.request("GET", "https://covid-19-data.p.rapidapi.com/totals", headers=headers)    
    while response.status_code != 200:
        time.sleep(1.1)
        response = requests.request("GET", "https://covid-19-data.p.rapidapi.com/totals", headers=headers) 
    
    update.message.reply_text(build_response_message(response))
    return ConversationHandler.END

# Send Covid19 statistics of a country
def country_report(update, context):
    if update.message.text not in countries:
        update.message.reply_text('Sorry this is not a valid Country',reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    querystring = {"code":get_iso(update.message.text),"format":"json"}
    response = requests.request("GET", "https://covid-19-data.p.rapidapi.com/country/code", headers=headers, params=querystring)    
    while response.status_code != 200:
        time.sleep(1.1)
        response = requests.request("GET", "https://covid-19-data.p.rapidapi.com/country/code", headers=headers, params=querystring)    

    update.message.reply_text(
        build_response_message(response,update.message.text),
        reply_markup = ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Error log
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Binding bot to code
    updater = Updater(os.environ['TELEGRAMAPIKEY'], use_context=True)
    create_country_list()

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # /start handler
    dp.add_handler(CommandHandler('start', start))

    # /info handler
    dp.add_handler(CommandHandler('info', info))

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('worldstats', worldstats),CommandHandler('countrystats', countrystats)],
        states={
            1: [MessageHandler(Filters.text, country_report)],
        },
        fallbacks=[],
    )
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()

if __name__ == '__main__':
    main()
