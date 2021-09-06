# coding=utf8
import requests
import random
import telebot
from telebot import types
from telebot.types import InlineKeyboardButton
import re
import pymongo
import cherrypy
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import cherrypy_cors
from cherrypy.lib.httputil import parse_query_string
import sys
import schedule
import time
import _thread

LEVELS = [50, 105, 165, 231, 304, 384, 472, 569, 676, 793, 922, 1064, 1220, 1392, 1581, 1789, 2018, 2270, 2547, 2852,
          3188, 3558, 3965, 4412, 4904, 5445, 6040, 6695, 7416, 8209, 9081, 10040, 11095, 12256, 13533, 14938, 16483,
          18183, 20053, 22110, 24372, 26861, 29599, 32611, 35924, 39568, 43576, 47985, 52835, 58170, 64039, 70495,
          77597, 85409, 94002, 103454, 113852, 125290, 137871, 151711, 166935, 183681, 202102, 222365, 244654, 269172,
          296142, 325809, 358443, 394340, 433827, 477263, 525042, 577599, 635412, 699006, 768960, 845909, 930553,
          1023662, 1126082, 1238744, 1362672, 1498993, 1648946, 1813894, 1995337, 2194924, 2414470, 2655971, 2921622,
          3213838, 3535275, 3888856, 4277795, 4705628, 5176245, 5693923, 6263369, 6889760]

prices = {
    "40": 5000,
    "100": 11000,
    "200": 19000,
    "500": 38000,
    "1000": 69000
}
sub_prices = {
    "31": 14000,
    "100": 33000
}

API_KEY = "YOUR API KEY"
bot = telebot.TeleBot(API_KEY)
client = pymongo.MongoClient(host="localhost", port=27017)
db = client["pass_finder"]
users_coll = db["users"]
games_coll = db["games"]
pays_coll = db["pays"]
moves_coll = db["moves"]

GUIDE = "☑️ راهنمای بازی رمزجو(بازی فکر و بکر)\n\n✌️ برگرفته از بازی معروف فکر و بکر\n\nهدف بازی :  پیدا کردن رمز\n\nروش بازی:\nیک رمز چند کاراکتری  توسط ربات تعیین می شود و شما میبایست با استفاده از آیکونهای داده شده رمز را کشف کنید.\nبعد از زدن هر رمزی نتیجه به صورت چراغ به شما نشان داده میشود که معنی چراغ ها به صورت زیر است 👇\n🔴 این چراغ یعنی یک رقم از رمزتان کاملا غلط است و اگر مثلا 2 چراغ قرمز گرفتید یعنی دو رقم از رمز صحیح نیست\n🟡 این چراغ یعنی یک رقم از رمزتان صحیح است ولی جای آن غلط مثلا اگر رمز 134 باشد و شما بزنید 314 دوچراغ زرد میگیرید چون 3 و 1 درست است ولی جای آنها غلط\n🟢 این چراغ نشانه دقیق بودن رمز است یعنی هم رقم رمز درست و هم جای آن صحیح هست مثلا اگر رمز 134 باشد و شما بزنید 314، دو چراغ زرد بابت 3 و 1 میگیرید و یک چراغ سبز بخاطر عدد 4 \n⚠️ نمایش چراغ ها به صورت رنگ سبز اول و بعد رنگ زرد و در آخر رنگ قرمز می باشد و ترتیب آن نقشی در ترتیب رمز ندارد⚠️\n\nانواع بازی: این بازی را هم به صورت تک نفره داخل ربات و هم به صورت چند نفره(دوستان) در گروهها، کانال یا پیوی میتوانید انجام دهید.\nبازی دوستانه در پنج حالت آبکی، ساده، متوسط، سخت و حرفه ای در دسترس است.\nحالت ابکی 👈 پیدا کردن رمزی دو رقمی از بین سه کاراکتر عددی در 5 دقیقه\nحالت ساده 👈 پیدا کردن رمزی سه رقمی از بین چهار کاراکتر عددی در 5 دقیقه\nحالت متوسط 👈 پیدا کردن رمزی چهار رقمی از بین پنج کاراکتر ترکیبی در 10 دقیقه\nحالت سخت 👈 پیدا کردن رمزی پنج رقمی از بین شش کاراکتر ترکیبی در 15 دقیقه\nحالت حرفه ای 👈 پیدا کردن رمزی شش رقمی از بین هفت کاراکتر ترکیبی در 20 دقیقه\n\nجهت انجام بازی دوستانه کافیست از طریق منو و دکمه بازی با دوستان اقدام نمایید یا از طریق تایپ آدرس ربات در مکانی که قصد بازی دارید\n\nامتیاز : محاسبه بر اساس اخرین وضعیت چراغ ها \nهر چراغ سبز 3 امتیاز و هر چراغ زرد یک امتیاز و بسته به اینکه در کدام حالت بازی برنده شده اید مقداری امتیاز اضافه تعلق میگیرد\nلازم به ذکر است که امتیاز بازیهای انفرادی داخل ربات، تاثیری در رتبه و ارتقا سطح ندارد.\n\nراهنما : \nراهنمای رمز🔐 که به شما یکی از رقم های رمز را نشان میده.\nلازم به ذکر است که در بازی های آبکی و ساده فقط یکبار و در سایر بازی ها دو بار قابلیت استفاده دارید و با داشتن سکه امکان پذیر است.\n\n🤖 @RamzJoBot\n📣 @TRexGames"
ICONS = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '♠️', '♣️', '♥️', '♦️', '🔔', '✂️', '🎈',
         '🎁', '🛎', '🎉', '💣', '🔫', '🧲', '🔮', '🧿', '💎', '📚', '⏳', '📺', '📞', '📡', '☎️', '🕋', '🚁', '🚀',
         '✈️', '🚗', '🛵', '🚑', '🚜', '🎳', '🎯', '♟', '🎲', '🎬', '🎭', '🎧', '⚽️', '🏀', '🏈', '🥎', '🎱', '🏉', '⛸',
         '🍯', '🎂', '🍩', '🍔', '🍎', '🍒', '🥦', '🍗', '🍋', '🍓', '🥥', '🍇', '☃️', '🌼', '🍄', '🐿', '🌳', '🦜',
         '🐏', '🐠', '🦀', '🐝', '🦄', '🐥', '🐛', '🐜', '🐞', '🐌', '🐼', '🐶', '🐒', '🦉', '🦋', '🦖', '🎩', '🧶',
         '👁', '👻', '💀', '😎', '🤕', '😱', '😇', '😃', '🥺', '😭', '😍', '🥳', '💪', '🇮🇷']

WEBHOOK_HOST = 'localhost'
WEBHOOK_PORT = 20000  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_URL_PATH = "/%s/" % (API_KEY)
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)


