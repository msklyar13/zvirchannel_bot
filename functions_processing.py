import functions_linguistics
import csv
import pandas as pd
import re
import emoji
import math


def form_dict_raw(file_list):
    dict_raw = {}
    for file in file_list:
        channel_name = file.split('/')[-1][:3]  # Визначаємо назви ключів
        df = pd.read_csv(file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        for month in range(1, 5):  # Розсортовуємо вибірки з каналів помісячно (01-04 місяць 2024) 
            key_base = f"{channel_name}{str(month).zfill(2)}"
            monthly_df = df[df['timestamp'].dt.month == month]
            monthly_text = ' '.join(monthly_df['text'])

            # Якщо текст за місяць відсутній -- видаляємо ключ і значення
            if not monthly_text.strip():
                continue

            # Розділяємо помісячні тексти на 4 рівні підвибірки (виходять підвибірки від 7000 слів до 15000)
            words = monthly_text.split()
            avg_length = len(words) // 4
            split_texts = [' '.join(words[i * avg_length: (i + 1) * avg_length]) for i in range(4)]
            
            # До ключів підвибірок додаємо ідентифікатори (_01, _02, _03, _04)
            if len(words) % 4 != 0:
                split_texts[-1] = ' '.join(words[3 * avg_length:])

            # Задаємо назви ключів підвибірок
            for i, part_text in enumerate(split_texts, start=1):
                key = f"{key_base}_{i}"
                dict_raw[key] = part_text
                
    return dict_raw


def form_dict_preprocessed(dict_raw):
    dict_preprocessed = {}
    for subsample in dict_raw:
        text = ' '.join(dict_raw[subsample].split(' ')[:7000]) # Обмежуємо об'єм інформації до опрацювання, щоб зменшити навантаження
        dict_preprocessed[subsample] = functions_linguistics.preprocess_text(text)
    return dict_preprocessed


def form_subsamples(sample_dict): # Урізає значення ключів до 5000 слів кожен (підвибірка)
    subsamples_dict = {}
    for subsample in sample_dict:
        text = sample_dict[subsample]
        subsamples_dict[subsample] = ' '.join(text.split(' ')[:5000])
    return subsamples_dict


def calculate_stats(metric, subsamples_dict, calculation_function):
    result_data = {}
    for key, text in subsamples_dict.items():
        counts = calculation_function(text)
        result_data[key] = counts
    
    x_i_counts = {}
    for key, counts in result_data.items():
        if metric in counts:
            count = counts[metric]
            if count in x_i_counts:
                x_i_counts[count] += 1
            else:
                x_i_counts[count] = 1
    
    x_i = list(x_i_counts.keys())
    n_i = list(x_i_counts.values())
    
    if sum(n_i) == 0:
        return pd.DataFrame(), [f"Прикладів для '{metric}' не знайдено."]
    
    x_i_ni = [xi * ni for xi, ni in zip(x_i, n_i)]
    x_ave = round(sum(x_i_ni) / sum(n_i), 2)

    return x_ave