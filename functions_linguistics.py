import re
import emoji
from collections import Counter
import spacy
nlp = spacy.load('uk_core_news_lg')


def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text).lower()  # Прибираємо пунктуацію, обертаємо всі літери на маленькі
    text = ''.join([i for i in text if not i.isdigit()])  # Прибираємо цифри
    text = ' '.join(text.split())  # Прибираємо зайві пробіли
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Прибираємо покликання
    text = ''.join(char for char in text if char not in emoji.EMOJI_DATA)  # Прибираємо емодзі

    doc = nlp(text) # Лематизуємо текст
    processed_text = ' '.join(token.lemma_ for token in doc if token.lemma_ is not token.is_punct and not token.is_digit)
    return processed_text


def remove_prop_nouns(text):
    doc = nlp(text)
    new_text = []
    for token in doc:
        if token.pos_ != 'PROPN':
            new_text.append(token.text)
    return ' '.join(new_text)


def calculate_links(text):
    links = {}
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)

    internal_links = sum(1 for url in urls if url.startswith('https://t.me/'))
    external_links = len(urls) - internal_links

    links['Internal'] = internal_links
    links['External'] = external_links
    return links


def calculate_emojis(text):
    emoji_list = [char for char in text if char in emoji.EMOJI_DATA]
    emojis = len(emoji_list)
    return {'emoji': emojis}


def calculate_capitalization(text):
    text = remove_prop_nouns(text)
    capitalized_count = sum(1 for word in text.split() if word.isupper())
    return {'capitalized': capitalized_count}


def calculate_pos(text):
    doc = nlp(text)
    pos_counts = Counter([token.pos_ for token in doc if not token.is_space])
    return pos_counts


def calculate_pers_pronouns(text):
    pers_pron_count = {1: 0, 2: 0, 3: 0}
    doc = nlp(text)
    for token in doc:
        if token.pos_ == 'PRON':
            person = token.morph.get('Person')
            if person:
                person_number = int(person[0])
                if person_number in pers_pron_count:
                    pers_pron_count[person_number] += 1
    return pers_pron_count


def calculate_comparative_superlative(text):
    comp_sup_count = {'Cmp': 0, 'Sup': 0}
    doc = nlp(text)
    for token in doc:
        if token.pos_ == 'ADJ':
            degree = token.morph.get('Degree')
            if degree:
                adj_form = degree[0]
                if adj_form in comp_sup_count:
                    comp_sup_count[adj_form] += 1
    return comp_sup_count

