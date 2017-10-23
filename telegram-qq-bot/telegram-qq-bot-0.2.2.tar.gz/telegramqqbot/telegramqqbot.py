from pyqqclient.SmartqqClient import SmartqqClient
from pyqqclient.Logger import logger
from pyqqclient.UnknownUserException import UnknownUserException
from pyqqclient.LoginExpiredException import LoginExpiredException
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
import threading
import json


BOT_LOGIN, IDLE, LOGGED_IN, REPLYING = range(4)


def double_map(func, list0, list1):
    if len(list0) != len(list1):
        return None
    ans = []
    for i in range(len(list0)):
        ans.append(func(list0[i], list1[i]))
    return ans


def nested_double_map(func, nested_list0, nested_list1):
    return double_map(lambda list0, list1: double_map(func, list0, list1), nested_list0, nested_list1)


def get_callback_markup(text_list: [], data_list: []) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        nested_double_map(
            lambda text, data: InlineKeyboardButton(text=text, callback_data=json.dumps(data)),
            text_list, data_list
        )
    )


def get_reply_contact_button(uin: int) -> InlineKeyboardMarkup:
    return get_callback_markup([["Reply"]], [[["reply_contact", uin]]])


def get_reply_group_button(gid: int) -> InlineKeyboardMarkup:
    return get_callback_markup([["Reply"]], [[["reply_group", gid]]])


def get_contact_keyboard(uin: int, subscribed) -> InlineKeyboardMarkup:
    return (
        get_callback_markup([["Subscribe"]], [[["sub_contact", uin]]]) if uin not in subscribed
        else get_callback_markup(
            [["Unsubscribe", "Send message"]],
            [[["unsub_contact", uin], ["reply_contact", uin]]]
        )
    )


def get_group_keyboard(gid: int, subscribed) -> InlineKeyboardMarkup:
    return (
        get_callback_markup([["Subscribe"]], [[["sub_group", gid]]]) if gid not in subscribed
        else get_callback_markup(
            [["Unsubscribe", "Send message"]],
            [[["unsub_group", gid], ["reply_group", gid]]]
        )
    )


def reply_subbed_contact(reply_callback, contact, subscribed_contact):
    reply_callback(
        text=SmartqqClient.get_user_name(contact),
        reply_markup=get_contact_keyboard(contact["uin"], subscribed_contact)
    )


def reply_subbed_group(reply_callback, group, subscribed_group):
    reply_callback(
        text=SmartqqClient.get_group_name(group),
        reply_markup=get_group_keyboard(group["gid"], subscribed_group)
    )


def error(bot, update, received_error):
    logger.warning('Update "%s" caused error "%s"' % (update, received_error))


def start_handler(bot, update, user_data):
    update.message.reply_text("Hello there, if you're my master, type the password below:")
    user_data["logged_in"] = False
    user_data["listed_items"] = []

    def forward_contact_message_handler(message, env=None):
        content = message["value"]
        uin = content["from_uin"]
        if user_data["print_all"] or (uin in user_data["subscribed_contact"]):
            name = SmartqqClient.get_user_name(env["contact_manager"].get_contact_info(uin))
            return update.message.reply_text(
                "[%s]%s" % (
                    name,
                    SmartqqClient.get_message_content(content)
                ),
                reply_markup=get_reply_contact_button(uin)
            )

    def forward_group_message_handler(message, env=None):
        content = message["value"]
        gid = content["from_uin"]
        uin = content["send_uin"]
        if env is not None and uin == env["uin"]:
            return None
        group_manager = env["group_manager"]
        if user_data["print_all"] or (gid in user_data["subscribed_group"]):
            name = SmartqqClient.get_group_name(group_manager.get_group_info(gid))
            return update.message.reply_text(
                "[[%s] - [%s]]%s" % (
                    name,
                    SmartqqClient.get_user_name(group_manager.get_member_info(gid, uin)),
                    SmartqqClient.get_message_content(content)
                ),
                reply_markup=get_reply_group_button(gid)
            )

    def message_exception_handler(ex):
        if ex.__class__ == LoginExpiredException:
            update.message.reply_text("Login expired, please use /logout and /clear_login to login again.")

    def login_done():
        user_data["logged_in"] = True
        user_data["env"] = user_data["client"].env
        update.message.reply_text("You've logged in successfully")
    client = SmartqqClient(
        barcode_handler=lambda barcode: update.message.reply_photo(
            barcode, caption="Please scan the barcode to login."
        ),
        db_identify_string=str(update.message.chat_id),
        friend_message_handler=forward_contact_message_handler,
        group_message_handler=forward_group_message_handler,
        message_exception_handler=message_exception_handler,
        login_done_handler=login_done,
        passing_env=True
    )
    user_data["client"] = client
    return BOT_LOGIN


