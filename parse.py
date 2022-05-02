                # <-- Libraries

import telebot
from telebot import types
import requests
import json

from doc import token
from doc import token_novokosino
from doc import token_nekrasovka

from doc import Internal_Integration_Token
from doc import Base_URL
from doc import Page_URL
from doc import DataBase_Staff_URL
from doc import DataBase_Staff_ID
                # --> Libraries


                # <-- Bot tokens

bot = telebot.TeleBot(token)
bot_Novokosino = telebot.TeleBot(token_novokosino)
bot_Nekrasovka = telebot.TeleBot(token_nekrasovka)

                # --> Bot tokens


                # <-- Request Parameters

headers_for_POST = {'Authorization': Internal_Integration_Token,
                    'Notion-Version': '2021-08-16',
                    'Content-Type': 'application/json'}

                # --> Request Parameters


                # <-- Notion

def readStaffData(databaseId, headers):
    full_link = f"{Base_URL + databaseId}/query"

    res = requests.request("POST", full_link, headers=headers)
    collectedData = res.json()
    if res.status_code != 200:
        print(res.status_code)
        print(res.text)
    with open('./collectedData.json', 'w', encoding='UTF-8') as f:
        json.dump(collectedData, f, ensure_ascii=False)


def retriveWorkerRank(workerId):
    workerRank = 'Unknown'

    with open('./collectedData.json', encoding='UTF-8') as json_data:
        data = json.load(json_data)
        for worker in data['results']:
            if worker["properties"]["ID"]["number"] == workerId:
                workerRank = worker['properties']['Rank']['select']['name']
                break

    return workerRank


def retriveWorkerName(workerId):
    workerName = 'Unknown'

    with open('./collectedData.json', encoding='UTF-8') as json_data:
        data = json.load(json_data)
        for worker in data['results']:
            if worker["properties"]["ID"]["number"] == workerId:
                workerName = worker['properties']['FIO']['title'][0]['text']['content']
                break

    return workerName


def ChangeCassaStatus(pageId, headers, cassaName):
    full_link = f"{Page_URL + pageId}"

    dataJSONformat = {
        "properties": {
            "Cashier Status": {
                "select": {
                    "name": cassaName
                }
            }
        }
    }

    data = json.dumps(dataJSONformat)

    res = requests.request("PATCH", full_link, headers=headers, data=data)

    if res.status_code != 200:
        print(res.status_code)
        print(res.text)

    readStaffData('d12fc3a11d0740758123dbbbb567ef33', headers)


def OpenCashBox(workerId, cassa_location, message):

    fl = True
    cassaCanBeOpened = True
    currentUserPageId = None

    with open('./collectedData.json', encoding='UTF-8') as json_data:
        data = json.load(json_data)
        for worker in data['results']:
            if fl:
                if worker["properties"]["ID"]["number"] == workerId:
                    currentUserPageId = worker['id']
                    fl = False
                    if worker["properties"]["Cashier Status"]["select"]["name"] != "Closed":
                        bot.reply_to(message, "You already have opened shift.\n"
                                              "Please close it before starting a new one")
                        cassaCanBeOpened = False
                        break

            if worker["properties"]["Cashier Status"]["select"]["name"] == cassa_location:
                bot.reply_to(message, "This CashBox has been already opened\n"
                                      "If you think u see this message by mistake, please contact our support team")
                cassaCanBeOpened = False
                break

    if cassaCanBeOpened:
        if cassa_location == 'Novokosino':
            ChangeCassaStatus(currentUserPageId, headers_for_POST, cassa_location)
        if cassa_location == 'Nekrasovka':
            ChangeCassaStatus(currentUserPageId, headers_for_POST, cassa_location)


