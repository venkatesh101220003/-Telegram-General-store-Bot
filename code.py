from pymongo import MongoClient
from datetime import date
from typing import Final
import telegram
from telegram.ext import (
    CommandHandler, CallbackContext,
    ConversationHandler, MessageHandler,
    filters, Updater, CallbackQueryHandler
)
# pip install python-telegram-bot
from telegram import *
from telegram.ext import Application,CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
# Define Options
CHOOSEUSER,ADMINMENUE,CLIENTMENUE,CHECKOUT,PRODUCT,CLIENTMENUESELECTION,PRODUCTCATEGORY,CART,CONFIRMATION,ADMINMENUESELECTION = range(10)
CONNECTION_STRING = "mongodb+srv://koushik:koushik2003@cluster0.zvmhh43.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
dbname = client['Bot']

print('Starting up bot...')

TOKEN: Final = '5882226477:AAGq_kbQseCTqITZTwq5elcVkpa-XHoXNTA'
BOT_USERNAME: Final = '@super_general_store_bot'
usersName=''



# Lets us use the /start command
async def start(update: Update, context: ContextTypes):
    print("Started")
    bot = context.bot
    chat_id = update.message.chat.id
    await bot.send_message(
        chat_id=chat_id,
        text='''Welcome to Super Store! Please enter your username and password Separated by comma
        Eg: pullurikoushik,koushik123'''
    )
    print('testing')
    return CHOOSEUSER

async def choose_user(update, context):
    global usersName
    bot = context.bot
    chat_id = update.message.chat.id
    print(chat_id)
    # create new data entry
    data = update.message.text.split(',')
    if len(data) < 2 or len(data) > 2:
        bot.send_message(
            chat_id=chat_id,
            text="Invalid entry, please make sure to input the details "
                 "as requested in the instructions"
        )
        bot.send_message(
            chat_id=chat_id,
            text="Type /start, to restart bot"
        )
        return ConversationHandler.END

    collection_user = dbname["User"]
    user_dict= collection_user.find_one({
       'user_name': data[0]
    })

    if(user_dict!=None and user_dict['admin']=="Y" and  user_dict['pass']==data[1]):
        reply_keyboard = [
            ["Continue"],
            ["logout"]
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        usersName=data[0]
        await bot.send_message(
            chat_id=chat_id,
            text="Hey Admin, "
                 "Your login is successful, please select the option",
            reply_markup=markup
        )
        return ADMINMENUE
    elif(user_dict!=None and user_dict['admin']=="N" and  user_dict['pass']==data[1]):
        reply_keyboard = [
            ["Continue"],
            ["logout"]
        ]
        usersName = data[0]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        await bot.send_message(

            chat_id=chat_id,
            text="Hey Customer, "
                 "Your login is successful, please select the option",
            reply_markup=markup
        )
        return CLIENTMENUE
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="Invalid Username/Password"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="Type /start, to restart bot"
        )
        return ConversationHandler.END

