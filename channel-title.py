from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    r'C:\Users\Park-Edge\Documents\Default Project\youtube-automation\token.json',
    ['https://www.googleapis.com/auth/youtube.upload',
     'https://www.googleapis.com/auth/youtube'])
yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)

for title in ['Motion Draft Studio', 'Motion-Draft Studio', 'Motion Draft Studio (Official)']:
    try:
        r = yt.channels().update(part='brandingSettings', body={
            'id': 'UCzU1cvWNsJJrbbp6HMkxIOg',
            'brandingSettings': {'channel': {'title': title}}
        }).execute()
        new_title = r.get('brandingSettings', {}).get('channel', {}).get('title')
        print(f'tried "{title}" -> returned "{new_title}"')
    except Exception as e:
        print(f'"{title}": FAIL: {e}')
