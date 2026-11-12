from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    r'C:\Users\Park-Edge\Documents\Default Project\youtube-automation\token.json',
    ['https://www.googleapis.com/auth/youtube.upload',
     'https://www.googleapis.com/auth/youtube'])
yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)

# 1. Channel snippet/status
ch = yt.channels().list(part='snippet,status,brandingSettings,contentDetails', mine=True).execute()['items'][0]
print('=== CHANNEL ===')
print('Title        :', repr(ch['snippet']['title']))
print('Custom URL   :', ch['snippet'].get('customUrl'))
print('Description  :', repr(ch['snippet'].get('description', ''))[:150])
print('Privacy      :', ch['status']['privacyStatus'])
print('LongUploads  :', ch['status'].get('longUploadsStatus'))
print('Linked       :', ch['status'].get('isLinked'))
print('Monetized    :', ch['status'].get('isChannelMonetizationEnabled'))
print('Default lang :', ch['snippet'].get('defaultLanguage'))
print('Country      :', ch['snippet'].get('country'))

# 2. All uploads (chronological newest first)
up = ch['contentDetails']['relatedPlaylists']['uploads']
items = yt.playlistItems().list(part='snippet,status', playlistId=up, maxResults=50).execute()
print('\n=== UPLOADS (%d items) ===' % len(items.get('items', [])))
for it in items.get('items', []):
    s = it['snippet']
    vid = s['resourceId']['videoId']
    vresp = yt.videos().list(part='contentDetails,status', id=vid).execute()
    if not vresp.get('items'):
        title = s.get('title', '?').encode('ascii', 'replace').decode()[:55]
        print(f'  {s["publishedAt"][:10]} | ----   | DELETED | {vid} | {title}')
        continue
    v = vresp['items'][0]
    dur = v['contentDetails']['duration']
    priv = v['status']['privacyStatus']
    rm = v['status'].get('uploadStatus')
    title = s.get('title', '?').encode('ascii', 'replace').decode()[:55]
    print(f'  {s["publishedAt"][:10]} | {dur:6s} | {priv:7s} | {vid} | {title}')

# 3. Playlists on channel
plats = yt.playlists().list(part='snippet,contentDetails', mine=True).execute()
print('\n=== PLAYLISTS (%d) ===' % len(plats.get('items', [])))
for p in plats.get('items', []):
    print(' ', p['id'], '|', p['snippet']['title'].encode('ascii', 'replace').decode(), '| count:', p['contentDetails']['itemCount'])
