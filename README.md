# YouTube Automation â€” Daily Episode Uploader

Roz (11:00 PM PKT) automatically ek episode generate hoti hai aur aapke channel **@MotionDraftStudio** par upload ho jati hai:

```
LLM (OpenRouter free) â†’ Chinese-animation-style images (Pollinations, free)
â†’ edge-tts English female voice (free) â†’ subtitles + Ken Burns video (ffmpeg)
â†’ YouTube upload (YouTube Data API v3) â†’ Google Drive backup
```

Koi video editing nahi, koi upload nahi â€” 100% automatic. Cost: **$0/month** (GitHub Actions 2000 free min).

---

## Pehle ek baar yeh setup karein (~20 minutes)

### STEP 1 â€” Google Cloud project (ye zaroori hai)

1. [console.cloud.google.com](https://console.cloud.google.com) â†’ à¤‰à¤¸à¥€ Google account se sign in karein jis se **MotionDraftStudio** channel chalta hai (naya Gmail **nahi** banana)
2. Top bar â†’ **Select project** â†’ **New Project** â†’ naam: `YouTubeAutomation` â†’ Create

### STEP 2 â€” APIs enable karein

1. Menu (â˜°) â†’ **APIs & Services** â†’ **Library**
2. Search: **YouTube Data API v3** â†’ Enable
3. Search: **Google Drive API** â†’ Enable

### STEP 3 â€” OAuth consent screen (sabse important!)

1. **APIs & Services** â†’ **OAuth consent screen**
2. User Type: **External** â†’ Create
3. Fill karein:
   - App name: `YouTubeAutomation`
   - User support email: aapka email
   - Developer contact: aapka email
4. **Scopes** â†’ Add: `youtube.upload`, `drive.file`, `youtube` â†’ Save & Continue
5. **Test users** â†’ **Add Users** â†’ apna Gmail add karein â†’ Save
6. âš ï¸ **SCORE-FINAL STEP â€” Publish App**: consent screen page par wapas jaayein â†’ **"Publish app"** daba dein â†’ Confirm.
   (Agar app Testing mode mein rahegi to aapka refresh token **har 7 din baad expire** ho jayega aur daily upload band ho jayega!)

### STEP 4 â€” OAuth Client ID (Desktop)

1. **Credentials** â†’ **+ Create Credentials** â†’ **OAuth client ID**
2. Application type: **Desktop app** â†’ Name: `uploader` â†’ Create
3. **Download JSON** â†’ file ka naam badal kar **`client_secret.json`** kar dein
4. Us file ko is folder mein rakh dein: `youtube-automation\client_secret.json`

### STEP 5 â€” Local token (ek baar, browser mein allow)

PowerShell:
```powershell
cd "C:\Users\Park-Edge\Documents\Default Project\youtube-automation"
python -m pip install -r requirements.txt
python get_token.py
```
Browser khulega â†’ Google account select â†’ **Allow** â†’ folder mein **token.json** ban jayega.
(Agar aapka PC abhi "Fully Automatic" nahi chalega â€” token GitHub par jaayega, PC nahi chalta.)

### STEP 6 â€” GitHub repo + secrets

1. GitHub par naya repo banayein (ya `gh` se â€” main aapke liye banwa sakta hoon):
   `NO-NAME7861/youtube-automation` â€” **Private** rakhein (token.json hidden à¤°à¤¹à¤¤à¤¾ hai; code public bhi ho sakta hai, secrets hamesha alag hote hain)
2. Secrets add karein â€” 3 commands:
```powershell
# 1) OpenRouter API key jo aapne banayi (copy/paste mein carefully):
gh secret set OPENROUTER_API_KEY

# 2) token.json ka base64 (uploader credentials):
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$PWD\token.json")) | gh secret set YOUTUBE_TOKEN_JSON

# 3) (Optional) Urdu/Hindi voice:
gh variable set TTS_VOICE --body "en-US-JennyNeural"
```
3. Code push karein:
```powershell
git init
git add .
git commit -m "Initial YouTube automation"
git branch -M main
git remote add origin https://github.com/NO-NAME7861/youtube-automation.git
git push -u origin main
```

### STEP 7 â€” Pehla run (PRIVATE se test karein!)

1. GitHub repo â†’ **Actions** tab â†’ **Daily Episode Upload** â†’ **Run workflow**
2. `privacy: private` chun ke â†’ **Run workflow**
3. ~20-60 min (LLM + 12 images + TTS + render + upload)
4. Notifications/logs dekhen â€” fail ho to error read karke batayein
5. Jab sab theek chal rahe ho â†’ same workflow public chalayein

Iske baad roz **raat 11 PM PKT** khud hota rahega. Manual test ke liye: Actions â†’ Run workflow.

---

## Customize kaise karein

| Cheez | Kaise |
|---|---|
| Narration voice | `vars.TTS_VOICE`: `en-US-JennyNeural` (US female), `hi-IN-SwaraNeural` (Hindi), `ur-PK-UzmaNeural` (Urdu) |
| LLM model | `vars.OPENROUTER_MODEL`: default DeepSeek free; alternatives: `qwen/qwen-2.5-72b-instruct:free`, `google/gemini-2.0-flash-exp:free` |
| Daily time | `.github/workflows/daily.yml` â†’ cron `0 18 * * *` (UTC) badlein |
| Episode list | `episodes.csv` mein 30 topics hain; aap apna add/edit kar sakte hain |
| Categories | `generate_episode.py` mein `categoryId` (24=Entertainment, 27=Education, 22=People) |
| Image count/resolution | `N_IMAGES` (12) aur `W,H` (1024x576) â€” CPU free tier ke liye ye barabar hai |

## Important policies & realities

1. **Altered content disclosure**: YouTube bolta hai realistic synthetic content disclose karna zaroori hai. Video description mein pehle se disclaimer hai; **pehli upload ke baad Studio mein "altered or synthetic content" toggle check karein** (API se nahi ho sakta â€” manual ek baar ka kaam).
2. **Copyright**: Jo titles use ho rahe hain wo original archetypes hain (in searches/guides mein common generic retellings). Agar aap actual copyrighted anime/novel footage use karein to video remove/strike ho sakta hai â€” **is pipeline mein sirf AI-generated original visuals hain, sab safe hai.**
3. **Fact-check**: AI hamisha to galat ho sakta hai â€” ek baar kabhi-kabhi upload HAW dekhein (Studio analytics + comment) taake quality drop na honi lage.
4. **Quota**: YouTube API daily quota ~10,000 units; ek upload = 1,600 units â†’ ~6 uploads/day possible; 1/day kafi hai.
5. **Token expiry**: Agar "refresh token expired" error aaye to app Testing mode mein hai â†’ Step 3.6 "Publish app" karein, phir get_token.py dobara chalayein.

## Files

- `generate_episode.py` â€” main pipeline
- `get_token.py`      â€” one-time browser OAuth â†’ token.json
- `episodes.csv`      â€” 30 episode briefs (apne topics add karein)
- `state/episodes.json` â€” kaunsa episode next hai (GitHub Actions khud commit karti hai)
- `.github/workflows/daily.yml` â€” daily 11 PM PKT cron + manual run

## Troubleshooting

| Problem | Solution |
|---|---|
| LLM returns no JSON | OPENROUTER_MODEL badlein; logs mein `Raw reply` check karein |
| Images fail | Pollinations rate-limited; workflow re-run karein |
| `token.json missing` | Step 5 dobara chalayein; token.json repo mein **kabhi commit na karein** (gitignore dekhein) |
| `invalid_grant` | App Testing mode mein hai â†’ Publish app â†’ token dobara banayein |
| Upload forbidden | Channel active v1 ho? YouTube API disabled? Step 2 check karein |
| Video blur/glitch | Resolution badlein ya `-crf 26` kam karein (24/22 = better quality) |

.gitignore is already configured to ignore token.json, client_secret*.json, work/, token.json.

