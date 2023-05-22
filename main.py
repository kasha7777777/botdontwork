import telebot
import requests
from bs4 import BeautifulSoup

# Замените <YOUR_TOKEN> на токен вашего Telegram-бота
bot = telebot.TeleBot('5865446190:AAH8AxbkA0wp0ETzkItEAsAABuoVpE5eU5Y')

# Список сохраненных аниме
saved_anime = []

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для поиска и сохранения аниме. Чтобы начать, используйте команду /help.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help(message):
    help_text = "Я могу помочь вам найти аниме и сохранить их в список.\n\n" \
                "Доступные команды:\n" \
                "/find - Найти аниме по названию\n" \
                "/save - Сохранить аниме в список\n" \
                "/list - Показать список сохраненных аниме"
    bot.send_message(message.chat.id, help_text)

# Обработчик команды /find
@bot.message_handler(commands=['find'])
def find_anime(message):
    bot.send_message(message.chat.id, "Введите название аниме:")
    bot.register_next_step_handler(message, process_find_step)

# Обработчик ввода названия аниме
def process_find_step(message):
    anime_name = message.text.strip()
    search_results = search_anime_on_shikimori(anime_name)

    if search_results:
        keyboard = telebot.types.InlineKeyboardMarkup()
        for anime in search_results:
            callback_data = f"save_anime_{anime['link']}"
            keyboard.add(telebot.types.InlineKeyboardButton(text=anime['title'], callback_data=callback_data))

        bot.send_message(message.chat.id, "Результаты поиска:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "По вашему запросу ничего не найдено.")

# Функция для поиска аниме на сайте Shikimori.me
def search_anime_on_shikimori(anime_name):
    url = f"https://shikimori.me/search?search={anime_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    search_results = []
    anime_list = soup.find_all('div', class_='anime-card')

    for anime in anime_list:
        title = anime.find('a', class_='link').text
        link = anime.find('a', class_='link')['href']
        search_results.append({'title': title, 'link': link})

    return search_results

# Обработчик команды /save
@bot.message_handler(commands=['save'])
def save_anime(message):
    bot.send_message(message.chat.id, "Введите ссылку на страницу аниме для сохранения:")
    bot.register_next_step_handler(message, process_save_step)

# Обработчик ввода ссылки на страницу аниме для сохранения
def process_save_step(message):
    anime_link = message.text.strip()
    anime = get_anime_by_link(anime_link)

    if anime:
        saved_anime.append(anime)
        bot.send_message(message.chat.id, "Аниме успешно сохранено!")
    else:
        bot.send_message(message.chat.id, "Не удалось сохранить аниме. Проверьте правильность введенной ссылки.")

# Функция для получения информации об аниме по ссылке
def get_anime_by_link(anime_link):
    url = f"https://shikimori.me{anime_link}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('span', itemprop='name').text
    rating = soup.find('span', itemprop='ratingValue').text

    return {'title': title, 'rating': rating}

# Обработчик команды /list
@bot.message_handler(commands=['list'])
def list_saved_anime(message):
    if saved_anime:
        anime_list = "\n".join([f"Название: {anime['title']}\nРейтинг: {anime['rating']}" for anime in saved_anime])
        bot.send_message(message.chat.id, "Список сохраненных аниме:\n" + anime_list)
    else:
        bot.send_message(message.chat.id, "Список сохраненных аниме пуст.")

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith('save_anime_'))
def save_anime_callback(call):
    anime_link = call.data.split('_')[2]
    anime = get_anime_by_link(anime_link)

    if anime:
        saved_anime.append(anime)
        bot.send_message(call.message.chat.id, "Аниме успешно сохранено!")
    else:
        bot.send_message(call.message.chat.id, "Не удалось сохранить аниме. Проверьте правильность введенной ссылки.")

# Запуск бота
bot.polling()