def CloseCashBox(workerId, cassa_location, message):

    fl = True
    cassaCanBeClosed = True
    currentUserPageId = None

    with open('./collectedData.json', encoding='UTF-8') as json_data:
        data = json.load(json_data)
        for worker in data['results']:
            if fl:
                if worker["properties"]["ID"]["number"] == workerId:
                    currentUserPageId = worker['id']
                    fl = False

                    if worker["properties"]["Cashier Status"]["select"]["name"] == 'Closed':
                        bot.reply_to(message, "This CashBox has been already closed\n"
                                              "If you think u see this message by mistake, please contact our support team")
                        cassaCanBeClosed = False
                        break

    if cassaCanBeClosed:
        if cassa_location == 'Closed':
            ChangeCassaStatus(currentUserPageId, headers_for_POST, cassa_location)

                # --> Notion


                # <-- Construct ReplyButton

def createReplyKeyboard(keys):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for key in keys:
        button = types.KeyboardButton(key)
        keyboard.add(button)
    return keyboard


                # <-- Construct ReplyButton


                # <-- Start menu

@bot.message_handler(commands=['start'])
def start(message):

    readStaffData(DataBase_Staff_ID, headers_for_POST)
    user_id = message.from_user.id

    bot.send_message(message.chat.id, f'Добро пожаловать,{retriveWorkerName(user_id)}! \n Я замена старой тетрадки'
                                      f' и меня создали, потому что у'
                                      ' одного из работников закончилаь ручка, он страдал всю смену и было решено'
                                      ' запустить меня \n Вот список команд, которые тебе помогут: \n ')

    CurrentUserRank = retriveWorkerRank(user_id)

                            #<-- Retrive user ID
    # user_username = message.from_user.username
    # fl = False
    # with open('./StaffId.txt', 'r+', encoding='UTF-8') as f:
    #    for line in f:
    #        if line.find(str(user_id)) != -1:
    #            fl = True
    #    if not fl:
    #        f.write(f"{user_username} has id = {user_id}\n")
    #        #bot.send_message(message.chat.id, "Успешно получен ваш id, спасибо! <3")
                            #--> Retrive user ID


                            # <-- Create markup keyboards

    RankMarkupCashier = createReplyKeyboard(['Cashier'])
    RankMarkupManager = createReplyKeyboard(['Cashier', 'Manager'])
    RankMarkupAdmin = createReplyKeyboard(['Cashier', 'Manager', 'Admin'])


                            # --> Create markup keyboards


                            # <-- Accessing the category

    if CurrentUserRank == 'Cashier':
        bot.send_message(message.chat.id, f"You have permission level: {CurrentUserRank}"
                                          f"\nPlease choose which category u want access to:\n",
                         reply_markup=RankMarkupCashier)
    elif CurrentUserRank == 'Manager':
        bot.send_message(message.chat.id, f"You have permission level: {CurrentUserRank}"
                                          f"\nPlease choose which category u want access to:\n",
                         reply_markup=RankMarkupManager)
    elif CurrentUserRank == 'Admin':
        bot.send_message(message.chat.id, f"You have permission level: {CurrentUserRank}"
                                          f"\nPlease choose which category u want access to:\n",
                         reply_markup=RankMarkupAdmin)
    else:
        bot.send_message(message.chat.id, "I have a little problem with your sexual orientation"
                                          "\nPlease contact our support")

                            # --> Accessing the category


                # --> Start menu


                # <-- Select role