# bot.remove_webhook()
# bot.set_webhook(url="https://sudoku.appteams.ir/api/v1.1/telegram-web-hook")


def check_user_membership(message):
    if bot.get_chat_member(-1001319848880, message.from_user.id).status == 'left':
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("عضویت در کانال", url="https://t.me/TRexGames"))
        bot.send_message(message.chat.id,
                         "کاربر " + message.from_user.first_name + "\n.برای ساخت بازی ابتدا عضو کانال زیر شوید 👇\n@TRexGames",
                         reply_markup=markup)
        return False
    return True


def create_keyboards(keyboards, game_id):
    lock_keyboards = []
    game = games_coll.find_one({"_id": ObjectId(game_id)})
    if not game["is_finished"]:
        text = ''
        for i in range(len(game["password_arr"])):
            text += '⚪️'
        lock_keyboards.append(
            InlineKeyboardButton('رمز ' + str(len(game["password_arr"])) + ' تایی ' + text + ' با آیکون‌های زیر',
                                 callback_data='🔐/' + game_id))
    else:
        for password in game["password_arr"]:
            lock_keyboards.append(InlineKeyboardButton(password, url="t.me/RamzJoBot"))
    inline_keyboards = []
    secondary_keyboards = []
    if game["hardness"] != 'special':
        for keyboard in keyboards:
            if not game["is_finished"]:
                inline_keyboards.append(InlineKeyboardButton(keyboard, callback_data="i/" + keyboard + "/" + game_id))
            else:
                inline_keyboards.append(InlineKeyboardButton(keyboard, url="t.me/RamzJoBot"))
    else:
        for i, keyboard in enumerate(keyboards):
            if not game["is_finished"]:
                if i < 4:
                    inline_keyboards.append(
                        InlineKeyboardButton(keyboard, callback_data="i/" + keyboard + "/" + game_id))
                else:
                    secondary_keyboards.append(
                        InlineKeyboardButton(keyboard, callback_data="i/" + keyboard + "/" + game_id))
            else:
                if i < 4:
                    inline_keyboards.append(InlineKeyboardButton(keyboard, url="t.me/RamzJoBot"))
                else:
                    secondary_keyboards.append(InlineKeyboardButton(keyboard, url="t.me/RamzJoBot"))

    play_with_others = InlineKeyboardButton(' 🤝 بازی با دوستانم(گروه، کانال و ...) 🤝', switch_inline_query="")
    if not game["is_finished"]:
        remove = [InlineKeyboardButton('❌', callback_data='❌/' + game_id),
                  InlineKeyboardButton('🔐 راهنمای رمز', callback_data='guide/' + game_id)]
        if game["hardness"] != 'special':
            return types.InlineKeyboardMarkup([lock_keyboards, inline_keyboards, remove, [play_with_others]])
        else:
            return types.InlineKeyboardMarkup(
                [lock_keyboards, inline_keyboards, secondary_keyboards, remove, [play_with_others]])
    else:
        trex_games = InlineKeyboardButton('🎮🟡 بازی‌های تیرکس 🟡🎮', url='https://t.me/TRexGames/599')
        if game["mode"] == 'multi':
            finish_buttons = [InlineKeyboardButton('🛒 فروشگاه', callback_data='shop'),
                              InlineKeyboardButton('🔁 دوباره', switch_inline_query_current_chat="")]
            return types.InlineKeyboardMarkup(
                [lock_keyboards, finish_buttons, [play_with_others], [trex_games]])
        else:
            return types.InlineKeyboardMarkup(
                [lock_keyboards, [play_with_others], [trex_games]])


def create_game(hardness, mode, message):
    password = ''
    keyboards = []
    password_arr = []
    icons = []
    pre_icons = ICONS
    if hardness == 'too easy':
        pre_icons = ICONS[0:10]
        limit = 2
    elif hardness == 'easy':
        pre_icons = ICONS[0:10]
        limit = 3
    elif hardness == 'medium':
        limit = 4
    elif hardness == 'hard':
        limit = 5
    elif hardness == 'pro':
        limit = 6
    elif hardness == 'special':
        limit = 7
    # print("pre icons", pre_icons)
    while len(icons) != limit + 1:
        icon = pre_icons[random.randint(0, len(pre_icons) - 1)]
        if icon not in icons:
            icons.append(icon)
    # print("icons", icons)
    for i in range(0, limit):
        icon = icons[random.randint(0, len(icons) - 1)]
        password += icon
        password_arr.append(icon)
    keyboards = icons
    print(password)
    print(keyboards)
    random.shuffle(keyboards)
    if mode == "single":
        chat_id = message.from_user.id
        inline_id = message.message.message_id
        is_started = True
    else:
        chat_id = ''
        inline_id = message.inline_message_id
        is_started = False
    game_id = games_coll.insert_one(
        {"hardness": hardness, "mode": mode, "date": datetime.today().replace(microsecond=0),
         "users": [{"user_id": str(message.from_user.id), "guide": 0}], "password": password, "keyboards": keyboards,
         "last_time_edited": datetime.today().replace(microsecond=0), "is_edited": False, "is_finished": False,
         "inline_message_id": inline_id, "chat_id": chat_id, "password_arr": password_arr,
         "is_started": is_started, "winner_id": -1}).inserted_id
    moves_coll.insert_one({"game_id": game_id, "user_id": str(message.from_user.id), "moves": []})
    return create_keyboards(keyboards, str(game_id))


def get_total_rank(users, id):
    previous_rank = 0
    previous_point = 0
    for i, user in enumerate(users):
        if i == 0:
            previous_rank = 1
            previous_point = user["total_point"]
        elif previous_point != user["total_point"]:
            previous_point = user["total_point"]
            previous_rank += 1
        if str(user["tel_id"]) == str(id):
            return previous_rank
    return ''