async def ClientMenue(update, context):
    if(update.message.text=='Clear Cart'):
        collection_cart = dbname["cart"]
        collection_cart.delete_many({
            'user_name':usersName
        })
        bot = context.bot
        chat_id= update.message.chat.id
        await bot.send_message(
            chat_id=chat_id,
            text='Your Cart is cleared',
        )

    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["SelectProducts"],
        ["ViewHistory"],
        ["Cart"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await bot.send_message(
        chat_id=chat_id,
        text='Please select Option',
        reply_markup=markup
    )
    return CLIENTMENUESELECTION



async def AdminMenue(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["Analytics"],
        ["Your Orders"],
        ["Add Products"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await bot.send_message(
        chat_id=chat_id,
        text="Please select Option",
        reply_markup=markup
    )
    return ADMINMENUESELECTION


async def AdminMenueSelection(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["Back"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await bot.send_message(
        chat_id=chat_id,
        text=
        '''
        Analytics 
        ---------
        
        Sales Analytics
        ---------------
        Annual Revenue:  3cr
        Current Month Revenue: 20L
        Revenue same Month Last year: 10L
        Revenue from NetNew Customers this month: 2L
        
        Product Analytics
        ----------------
        Shortage Products: Thumsup 500 ml , Lays 50g
        Most Ordered Product: Lays 50g
        
        People Analytics
        ---------------
        Total Active Customers: 2000
        New Customers this month: 55
        
        ''',
        reply_markup=markup
    )
    return ADMINMENUE


#products command
async def products_command(update: Update, context: ContextTypes):
    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["Back", "Cart"],
        ["Food and beverages"],
        ["Personal care and hygiene"],
        ["Household items"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await bot.send_photo(
        chat_id=chat_id,
        photo='https://media.istockphoto.com/id/1320617333/photo/shopping-cart-full-of-food-isolated-on-white-grocery-and-food-store-concept.jpg?b=1&s=170667a&w=0&k=20&c=R99lGco7R13270Hr0qfzZ-u28ZIzV0ENhHDuERjsTec=',
        caption="Please Select Product",
        reply_markup=markup
    )

    return PRODUCT


# Lets us use the /start command
async def select_product_command(update: Update, context: ContextTypes):
    bot = context.bot
    chat_id = update.message.chat.id

    collection_product = dbname["product"]
    user_di = collection_product.find({
        "category": update.message.text
    })
    reply_keyboard = []
    reply_keyboard.append(["Back", "Cart"])
    for i in user_di:
        l = [i['product_name'] + "- " + i['weight'] + ' - ' + str(i['price']) + "/Rs"]
        reply_keyboard.append(l)
        img=i['image']

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption="Please Select Product",
            reply_markup=markup
        )


    return CLIENTMENUESELECTION

async def CheckOut(update: Update, context: ContextTypes):
    bot = context.bot
    chat_id = update.message.chat.id
    if update.message.text == 'Cart':
        reply_keyboard = [
            ["Clear Cart"],
            ["Checkout"]
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        totalAmount=0
        collection_cart = dbname["cart"]
        cartobj=collection_cart.find({
            'user_name':usersName
        })
        checkoutstring="Cart\n\n--------------\n"
        for dict in cartobj:
            checkoutstring+=dict['product_name']+" - "+str(dict['price'])+'-/Rs'+'\n\n'
            totalAmount+=dict['price']
        checkoutstring+="------------------"+'\n\n'+"Total  amount is:"+str(totalAmount)+'-/Rs'
        await bot.send_message(
            chat_id=chat_id,
            text=checkoutstring,

        reply_markup = markup
        )
        return CHECKOUT


async def FinalCheckout(update: Update, context: ContextTypes):
    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["Yes"],
        ["No, cancel"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    totalAmount = 0
    collection_cart = dbname["cart"]
    cartobj = collection_cart.find({
        'user_name': usersName
    })
    checkoutstring = "Is everything correct?\n\nCart\n\n--------------\n"
    for dict in cartobj:
        checkoutstring += dict['product_name'] + " - " + str(dict['price']) + '\Rs' + '\n\n'
        totalAmount += dict['price']
    checkoutstring += "------------------" + '\n\n' + "Delivery Address: Hyderabad\nPayment: Cash\nContact request: +91778076****\nPlease select..\n\nTotal  amount is:" + str(totalAmount)+"-/RS"

    await bot.send_message(
        chat_id=chat_id,
        text=checkoutstring,

    reply_markup = markup
    )
    return CONFIRMATION

async def Confirmation(update: Update, context: ContextTypes):
    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["Continue shopping"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    collection_order = dbname["order"]
    collection_cart = dbname["cart"]
    largest_order =collection_order.find_one({}, sort=[('_id', -1)])
    order_id=1
    if(largest_order==None):
        order_id=1
    else:
        order_id = largest_order['_id']+1

    cart_items=collection_cart.find({
        'user_name':usersName
    })

    collection_order.insert_one({
        '_id':order_id,
        'user_name':usersName,
         'data':list(cart_items)

    })


    collection_cart.delete_many({
        'user_name': usersName
    })
    await bot.send_message(
        chat_id=chat_id,
        text='''Thank you! Your order is confirmed Our manager will contact you soon''',
        reply_markup=markup
    )
    return CLIENTMENUE

async def AddingMessage(update: Update, context: ContextTypes):

    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["Continue shopping"],
        ["Cart"]
    ]

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    name_of_product=update.message.text.split('-')
    collection_product = dbname["product"]
    collection_cart = dbname["cart"]
   # print(name_of_product[0])
    pro_dict=collection_product.find_one({
        'product_name':name_of_product[0]
    })
    amt=pro_dict['price']
    collection_cart.insert_one({
        'user_name':usersName,
        'product_name':name_of_product[0],
        'price':amt
    })
    await bot.send_message(
        chat_id=chat_id,
        text='''Product is added to Cart...''',
        reply_markup = markup
    )
    return CLIENTMENUE


async def ClientHistory(update: Update, context: ContextTypes):
    bot = context.bot
    chat_id = update.message.chat.id
    reply_keyboard = [
        ["Continue shopping"],
        ["Cart"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await bot.send_message(
        chat_id=chat_id,
        text='''Your orders:
        1) Order ID     -   542372
           Date         -   01-05-2023
           Total Price  -   600
           
        2) Order ID     -   738262
           Date         -   03-04-2023
           Total Price  -   900'''
        ,
        reply_markup = markup
    )
    return CLIENTMENUE



async def handle_response(text: str) -> str:
    # Create your own response logic
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    if 'how are you' in processed:
        return 'I\'m good!'

    if 'i love python' in processed:
        return 'Remember to subscribe!'

    await 'test'

    return 'I don\'t understand'

def handle_message(update: Update, context: ContextTypes):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # React to group messages only if users mention the bot directly
    if message_type == 'group':
        # Replace with your bot username
        if BOT_USERNAME in text:
            response: str = '''Sorry, We don't take orders in a group chat'''
        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    else:
        response: str = handle_response(text)

    # Reply normal if the message is in private
    print('Bot:', response)
    update.message.reply_text(response)


async def cancel():
    print("You called")
    await 'Cancel'
    return 'cancel'

# Run the program
if __name__ == '__main__':

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSEUSER:[
                MessageHandler(
                    telegram.ext.filters.ALL,choose_user
                )
            ],
            CLIENTMENUE:[
                MessageHandler(
                    telegram.ext.filters.Regex("Cart"),#
                    CheckOut
                ),
                MessageHandler(
                    telegram.ext.filters.TEXT,
                    ClientMenue
                )
            ],
            ADMINMENUE:[

                MessageHandler(
                    telegram.ext.filters.TEXT,
                    AdminMenue
                )
            ],
            ADMINMENUESELECTION:[

                MessageHandler(
                    telegram.ext.filters.TEXT,
                    AdminMenueSelection
                )
            ],
            CLIENTMENUESELECTION : [
                MessageHandler(
                    telegram.ext.filters.Regex("Cart"),
                    CheckOut
                ),
                MessageHandler(
                    telegram.ext.filters.Regex("Back"),
                    products_command
                ),
                MessageHandler(
                    telegram.ext.filters.Regex("SelectProducts"),
                    products_command
                ),
                MessageHandler(
                    telegram.ext.filters.Regex("ViewHistory"),
                    ClientHistory
                ),
                MessageHandler(
                    telegram.ext.filters.ALL,
                    AddingMessage
                )
            ],
            PRODUCT: [
                MessageHandler(
                    telegram.ext.filters.Regex("Back"),
                    ClientMenue
                ),
                MessageHandler(
                    telegram.ext.filters.Regex("Cart"),
                    CheckOut
                ),
                MessageHandler(
                    telegram.ext.filters.TEXT,
                    select_product_command
                ),
            ],
            CART:[
                MessageHandler(
                    telegram.ext.filters.Regex("Back"),
                    products_command
                ),
                MessageHandler(
                    telegram.ext.filters.TEXT, CheckOut
                ),
            ],
            CHECKOUT: [
                MessageHandler(
                    telegram.ext.filters.Regex("Clear Cart"),

                    ClientMenue
                ),
                MessageHandler(
                    telegram.ext.filters.TEXT, FinalCheckout
                ),
            ],
            CONFIRMATION: [
                MessageHandler(
                    telegram.ext.filters.Regex("Yes"),
                    Confirmation
                ),
                MessageHandler(
                    telegram.ext.filters.TEXT, ClientMenue
                ),
            ],

        },
        fallbacks=[CommandHandler('cancel',cancel)],
        allow_reentry=True
    )
   # app = Application.builder().token(TOKEN).build()
   # app.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.add_handler(conv_handler)
    print('Polling...')
    application.run_polling()
    print('debug3')




