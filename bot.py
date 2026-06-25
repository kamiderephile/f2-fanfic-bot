import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatAction
from telegram.error import BadRequest

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHOR_CHAT_ID = int(os.getenv("AUTHOR_CHAT_ID"))

SUBSCRIBERS_FILE = "subscribers.json"
RATINGS_FILE = "ratings.json"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

CHARACTERS_DB = {
    "main": {
        "Алексия Ривера": "alexia",
        "Юри Випс": "yuri",
        "Франц (Инженер)": "franz",
        "Шарль Ривера": "charles",
        "Шарлотта Ривера": "charlotte",
        "Другие": "others"
    },
    "details": {
        "alexia": (
            "👩 *А Л Е К С И Я   Р И В Е Р А*\n\n"
            "*Полное имя:* Алексия Рене Ривера\n"
            "*Роль:* Пилот Hitech Grand Prix (F2)\n"
            "*Возраст:* 18 лет | *Рост:* 163 см | *Родина:* Монако\n\n"
            "*О   П Е Р С О Н А Ж Е:*\n"
            "Дебютантка F2, выгрызшая место в мужском мире через картинг. Балансирует между жесткими правилами паддока и любовью к морю, французским шансонам и родному Монте-Карло.\n\n"
            "*Х А Р А К Т Е Р:*\n"
            "Упрямая, как болид на холодной резине. За хрупкостью скрывается стальной стержень и ум инженера. На трассе агрессивна: поздние торможения и обгоны по внешней, в стиле Макса Ферстаппена. Вне трассы может быть резкой, но тает от котят и комплиментов отца.\n\n"
            "❤️ *Л Ю Б И Т:*\n"
            "• Dracula от Tame Impala и  Sharks от Imagine Dragons перед гонкой\n"
            "• Чай с персиком и манго c 3 ложками сахара\n"
            "• Ночные заезды на отцовском Peugeot 504 Cabriolet\n"
            "• Певиц Dua Lipa и Sabrina Carpenter\n"
            "• Lego Technic (традиция с отцом на Рождество)\n"
            "• Гипсофилы в вазе и запеченную картошку мамы\n\n"
            "💔 *Н Е   Л Ю Б И Т:*\n"
            "• Вопросы «Каково быть девушкой в автоспорте?»\n"
            "• Дождь в квалификации (превращает гонку в лотерею)\n"
            "• Объятия без спроса и холодный чай\n"
            "• Розы, болгарский перец, баклажаны и математику\n\n"
            "⚡ *Ф А К Т Ы:*\n"
            "1. Кумир — Найджел Мэнселл («Лев»), чемпион 1992 года за команду Williams.\n"
            "2. Водительские права получила в первый день совершеннолетия, первая поездка была ночью под Джо Дассена.\n"
            "3. Боится высоты, змей, медведей и казуаров из-за документальных фильмов и энциклопедий в детстве.\n"
            "4. На заставке телефона — фото Алексии со смешной гримасой в толстовке Юри"
        ),
        "yuri": (
            "🏎️ *Ю Р И   В И П С*\n\n"
            "*Полное имя:* Юри Випс\n"
            "*Роль:* Пилот Hitech Grand Prix (F2)\n"
            "*Возраст:* 20 лет | *Рост:* 181 см | *Родина:* Таллин\n\n"
            "*О   П Е Р С О Н А Ж Е:*\n"
            "Эстонец с ледяным спокойствием. Говорит мало, думает много. В паддоке известен как сдержанный пилот, но на трассе проявляет холодную агрессию. Вырос в семье архитектора и учительницы музыки, выбрав трассу как место встречи расчета и риска.\n\n"
            "С Алексией прошел путь от соперничества до глубокой связи. Юри балансирует на грани, но никогда не срывается.\n\n"
            "*Х А Р А К Т Е Р:*\n"
            "Спокоен, как штиль. Эмоции держит при себе, но замечает все: усталость Алексии и ее скрытую злость. Обладает специфическим ироничным юмором, который понимает только Алексия.\n\n"
            "❤️ *Л Ю Б И Т:*\n"
            "• Тишину ранним утром на пустой трассе\n"
            "• Черный кофе без сахара\n"
            "• Джаз (Майлз Дэвис, Колтрейн) и архитектуру городов\n"
            "• Когда Алексия злится, но скрывает это\n"
            "• Как Алексия собирает волосы в пучок перед гонкой\n\n"
            "💔 *Н Е   Л Ю Б И Т:*\n"
            "• Нарушение личного пространства\n"
            "• Пустые светские беседы\n"
            "• Когда его называют «холодным»\n"
            "• Беспорядок в моторхоуме и молчание Алексии о проблемах\n\n"
            "⚡ *Ф А К Т Ы:*\n"
            "1. Тайно играет на фортепиано, о чем знает только Алексия.\n"
            "2. Родинка на левом плече, которую заметила Алексия в Бахрейне.\n"
            "3. Коллекционирует винил с джазом, возит с собой на гонки.\n"
            "4. Боится медуз после случая в детстве в Пярну.\n"
            "5. Тайно следит за Инстаграмом Алексии, оставляя редкие комментарии."
        ),
        "franz": (
            "📊 *Ф Р А Н Ц*\n\n"
            "*Имя:* Франц Майер\n"
            "*Роль:* Старший инженер Алексии\n"
            "*Возраст:* 54 года | *Родина:* Штутгарт\n\n"
            "*О   П Е Р С О Н А Ж Е:*\n"
            "Немец старой закалки. Начинал, когда телеметрии еще не было. Сначала скептически относился к Алексии, но после ее успеха на мокрой трассе сказал «Gut gemacht». Теперь ее главный наставник и защитник.\n\n"
            "*Х А Р А К Т Е Р:*\n"
            "Педантичный и требовательный. Не терпит опозданий и пустых оправданий. За резкостью скрывается искренняя забота о пилоте и машине.\n\n"
            "❤️ *Л Ю Б И Т:*\n"
            "• Порядок в боксах и телеметрии\n"
            "• Хороший кофе и тишину после работы\n"
            "• Умные вопросы от пилотов\n\n"
            "💔 *Н Е   Л Ю Б И Т:*\n"
            "• Фразу «я не знаю» без попыток узнать\n"
            "• Журналистов и провокационные вопросы\n\n"
            "⚡ *Ф А К Т Ы:*\n"
            "1. Дома живет пес Отто, подобранный на трассе.\n"
            "2. Носит одни ботинки 15 лет «на удачу»."
        ),
        "charles": (
            "💼 *Ш А Р Л Ь   Р И В Е Р А*\n\n"
            "*Имя:* Шарль Марти Ривера\n"
            "*Роль:* Отец Алексии\n"
            "*Профессия:* Владелец логистической компании\n\n"
            "*О   П Е Р С О Н А Ж Е:*\n"
            "Строгий, но справедливый. Не говорит «люблю» словами, но встает в 4 утра, чтобы отвезти дочь на тренировку. Научил ее разбирать двигатель и читать телеметрию.\n\n"
            "*Х А Р А К Т Е Р:*\n"
            "Сдержанный и сухой. Редко улыбается на людях, но дома позволяет себе быть другим. Замечает каждую мелочь в состоянии дочери.\n\n"
            "❤️ *Л Ю Б И Т:*\n"
            "• Свой Peugeot 504 и бумажные газеты\n"
            "• Оладьи жены по утрам\n"
            "• Когда дочь звонит просто поболтать\n\n"
            "💔 *Н Е   Л Ю Б И Т:*\n"
            "• Сомнения в талантах Алексии\n"
            "• Хаос в гараже и споры с женой\n\n"
            "⚡ *Ф А К Т Ы:*\n"
            "1. В молодости хотел стать гонщиком, но стал инженером.\n"
            "2. Тайно ведет статистику всех гонок дочери в блокноте."
        ),
        "charlotte": (
            "🎨 *Ш А Р Л О Т Т А   Р И В Е Р А*\n\n"
            "*Имя:* Шарлотта Рене Ривера\n"
            "*Роль:* Мать Алексии\n"
            "*Профессия:* Дизайнер интерьеров\n\n"
            "*О   П Е Р С О Н А Ж Е:*\n"
            "Душа семьи. Эмоциональная и щедрая на объятия. Учит дочь видеть красоту вокруг и всегда рядом на гонках с термосом чая.\n\n"
            "*Х А Р А К Т Е Р:*\n"
            "Порывистая и энергичная. Говорит быстро на смеси французского и итальянского. Умеет быть тихой и поддерживающей, когда дочке плохо.\n\n"
            "❤️ *Л Ю Б И Т:*\n"
            "• Готовить картошку с розмарином\n"
            "• Французские фильмы и свежие цветы\n"
            "• Когда вся семья собирается дома\n\n"
            "💔 *Н Е   Л Ю Б И Т:*\n"
            "• Тишину в пустом доме, из-за чего часто в одиночестве вяжет крючком\n"
            "• Когда кто-то обижает ее «львицу»-дочь\n\n"
            "⚡ *Ф А К Т Ы:*\n"
            "1. В молодости мечтала стать певицей.\n"
            "2. Смотрит все трансляции гонок дочери в 3 ночи, зная расписание наизусть."
        ),
        "others": (
            "📂 *Список пополняется...*\n\n"
            "Новые персонажи будут добавлены по мере развития сюжета."
        )
    }
}

