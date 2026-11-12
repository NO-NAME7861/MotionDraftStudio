from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    r'C:\Users\Park-Edge\Documents\Default Project\youtube-automation\token.json',
    ['https://www.googleapis.com/auth/youtube.upload',
     'https://www.googleapis.com/auth/youtube'])
yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)

desc = (
    "Motion Draft Studio — Bringing Chinese animation & Japanese 2D recap stories to life with AI voiceover and cinematic narration.\n\n"
    "Every episode retells legendary cultivation and fantasy tales with honest English narration, "
    "paired with original visuals that capture the spirit of each story.\n\n"
    "One moral per episode — because great stories don't just entertain, they remind us how to live.\n\n"
    "New episodes daily."
)

try:
    r = yt.channels().update(part='brandingSettings', body={
        'id': 'UCzU1cvWNsJJrbbp6HMkxIOg',
        'brandingSettings': {'channel': {
            'title': 'Motion Draft Studio',
            'description': desc,
            'defaultLanguage': 'en',
            'country': 'PK',
            'keywords': 'chinese animation recap, japanese anime recap, novel recap, cultivation animation, animated story, cultivation recap, anime recap english, motion draft studio, chinese fantasy recap, donghua recap, cultivation novel',
        }}
    }).execute()
    print('updated title:', r['brandingSettings']['channel'].get('title'))
    print('desc:', r['brandingSettings']['channel'].get('description')[:200])
    print('keywords:', r['brandingSettings']['channel'].get('keywords'))
except Exception as e:
    print('FAIL:', e)
