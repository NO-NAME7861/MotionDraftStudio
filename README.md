# YouTube Automation — Daily Episode Uploader

Roz (11:00 PM PKT) automatically ek episode generate hoti hai aur aapke channel **@MotionDraftStudio** par upload ho jati hai:

```
LLM (OpenRouter free) → Chinese-animation-style images (Pollinations, free)
→ edge-tts English female voice (free) → subtitles + Ken Burns video (ffmpeg)
→ YouTube upload (YouTube Data API v3) → Google Drive backup
```

Koi video editing nahi, koi upload nahi — 100% automatic. Cost: **$0/month** (GitHub Actions 2000 free min).

---

## Pehle ek baar yeh setup karein (~20 minutes)

### STEP 1 — Google Cloud project (ye zaroori hai)

1. [console.cloud.google.com](https://console.cloud.google.com) → उसी Google account se sign in karein jis se **MotionDraftStudio** channel chalta hai (naya Gmail **nahi** banana)
2. Top bar → **Select project** → **New Project** → naam: `YouTubeAutomation` → Create

### STEP 2 — APIs enable karein

1. Menu (☰) → **APIs & Services** → **Library**
2. Search: **YouTube Data API v3** → Enable
3. Search: **Google Drive API** → Enable

### STEP 3 — OAuth consent screen (sabse important!)

1. **APIs & Services** → **OAuth consent screen**
2. User Type: **External** → Create
3. Fill karein:
   - App name: `YouTubeAutomation`
   - User support email: aapka email
   - Developer contact: aapka email
4. **Scopes** → Add: `youtube.upload`, `drive.file`, `youtube` → Save & Continue
5. **Test users** → **Add Users** → apna Gmail add karein → Save
6. ⚠️ **SCORE-FINAL STEP — Publish App**: consent screen page par wapas jaayein → **"Publish app"** daba dein → Confirm.
   (Agar app Testing mode mein rahegi to aapka refresh token **har 7 din baad expire** ho jayega aur daily upload band ho jayega!)

### STEP 4 — OAuth Client ID (Desktop)

1. **Credentials** → **+ Create Credentials** → **OAuth client ID**
2. Application type: **Desktop app** → Name: `uploader` → Create
3. **Download JSON** → file ka naam badal kar **`client_secret.json`** kar dein
4. Us file ko is folder mein rakh dein: `youtube-automation\client_secret.json`

### STEP 5 — Local token (ek baar, browser mein allow)

PowerShell:
```powershell
cd "C:\Users\Park-Edge\Documents\Default Project\youtube-automation"
python -m pip install -r requirements.txt
python get_token.py
```
Browser khulega → Google account select → **Allow** → folder mein **token.json** ban jayega.
(Agar aapka PC abhi "Fully Automatic" nahi chalega — token GitHub par jaayega, PC nahi chalta.)

### STEP 6 — GitHub repo + secrets

1. GitHub par naya repo banayein (ya `gh` se — main aapke liye banwa sakta hoon):
   `NO-NAME7861/youtube-automation` — **Private** rakhein (token.json hidden रहता hai; code public bhi ho sakta hai, secrets hamesha alag hote hain)
2. Secrets add karein — 3 commands:
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

### STEP 7 — Pehla run (PRIVATE se test karein!)

1. GitHub repo → **Actions** tab → **Daily Episode Upload** → **Run workflow**
2. `privacy: private` chun ke → **Run workflow**
3. ~20-60 min (LLM + 12 images + TTS + render + upload)
4. Notifications/logs dekhen — fail ho to error read karke batayein
5. Jab sab theek chal rahe ho → same workflow public chalayein

Iske baad roz **raat 11 PM PKT** khud hota rahega. Manual test ke liye: Actions → Run workflow.

---

## Customize kaise karein

| Cheez | Kaise |
|---|---|
| Narration voice | `vars.TTS_VOICE`: `en-US-JennyNeural` (US female), `hi-IN-SwaraNeural` (Hindi), `ur-PK-UzmaNeural` (Urdu) |
| LLM model | `vars.OPENROUTER_MODEL`: default DeepSeek free; alternatives: `qwen/qwen-2.5-72b-instruct:free`, `google/gemini-2.0-flash-exp:free` |
| Daily time | `.github/workflows/daily.yml` → cron `0 18 * * *` (UTC) badlein |
| Episode list | `episodes.csv` mein 30 topics hain; aap apna add/edit kar sakte hain |
| Categories | `generate_episode.py` mein `categoryId` (24=Entertainment, 27=Education, 22=People) |
| Image count/resolution | `N_IMAGES` (12) aur `W,H` (1024x576) — CPU free tier ke liye ye barabar hai |

## Important policies & realities

1. **Altered content disclosure**: YouTube bolta hai realistic synthetic content disclose karna zaroori hai. Video description mein pehle se disclaimer hai; **pehli upload ke baad Studio mein "altered or synthetic content" toggle check karein** (API se nahi ho sakta — manual ek baar ka kaam).
2. **Copyright**: Jo titles use ho rahe hain wo original archetypes hain (in searches/guides mein common generic retellings). Agar aap actual copyrighted anime/novel footage use karein to video remove/strike ho sakta hai — **is pipeline mein sirf AI-generated original visuals hain, sab safe hai.**
3. **Fact-check**: AI hamisha to galat ho sakta hai — ek baar kabhi-kabhi upload HAW dekhein (Studio analytics + comment) taake quality drop na honi lage.
4. **Quota**: YouTube API daily quota ~10,000 units; ek upload = 1,600 units → ~6 uploads/day possible; 1/day kafi hai.
5. **Token expiry**: Agar "refresh token expired" error aaye to app Testing mode mein hai → Step 3.6 "Publish app" karein, phir get_token.py dobara chalayein.

## Files

- `generate_episode.py` — main pipeline
- `get_token.py`      — one-time browser OAuth → token.json
- `episodes.csv`      — 30 episode briefs (apne topics add karein)
- `state/episodes.json` — kaunsa episode next hai (GitHub Actions khud commit karti hai)
- `.github/workflows/daily.yml` — daily 11 PM PKT cron + manual run

## Troubleshooting

| Problem | Solution |
|---|---|
| LLM returns no JSON | OPENROUTER_MODEL badlein; logs mein `Raw reply` check karein |
| Images fail | Pollinations rate-limited; workflow re-run karein |
| `token.json missing` | Step 5 dobara chalayein; token.json repo mein **kabhi commit na karein** (gitignore dekhein) |
| `invalid_grant` | App Testing mode mein hai → Publish app → token dobara banayein |
| Upload forbidden | Channel active v1 ho? YouTube API disabled? Step 2 check karein |
| Video blur/glitch | Resolution badlein ya `-crf 26` kam karein (24/22 = better quality) |

.gitignore is already configured to ignore token.json, client_secret*.json, work/, token.json.
