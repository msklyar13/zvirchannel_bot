import asyncio
from telethon.sync import TelegramClient
import pandas as pd
import re
from datetime import datetime
from pytz import timezone

api_id = ...
api_hash = '...'
username = '...'

client = TelegramClient(username, api_id, api_hash)

async def extract_messages(channel_link):
    await client.start()

    local_tz = timezone('Europe/Kiev')
    channel = await client.get_entity(channel_link)

    start_period = datetime(2024, 1, 1).replace(tzinfo=timezone('UTC')).astimezone(local_tz)
    end_period = datetime(2024, 5, 1).replace(tzinfo=timezone('UTC')).astimezone(local_tz)

    data = []
    token_count = 0

    async for message in client.iter_messages(channel, offset_date=end_period, reverse=False):
        if message.date.astimezone(local_tz) < start_period:
            break

        if message.message:
            tokens = message.message.split()
            token_count += len(tokens)

            data.append({
                'timestamp': message.date.astimezone(local_tz).strftime('%Y-%m-%d %H:%M:%S'),
                'text': message.message
            })

    df = pd.DataFrame(data)

    # Визначаємо назву csv файлу з введеного користувачем покликання
    if channel_link.startswith('http') or channel_link.startswith('t.me'):
        channel_name = re.search(r'.+/(.+)', channel_link).group(1)
    else:
        channel_name = channel_link

    csv_filename = f'{channel_name}.csv'
    df.to_csv(csv_filename, index=False)
    return csv_filename  # повертаємо покликання на файл у системі


def get_messages(channel_link):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    messages = loop.run_until_complete(extract_messages(channel_link))
    return messages

