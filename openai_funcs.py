import os

from dotenv import load_dotenv
import openai
from PIL import Image
import pytesseract

load_dotenv()

openai.organization = os.environ.get('OPENAI_ORG')
openai.api_key = os.environ.get('OPENAI_API_KEY')
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'


def get_text_image(lang):
    image = Image.open('image.png')

    custom_config = r'--oem 3 --psm 6'
    string = pytesseract.image_to_string(image, config=custom_config, lang=lang)
    os.remove('image.png')
    return string


def create_message(question):
    messages = {}
    messages.update({"role": "user", "content": question})
    return messages


def ask_short_question(question):
    messages = [{"role": "system", "content": "Ты хороший специалист и помощник."}, create_message(question)]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']