F2_CALENDAR_TEXT = """
📅 *Гран-при Формулы-2: Сезон 2021*

🇧🇭 *Бахрейн* (Сахир) | 26–28 марта
Быстрая трасса с длинными прямыми.

🇲🇨 *Монако* (Монте-Карло) | 20–22 мая
Домашний этап Алексии. Узкие улицы, где ошибка стоит вылета.

🇦🇿 *Азербайджан* (Баку) | 5–6 июня
Самая быстрая городская трасса с прямой вдоль набережной.

🇬🇧 *Великобритания* (Сильверстоун) | 16–18 июля
Классика: быстрые повороты Maggotts и Becketts.

🇮🇹 *Италия* (Монца) | 10–12 сентября
Храм скорости. Минимум прижимной силы, максимум мощности.

🇷🇺 *Россия* (Сочи) | 24–26 сентября
Плавные повороты вокруг Олимпийского парка.

🇸🇦 *Саудовская Аравия* (Джидда) | 3–5 декабря
Новая сверхбыстрая трасса вдоль Красного моря.

🇦🇪 *ОАЭ* (Абу-Даби) | 10–12 декабря
Финиш сезона под светом прожекторов на Яс Марина.
"""

SUPPORT_INFO = "💳 *Поддержать автора*\n\n" \
               "Если Вам нравится фанфик, Вы можете поддержать развитие проекта:\n" \
               "• Реквизиты указаны в закрепленном сообщении канала.\n" \
               "Спасибо за Вашу поддержку! ❤️"

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} if filename == RATINGS_FILE else []

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_rating(user_id, rating):
    ratings = load_json(RATINGS_FILE)
    entry = {
        "user_id": user_id,
        "rating": rating,
        "timestamp": str(__import__('datetime').datetime.now())
    }
    if "ratings" not in ratings:
        ratings["ratings"] = []
    ratings["ratings"].append(entry)
    save_json(RATINGS_FILE, ratings)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    keyboard = [
        [KeyboardButton("👥 Персонажи"), KeyboardButton("📅 Календарь сезона")],
        [KeyboardButton("⭐ Оценить главу"), KeyboardButton("💰 Поддержать автора")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = "Привет! Я бот фанфика *«Разрешённый риск»*. \n\nВыбери раздел в меню ниже:"
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def characters_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    keyboard = []
    for name in CHARACTERS_DB["main"]:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"char_{CHARACTERS_DB['main'][name]}")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text("Выбери персонажа:", reply_markup=reply_markup)
        except BadRequest:
            await update.callback_query.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)
            await update.callback_query.message.delete()
    else:
        await update.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)

