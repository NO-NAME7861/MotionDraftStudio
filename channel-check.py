from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    r'C:\Users\Park-Edge\Documents\Default Project\youtube-automation\token.json',
    ['https://www.googleapis.com/auth/youtube.upload',
     'https://www.googleapis.com/auth/youtube'])
yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)

r = yt.channels().list(part='snippet,brandingSettings,status', mine=True).execute()
c = r['items'][0]
print('Title     :', c['snippet']['title'])
print('customUrl :', c['snippet'].get('customUrl'))
print('country   :', c['snippet'].get('country'))
print('language  :', c['snippet'].get('defaultLanguage'))
print('publishedAt:', c['snippet']['publishedAt'])
print('banner     :', 'set' if c['brandingSettings'].get('image', {}).get('bannerExternalUrl') else 'NOT SET')
print('avatar     :', c['snippet']['thumbnails'])
print('privacy    :', c['status']['privacyStatus'])
print('longUploads:', c['status'].get('longUploadsStatus'))
print('monetized  :', c['status'].get('isChannelMonetizationEnabled'))
print('linked     :', c['status'].get('isLinked'))
print()
print('brandingSettings keys:', list(c['brandingSettings'].get('channel', {}).keys()))