def update_profiles(users, game_id):
    for i in users:
        total_points = users_coll.find_one({"tel_id": i["user_id"]})["total_point"]
        moves = moves_coll.find_one({"user_id": i["user_id"], "game_id": ObjectId(game_id)})["moves"]
        game = games_coll.find_one({"_id": ObjectId(game_id)})
        # print("game", game)
        if len(moves) == 0 or (len(moves) > 0 and len(moves[-1]["input_arr"]) < len(game["password_arr"])):
            point = 0
        elif len(moves) > 0 and len(moves[-1]["input_arr"]) == len(game["password_arr"]):
            point = moves[-1]["point"]
        elif len(moves) > 0 and len(moves[-2]["input_arr"]) == len(game["password_arr"]):
            point = moves[-2]["point"]
        if str(i["user_id"]) == str(game["winner_id"]):
            if game["hardness"] == 'easy' or game["hardness"] == 'too easy':
                point += 5
            elif game["hardness"] == 'medium':
                point += 10
            elif game["hardness"] == 'hard':
                point += 15
            elif game["hardness"] == 'pro':
                point += 20
        games_coll.update_one({"_id": ObjectId(game_id), "users.user_id": i["user_id"]}, {"$set": {
            "users.$.point": point
        }})
        # print(i["user_id"], "total_points", total_points)
        # print(i["user_id"], "point", point)
        total_points += point
        # print(i["user_id"], "total_points", total_points)
        users_coll.update_one({"tel_id": i["user_id"]}, {"$set": {"total_point": total_points}})
        for j, level in enumerate(LEVELS):
            if total_points < level:
                if users_coll.find_one({"tel_id": i["user_id"]})["level"] < j:
                    try:
                        bot.send_message(chat_id=int(i["user_id"]),
                                         text="💪ایول " + users_coll.find_one({"tel_id": i["user_id"]})[
                                             "first_name"] + "\nتبریک!🎊  سطح شما به " + str(
                                             j) + " ارتقا یافت و 10 سکه هدیه گرفتی\n🕺🕺💃💃")
                    except Exception as e:
                        print("line", 212, e)
                    users_coll.update_one({"tel_id": i["user_id"]},
                                          {"$set": {"total_point": total_points, "level": j},
                                           "$inc": {"coins": 10}})
                break
    for i in users:
        users_coll.update_one({"tel_id": i["user_id"]}, {
            "$set": {"total_rank": get_total_rank(users_coll.find().sort("total_point", -1), i["user_id"])}})


def check_subs():
    golden_users = users_coll.find({"golden_sub": True})
    for user in golden_users:
        days = user["golden_days"]
        start_date = user["golden_start_date"]
        if (datetime.today().replace(microsecond=0) - start_date).days > days:
            users_coll.update_one({"tel_id": user["tel_id"]}, {"$set": {"golden_sub": False},
                                                               "$unset": {"golden_start_date": "", "golden_days": ""}
                                                               })


def update_texts():
    games = games_coll.find({"is_finished": False, "mode": "multi", "is_started": True})
    for game in games:
        game = games_coll.find_one({"_id": game["_id"]})
        if game["is_finished"]:
            continue
        if game["hardness"] == "easy" or game["hardness"] == "too easy":
            limit = 5
        elif game["hardness"] == "medium":
            limit = 10
        elif game["hardness"] == "hard":
            limit = 15
        elif game["hardness"] == "pro" or game["hardness"] == 'special':
            limit = 20
        if (datetime.today().replace(microsecond=0) - game["date"]).total_seconds() / 60 > limit:
            games_coll.update_one({"_id": game["_id"]}, {"$set": {"is_finished": True}})
            if game["mode"] == "multi":
                update_profiles(game["users"], game["_id"])
                try:
                    bot.edit_message_text(update_game_text(game["users"], str(game["_id"])),
                                          inline_message_id=game["inline_message_id"],
                                          reply_markup=create_keyboards(game["keyboards"], str(game["_id"])))
                except Exception as e:
                    print("line", 242, e)
            else:
                try:
                    bot.edit_message_text(update_game_text(game["users"], str(game["_id"])), chat_id=game["chat_id"],
                                          message_id=game["inline_message_id"],
                                          reply_markup=create_keyboards(game["keyboards"], str(game["_id"])))
                except Exception as e:
                    print("line", 249, e)
    games = games_coll.find({"is_edited": True, "is_finished": False})
    for game in games:
        # print("game update text", game)
        game = games_coll.find_one({"_id": game["_id"]})
        if game["is_finished"]:
            continue
        if game["mode"] == "multi":
            try:
                bot.edit_message_text(update_game_text(game["users"], str(game["_id"])),
                                      inline_message_id=game["inline_message_id"],
                                      reply_markup=create_keyboards(game["keyboards"], str(game["_id"])))
            except Exception as e:
                print("line", 258, e)
        else:
            try:
                bot.edit_message_text(update_game_text(game["users"], str(game["_id"])), chat_id=game["chat_id"],
                                      message_id=game["inline_message_id"],
                                      reply_markup=create_keyboards(game["keyboards"], str(game["_id"])))
            except Exception as e:
                print("line", 265, e)
        games_coll.update_one({"_id": game["_id"]}, {"$set": {"is_edited": False}})


if sys.argv[1] == "20101":
    schedule.every(5).seconds.do(update_texts)
    schedule.every().hour.do(check_subs)


def return_character(number):
    if number == 0:
        return "0️⃣"
    elif number == 1:
        return "1️⃣"
    elif number == 2:
        return "2️⃣"
    elif number == 3:
        return "3️⃣"
    elif number == 4:
        return "4️⃣"
    elif number == 5:
        return "5️⃣"
    elif number == 6:
        return "6️⃣"
    elif number == 7:
        return "7️⃣"
    elif number == 8:
        return "8️⃣"
    elif number == 9:
        return "9️⃣"


def get_element(id, arr, index_str):
    return next((item for item in arr if item[index_str] == id), None)


