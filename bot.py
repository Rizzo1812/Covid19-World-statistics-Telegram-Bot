import requests
import os
import flag
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

# Header of the requests
headers = {
    'x-rapidapi-host': "vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com",
    'x-rapidapi-key': os.environ['RAPIDAPIKEY']
    }

# Split list of countries in chuncks of n
def divide_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

# Create the list containing all countries 
def get_country_keyboard(response):
    response = response.json()
    global countries
    list_of_countries = list()
    for country in response:
        list_of_countries.append("{} {}".format(country['Country'], flag.flag(country['TwoLetterSymbol'])))
    countries = list_of_countries
    countries.sort()
    return list(divide_chunks(countries, 2))

# Build the message to send to user with statistics
def build_world_response_message(response):
    world_stats = response.json()[0]

    message = "🌎  World:\n\n" +\
    "📊  Total\n" +\
    "🦠  Total cases: "+str(f'{world_stats["TotalCases"]:,}') + "\n" +\
    "❤️‍🩹  Total recovered: "+str(f'{int(world_stats["TotalRecovered"]):,}') + "\n" +\
    "🏥  Critical cases: "+str(f'{world_stats["Serious_Critical"]:,}') + "\n" +\
    "☠️  Total deaths: "+str(f'{world_stats["TotalDeaths"]:,}') + "\n\n" +\
    "📈  Daily\n" +\
    "🤒  Active Cases: "+str(f'{world_stats["ActiveCases"]:,}') + "\n" +\
    "🦠  New cases: "+str(f'{world_stats["NewCases"]:,}') + "\n" +\
    "❤️‍🩹  New recovered: "+str(f'{world_stats["NewRecovered"]:,}') + "\n" +\
    "☠️  New deaths: "+str(f'{world_stats["NewDeaths"]:,}')
    
    return message

# Build the message to send to user with statistics
def build_country_response_message(response, selected_country):
    country_stats = [country for country in response if country['Country'] == selected_country[:-3]][0]

    message = selected_country + ":\n\n" +\
    "🗺️  Country informations\n" +\
    "👥  Population: "+str(f'{country_stats["Population"]:,}') + "\n" +\
    "🤒  Infection risk: "+str(f'{country_stats["Infection_Risk"]:,}') + "%\n" +\
    "🔬  Test percentage: "+str(f'{country_stats["Test_Percentage"]:,}') + "%\n" +\
    "❤️‍🩹  Recovery percentage: "+str(f'{country_stats["Recovery_Proporation"]:,}') + "%\n" +\
    "☠️  Fatality rate: "+str(f'{country_stats["Case_Fatality_Rate"]:,}') + "%\n\n" +\
    "📊  Total\n" +\
    "🦠  Total cases: "+str(f'{country_stats["TotalCases"]:,}') + "\n" +\
    "❤️‍🩹  Total recovered: "+str(f'{int(country_stats["TotalRecovered"]):,}') + "\n" +\
    "🔬  Total tests: "+str(f'{int(country_stats["TotalTests"]):,}') + "\n" +\
    "🏥  Critical cases: "+str(f'{country_stats["Serious_Critical"]:,}') + "\n" +\
    "☠️  Total deaths: "+str(f'{country_stats["TotalDeaths"]:,}') + "\n\n" +\
    "📈  Daily\n" +\
    "🦠  New cases: "+str(f'{country_stats["NewCases"]:,}') + "\n" +\
    "🤒  Active Cases: "+str(f'{country_stats["ActiveCases"]:,}') + "\n" +\
    "❤️‍🩹  New recovered: "+str(f'{country_stats["NewRecovered"]:,}') + "\n" +\
    "☠️  New deaths: "+str(f'{country_stats["NewDeaths"]:,}')

    return message

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
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

# Handle /info command
def info(update, contex):
    """Send a message with more info about the BOT when the command /info is issued."""
    info_message = ("Welcome to Covid-19 World Statistics 👋\n"
        "This is a simple telegram BOT that allows you to get statistics about the Covid-19 pandemic 😷\n\n"
        "Use the following commands:\n"
        "/worldstats  - Get latest Covid-19 worldwide statistics\n"
        "/countrystats - Get latest Covid-19 statistic of a specific country\n"
        "/info - More info and credits\n\n\n"
        "ℹ️ MORE INFO ℹ️\n"
        "The code of this BOT is open source\n"
        "Source code is on GitHub: https://github.com/Rizzo1812/Covid19-World-statistics-Telegram-Bot\n\n"
        "🤒 Infection percentage: Total Number of covid-19 cases divided by Total Population since the beginning of outbreak\n"
        "🔬 Test percentage: Total number of tests divided by total population\n"
        "❤️‍🩹 Recovery percentage: Total number of recovered cases divided by Total number of covid-19 cases\n"
        "☠️ Fatality rate: Total Number of Deaths due to Covid-19 divided by Total Number of confirmed cases since the beginning of outbreak (It shows that how lethal covid-19 is in any country)\n\n"
        "©️ Credits ©️\n"
        "This BOT uses free API provided by VACCOVID(https://vaccovid.live/) which can be found on RapidAPI")
    update.message.reply_text(info_message)

# Handle /worldstats command
def worldstats(update, context):
    response = requests.request("GET", "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/npm-covid-data/world", headers=headers)    
    
    update.message.reply_text(build_world_response_message(response))
    return ConversationHandler.END

# Handle /countrystats command
def countrystats(update, context):
    response = requests.request("GET", "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/npm-covid-data/countries", headers=headers)
    country_keyboard = get_country_keyboard(response)

    update.message.reply_text(
        'Now select the country for which you want to get statistics',
        reply_markup=ReplyKeyboardMarkup(
            country_keyboard, one_time_keyboard=True, input_field_placeholder='Select country'
        ),
    )
    return 1

# Send Covid19 statistics of a country
def country_report(update, context):
    if update.message.text not in countries:
        update.message.reply_text('This is not a valid Country',reply_markup = ReplyKeyboardRemove())
        return ConversationHandler.END

    response = requests.request("GET", "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/npm-covid-data/countries", headers=headers).json()
    
    update.message.reply_text(
        build_country_response_message(response,update.message.text),
        reply_markup = ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Error log
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# BOT start
def main():
    """Start the bot."""
    # Binding bot to code
    updater = Updater(os.environ['TELEGRAMAPIKEY'], use_context=True)

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
