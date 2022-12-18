from os.path import exists

import requests
from bs4 import BeautifulSoup
import os
import json

# Replace YOUR_API_KEY with your actual API key
api_key = '35f9736be042660d1010'
translations = {}

# Initialize an empty list to store the file names
file_names = []
if exists("translations.json"):
    with open("translations.json", "r") as file:
        translations = json.load(file)

# Walk through the directory tree and get the names of all files
path = "files"
for root, dirs, files in os.walk(path):
    for file in files:
        file_names.append(os.path.join(root, file))

# Print the file names
def filterTags(texts):
    filtered_arr = list(filter(lambda x: '"' not in x, texts))
    filtered_arr = list(filter(lambda x: '&' not in x, filtered_arr))
    filtered_arr = list(filter(lambda x: '×' not in x, filtered_arr))
    filtered_arr = list(filter(lambda x: "'" not in x, filtered_arr))
    filtered_arr = list(filter(lambda x: "..." not in x, filtered_arr))
    filtered_arr = list(filter(lambda x: "#" not in x, filtered_arr))
    filtered_arr = list(filter(lambda x: ">" not in x, filtered_arr))

    filtered_arr = list(filter(None, filtered_arr))
    filtered_arr = list(filter(bool, filtered_arr))
    filtered_arr = list(filter(len, filtered_arr))
    filtered_arr = list(filter(lambda item: item, filtered_arr))
    filtered_arr = list(filter(lambda x: "Dashboard" not in x, filtered_arr))
    filtered_arr = list(filter(lambda x: "dashboard" not in x, filtered_arr))

    return filtered_arr

for filename in file_names:
    # Load the HTML file
    with open(filename, "r") as file:
        html = file.read()

    # Parse the HTML file
    soup = BeautifulSoup(html, "html.parser")

    # Tags to find
    tags = [
        "h1",
        "li",
        "h3",
        "label",
        "option",
        "th",
        "button",
        "small"
    ]

    # Set the source and target languages
    src_lang = 'tr'
    tgt_lang = 'en'

    # Set the API endpoint and headers
    endpoint = 'https://api.mymemory.translated.net/get'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # Extract the text from the elements you want to translate
    texts = [element.text for element in soup.find_all(tags)]

    # filter tags
    texts = filterTags(texts)

    translated_texts = []
    for text in texts:
        text = text.strip()
        if text == 'Dashboard':
            print("It has only white spaces or Dashboard passing api call")
            continue
        print("text: " + text)

        # Set the request data
        data = {
            'q': text.lower(),
            'langpair': f"{src_lang}|{tgt_lang}",
            'key': api_key
        }

        savedTranslation = translations.get(text.lower())

        translation = savedTranslation

        if savedTranslation is None:
            print("make api call is not exist on cache")
            # Make the request
            response = requests.post(endpoint, headers=headers, data=data)
            # Extract the translated text from the response
            translation = response.json()['responseData']['translatedText'].capitalize()

            translations.setdefault(text.lower(), translation.lower())

        print("translation: " + translation)

        # Replace the original text with the translated text
        translated_texts.append(translation)

    for element, translated_text in zip(soup.find_all(tags), translated_texts):
        element.string = translated_text.capitalize()

    # Extract the path and the file name
    path, file_name = os.path.split(filename)

    translated_path = "files-translated/" + path + "/"

    if not os.path.exists(translated_path):
        os.makedirs(translated_path)

    # Save the modified HTML file

    if exists(translated_path + file_name):
        os.remove(translated_path + file_name)
    with open(translated_path + file_name, "x", encoding="utf-8") as file:
        file.write(
            str(soup).replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("&amp;&amp;", "&&")
        )

    if exists("translations.json"):
        os.remove("translations.json")
    with open("translations.json", "w", encoding="utf-8") as file:
        json.dump(translations, file)