def stop_handler(bot, update, user_data: dict):
    logout_handler(bot, update, user_data)
    update.message.reply_text("bye.")
    # history_contact_name = set(user_data["subscribed_contact"].values())
    # history_group_name = set(user_data["subscribed_group"].values())
    user_data.clear()
    # user_data["history_contact_name"] = history_contact_name
    # user_data["history_group_name"] = history_group_name
    return ConversationHandler.END


def login_handler(bot, update, user_data, args=None):
    user_data["subscribed_contact"] = {}
    user_data["subscribed_group"] = {}
    user_data["print_all"] = (args is not None) and ("print_all" in args)
    client = user_data["client"]
    client.stopped = False
    client_thread = threading.Thread(target=client.run)
    user_data["client_thread"] = client_thread
    client_thread.start()
    return LOGGED_IN


def clear_login_handler(bot, update, user_data, args=None):
    user_data["client"].login_data = None
    user_data["logged_in"] = False
    return login_handler(bot, update, user_data, args=args)


def bot_login_handler(bot, update):
    if update.message.text == "mypasswd":
        update.message.reply_text("Welcome, my master")
        return IDLE
    else:
        update.message.reply_text("You're not my master!\nRetry:")
        return BOT_LOGIN


def logout(reply_callback, user_data):
    client = user_data["client"]
    client_thread = user_data["client_thread"]
    client.stopped = True
    reply_callback("Waiting for the client instance to stop...")
    client_thread.join()
    client.db_clear_all()
    history_contact_name = set(user_data["subscribed_contact"].values())
    history_group_name = set(user_data["subscribed_group"].values())
    history_listed_items = user_data["listed_items"]
    user_data.clear()
    user_data["client"] = client
    user_data["logged_in"] = False
    user_data["history_contact_name"] = history_contact_name
    user_data["history_group_name"] = history_group_name
    user_data["listed_items"] = history_listed_items
    reply_callback("Logged out.")


def logout_handler(bot, update, user_data):
    logout(update.message.reply_text, user_data)
    return IDLE


def reply_with_contact(reply_callback, contact, subscribed_contact):
    return reply_callback(
        text=SmartqqClient.get_user_name(contact),
        reply_markup=get_contact_keyboard(contact["uin"], subscribed_contact)
    )


def reply_with_group(reply_callback, group, subscribed_group):
    return reply_callback(
        text=SmartqqClient.get_group_name(group),
        reply_markup=get_group_keyboard(group["gid"], subscribed_group)
    )


def get_category_button(category):
    return get_callback_markup([["List"]], [[["list_category", category["index"]]]])


def reply_with_category(update, category):
    return update.message.reply_text(
        text=category["name"],
        reply_markup=get_category_button(category)
    )


def list_contact_handler(bot, update, user_data, args=None):
    listed_items = user_data["listed_items"]
    if not user_data["logged_in"]:
        update.message.reply_text("The login process haven't finished, please wait for a few seconds...")
        return LOGGED_IN
    client_contact_manager = user_data["env"]["contact_manager"]
    if (args is not None) and ("-c" in args):
        categories = client_contact_manager.get_categories_info()
        for category in categories:
            listed_items.append(reply_with_category(update, category))
    else:
        contacts = client_contact_manager.get_contacts_info()
        for contact in contacts:
            listed_items.append(reply_with_contact(update.message.reply_text, contact, user_data["subscribed_contact"]))
    return LOGGED_IN


def list_category_handler(bot, update, user_data):
    reply_callback = update.callback_query.message.reply_text
    if not user_data["logged_in"]:
        reply_callback("The login process haven't finished, please wait for a few seconds...")
        return LOGGED_IN
    listed_items = user_data["listed_items"]
    client_contact_manager = user_data["env"]["contact_manager"]
    query = json.loads(update.callback_query.data)
    contacts = client_contact_manager.get_contacts_info_in_category(query[1])
    listed_items.append(reply_callback("Contacts under selected category:"))
    for contact in contacts:
        listed_items.append(reply_with_contact(reply_callback, contact, user_data["subscribed_contact"]))
    update.callback_query.answer()
    return LOGGED_IN


def list_group_handler(bot, update, user_data):
    listed_items = user_data["listed_items"]
    if not user_data["logged_in"]:
        listed_items.append(update.message.reply_text("The login process haven't finished," +
                                                      " please wait for a few seconds..."))
        return LOGGED_IN
    client_group_manager = user_data["env"]["group_manager"]
    groups = client_group_manager.get_groups_info()
    for group in groups:
        listed_items.append(reply_with_group(update.message.reply_text, group, user_data["subscribed_group"]))
    return LOGGED_IN


