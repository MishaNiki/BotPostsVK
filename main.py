from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardRemove, InputMediaPhoto, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from storage import storage
from model import chat
from vk import vk
import config


STORAGE = storage.TestStorage()
VK = vk.VK(config.VK_TOKEN)
bot = Bot(config.BOT_TOKEN) # necessary for sending a media group


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("""\
        Добро пожаловать!
        С моей помошью ты сможешь просматривать обновленния в сообществах в вконтакте, не заходя в саму соц сеть.
    """)
    STORAGE.get_chat(update.message.chat.id).set_state(chat.State.INACTIVE)


# help
def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("""
                            /get_posts - вывод постов сообщества\n/community - вывод ваших сообществ
                            """)
    STORAGE.get_chat(update.message.chat.id).set_state(chat.State.INACTIVE)


def get_posts(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введите uuid или ссылку сообщества')

    STORAGE.get_chat(update.message.chat.id).set_state(chat.State.GET_POSTS_STAGE_1)


def get_community(update, context):
    """get list community"""

    # create menu
    menu = []
    # getting the list of communities of this chat
    for key, value in STORAGE.get_chat(update.message.chat.id).groups.items():
        menu_item = []
        menu_item.append(InlineKeyboardButton(value, callback_data=str(key))) # callback_data is community id
        menu.append(menu_item)

    if len(menu) == 0:
        # menu empty
        update.message.reply_text('У вас пока нет сообществ')
    else:
        # send menu
        reply_markup = InlineKeyboardMarkup(menu)
        update.message.reply_text('Ваши сообщества:', reply_markup=reply_markup)


def select_group(update, context):
    """Select group"""
    query = update.callback_query
    print(query)
    query.answer()
    query.edit_message_text(text="Введите количество постов")
    STORAGE.get_chat(query.message.chat.id).select_group_id(query.data)

    # update state chat
    STORAGE.get_chat(query.message.chat.id).set_state(chat.State.GET_POSTS_STAGE_2)


def text(update, context):
    """ Execute commands based on chat status """

    state = STORAGE.get_chat(update.message.chat.id).state # get state chat

    if state == chat.State.INACTIVE:
        update.message.reply_text('введите /help')

    elif state == chat.State.GET_POSTS_STAGE_1:
        # Checking uuid vk community
        id_group = VK.check_by_uuid(update.message.text.strip()) # get id community

        if id_group < 0:
            # community does not exist
            STORAGE.get_chat(update.message.chat.id).set_state(chat.State.INACTIVE)
            update.message.reply_text('Нет такого сообщества')
            return

        # community exists
        # set community id to select chat
        STORAGE.get_chat(update.message.chat.id).select_group_id(id_group)
        update.message.reply_text('Введите количество постов')
        # update state
        STORAGE.get_chat(update.message.chat.id).set_state(chat.State.GET_POSTS_STAGE_2)

    elif state == chat.State.GET_POSTS_STAGE_2:
        # output posts
        # verification of entered data
        if not update.message.text.strip().isdigit():
            update.message.reply_text('Вы ввели не число, попробуйте ещё раз)')
            return
        elif int(update.message.text.strip()) < 0 :
            update.message.reply_text('Количество не может быть отрицательным, попробуйте ещё раз)')


        # receiving posts and community names by id and quantity
        posts, name_group = VK.get_posts_by_id(STORAGE.get_chat(update.message.chat.id).group_id,
                                   int(update.message.text.strip()))

        # add group to chat dictionary
        STORAGE.get_chat(update.message.chat.id).set_group(name_group)
        update.message.reply_text('Найдено: ' + str(len(posts)),
                                  reply_markup=ReplyKeyboardRemove())

        # send posts
        for post in posts:

            if len(post.photos) == 0:
                # the post has no content only text
                update.message.chat.send_message(post.text + '\n' + str(post.date))
            elif len(post.photos) == 1 and len(post.text) < 550:
                # the post has one image and the text fits into the description
                update.message.chat.send_photo(post.photos[0], caption=post.text + '\n' + str(post.date))
            else :
                # more than one image, add a media group
                update.message.chat.send_message(str(post.date) + '\n' + post.text)
                # create media group
                media = []
                for photo in post.photos:
                    media.append(InputMediaPhoto(photo))
                bot.send_media_group(update.message.chat.id, media)

        # update state chat
        STORAGE.get_chat(update.message.chat.id).set_state(chat.State.INACTIVE)


def main():
    print('Run telegram bot')

    updater = Updater(config.BOT_TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("get_posts", get_posts))
    dp.add_handler(CommandHandler("community", get_community))
    dp.add_handler(CallbackQueryHandler(select_group))
    dp.add_handler(MessageHandler(Filters.text, text))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