def update_game_text(users, game_id):
    game = games_coll.find_one({"_id": ObjectId(game_id)})
    text = ''
    points = {}
    real_points = {}
    for i in users:
        moves = moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": i["user_id"]})["moves"]
        if len(moves) == 0 or (len(moves) == 1 and len(moves[-1]["input_arr"]) < len(game["password_arr"])):
            points[i["user_id"]] = 0
            real_points[i["user_id"]] = 0
        else:
            points[i["user_id"]] = 0
            real_points[i["user_id"]] = 0
            if len(moves[- 1]["input_arr"]) == len(game["password_arr"]):
                points[i["user_id"]] += (moves[- 1]["state"].count('🟡'))
                points[i["user_id"]] += (
                        moves[- 1]["state"].count('🟢') * 3)

            else:
                points[i["user_id"]] += (moves[- 2]["state"].count('🟡'))
                points[i["user_id"]] += (
                        moves[- 2]["state"].count('🟢') * 3)

    points = dict(sorted(points.items(), key=lambda x: x[1], reverse=True))
    # print("points1", points)
    # for i, id in enumerate(points):
    #     if i == 0:
    #         point = points[id]
    #         pre_id = id
    #     elif point == points[id]:
    #         try:
    #             moves = moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": pre_id})["moves"]
    #             pre_greens = moves[-1]["state"].count('🟢')
    #             # print("pre id", pre_id)
    #             moves = moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": id})["moves"]
    #             cur_greens = moves[-1]["state"].count('🟢')
    #             # print("id", id)
    #             if pre_greens > cur_greens:
    #                 new_points = {}
    #                 # print("points2", points)
    #                 for i, id2 in enumerate(points):
    #                     if id2 == pre_id:
    #                         new_points[id2] = points[id]
    #                     elif id2 == id:
    #                         new_points[id2] = points[pre_id]
    #                     else:
    #                         new_points[id2] = points[id2]
    #                 points = new_points
    #                 # print("points3", points)
    #         except Exception as e:
    #             print("line", 349, e)
    #     else:
    #         pre_id = id
    #         point = points[id]
    previous_point = next(iter(points.values()))
    previous_rank = 1
    for i, id in enumerate(points):
        line = u'\u200e'
        user = users_coll.find_one({"tel_id": str(id)})
        if i == 0:
            line = return_character(1)
        elif i != 0 and points[id] == previous_point:
            for x in str(previous_rank):
                line += return_character(int(x))
        else:
            previous_point = points[id]
            previous_rank += 1
            for x in str(previous_rank):
                line += return_character(int(x))
        moves = moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": str(id)})["moves"]
        if len(moves) == 0 or (len(moves) == 1 and len(
                moves[- 1]["input_arr"]) < len(game["password_arr"])):
            status = ''
            for i in range(len(game["password_arr"])):
                status += '🔴'
        elif len(moves[- 1]["input_arr"]) == len(game["password_arr"]):
            status = moves[- 1]["state"]
        else:
            status = moves[- 2]["state"]
        if game["mode"] == 'single':
            line = ''
        line += u'\u200e' + user["first_name"] + ' 〽️' + str(
            user["level"]) + ' 🎖 ' + str(user["total_rank"]) + '\n'
        if game["is_finished"] and game["mode"] == 'multi':
            if game["mode"] == 'multi':
                if game["hardness"] == 'easy' or game["hardness"] == 'too easy':
                    extra_point = 5
                elif game["hardness"] == 'medium':
                    extra_point = 10
                elif game["hardness"] == 'hard':
                    extra_point = 15
                elif game["hardness"] == 'pro' or game["hardness"] == 'special':
                    extra_point = 20
            if len(moves) > 0:
                if points[id] == len(game["password_arr"]) * 3 and game["mode"] == "multi":
                    point = points[id] + extra_point
                else:
                    point = points[id]
                line += "🔰" + str(point) + ' ' + status + "\n\n"
            else:
                line += "🔰" + str(points[id]) + ' ' + status + "\n\n"
        else:
            line += status + "\n\n"
        text = line + text
        if i >= 25:
            text = "و " + str(len(points) - 25) + " نفر دیگر ...\n" + text
            break
    if game["mode"] == 'multi':
        text = '🔰امتیازات\n' + text

    if game["is_finished"]:
        text = '🇮🇷پایان بازی🇮🇷\n\n' + text
    game_time = ''
    if game["hardness"] == 'easy':
        if game["mode"] == 'multi':
            game_time = '⏳ زمان 5 دقیقه\n\n'
        text = game_time + '💎سطح آسان (رمز 3 تایی)\n' + text
    elif game["hardness"] == 'medium':
        if game["mode"] == 'multi':
            game_time = '⏳ زمان 10 دقیقه\n\n'
        text = game_time + '💎سطح متوسط (رمز 4 تایی)\n' + text
    elif game["hardness"] == 'hard':
        if game["mode"] == 'multi':
            game_time = '⏳ زمان 15 دقیقه\n\n'
        text = game_time + '💎سطح سخت (رمز 5 تایی)\n' + text
    elif game["hardness"] == 'pro':
        if game["mode"] == 'multi':
            game_time = '⏳ زمان 20 دقیقه\n\n'
        text = game_time + '💎سطح حرفه‌ای (رمز 6 تایی)\n' + text
    elif game["hardness"] == 'too easy':
        if game["mode"] == 'multi':
            game_time = '⏳ زمان 5 دقیقه\n\n'
        text = game_time + '💎سطح آبکی (رمز 2 تایی)\n' + text
    elif game["hardness"] == 'special':
        if game["mode"] == 'multi':
            game_time = '⏳ زمان 20 دقیقه\n\n'
        text = game_time + '💎سطح ویژه (رمز 7 تایی)\n' + text

    if not game["is_finished"]:
        text = '📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست.\nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n' + text

    text = '🔐رمزجو(بازی فکر و بکر)🔐\n\n' + text

    if game["is_finished"] and game["mode"] == 'multi' and game["winner_id"] != -1:
        text += '🔓  بازی توسط *' + users_coll.find_one({"tel_id": game["winner_id"]})[
            "first_name"] + '* با *' + str(len(
            moves_coll.find_one({"game_id": game["_id"], "user_id": game["winner_id"]})[
                "moves"]))  + '* حرکت رمزگشایی  شد 💪🕺💃\n\n'

    text += '🤖@RamzJoBot'

    return text


def add_user(message):
    if users_coll.find_one({"tel_id": str(message.from_user.id)}) is not None:
        return
    if len(message.from_user.first_name) > 20:
        message.from_user.first_name = message.from_user.first_name[0:20]
    users_coll.insert_one(
        {"tel_id": str(message.from_user.id), "first_name": message.from_user.first_name, "total_point": 0, "coins": 20,
         "level": 0, "total_rank": '', "golden_sub": False})


def get_total_ranking(users):
    text = 'رنکینگ امتیاز کل\n\n'
    counter = 1
    for i, user in enumerate(users):
        if user["total_rank"] == '':
            counter -= 1
            continue
        text += u'\u200e' + str(counter) + ". " + u'\u200e' + user["first_name"] + '  ' + u'\u200e' + str(
            user["total_point"]) + '\n'
        counter += 1
        if counter == 50:
            break
    text += '\n🤖 @RamzJoBot\n📣 @TRexGames'
    return text


def get_seven_ranking(games):
    points = {}
    for game in games:
        for user in game["users"]:
            try:
                if user["user_id"] not in points:
                    points[user["user_id"]] = user["point"]
                else:
                    points[user["user_id"]] += user["point"]
            except Exception as e:
                print("line", 477, e)
    points = dict(sorted(points.items(), key=lambda x: x[1], reverse=True))
    text = 'رنکینگ هفت روز اخیر\n\n'
    counter = 0
    for i, user in enumerate(points):
        if users_coll.find_one({"tel_id": str(user)}):
            counter += 1
            text += u'\u200e' + str(i + 1) + ". " + u'\u200e' + \
                    users_coll.find_one({"tel_id": str(user)}, {"first_name": 1})[
                        "first_name"] + '   ' + u'\u200e' + str(points[user]) + "\n"
        if counter == 50:
            break
    text += '\n🤖 @RamzJoBot\n📣 @TRexGames'
    return text


def add_user_to_game(game_id, call):
    games_coll.update_one({"_id": ObjectId(game_id)},
                          {"$push": {"users": {"user_id": str(call.from_user.id), "guide": 0}}})
    moves_coll.insert_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id), "moves": []})
    game = games_coll.find_one({"_id": ObjectId(game_id)})
    if len(game["users"]) == 2:
        games_coll.update_one({"_id": ObjectId(game_id)}, {"$set": {
            "date": datetime.today().replace(microsecond=0),
            "is_started": True
        }})
        bot.edit_message_text(update_game_text(game["users"], game_id), inline_message_id=call.inline_message_id,
                              reply_markup=create_keyboards(game["keyboards"], game_id))


