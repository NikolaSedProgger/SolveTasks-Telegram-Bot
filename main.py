import os

from openai_funcs import ask_short_question, get_text_image
from dotenv import load_dotenv

from revChatGPT.V1 import Chatbot
from telebot import *

load_dotenv()

GPT_TOKEN = os.environ.get('GPT_TOKEN')
TG_TOKEN = os.environ.get('TG_TOKEN')
config = {
    "session_token": GPT_TOKEN
}
TGBOT = telebot.TeleBot(TG_TOKEN)
GPTBOT = Chatbot(config=config)


def get_gpt_answer(question):
    prev_text = ""
    gpt_answer = "- "
    for data in GPTBOT.ask(f'Реши задачу: {question}'):
        gpt_answer = gpt_answer + data["message"][len(prev_text):]
        prev_text = data["message"]
    return gpt_answer


def format_message(message):
    formatted_message = message.replace('$', '').replace('sqrt', '√')
    return formatted_message


@TGBOT.message_handler(commands=['help', 'start'])
def send_help_message(message):
    if 'help' or 'start' in message.text:
        help_message = """ﾟ✧ Привет! Я SolveTasks_NSbot (⌒‿⌒)ﾉﾟ✧
            Можешь задать любые интересующие тебя вопросы, решить задачку по физике или математике
            Или же помочь приготовить наггетсы. Если мой ответ был недостаточно полным, 
            То добавь слово "Подробно" в своё сообщение, и я постараюсь дать более развёрнутый ответ. ﾟ✧
            """
        TGBOT.send_message(message.from_user.id, help_message)


@TGBOT.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text:
        print(f'{message.from_user.first_name, message.from_user.last_name} отправил сообщение: {message.text}')
        bot_message = TGBOT.send_message(message.from_user.id, 'Думаю...')
        answer = format_message(ask_short_question(message.text))
        TGBOT.edit_message_text(chat_id=message.from_user.id, message_id=bot_message.message_id, text=answer)
    elif 'Подробн' or 'подробн' in message.text:
        print(f'{message.from_user.first_name, message.from_user.last_name} отправил сообщение: {message.text}')
        bot_message = TGBOT.send_message(message.from_user.id, 'Думаю...')
        prev_text = ""
        gpt_answer = "- "
        for data in GPTBOT.ask(message.text):
            gpt_answer = gpt_answer + data["message"][len(prev_text):]
            prev_text = data["message"]
        answer = format_message(gpt_answer)
        TGBOT.edit_message_text(chat_id=message.from_user.id, message_id=bot_message.message_id, text=answer)


@TGBOT.message_handler(content_types=['photo'])
def get_photo(message):
    print(f'{message.from_user.first_name, message.from_user.last_name} отправил фотографию')

    file_id = message.photo[-1].file_id
    file_info = TGBOT.get_file(file_id)
    downloaded_file = TGBOT.download_file(file_info.file_path)
    with open(f"image.png", 'wb') as new_file:
        new_file.write(downloaded_file)

    image_text = get_text_image('rus')
    TGBOT.send_message(message.from_user.id,
                       f'Текст на картинке: {image_text}. Если что-то неверно, переотправьте картинку в более хорошем качестве.')

    bot_message = TGBOT.send_message(message.from_user.id, 'Думаю...')
    short_answer = TGBOT.edit_message_text(chat_id=message.from_user.id,
                                           message_id=bot_message.message_id,
                                           text=f'Краткий ответ: {ask_short_question(image_text)}\n данный ответ может быть неверным, поэтому дождитесь полного решения...')

    gpt_answer = get_gpt_answer(image_text)
    TGBOT.edit_message_text(chat_id=message.from_user.id, message_id=short_answer.message_id, text=gpt_answer)


if __name__ == '__main__':
    print('Бот запущен')
    TGBOT.polling(non_stop=True, interval=0)
