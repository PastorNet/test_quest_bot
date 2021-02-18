class Configuration:
    TOKEN = ''
    DB_NAME = ''
    API = 'https://api.exchangeratesapi.io/'
    HELP_MESSAGE = 'What can this bot do?\n\n' \
                   'You can explore rates of  currency, exchange currency and get a graph of Week-rate changes!\n\n' \
                   'Example:\n\n/history CAD - gets a graph of week-rate changes for CAD based on USD.\n\n' \
                   '/list or /lst - gets a list of current rates based on USD\n\n' \
                   '/exchange 10 USD to CAD - gets a current exchanged money based on USD\n\n'