def schedule_function():
    while True:
        schedule.run_pending()
        time.sleep(1)


def get_past_seven_points(games, user_id):
    point = 0
    for game in games:
        try:
            point += get_element(user_id, game["users"], "user_id")["point"]
        except Exception as e:
            print("line", 519, e)
    return str(point)


def get_past_seven_rank(games, user_id):
    points = {}
    for game in games:
        for user in game["users"]:
            try:
                if user["user_id"] not in points:
                    points[user["user_id"]] = user["point"]
                else:
                    points[user["user_id"]] += user["point"]
            except Exception as e:
                print("line", 533, e)
    points = dict(sorted(points.items(), key=lambda x: x[1], reverse=True))
    if user_id not in list(points.keys()):
        return ''
    return str(list(points.keys()).index(user_id) + 1)


def display_shop_message(message):
    text = '🛒 فروشگاه\n\n📚هر راهنمای جارو  یا جهش  5 سکه نیاز دارد\n\n👇برای خرید سکه یکی از موارد زیر را ' \
           'انتخاب نمایید👇 '
    markup = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton('💰 40 سکه💰 👈 5000 تومان', callback_data='c40'),
        types.InlineKeyboardButton('💰 100 سکه💰 👈 11000 تومان', callback_data='c100'),
        types.InlineKeyboardButton('💰 200 سکه💰 👈 19000 تومان', callback_data='c200'),
        types.InlineKeyboardButton('💰 500 سکه💰 👈 38000 تومان', callback_data='c500'),
        types.InlineKeyboardButton('💰 1000 سکه💰 👈 69000 تومان', callback_data='c1000'),
        types.InlineKeyboardButton('31 روز اشتراک طلایی 👈 14000 تومان', callback_data='s/31'),
        types.InlineKeyboardButton('100 روز اشتراک طلایی 👈 33000 تومان', callback_data='s/100'),

    )
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)


@bot.message_handler(commands=['update'])
def update(message):
    if message.from_user.id != 396539934:
        return
    users_coll.update_many({}, {"$set": {"golden_sub": False}})
    bot.send_message(message.from_user.id, 'done!')


@bot.message_handler(commands=['start'])
def start(message):
    print("start", message)
    if '/start shop' == message.text:
        # bot.send_message(chat_id=message.chat.id, text='به زودی راه اندازی می شود')
        # return
        display_shop_message(message)
        return
    add_user(message)
    markup = types.ReplyKeyboardMarkup(row_width=2)
    single_player_btn = types.KeyboardButton("🏆 بازی تک نفره")
    multi_player_btn = types.KeyboardButton("🤝 بازی چند نفره")
    profile_btn = types.KeyboardButton("👤 پروفایل")
    champions_btn = types.KeyboardButton("🏅 قهرمانان")
    shop_btn = types.KeyboardButton("🛒 فروشگاه")
    guide_btn = types.KeyboardButton("📚 راهنما")
    markup.add(single_player_btn, multi_player_btn, profile_btn, champions_btn, shop_btn, guide_btn)
    bot.send_message(message.chat.id, "به بازی رمزجو(بازی فکر و بکر) خوش آمدید!", reply_markup=markup)


@bot.message_handler()
def menu(message):
    print("message", message)
    if message.text == "🏆 بازی تک نفره":
        if not check_user_membership(message):
            return
        golden_sub = users_coll.find_one({"tel_id": str(message.from_user.id)})["golden_sub"]
        if golden_sub:
            lock = ''
        else:
            lock = '🔐 '
        markup = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton('سطح آبکی', callback_data='single/too easy'),
            types.InlineKeyboardButton('سطح ساده', callback_data='single/easy'),
            types.InlineKeyboardButton(lock + 'سطح متوسط', callback_data='single/medium'),
            types.InlineKeyboardButton(lock + 'سطح سخت', callback_data='single/hard'),
            types.InlineKeyboardButton(lock + 'سطح حرفه‌ای', callback_data='single/pro'),
            types.InlineKeyboardButton(lock + 'سطح ویژه', callback_data='single/special')
        )
        bot.send_message(message.chat.id, 'لطفا سطح مورد نظر خود را انتخاب کنید:', reply_markup=markup)
    elif message.text == "🤝 بازی چند نفره":
        if not check_user_membership(message):
            return
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("یک گروه انتخاب کن", switch_inline_query=""))
        bot.send_message(message.chat.id, "برای بازی چند نفره بر روی دکمه‌ی زیر کلیک کنید : ", reply_markup=markup)
    elif message.text == "🛒 فروشگاه":
        display_shop_message(message)
    elif message.text == "📚 راهنما":
        bot.send_message(chat_id=message.chat.id, text=GUIDE)
    elif message.text == "👤 پروفایل":
        user = users_coll.find_one({"tel_id": str(message.from_user.id)})
        text = 'پروفایل\n\n' + '👤نام   👈 ' + user["first_name"] + '\n💎سطح  👈 ' + str(
            user["level"]) + '\n🔰 تعداد بازی  👈 ' + str(games_coll.count_documents(
            {"users.user_id": str(message.from_user.id)})) + '\n〽️ امتیاز تا سطح بعد  👈 ' + str(
            LEVELS[user["level"]] - user["total_point"]) + '\n🎖 رتبه 👈 ' + str(user["level"]) + '\n💰سکه 👈 ' + str(
            user["coins"]) + '\n\nاسپانسر @TRexGames'
        bot.send_message(chat_id=message.chat.id, text=text)
    elif message.text == "🏅 قهرمانان":
        user = users_coll.find_one({"tel_id": str(message.from_user.id)})
        total_rank = user["total_rank"]

        past_seven_days_points = get_past_seven_points(
            games_coll.find({"date": {"$gte": datetime.today().replace(microsecond=0) - timedelta(7)}, "mode": "multi",
                             "users.user_id.": str(message.from_user.id), "is_finished": True}, {"users": 1}),
            str(message.from_user.id))
        past_seven_days_rank = get_past_seven_rank(games_coll.find(
            {"date": {"$gte": datetime.today().replace(microsecond=0) - timedelta(7)}, "mode": "multi",
             "is_finished": True}, {"users": 1}),
            str(message.from_user.id))

        markup = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton('رنکینگ هفت روز اخیر', callback_data="seven ranking"),
            types.InlineKeyboardButton('رنکینگ کل', callback_data="total ranking"))

        bot.send_message(chat_id=message.chat.id,
                         text='قهرمانان\n\n' + '👤نام   👈 ' + message.from_user.first_name + '\n\nامتیاز کل  👈 ' +
                              str(user["total_point"]) + "\n🔰رتبه کل  👈 " + str(
                             total_rank) + "\n\nامتیاز هفت روز اخیر " + past_seven_days_points + "\n🔰 رتبه هفت روز اخیر 👈 " + past_seven_days_rank + "\n\nاسپانسر @TRexGames",
                         reply_markup=markup)


