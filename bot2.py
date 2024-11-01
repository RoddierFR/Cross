from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import logging

# Remplacez par votre token Telegram Bot
TOKEN = "7152188372:AAHVkH3PqkjlHcbOITi8yI-eo1FwjhCM1oA"

# Initialisation du logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stockage temporaire pour les posts en cours de création par chaque utilisateur
user_posts = {}

def start(update: Update, context: CallbackContext) -> None:
    """Commande /start pour accueillir l'utilisateur."""
    update.message.reply_text(
        "Bienvenue dans le bot de création de posts ! Utilisez /newpost pour commencer à créer un post."
    )

def new_post(update: Update, context: CallbackContext) -> None:
    """Initialise un nouveau post pour l'utilisateur."""
    user_id = update.message.from_user.id
    user_posts[user_id] = {"text": "", "image_url": "", "buttons": []}
    update.message.reply_text("Démarrage de la création d'un nouveau post.\nEnvoyez une image pour votre post.")

def handle_image(update: Update, context: CallbackContext) -> None:
    """Gère l'ajout d'une image au post."""
    user_id = update.message.from_user.id
    if user_id not in user_posts:
        update.message.reply_text("Utilisez /newpost pour commencer un post avant d'envoyer une image.")
        return

    photo = update.message.photo[-1].get_file()
    photo_url = photo.file_path
    user_posts[user_id]["image_url"] = photo_url
    update.message.reply_text("Image ajoutée ! Envoyez maintenant le texte pour votre post.")

def handle_text(update: Update, context: CallbackContext) -> None:
    """Gère l'ajout de texte au post."""
    user_id = update.message.from_user.id
    if user_id not in user_posts:
        update.message.reply_text("Utilisez /newpost pour commencer un post avant d'envoyer le texte.")
        return

    user_posts[user_id]["text"] = update.message.text
    update.message.reply_text("Texte ajouté ! Utilisez /addbutton pour ajouter des boutons de lien ou /preview pour prévisualiser le post.")

def add_button(update: Update, context: CallbackContext) -> None:
    """Ajoute un bouton de lien au post."""
    user_id = update.message.from_user.id
    if user_id not in user_posts:
        update.message.reply_text("Utilisez /newpost pour commencer un post avant d'ajouter des boutons.")
        return

    if len(context.args) < 2:
        update.message.reply_text("Format : /addbutton <nom_bouton> <url>")
        return

    button_text = context.args[0]
    button_url = context.args[1]
    user_posts[user_id]["buttons"].append((button_text, button_url))
    update.message.reply_text(f"Bouton ajouté : {button_text} -> {button_url}")

def preview_post(update: Update, context: CallbackContext) -> None:
    """Prévisualise le post avant publication."""
    user_id = update.message.from_user.id
    if user_id not in user_posts:
        update.message.reply_text("Utilisez /newpost pour commencer un post avant de prévisualiser.")
        return

    post_data = user_posts[user_id]
    if not post_data["image_url"] or not post_data["text"]:
        update.message.reply_text("Assurez-vous d'avoir ajouté une image et du texte à votre post.")
        return

    keyboard = [
        [InlineKeyboardButton(text, url=url)] for text, url in post_data["buttons"]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Prévisualisation du post
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=post_data["image_url"],
        caption=post_data["text"],
        reply_markup=reply_markup
    )

def publish_post(update: Update, context: CallbackContext) -> None:
    """Publie le post pour tous les utilisateurs du bot."""
    user_id = update.message.from_user.id
    if user_id not in user_posts:
        update.message.reply_text("Utilisez /newpost pour commencer un post avant de le publier.")
        return

    post_data = user_posts[user_id]
    if not post_data["image_url"] or not post_data["text"]:
        update.message.reply_text("Assurez-vous d'avoir ajouté une image et du texte à votre post.")
        return

    keyboard = [
        [InlineKeyboardButton(text, url=url)] for text, url in post_data["buttons"]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Publication du post dans le groupe
    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=post_data["image_url"],
        caption=post_data["text"],
        reply_markup=reply_markup
    )

    # Réinitialise le post de l'utilisateur après publication
    del user_posts[user_id]
    update.message.reply_text("Post publié avec succès !")

def main() -> None:
    """Démarre le bot et configure les gestionnaires de commande."""
    updater = Updater(TOKEN)
    
    dispatcher = updater.dispatcher
    
    # Commandes de gestion du post
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("newpost", new_post))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dispatcher.add_handler(CommandHandler("addbutton", add_button))
    dispatcher.add_handler(CommandHandler("preview", preview_post))
    dispatcher.add_handler(CommandHandler("publish", publish_post))
    
    # Démarrage du bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