def list_subscribed_handler(bot, update, user_data):
    listed_items = user_data["listed_items"]
    listed_items.append(update.message.reply_text("Subscribed contacts:"))
    subscribed_contact = user_data["subscribed_contact"]
    client_contact_manager = user_data["env"]["contact_manager"]
    for contact in map(client_contact_manager.get_contact_info, subscribed_contact.keys()):
        listed_items.append(reply_with_contact(update.message.reply_text, contact, subscribed_contact))
    listed_items.append(update.message.reply_text("Subscribed groups:"))
    subscribed_group = user_data["subscribed_group"]
    client_group_manager = user_data["env"]["group_manager"]
    for group in map(client_group_manager.get_group_info, subscribed_group.keys()):
        listed_items.append(reply_with_group(update.message.reply_text, group, subscribed_group))
    return LOGGED_IN


def clear_list_handler(bot, update, user_data):
    listed_items = user_data["listed_items"]
    for item in listed_items:
        item.delete()
    user_data["listed_items"].clear()
    update.message.reply_text("Cleared listed items.")
    return LOGGED_IN


def subscribe_contact(user_data, uin: int):
    try:
        contact = user_data["env"]["contact_manager"].get_contact_info(uin)
    except UnknownUserException:
        return None
    user_data["subscribed_contact"][uin] = SmartqqClient.get_user_name(contact)
    return contact


def unsubscribe_contact(user_data, uin: int):
    if uin in user_data["subscribed_contact"]:
        del user_data["subscribed_contact"][uin]


def sub_contact_callback_handler(bot, update, user_data):
    query = json.loads(update.callback_query.data)
    contact = subscribe_contact(user_data, query[1])
    update.callback_query.message.edit_reply_markup(
        reply_markup=get_contact_keyboard(contact["uin"], user_data["subscribed_contact"])
    )
    update.callback_query.answer()
    return LOGGED_IN


def unsub_contact_callback_handler(bot, update, user_data):
    uin = json.loads(update.callback_query.data)[1]
    unsubscribe_contact(user_data, uin)
    update.callback_query.message.edit_reply_markup(
        reply_markup=get_contact_keyboard(uin, user_data["subscribed_contact"])
    )
    update.callback_query.answer()
    return LOGGED_IN


def subscribe_group(user_data, gid: int):
    try:
        group = user_data["env"]["group_manager"].get_group_info(gid)
    except UnknownUserException:
        return None
    user_data["subscribed_group"][gid] = SmartqqClient.get_group_name(group)
    return group


def unsubscribe_group(user_data, gid: int):
    if gid in user_data["subscribed_group"]:
        del user_data["subscribed_group"][gid]


def sub_group_callback_handler(bot, update, user_data):
    query = json.loads(update.callback_query.data)
    group = subscribe_group(user_data, query[1])
    update.callback_query.message.edit_reply_markup(
        reply_markup=get_group_keyboard(group["gid"], user_data["subscribed_group"])
    )
    update.callback_query.answer()
    return LOGGED_IN


def unsub_group_callback_handler(bot, update, user_data):
    gid = json.loads(update.callback_query.data)[1]
    unsubscribe_group(user_data, gid)
    update.callback_query.message.edit_reply_markup(
        reply_markup=get_contact_keyboard(gid, user_data["subscribed_group"])
    )
    update.callback_query.answer()
    return LOGGED_IN


def resub_handler(bot, update, user_data):
    history_contact_name = user_data["history_contact_name"]
    client_contact_manager = user_data["env"]["contact_manager"]
    success_contact_number = 0
    success_contact_name = ""
    for contact in client_contact_manager.get_contacts_info():
        name = SmartqqClient.get_user_name(contact)
        if name in history_contact_name:
            subscribe_contact(user_data, contact["uin"])
            success_contact_number += 1
            success_contact_name += name + "\n"
    history_group_name = user_data["history_group_name"]
    client_group_manager = user_data["env"]["group_manager"]
    success_group_number = 0
    success_group_name = ""
    for group in client_group_manager.get_groups_info():
        name = SmartqqClient.get_group_name(group)
        if name in history_group_name:
            subscribe_group(user_data, group["gid"])
            success_group_number += 1
            success_group_name += name + "\n"
    update.message.reply_text(
        "Successully auto re-subbed %d contacts: \n\n%s\nand %d groups: \n\n%s" % (
            success_contact_number,
            success_contact_name,
            success_group_number,
            success_group_name
        )
    )
    return LOGGED_IN


def get_reply_cancel_button() -> InlineKeyboardMarkup:
    return get_callback_markup([["Cancel"]], [[["cancel_reply", 0]]])


def clear_hints(user_data):
    if "hint_message" in user_data:
        user_data["hint_message"].delete()
    if "replied_hint_message" in user_data:
        user_data["replied_hint_message"].delete()
        del user_data["replied_hint_message"]


