import os
import requests
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

TELEGRAM_API_KEY = os.getenv('7256019218:AAHDhLGcE-Pa0DD59XVY9UYKZinVAEEfuT8')
API_FOOTBALL_KEY = os.getenv('f48c27d7704d2ccba35a19a88c5907e9')

# Fonction pour obtenir les matchs du jour avec les cotes
def get_matches_with_odds():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f'https://v3.football.api-sports.io/fixtures?date={today}&timezone=Europe/Paris'
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

def get_odds(fixture_id):
    url = f'https://v3.football.api-sports.io/odds?fixture={fixture_id}&timezone=Europe/Paris'
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

# Commande /start
def start(update, context):
    update.message.reply_text('Bienvenue sur le bot de paris sportifs ! Utilisez /matches pour voir les matchs du jour.')

# Commande /help
def help_command(update, context):
    update.message.reply_text('Utilisez /matches pour voir les matchs du jour et /bet pour placer un pari.')

# Commande /matches
def matches(update, context):
    data = get_matches_with_odds()
    if data and 'response' in data:
        fixtures = data['response']
        if fixtures:
            for fixture in fixtures:
                home_team = fixture['teams']['home']['name']
                away_team = fixture['teams']['away']['name']
                match_time = fixture['fixture']['date']
                fixture_id = fixture['fixture']['id']
                odds_data = get_odds(fixture_id)
                if odds_data and 'response' in odds_data:
                    odds = odds_data['response']
                    if odds:
                        home_odds = odds[0]['bookmakers'][0]['bets'][0]['values'][0]['odd']
                        away_odds = odds[0]['bookmakers'][0]['bets'][0]['values'][1]['odd']
                        match_info = f"{home_team} vs {away_team} - {match_time}\nCotes: {home_team} {home_odds} / {away_team} {away_odds}"
                        keyboard = [[InlineKeyboardButton("Parier", callback_data=str(fixture_id))]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        update.message.reply_text(match_info, reply_markup=reply_markup)
        else:
            update.message.reply_text('Aucun match trouvé pour aujourd\'hui.')
    else:
        update.message.reply_text('Impossible d\'obtenir les matchs pour le moment.')

# Gestion des boutons de pari
def button(update, context):
    query = update.callback_query
    match_id = query.data
    context.user_data['match_id'] = match_id
    query.answer()
    query.edit_message_text(text=f"Vous avez sélectionné le match ID: {match_id}. Veuillez entrer votre pari (montant et résultat).")

# Gestion des messages
def handle_message(update, context):
    if 'match_id' in context.user_data:
        match_id = context.user_data['match_id']
        bet = update.message.text
        # Logique pour enregistrer le pari
        update.message.reply_text(f'Pari enregistré pour le match ID {match_id}: {bet}')
        del context.user_data['match_id']
    else:
        update.message.reply_text('Utilisez /matches pour voir les matchs du jour.')

# Fonction principale
def main():
    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("matches", matches))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
