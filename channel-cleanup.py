from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    r'C:\Users\Park-Edge\Documents\Default Project\youtube-automation\token.json',
    ['https://www.googleapis.com/auth/youtube.upload',
     'https://www.googleapis.com/auth/youtube.force-ssl'])
yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)

# caller videos.deletingvideo requires auth scope youtube.force-ssl which current token doesn't have.
# So just remove the duplicate from playlist via playlistItems.delete? That doesn't delete the video either.
# Actually we can DELETE video via videos.delete() — let's try
try:
    yt.videos().delete(id='rjPUihrPn5g').execute()
    print('deleted duplicate: rjPUihrPn5g (Which is stronger: Mercy or Revenge?)')
except Exception as e:
    print('delete failed:', e)

try:
    yt.playlists().delete(id='PLfE9RY2EzLWE').execute()
    print('deleted empty playlist: PLfE9RY2EzLWE')
except Exception as e:
    print('playlist delete failed (may need force-ssl):', e)