def reply_contact_handler(bot, update, user_data):
    query = json.loads(update.callback_query.data)
    clear_hints(user_data)
    user_data["reply_callback"] = lambda x: user_data["client"].send_message(query[1], x)
    user_data["callback_query"] = update.callback_query
    user_data["hint_message"] = update.callback_query.message.reply_text(
        "Sending message to [%s]:" % user_data["subscribed_contact"][query[1]],
        reply_markup=get_reply_cancel_button()
    )
    return REPLYING


def reply_group_handler(bot, update, user_data):
    query = json.loads(update.callback_query.data)
    clear_hints(user_data)
    user_data["reply_callback"] = lambda x: user_data["client"].send_group_message(query[1], x)
    user_data["callback_query"] = update.callback_query
    user_data["hint_message"] = update.callback_query.message.reply_text(
        "Sending message to group [%s]:" % user_data["subscribed_group"][query[1]],
        reply_markup=get_reply_cancel_button()
    )
    return REPLYING


def replying_handler(bot, update, user_data):
    if "reply_callback" not in user_data:
        return LOGGED_IN
    response = user_data["reply_callback"](update.message.text)
    # logger.info("replying " + update.message.text + " with response: " + repr(response))
    user_data["replied_hint_message"] = update.message.reply_text("The message above has been sent, with response:" +
                                                                  repr(response))
    try:
        user_data["callback_query"].answer(text="Message successfully sent")
    finally:
        user_data["hint_message"].delete()
        del user_data["reply_callback"]
        del user_data["callback_query"]
        del user_data["hint_message"]
        return LOGGED_IN


def cancel_reply_handler(bot, update, user_data):
    if "reply_callback" not in user_data:
        update.callback_query.answer("No pending replies")
        update.callback_query.message.delete()
        return LOGGED_IN
    try:
        user_data["callback_query"].answer(text="Message cancelled")
    finally:
        user_data["hint_message"].delete()
        del user_data["reply_callback"]
        del user_data["callback_query"]
        del user_data["hint_message"]
        return LOGGED_IN


def main():
    updater = Updater("TOKEN")
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error)
    reply_contact_callback_handler = CallbackQueryHandler(
        reply_contact_handler, pass_user_data=True, pattern="^\[\"reply_contact\", .+\]$")
    reply_group_callback_handler = CallbackQueryHandler(
        reply_group_handler, pass_user_data=True, pattern="^\[\"reply_group\", .+\]$")
    reply_cancel_callback_handler = CallbackQueryHandler(
        cancel_reply_handler, pass_user_data=True, pattern="^\[\"cancel_reply\", .+\]$")
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_handler, pass_user_data=True)
        ],
        states={
            BOT_LOGIN: [MessageHandler(Filters.text, bot_login_handler)],
            IDLE: [
                CommandHandler("login", login_handler, pass_user_data=True, pass_args=True),
                CommandHandler("clear_login", clear_login_handler, pass_user_data=True, pass_args=True)
            ],
            LOGGED_IN: [
                CommandHandler("logout", logout_handler, pass_user_data=True),
                CommandHandler("list_contacts", list_contact_handler, pass_user_data=True, pass_args=True),
                CommandHandler("list_groups", list_group_handler, pass_user_data=True),
                CommandHandler("list_subscribed", list_subscribed_handler, pass_user_data=True),
                CommandHandler("resub", resub_handler, pass_user_data=True),
                CommandHandler("clear_listed", clear_list_handler, pass_user_data=True),
                CallbackQueryHandler(sub_contact_callback_handler, pass_user_data=True,
                                     pattern="^\[\"sub_contact\", .+\]$"),
                CallbackQueryHandler(unsub_contact_callback_handler, pass_user_data=True,
                                     pattern="^\[\"unsub_contact\", .+\]$"),
                CallbackQueryHandler(sub_group_callback_handler, pass_user_data=True,
                                     pattern="^\[\"sub_group\", .+\]$"),
                CallbackQueryHandler(unsub_group_callback_handler, pass_user_data=True,
                                     pattern="^\[\"unsub_group\", .+\]$"),
                CallbackQueryHandler(list_category_handler, pass_user_data=True,
                                     pattern="^\[\"list_category\", .+\]$"),
                reply_contact_callback_handler,
                reply_group_callback_handler,
                reply_cancel_callback_handler
            ],
            REPLYING: [
                reply_contact_callback_handler,
                reply_group_callback_handler,
                reply_cancel_callback_handler,
                MessageHandler(Filters.all, replying_handler, pass_user_data=True)
            ]
        },
        fallbacks=[
            CommandHandler("stop", stop_handler, pass_user_data=True)
        ]
    )

    dispatcher.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