@bot.chosen_inline_handler(func=lambda message: True)
def handler(message):
    print("chosen", message)
    user = users_coll.find_one({"tel_id": str(message.from_user.id)})
    if not check_user_membership(message):
        return
    if message.result_id == 'te':
        preline = '🔐رمزجو(بازی فکر و بکر)🔐\n\n📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست.\nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n💎سطح آبکی (رمز 2 تایی)\n⏳ زمان 5 دقیقه\n\n🔰امتیازات\n'
        line = u'\u200e' + '1️⃣' + user["first_name"] + '  〽️' + str(
            user["level"]) + '  🎖' + str(user["total_rank"]) + '\n' + '🔴🔴' + "\n\n🤖@RamzJoBot"
        bot.edit_message_text(
            text=preline + line,
            inline_message_id=message.inline_message_id,
            reply_markup=create_game('too easy', 'multi', message)
        )
    elif message.result_id == 'e':
        preline = '🔐رمزجو(بازی فکر و بکر)🔐\n\n📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست. \nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n💎سطح آسان (رمز 3 تایی)\n⏳ زمان 5 دقیقه\n\n🔰امتیازات\n'
        line = u'\u200e' + '1️⃣' + user["first_name"] + '  〽️' + str(
            user["level"]) + '  🎖' + str(user["total_rank"]) + '\n' + '🔴🔴🔴' + "\n\n🤖@RamzJoBot"
        bot.edit_message_text(
            text=preline + line,
            inline_message_id=message.inline_message_id,
            reply_markup=create_game('easy', 'multi', message)
        )
    elif message.result_id == 'm':
        preline = '🔐رمزجو(بازی فکر و بکر)🔐\n\n📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست. \nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n💎سطح متوسط (رمز 4 تایی)\n⏳ زمان 10 دقیقه\n\n🔰امتیازات\n'
        line = u'\u200e' + '1️⃣' + user["first_name"] + '  〽️' + str(
            user["level"]) + '  🎖' + str(user["total_rank"]) + '\n' + '🔴🔴🔴🔴' + "\n\n🤖@RamzJoBot"
        bot.edit_message_text(
            text=preline + line,
            inline_message_id=message.inline_message_id,
            reply_markup=create_game('medium', 'multi', message)
        )
    elif message.result_id == 'h':
        preline = '🔐رمزجو(بازی فکر و بکر)🔐\n\n📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست. \nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n💎سطح سخت (رمز 5 تایی)\n⏳ زمان 15 دقیقه\n\n🔰امتیازات\n'
        line = u'\u200e' + '1️⃣' + user["first_name"] + '  〽️' + str(
            user["level"]) + '  🎖' + str(user["total_rank"]) + '\n' + '🔴🔴🔴🔴🔴' + "\n\n🤖@RamzJoBot"
        bot.edit_message_text(
            text=preline + line,
            inline_message_id=message.inline_message_id,
            reply_markup=create_game('hard', 'multi', message)
        )
    elif message.result_id == 'p':
        preline = '🔐رمزجو(بازی فکر و بکر)🔐\n\n📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست. \nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n💎سطح حرفه‌ای (رمز 6 تایی)\n⏳ زمان 20 دقیقه\n\n🔰امتیازات\n'
        line = u'\u200e' + '1️⃣' + user["first_name"] + '  〽️' + str(
            user["level"]) + '  🎖' + str(user["total_rank"]) + '\n' + '🔴🔴🔴🔴🔴🔴' + "\n\n🤖@RamzJoBot"
        bot.edit_message_text(
            text=preline + line,
            inline_message_id=message.inline_message_id,
            reply_markup=create_game('pro', 'multi', message)
        )
    elif message.result_id == 's':
        preline = '🔐رمزجو(بازی فکر و بکر)🔐\n\n📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست. \nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n💎سطح وِیژه (رمز 7 تایی)\n⏳ زمان 20 دقیقه\n\n🔰امتیازات\n'
        line = u'\u200e' + '1️⃣' + user["first_name"] + '  〽️' + str(
            user["level"]) + '  🎖' + str(user["total_rank"]) + '\n' + '🔴🔴🔴🔴🔴🔴🔴' + "\n\n🤖@RamzJoBot"
        bot.edit_message_text(
            text=preline + line,
            inline_message_id=message.inline_message_id,
            reply_markup=create_game('special', 'multi', message)
        )