async def show_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    char_key = query.data.split("_")[1]
    text = CHARACTERS_DB["details"].get(char_key, "Информация не найдена.")
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад к списку", callback_data="chars_list")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")
    except BadRequest:
        await query.message.reply_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")
        await query.message.delete()

async def chars_list_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for name in CHARACTERS_DB["main"]:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"char_{CHARACTERS_DB['main'][name]}")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await query.edit_message_text("Выбери персонажа:", reply_markup=reply_markup)
    except BadRequest:
        await query.message.reply_text("Выбери персонажа:", reply_markup=reply_markup)
        await query.message.delete()

async def calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
    
    try:
        with open('calendar_f2_2021.jpg', 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=F2_CALENDAR_TEXT, parse_mode="Markdown")
    except FileNotFoundError:
        await update.message.reply_text(F2_CALENDAR_TEXT, parse_mode="Markdown")

async def rate_chapter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    keyboard = [
        [InlineKeyboardButton("⭐ 1", callback_data="rate_1"), InlineKeyboardButton("⭐ 2", callback_data="rate_2"), InlineKeyboardButton("⭐ 3", callback_data="rate_3")],
        [InlineKeyboardButton("⭐ 4", callback_data="rate_4"), InlineKeyboardButton("⭐ 5", callback_data="rate_5")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text("Как тебе последняя глава? Поставь оценку:", reply_markup=reply_markup)
        except BadRequest:
            await update.callback_query.message.reply_text("Как тебе последняя глава? Поставь оценку:", reply_markup=reply_markup)
            await update.callback_query.message.delete()
    else:
        await update.message.reply_text("Как тебе последняя глава? Поставь оценку:", reply_markup=reply_markup)

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    rating = query.data.split("_")[1]
    user_id = query.from_user.id
    
    save_rating(user_id, rating)
    
    notify_text = f"🌟 *Новая оценка главы*\n\nЗвезд: {rating}"
    try:
        await context.bot.send_message(chat_id=AUTHOR_CHAT_ID, text=notify_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Не удалось отправить оценку автору: {e}")
    
    text = f"Спасибо! Твоя оценка {rating} звезд сохранена."
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    except BadRequest:
        await query.message.reply_text(text=text, reply_markup=reply_markup)
        await query.message.delete()

async def notify_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != AUTHOR_CHAT_ID:
        await update.message.reply_text("Эта команда доступна только автору.")
        return
    
    message_text = " ".join(context.args)
    if not message_text:
        await update.message.reply_text("Используй формат: /notify Текст уведомления")
        return
    
    subscribers = load_json(SUBSCRIBERS_FILE)
    sent_count = 0
    
    for sub_id in subscribers:
        try:
            await context.bot.send_message(chat_id=sub_id, text=message_text)
            sent_count += 1
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {sub_id}: {e}")
            
    await update.message.reply_text(f"Уведомление отправлено {sent_count} подписчикам.")

async def support_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(SUPPORT_INFO, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(SUPPORT_INFO, parse_mode="Markdown")
            await update.callback_query.message.delete()
    else:
        await update.message.reply_text(SUPPORT_INFO, parse_mode="Markdown")

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [KeyboardButton("👥 Персонажи"), KeyboardButton("📅 Календарь сезона")],
        [KeyboardButton("⭐ Оценить главу"), KeyboardButton("💰 Поддержать автора")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await query.message.reply_text("Главное меню:", reply_markup=reply_markup)
    await query.message.delete()

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify", notify_subscribers))

    application.add_handler(MessageHandler(filters.Regex("^👥 Персонажи$"), characters_menu))
    application.add_handler(MessageHandler(filters.Regex("^📅 Календарь сезона$"), calendar))
    application.add_handler(MessageHandler(filters.Regex("^⭐ Оценить главу$"), rate_chapter))
    application.add_handler(MessageHandler(filters.Regex("^💰 Поддержать автора$"), support_author))

    application.add_handler(CallbackQueryHandler(show_character, pattern="^char_"))
    application.add_handler(CallbackQueryHandler(handle_rating, pattern="^rate_[1-5]$"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(chars_list_back, pattern="^chars_list$"))

    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()