@bot.message_handler(content_types=['text'])
def selectrole(message):

    user_id = message.from_user.id
    CurrentUserRank = retriveWorkerRank(user_id)
    ranklist = ['Cashier', 'Manager', 'Admin']
    pointlist = ['Новокосино', 'Некрасовка']
    CloseShiftList = ['Закрыть смену', 'Пойти нахуй']
    if message.text in ranklist:
        if message.text == 'Cashier':
            ChoosePoint = createReplyKeyboard(['Новокосино', 'Некрасовка'])
            bot.send_message(message.chat.id, "Welcome, cashier!\nPlease choose your selling point", reply_markup=ChoosePoint)
            #cashier(mesg)
        elif (message.text == 'Manager') and ((CurrentUserRank == 'Manager') or (CurrentUserRank == 'Admin')):
            mesg = bot.send_message(message.chat.id, "Welcome, manager")
            manager(mesg)
        elif (message.text == 'Admin') and (CurrentUserRank == 'Admin'):
            mesg = bot.send_message(message.chat.id, "Welcome, admin")
            admin(mesg)
        else:
            bot.send_message(message.chat.id, "You are not worthy!")

    elif message.text in pointlist:
        user_id = message.from_user.id
        if message.text == 'Новокосино':
            ClosePoint = createReplyKeyboard(CloseShiftList)
            OpenCashBox(user_id, "Novokosino", message)
            bot.send_message(message.chat.id, 'Добро пожаловать в Новокосино', reply_markup=ClosePoint)
        elif message.text == 'Некрасовка':
            bot.send_message(message.chat.id, "Добро пожаловать в некрасовку, самое опасное место востока. "
                                              "Давай уясним несколько правил нахождения тут: \n"
                                              "1. Узнай сразу, где тут сдавать телефоны, потому что это самая частая"
                                              " консультация, которую ты будешь давать на данной точке и отбиваться"
                                              " от пасивных мобов, которые нас не интересуют \n"
                                              "2. У босса данной локации есть способность включать колонку с ебучей "
                                              "музыкой. Даже если она не кажется тебе ебучей, ты не захочишь слышать"
                                              " ее второй раз, не сомневайся и отбивайся от этого своим артифактом"
                                              " - наушниками сразу, при включении \n"
                                              "3. Также важный момент, пассивные мобы часто просто смотрят,"
                                              " не спеши нападать на них, потому что моешь получить единицу,"
                                              " а иногда и все 100 физического урона\n"
                                              "4. Вспомни все свои навыки выживания в обычной локации - универ и"
                                              " применяй навык красноречия с каждым активным мобом, который пришел"
                                              " и может или потом сможет что-то купить \n"
                                              "5. Удачи в данной непростой локации лично от меня и всего состава"
                                              " Smoking Kills")
            OpenCashBox(user_id, "Nekrasovka", message)
    elif message.text in CloseShiftList:
        if message.text == 'Закрыть смену':
            CloseCashBox(user_id, "Closed", message)
            bot.send_message(message.chat.id, 'Смена закрыта, ваша ЗП: ')
    else:
        bot.send_message(message.chat.id, "I don't understand ):")

                # --> Select role


                # <-- Cashier function

# def cashier(message):
#     ChoosePoint = createReplyKeyboard(['Новокосино', 'Некрасовка'])
#     bot.send_message(message.chat.id, "Please choose your selling point", reply_markup=ChoosePoint)


                # <-- Cashier function


                # --> Two more Bots

def Novokosino_bot(message):
    pass

def Nekrasovka_bot(message):
    pass

                # <-- Two more Bots


                # <-- Manager function

def manager(message):
    pass

                # <-- Manager function


                # <-- Admin function

def admin(message):
    pass

                # <-- Admin function


@bot_Nekrasovka.message_handler(commands=['start'])
def start_Nekrasovka(message):
    bot_Nekrasovka.send_message(message.chat.id, "Добро пожаловать в некрасовку, самое опасное место востока. "
                                                 "Давай уясним несколько правил нахождения тут: \n"
                                                 "1. Узнай сразу, где тут сдавать телефоны, потому что это самая частая"
                                                 " консультация, которую ты будешь давать на данной точке и отбиваться"
                                                 " от пасивных мобов, которые нас не интересуют \n"
                                                 "2. У босса данной локации есть способность включать колонку с ебучей "
                                                 "музыкой. Даже если она не кажется тебе ебучей, ты не захочишь слышать"
                                                 " ее второй раз, не сомневайся и отбивайся от этого своим артифактом"
                                                 " - наушниками сразу, при включении \n"
                                                 "3. Также важный момент, пассивные мобы часто просто смотрят,"
                                                 " не спеши нападать на них, потому что моешь получить единицу,"
                                                 " а иногда и все 100 физического урона\n"
                                                 "4. Вспомни все свои навыки выживания в обычной локации - универ и"
                                                 " применяй навык красноречия с каждым активным мобом, который пришел"
                                                 " и может или потом сможет что-то купить \n"
                                                 "5. Удачи в данной непростой локации лично от меня и всего состава"
                                                 " Smoking Kills")





                # <-- Main

if __name__ == '__main__':
    bot.infinity_polling()

                # --> Main