@bot.inline_handler(func=lambda query: True)
def inline_handler(message):
    print("inline", message)
    add_user(message)
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("⏳", callback_data="1"))
    text = "در حال ساخت..."
    te = types.InlineQueryResultArticle(id='te', title='رمزجو(بازی فکر و بکر) سطح آبکی',
                                        input_message_content=types.InputTextMessageContent(text)
                                        , reply_markup=markup)
    e = types.InlineQueryResultArticle(id='e', title='رمزجو(بازی فکر و بکر) سطح ساده',
                                       input_message_content=types.InputTextMessageContent(text)
                                       , reply_markup=markup)
    m = types.InlineQueryResultArticle(id='m', title='رمزجو(بازی فکر و بکر) سطح متوسط',
                                       input_message_content=types.InputTextMessageContent(text)
                                       , reply_markup=markup)
    h = types.InlineQueryResultArticle(id='h', title='رمزجو(بازی فکر و بکر) سطح سخت',
                                       input_message_content=types.InputTextMessageContent(text)
                                       , reply_markup=markup)
    p = types.InlineQueryResultArticle(id='p', title='رمزجو(بازی فکر و بکر) سطح حرفه‌ای',
                                       input_message_content=types.InputTextMessageContent(text)
                                       , reply_markup=markup)
    s = types.InlineQueryResultArticle(id='s', title='رمزجو(بازی فکر و بکر) سطح ویژه',
                                       input_message_content=types.InputTextMessageContent(text)
                                       , reply_markup=markup)
    bot.answer_inline_query(message.id, [te, e, m, h, p, s])


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    print("call", call)
    add_user(call)
    if '❌' in call.data:
        game_id = call.data.split("/")[1]
        game = games_coll.find_one({"_id": ObjectId(game_id)})
        moves = moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)})
        if moves is None:
            add_user_to_game(game_id, call)
            moves = moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)})["moves"]
        else:
            moves = moves["moves"]
        if len(moves) == 0 or len(moves[- 1]["input_arr"]) == 0 or len(
                moves[- 1]["input_arr"]) == len(game["password_arr"]):
            bot.answer_callback_query(call.id, 'شما هنوز رمزی را وارد نکردید!')
            return
        if len(moves[- 1]["input_arr"]) < len(game["password_arr"]):
            index = str(len(moves) - 1)
            moves_coll.update_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)},
                                  {"$set": {"moves." + index + ".input": '', "moves." + index + ".input_arr": []}})
            bot.answer_callback_query(call.id, 'پاک شد!')
    elif 'single' in call.data:
        hardness = call.data.split("/")[1]
        user = users_coll.find_one({"tel_id": str(call.from_user.id)})
        if hardness != 'too easy' and hardness != 'easy' and not user["golden_sub"]:
            bot.edit_message_text(text='برای بازی در این سطح اشتراک طلایی فعال کنید', chat_id=call.from_user.id,
                                  message_id=call.message.message_id)
            return
        if hardness == 'too easy' or hardness == 'easy':
            game_time = 5
            if hardness == 'too easy':
                length = 2
                fr_hardness = 'آبکی'
            else:
                length = 3
                fr_hardness = 'آسان'
        elif hardness == 'medium':
            game_time = 10
            length = 4
            fr_hardness = 'متوسط'
        elif hardness == 'hard':
            game_time = 15
            length = 5
            fr_hardness = 'سخت'
        else:
            game_time = 20
            if hardness == 'pro':
                length = 6
                fr_hardness = 'حرفه‌ای'

            else:
                length = 7
                fr_hardness = 'ویژه'
        bubbles = ''
        for i in range(length):
            bubbles += '🔴'
        preline = '🔐رمزجو(بازی فکر و بکر)🔐\n\n📚با آیکون های داده شده رمز را پیدا کنید. \nچراغ 🟢 یکی از رقمهای رمز، دقیق است.\nچراغ 🟡 یکی از رقم های رمز، صحیح ولی جابجاست. \nچراغ 🔴 یکی از رقم های رمز غلط است.\n\n💎سطح ' + fr_hardness + ' (رمز ' + str(
            length) + ' تایی)\n\n'
        line = u'\u200e' + '1️⃣' + user["first_name"] + '  〽️' + str(
            user["level"]) + '  🎖' + str(user["total_rank"]) + '\n' + bubbles + "\n\n🤖@RamzJoBot"
        bot.edit_message_text(
            text=preline + line,
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=create_game(hardness, 'single', call)
        )

    elif 'total ranking' == call.data:
        markup = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton('رنکینگ هفت روز اخیر', callback_data="seven ranking"),
            types.InlineKeyboardButton('رنکینگ کل', callback_data="total ranking"))

        text = get_total_ranking(users_coll.find({}).sort("total_point", -1))

        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                              reply_markup=markup)
    elif call.data == 'seven ranking':
        markup = types.InlineKeyboardMarkup(row_width=2).add(
            types.InlineKeyboardButton('رنکینگ هفت روز اخیر', callback_data="seven ranking"),
            types.InlineKeyboardButton('رنکینگ کل', callback_data="total ranking"))

        text = get_seven_ranking(games_coll.find(
            {"date": {"$gte": datetime.today().replace(microsecond=0) - timedelta(7)}, "mode": "multi"},
            {"users": 1}))

        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                              reply_markup=markup)
    elif call.data == 'c40' or call.data == 'c100' or call.data == 'c200' or call.data == 'c500' or call.data == 'c1000' or 's/' in call.data:
        if 'c' in call.data:
            coins = int(re.sub('c', '', call.data))
            amount = str(prices[str(coins)])
            client_id = pays_coll.insert_one(
                {"user_id": str(call.from_user.id), "coins": coins, "type": "coin", "status": "paying",
                 "date": datetime.today().replace(microsecond=0)}).inserted_id
        elif 's/' in call.data:
            user = users_coll.find_one({"tel_id": str(call.from_user.id)})
            # if user["golden_sub"]:
            #     bot.edit_message_text('شما هنوز اشتراک فعال دارید.', call.from_user.id, call.message.message_id)
            #     return
            client_id = pays_coll.insert_one(
                {"user_id": str(call.from_user.id), "type": "golden sub", "days": int(call.data.split("/")[1]),
                 "status": "paying", "date": datetime.today().replace(microsecond=0)}).inserted_id
            amount = str(sub_prices[call.data.split("/")[1]])

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer 8a65d585ce24ea37cc87359866f186fcb3ec3782e6b18ac59317188bb5725ab7"
        }
        params = {
            "amount": amount,
            "payerIdentity": "",
            "payerName": "",
            "description": "",
            "returnUrl": "https://appteams.ir/verify-201.html",
            "clientRefId": str(client_id)
        }
        r = requests.post(url="https://api.payping.ir/v1/pay", json=params, headers=headers).json()
        try:
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('تکمیل پرداخت',
                                                                                 url="https://appteams.ir/verify-200.html?code=" +
                                                                                     r["code"] + ""))
            bot.edit_message_text('برای تکمیل خرید خود بر روی دکمه ی زیر کلیک کنید:', call.from_user.id,
                                  call.message.id, reply_markup=markup)



        except Exception as e:
            print("line", 782, e)
    elif 'guide/' in call.data:
        game_id = call.data.split('/')[1]
        game = games_coll.find_one({"_id": ObjectId(game_id)})
        print("game guide", game)
        user = get_element(str(call.from_user.id), game["users"], "user_id")
        user_prof = users_coll.find_one({"tel_id": str(call.from_user.id)})
        if user is None:
            add_user_to_game(game_id, call)
            game = games_coll.find_one({"_id": ObjectId(game_id)})
            user = get_element(str(call.from_user.id), game["users"], "user_id")
        if (game["hardness"] == 'too easy' or game["hardness"] == 'easy') and user["guide"] == 1:
            bot.answer_callback_query(call.id, 'شما 1 بار از راهنما استفاده کرده‌اید!')
            return
        if user_prof["coins"] < 5:
            bot.answer_callback_query(call.id, 'شما سکه‌ی کافی ندارید!')
            return
        elif len(game["users"]) == 1 and moves_coll.find_one(
                {"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)}) is not None and game[
            "mode"] == "multi":
            bot.answer_callback_query(call.id, "اول دیگر بازیکنان باید شروع کنند!")
            return
        elif user["guide"] == 2 and game["hardness"] != 'special':
            bot.answer_callback_query(call.id, 'شما 2 بار از راهنما استفاده کرده‌اید!')
            return
        elif user["guide"] == 2 and game["hardness"] == 'special':
            index = random.randint(0, len(game["password_arr"]) - 1)
            while index == user["last_guide"] or index == user["last_guide2"]:
                index = random.randint(0, len(game["password_arr"]) - 1)
            icon = game["password_arr"][index]
            games_coll.update_one({"_id": ObjectId(game_id), "users.user_id": str(call.from_user.id)},
                                  {"$set": {"users.$.guide": 3,
                                            "users.$.last_guide3": index}})
            users_coll.update_one({"tel_id": str(call.from_user.id)}, {"$inc": {"coins": -5}})
            bot.answer_callback_query(call.id, 'خانه‌ی شماره ' + str(index + 1) + ' رمز برابر ' + icon + ' است!')
        elif user["guide"] == 3 and game["hardness"] == 'special':
            bot.answer_callback_query(call.id, 'شما 3 بار از راهنما استفاده کرده‌اید!')
            return
        elif user["guide"] == 0:
            index = random.randint(0, len(game["password_arr"]) - 1)
            icon = game["password_arr"][index]
            games_coll.update_one({"_id": ObjectId(game_id), "users.user_id": str(call.from_user.id)},
                                  {"$set": {"users.$.guide": 1,
                                            "users.$.last_guide": index}})
            users_coll.update_one({"tel_id": str(call.from_user.id)}, {"$inc": {"coins": -5}})
            bot.answer_callback_query(call.id, 'خانه‌ی شماره ' + str(index + 1) + ' رمز برابر ' + icon + ' است!')
        elif user["guide"] == 1:
            index = random.randint(0, len(game["password_arr"]) - 1)
            while index == user["last_guide"]:
                index = random.randint(0, len(game["password_arr"]) - 1)
            icon = game["password_arr"][index]
            games_coll.update_one({"_id": ObjectId(game_id), "users.user_id": str(call.from_user.id)},
                                  {"$set": {"users.$.guide": 2,
                                            "users.$.last_guide2": index}})
            users_coll.update_one({"tel_id": str(call.from_user.id)}, {"$inc": {"coins": -5}})
            bot.answer_callback_query(call.id, 'خانه‌ی شماره ' + str(index + 1) + ' رمز برابر ' + icon + ' است!')


    elif 'i/' in call.data:
        icon = call.data.split("/")[1]
        game_id = call.data.split("/")[2]
        game = games_coll.find_one({"_id": ObjectId(game_id)})
        if game["is_finished"]:
            bot.answer_callback_query(call.id, "بازی به پایان رسیده!")
            return
        if game["mode"] == 'single' and call.message.message_id != game["inline_message_id"]:
            games_coll.update_one({"_id": ObjectId(game_id)}, {"$set": {"inline_message_id": call.message.message_id}})
        if moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)}) is None:
            add_user_to_game(game_id, call)
            game = games_coll.find_one({"_id": ObjectId(game_id)})
        if len(game["users"]) == 1 and moves_coll.find_one(
                {"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)}) is not None and game[
            "mode"] == "multi":
            bot.answer_callback_query(call.id, "اول دیگر بازیکنان باید شروع کنند!")
            return
        moves = moves_coll.find_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)})["moves"]
        if len(moves) == 0 or len(moves[- 1]["input_arr"]) == len(game["password_arr"]):
            moves_coll.update_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)},
                                  {"$push": {"moves": {
                                      "input": icon,
                                      "input_arr": [icon],
                                      "point": 0,
                                      "state": ''}}})
            bot.answer_callback_query(call.id, icon)
        else:
            moves[- 1]["input"] += icon
            if moves[- 1]["input"] == game["password"]:
                games_coll.update_one({"_id": ObjectId(game_id)},
                                      {"$set": {"is_finished": True, "winner_id": str(call.from_user.id)}})
            moves[- 1]["input_arr"].append(icon)
            text = ''
            state = ''
            point = 0
            counter = 0
            length = 0
            if len(moves[- 1]["input_arr"]) == len(game["password_arr"]):
                for i in range(0, len(moves[- 1]["input_arr"])):
                    if moves[- 1]["input_arr"][i] == game["password_arr"][i]:
                        counter += 1
                        text += '🟢'
                        state += '🟢'
                        point += 3
                        game["password_arr"][i] = '-1'
                        moves[-1]["input_arr"][i] = '+1'
                if 0 < counter < len(game["password_arr"]):
                    length = counter
                    text += ' , '
                    state += '  '
                for i in range(0, len(moves[- 1]["input_arr"])):
                    if moves[- 1]["input_arr"][i] != game["password_arr"][i] and moves[- 1]["input_arr"][i] in game[
                        "password_arr"]:
                        counter += 1
                        index = game["password_arr"].index(moves[- 1]["input_arr"][i])
                        game["password_arr"][index] = '-1'
                        moves[- 1]["input_arr"][i] = '+1'
                        text += '🟡'
                        state += '🟡'
                        point += 1
                if length < counter < len(game["password_arr"]):
                    text += ' , '
                    state += '  '
                if counter < len(game["password_arr"]):
                    for i in range(0, len(game["password_arr"]) - counter):
                        text += '🔴'
                        state += '🔴'
                bot.answer_callback_query(call.id, text)
                try:
                    # print(moves)
                    if len(moves) == 1:
                        games_coll.update_one({"_id": ObjectId(game_id)},
                                              {"$set": {"is_edited": True}})
                    elif moves[-2]["state"] != state:
                        games_coll.update_one({"_id": ObjectId(game_id)},
                                              {"$set": {"is_edited": True}})
                except Exception as e:
                    print("line", 896, e)
                moves_coll.update_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)},
                                      {"$set": {"moves." + str(len(moves) - 1): {
                                          "input": moves[- 1]["input"], "input_arr": moves[- 1]["input_arr"],
                                          "state": state, "point": point
                                      }}})
            else:
                moves_coll.update_one({"game_id": ObjectId(game_id), "user_id": str(call.from_user.id)},
                                      {"$set": {"moves." + str(len(moves) - 1): {
                                          "input": moves[- 1]["input"], "input_arr": moves[- 1]["input_arr"],
                                          "state": '', "point": 0
                                      }}})
            game = games_coll.find_one({"_id": ObjectId(game_id)})
            bot.answer_callback_query(call.id, moves[- 1]["input"])
            if moves[- 1]["input"] == game["password"] or game["is_finished"]:
                if game["mode"] == "single":
                    bot.edit_message_text(update_game_text(game["users"], game_id),
                                          message_id=call.message.message_id, chat_id=call.from_user.id,
                                          reply_markup=create_keyboards(game["keyboards"], game_id))
                else:
                    bot.edit_message_text(update_game_text(game["users"], game_id),
                                          inline_message_id=call.inline_message_id,
                                          reply_markup=create_keyboards(game["keyboards"], game_id),
                                          parse_mode="Markdown")
                    update_profiles(game["users"], game_id)

    elif call.data == 'shop':
        bot.answer_callback_query(url='t.me/RamzJoBot?start=shop', callback_query_id=call.id)


_thread.start_new_thread(schedule_function, ())

while True:
    bot.polling()


