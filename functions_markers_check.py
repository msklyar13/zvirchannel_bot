import functions_processing
import functions_linguistics
import message_extraction
import pandas as pd
import re
import io

# З файлу csv вивантажуємо маркери
markers = 'markers.csv'
mdf = pd.read_csv(markers)
# Створюємо словник для маркерів
grey_markers = {}
# Зберігаємо параметри до словника
for parameter in mdf['parameter'].unique():
    grey_markers[parameter] = [
        mdf.loc[mdf['parameter'] == parameter, 'grey_min'].values[0], 
        mdf.loc[mdf['parameter'] == parameter, 'grey_max'].values[0]
    ]


def apply_markers(n, grey_markers):
    if not pd.isna(grey_markers[0]) and n <= grey_markers[0]:
        return ' ⚠️'
    if not pd.isna(grey_markers[1]) and n >= grey_markers[1]:
        return ' ⚠️'
    else:
      return ' '


def metrics_print(metric, subsamples_channel, calculate_func, text, parameter_metric):
    x_ave = functions_processing.calculate_stats(metric, subsamples_channel, calculate_func)
    return f'{text} {x_ave} {apply_markers(x_ave, grey_markers[parameter_metric])}'


def check_channel_against_metrics(channel_csv):
    channel_name = re.search(r'.+/(.+)\.csv', channel_csv).group(1)

    dict_channel_raw = functions_processing.form_dict_raw([channel_csv])
    dict_channel_preprocessed = functions_processing.form_dict_preprocessed(dict_channel_raw)

    subsamples_channel_raw = functions_processing.form_subsamples(dict_channel_raw)
    subsamples_channel_preprocessed = functions_processing.form_subsamples(dict_channel_preprocessed)

    output = io.StringIO() # щоб виводити результати перевірки з функції в бота
    print(f'''<b><u>ПОКАЗНИКИ НА 5000 СЛІВ У КАНАЛІ {channel_name}.</u></b>''', file=output)
    print('\n<b>Покликання:</b>', file=output)
    print(metrics_print('Internal', subsamples_channel_raw, functions_linguistics.calculate_links, ' >  внутрішні:', 'int_links'), file=output)
    print(metrics_print('External', subsamples_channel_raw, functions_linguistics.calculate_links, ' >  зовнішні:', 'ext_links'), file=output)

    print('\n<b>Емодзі:</b>', file=output)
    print(metrics_print('emoji', subsamples_channel_raw, functions_linguistics.calculate_emojis, ' > ', 'emoji'), file=output)

    print('\n<b>Слова у верхньому регістрі:</b>', file=output)
    print(metrics_print('capitalized', subsamples_channel_raw, functions_linguistics.calculate_capitalization, ' > ', 'capitalization'), file=output)

    print('\n<b>Власні назви:</b>', file=output)
    print(metrics_print('PROPN', subsamples_channel_preprocessed, functions_linguistics.calculate_pos, ' > ', 'propn'), file=output)

    print('\n<b>Частини мови:</b>', file=output)
    print(metrics_print('ADJ', subsamples_channel_preprocessed, functions_linguistics.calculate_pos, ' >  прикметники:', 'adj'), file=output)
    print(metrics_print('Cmp', subsamples_channel_preprocessed, functions_linguistics.calculate_comparative_superlative, '    – вищий ступінь порівняння:', 'comp'), file=output)
    print(metrics_print('Sup', subsamples_channel_preprocessed, functions_linguistics.calculate_comparative_superlative, '    – найвищий ступінь порівняння:', 'sup'), file=output)
    print(metrics_print('ADV', subsamples_channel_preprocessed, functions_linguistics.calculate_pos, ' >  прислівники:', 'adv'), file=output)
    print(metrics_print('NUM', subsamples_channel_preprocessed, functions_linguistics.calculate_pos, ' >  числівники:', 'num'), file=output)
    print(metrics_print('PRON', subsamples_channel_preprocessed, functions_linguistics.calculate_pos, ' >  займенники:', 'pron'), file=output)
    print(metrics_print(1, subsamples_channel_preprocessed, functions_linguistics.calculate_pers_pronouns, '     –  1 особа:', 'pers1'), file=output)
    print(metrics_print(2, subsamples_channel_preprocessed, functions_linguistics.calculate_pers_pronouns, '     –  2 особа:', 'pers2'), file=output)
    print(metrics_print(3, subsamples_channel_preprocessed, functions_linguistics.calculate_pers_pronouns, '     –  3 особа:', 'pers3'), file=output)
    print(metrics_print('PART', subsamples_channel_preprocessed, functions_linguistics.calculate_pos, ' >  частки:', 'part'), file=output)

    print('''\n\nМатеріали опрацьовано.
<b>Зверніть увагу:</b> наявність позначки ⚠️ біля одного чи кількох критеріїв перевірки є маркером ненадійності каналу.

Щоб дізнатись більше про критерії, натисніть на кнопку «<b>Критерії перевірки ✅</b>» в меню бота.''', file=output)
    
    output.seek(0)
    return output.read()