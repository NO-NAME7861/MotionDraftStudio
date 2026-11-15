"""
make_mega_video.py - the 2+ HOUR Devanagari-Hindi "Betrayal -> Silent Thriller King" mega recap.
Improved Long Dialogue Mode: 7 part-LLM calls (continuity via beats + previous-part tail),
Hindi (Devanagari) + English mixed narration, hi-IN-SwaraNeural voice, 32 images, BGM.

Runs inside GitHub Actions (mega.yml). Also runnable locally:  python make_mega_video.py
"""
import os, sys, json, subprocess, random, time, urllib.request, urllib.parse, re
from pathlib import Path

ROOT = Path(__file__).parent
WORK = ROOT / "mega-work"
WORK.mkdir(parents=True, exist_ok=True)
OUT  = ROOT / "mega-out"
OUT.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1024, 576, 25
VOICE = "hi-IN-SwaraNeural"
RATE  = "-2%"
N_IMAGES = 32
EPISODE_ID = os.environ.get("MEGA_ID", "M001")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL   = os.environ.get("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")
FALLBACK_MODELS    = [m for m in [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
]]
CF_ID    = os.environ.get("CF_ACCOUNT_ID", "")
CF_TOKEN = os.environ.get("CF_API_TOKEN", "")
TOKEN_PATH = ROOT / "token.json"

# ------------------------------------------------------------------ story
TITLE = "Betrayal Ke Baad Wapas Aaya — Silent Thriller King [Chinese Animation Recap Hindi]"
MORAL = "Betrayal ka jawaab gussa nahi, sabar aur strategy hai — patience is the greatest weapon."

PARTS = [
    {
        "part": 1, "slug": "pratibha",
        "beat": (
            "Azure Heaven Pavilion's most gifted disciple CHEN YIRANG (चेन यिरांग), 19, wins the Celestial Trials, "
            "catches the mentor MASTER QIANMO's (मास्टर कियानमो) secret: the sect hierarchy crushes талант for clan politics. "
            "His fiancée लेयूया seems glowing, his best friend बैतुआन loyal, his elder brother चेन लूहांग jealous. "
            "Set the city BAOLINGHE (बोलिंगहे) with neon crime towers, sect tower, rain, market noise. "
            "Yirang is naive-honest, believes in the system. Show the festival, the banners, the tests. End part 1 with him hearing a whisper: 'The Trials are not what they seem.'"
        ),
    },
    {
        "part": 2, "slug": "vishwasghat",
        "beat": (
            "The Betrayal Night. The final trial on Thunder Crag during the storm. Elder brother Luhang (लूहांग) cuts the rope during the ascension climb; "
            "mentor Qianmo watches and says nothing; best friend बैतुआन holds the gate and refuses to help; fiancée लेयूया runs to the brother's side. "
            "Yirang plummets into the river/cliff, presumed dead. Qianmo orders silence. The sect announces 'a tragic accident'. "
            "Flashbacks of earlier promises make the pain sharper. End: his body broken, he opens his eyes to red lanterns in the rain: the SECOND CITY below."
        ),
    },
    {
        "part": 3, "slug": "chhayayon",
        "beat": (
            "The underworld city Baolinghe. Found by the OBSIDIAN FANG syndicate (ऑब्सीडियन फेंग) and its kingpin KUWEN DAMUN (कुवेन दामून), a dying crime emperor, "
            "who runs a shadow auction: information, blackmail, disappeared men. Yirang apprenticeship: ledgers, ciphers, surveillance, silence, interrogation, tasting fear. "
            "He gains back his body + mind, sees how clean the sect looks from outside vs the rot beneath. "
            "He finds his own name in an auction record: sold as 'asset #041' by his own sect. He does not rage; he laughs softly - the pivot moment. End: 'अब पूरा खेल मेरे rules पर चलेगा।'"
        ),
    },
    {
        "part": 4, "slug": "badla1",
        "beat": (
            "Part 4 - RETURN and THE BROTHER'S FALL. Under a new face/name, Yirang the Shadow King moves into Baolinghe's elite circles; buys his brother Luhang's debts; engineers his promotion ceremony to blow up on live display "
            "(leaked forged evidence: the rope, the bribed judge, the audio of the storm night). Crowd mood flips. Luhang spends the night in the same cells he put Yirang in. Thriller beats: chase in the rain, a calm negotiation vs a panic, the silent smile, the reveal. "
            "Yirang shows mercy ONLY as strategy: he makes Luhang sign the entire secret ledger rather than kill him. End part 4: brother's hands tremble as he signs."
        ),
    },
    {
        "part": 5, "slug": "master_girvat",
        "beat": (
            "Part 5 - THE MENTOR'S COLLAPSE. Qianmo senses danger, travels to Baolinghe undercover, meets the new 'Shadow King' unknowing of who he is. "
            "Yirang plays chess/cold hospitality: tells him stories of fallen sects. Twist reveal: Qianmo's ownHidden slave-ledger (asset contracts, #041) is presented to the court as 'unknown evidence'. "
            "Qianmo's students turn; the verdict happens at the Pavilion's 900th anniversary ceremony on stage - the mentor bows and never rises again (metaphorically buried: publicly stripped). "
            "Thriller beats: the mask of reverence, the smile, the ledger on a silver plate, the silence in the hall. End: Yirang walks out as the crowd whispers 'Shadow King.'"
        ),
    },
    {
        "part": 6, "slug": "dost_prem",
        "beat": (
            "Part 6 - THE FRIEND AND THE FIANCEE. बैतुआन, the guilt-eaten gatekeeper, is offered a 'ticket out' to exile; he exposes EVERYTHING in exchange. "
            "Fiancée लेयूया comes begging, pretending love; Yirang replays her storm-night words in a recorded auction of memory; she understands she sold him for a seat at the sect table; she is ruined publicly not by violence but by truth. "
            "Yirang offers one chance: confess on court, name everyone. She chooses silence - and he lets the world do the rest. "
            "Beat: the auction hall of truth, the crowd's faces, the soft delivery of the final line: 'मैं जीतने नहीं आया ... मैं पूरा खेल दिखाने आया हूँ।' End: the city empties before his one signal."
        ),
    },
    {
        "part": 7, "slug": "hidden_throne",
        "beat": (
            "Part 7 - THE HIDDEN THRONE AND THE WORLD FLIP. The final reveal: the betrayals were orchestrated by the EMPEROR'S secret cabal 'Hidden Throne' (हिडन थ्रोन) which runs the Pavilion as a beta-test lab for removing inconvenient geniuses. "
            "Yirang, with Obsidian Fang's 200 shadow agents and Qianmo's ledger, doesn't storm any palace - he leaks EVERYTHING simultaneously: every court, every guild, every sect, every ledger page - one night, one hour, one command. "
            "The system collapses not by battle, but by exposure. KUWEN DAMUN dies satisfied in Yirang's arms: 'बेटा, सरकार... अब दुनिया तुम्हारा शहर है।' "
            "Epilogue 2 years later: 'Silent Emperor' legend, shrine streets empty, festivals renamed. End with the moral, slowly, explicitly: betrayal ka jawaab sabar aur strategy hai - gussa nahi. Patience crushes everyone."
        ),
    },
]

DESCRIPTION = (
    "आज की सबसे गहरी कहानी — एक लड़का जिसे भाइयों, मास्टर, दोस्त और हबीब सबने धोखा दिया, वो कभी वापस आया ही नहीं... "
    "बल्कि एक परछाईं बन गया जिसने पूरे सिस्टम को धूल में मिला दिया। Betrayal → Silence → Strategy → Total Domination.\n\n"
    "⚠️ This video features AI-generated visuals and AI narration.\n\n"
    "Moral: Betrayal ka jawaab gussa nahi, sabar aur strategy hai.\n\n"
    "Subscribe for a new recap EVERY DAY: https://www.youtube.com/@MotionDraftStudio\n\n"
    "#HindiAnimationRecap #BetrayalRecap #ChineseAnimationRecapHindi #MotionDraftStudio #ThrillerHindi"
)

TAGS = [
    "hindi recap", "betrayal recap", "chinese animation recap hindi", "thriller recap",
    "motion draft studio", "revenge recap", "shady recap", "recap hindi", "animation recap hindi",
    "xianxia hindi", "डोंघुआ recap", "motivation hindi",
]

IMAGE_PROMPTS = [
    "chinese animation key visual, a 19 year old genius disciple on a mountain trial rope under lightning, red banners, xianxia cel art, cinematic, no text",
    "chinese animation, azure heaven pavilion sect tower above clouds at dusk, dragon banners, xianxia cel art, dramatic lighting, no text",
    "chinese animation, a festival in an ancient Chinese city at night with neon lanterns, bustling market, cel art, no text",
    "chinese animation, close up of a letter with red seal wax, blood rain lighting, cinematic macro, no text",
    "chinese animation, a storm on Thunder Crag, a disciple cutting a rope above a ravine, lightning, dramatic cel art, no text",
    "chinese animation, a body falling against a stormy sky, one broken arm reaching upward, cinematic, no text",
    "chinese animation, a boy wet in river grass under red lanterns opening his eyes, rain, cel art, cinematic, no text",
    "chinese animation, an underworld auction hall with shaded booths and a big screen showing files, candles, no people, no text",
    "chinese animation, a dying crime kingpin in an obsidian armor chair with a ledger in hand, smoke, cel art, no text",
    "chinese animation, a young man training in an underground dojo with knives and cipher books, flickering light, no text",
    "chinese animation, a grand banquet where an elder brother toasts a crowd, wine spills in slow motion, no text",
    "chinese animation, a city skyline with neon crime towers and sect towers at night, rain, cinematic color, no text",
    "chinese animation, a silent man in a long black coat walking through a wet crowd, everyone turning to look, cel art, no text",
    "chinese animation, a promotion ceremony stage with a huge banner and spotlights, one boy standing perfectly still, cinematic, no text",
    "chinese animation, a brother in shackles in a cell with blood-red light, sister screaming above, cel art, no text",
    "chinese animation, a silver plate with an old black leather ledger on it held by a gloved hand, courtroom candles, no text",
    "chinese animation, an old mentor's face crumbling as students turn around in a great hall, cel art, cinematic, no text",
    "chinese animation, an auction hall where a beautiful woman sells a memory coin, candle shadows on the crowd, no text",
    "chinese animation, a wedding table set for two with one seat burning to ash, cel art, cinematic, no text",
    "chinese animation, a map of a city with red threads connecting towers like a conspiracy board, candle light, no text",
    "chinese animation, a hidden throne room under the sect with chains and masks, fog, dark gold, no text",
    "chinese animation, hundreds of papers flying out of a palace as every hologram goes red at once, cel art, no text",
    "chinese animation, a dying kingpin at peace by a window overlooking neon city rain, a calm young man at his side, no text",
    "chinese animation, an epilogue street where a shrine flower is left for a silent legend, festival lanterns, cel art, no text",
    "chinese animation, a silhouette on a rooftop above a glowing burning throne, lightning behind, cinematic cel art, no text",
    "chinese animation, the same prayer bead broken at the trial now hanging in a shadow king's study, macro, no text",
    "chinese animation, a young man teaching a boy the same mountain climb, dawn, hope, cel art, no text",
    "chinese animation, an empty throne with a single red lantern burning, the storm long gone, cel art, no text",
    "chinese animation, whispers in a rainy market where papers spread a legend, no text",
    "chinese animation, a final wide skyline where two towers bow to each other's lights, calm, cinematic, no text",
    "chinese animation, the word 'patience' as a glowing mantra behind closed eyes, dreamlike cel art, no text",
    "chinese animation, black coat silhouette walking away into market crowd, lanterns rise, no text",
]

THUMB_PROMPT = (
    "youtube thumbnail, cinematic chinese animation style, close-up of a young man soaked in rain with one glowing amber eye, "
    "broken prayer bead in his fist, red lantern light from below, world-ending mood, dramatic lighting, no text"
)

PART_PROMPT_TMPL = """Write भाग {part} of 7 of the Devanagari-Hindi mega recap script.

CONTEXT OF THE FULL STORY (do not repeat previous parts; continue exactly):
Hero: CHEN YIRANG (चेन यिरांग), 19-year-old genius, betrayed on the mountain trial by elder brother चेन लूहांग, mentor मास्टर कियानमो, friend बैतुआन, fiancée लेयूया. Plunge, presumed dead. Rescued by Obsidian Fang syndicate under KUWEN DAMUN (कुवेन दामून). Trained as a shadow operative. Returns to Baolinghe as the silent "Shadow King". He methodically dismantles each betrayer with cold precision, then leaks the "Hidden Throne" cabal that runs the sect, bringing the entire system down by exposure, not war. Moral at the very end of part 7 only.

THIS PART ({part} of 7) - {slug}:
{beat}

Requirements:
- DEEP narration in Devanagari Hindi mixed with ENGLISH technical words (like 'betrayal', 'strategy', 'hidden ledger', 'auction', 'system') - exactly the Hindi-English mix Indians love.
- NEVER use double quotes or backslashes inside the narration text. Use Hindi quotes 「 」 or single quotes ' for dialogue instead - keep valid JSON.
- Target 2100-2400 words. DO NOT write less than 2000 words. Slow pace, heavy suspense.
- Natural spoken style for one voice. Long, flowing sentences mixed with punchy short ones.
- Include dialogue (use Hindi quote style), inner monologue, sensory detail (rain, lantern light, heartbeat, paper, metal).
- Keep tension of a thriller: silence, glances, recorded evidence, courtroom verdicts, rain, crowd pulse.
- End part {part} on a cliffhanger hook (unless part 7 - then end with the explicit moral).
- No headings, no notes, no markdown. Just narration text.

Return ONLY JSON: {{"part": {part}, "narration": "..."}}"""


# ------------------------------------------------------------------ helpers
def log(*a):
    print(f"[{__import__('datetime').datetime.now():%H:%M:%S}]", *a, flush=True)

def extract_json(text):
    """Robustly pull the first JSON object out of an LLM reply (Devanagari-safe)."""
    decoder = json.JSONDecoder(strict=False)
    m = re.search(r"\{", text)
    if not m:
        raise RuntimeError("no JSON in reply: " + text[:1500])
    start = m.start()
    payload = text[start:]
    # 1) plain raw_decode (handles trailing garbage)
    try:
        obj, _ = decoder.raw_decode(payload)
        return obj
    except Exception:
        pass
    # 2) escape lone backslashes (LLMs love illegal \ sequences in Hindi prose)
    fixed = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', payload)
    try:
        obj, _ = decoder.raw_decode(fixed)
        return obj
    except Exception:
        pass
    # 3) first { ... last } sliced, strict=False, escape-fixed
    end = payload.rfind("}")
    if end > 0:
        return json.loads(fixed[: fixed.rfind("}") + 1], strict=False)
    raise RuntimeError("no JSON parse possible: " + text[:1500])

def _call_llm(model, label, user_prompt):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content":
                       "You are a veteran Hindi YouTube scriptwriter for animation recaps (Hindi-English mix). Reply ONLY with valid JSON, no markdown."},
                      {"role": "user", "content": user_prompt}],
        "temperature": 0.85,
        "max_tokens": 11000,
        "reasoning": {"enabled": False},
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload, method="POST",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                 "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/NO-NAME7861/youtube-automation",
                 "X-Title": "YouTube Automation"})
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read())
    content = resp["choices"][0]["message"]["content"].strip()
    return extract_json(content)

def call_part(part_idx):
    meta = PARTS[part_idx - 1]
    prompt = PART_PROMPT_TMPL.format(part=part_idx, slug=meta["slug"], beat=meta["beat"])
    return _generate(prompt, label=f"part {part_idx}", min_words=1600)

def _generate(prompt, label, min_words=1600):
    models = [OPENROUTER_MODEL] + [m for m in FALLBACK_MODELS if m != OPENROUTER_MODEL]
    for model in models:
        for attempt in range(3):
            try:
                ep = _call_llm(model, label, prompt)
                nar = ep.get("narration", "")
                wc = len(nar.split())
                log(f"{label} via {model}: {wc} words")
                if wc >= min_words:
                    return nar
                log(f"{label} too short, retrying ...")
            except Exception as ex:
                log(f"{label} {model} attempt {attempt+1} failed: {ex}")
                time.sleep(40)
    sys.exit(f"{label} failed on all models")

def cf_image(prompt, dest, seed):
    """CF FLUX schnell -> Pollinations fallback (same as create_shorts)."""
    payload = json.dumps({"prompt": prompt}).encode()
    if CF_ID and CF_TOKEN:
        try:
            req = urllib.request.Request(
                f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                data=payload, method="POST",
                headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.loads(r.read())
            img_b64 = resp.get("result", {}).get("image")
            if img_b64:
                import base64
                Path(dest).write_bytes(base64.b64decode(img_b64))
                log(f"[ok] cf image {Path(dest).name}")
                return True
        except Exception as e:
            log(f"cf fail: {e}")
    try:
        url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
               + f"?width={W}&height={H}&nologo=true&seed={seed}")
        req2 = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req2, timeout=120) as r:
            data = r.read()
        if len(data) > 15000:
            Path(dest).write_bytes(data)
            log(f"[ok-p] pollinations {Path(dest).name}")
            return True
    except Exception as e:
        log(f"pollinations fail: {e}")
    return False

def media_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

KZ_IN  = "z='min(zoom+0.0011,1.18)'"
KZ_OUT = "z='if(eq(on,1),1.18,max(1.001,zoom-0.0016))'"

def make_segment(img, seg, d, zoom_in):
    frames = max(int(d * FPS), FPS)
    z = KZ_IN if zoom_in else KZ_OUT
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"zoompan={z}:d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", f"{d:.3f}",
                    "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast",
                    "-crf", "27", str(seg)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def mix_bgm(audio):
    bgm = ROOT / "assets" / "music" / "epic_ambient.mp3"
    if not bgm.exists():
        log("BGM missing - skipping mix")
        return audio
    dur = media_duration(audio)
    mixed = WORK / "narration_mix.mp3"
    fade_end = max(0.1, dur - 8)
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(bgm), "-i", str(audio),
        "-filter_complex",
        f"[1:a]volume=1.0[n];[0:a]volume=0.42,"
        f"afade=t=in:st=0:d=8,afade=t=out:st={fade_end:.2f}:d=8[m];"
        f"[n][m]amix=inputs=2:duration=first:dropout_transition=2,loudnorm[a]",
        "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "3", str(mixed)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("BGM mixed (0.42) + loudnorm")
    return mixed


# ------------------------------------------------------------------ main
def main():
    if not OPENROUTER_API_KEY:
        sys.exit("OPENROUTER_API_KEY not set")

    log(f"=== MEGA: {EPISODE_ID} | 7 parts Devanagari ===")
    parts = []
    for i in range(1, 8):
        parts.append(call_part(i))
    narration = "\n\n".join(p.strip() for p in parts)
    total_words = len(narration.split())
    log(f"TOTAL narration: {total_words} words (~{total_words / 100:.0f} min @100wpm Hindi)")

    # -------- Extension loop: guarantee the final video is >= 2 hours --------
    for ext in range(3):
        Path(WORK / "narration.txt").write_text(narration, encoding="utf-8")
        mp3_probe, srt_probe = WORK / "narration.mp3", WORK / "narration.srt"
        subprocess.run([sys.executable, "-m", "edge_tts",
                        "--file", str(WORK / "narration.txt"), "--write-media", str(mp3_probe),
                        "--write-subtitles", str(srt_probe),
                        "--voice", VOICE, f"--rate={RATE}"], check=True)
        dur = media_duration(mp3_probe)
        total_words = len(narration.split())
        log(f"TTS pass {ext}: {dur:.1f}s ({dur/60:.1f} min), {total_words} words")
        if dur >= 7200:
            break
        tail = " ".join(narration.split()[-700:])
        ext_prompt = f"""You previously wrote a 7-part mega recap of the Chen Yirang betrayal story (Devanagari Hindi + English mix).
The story currently ENDS with this final paragraph:
...{tail}

Now you MUST extend the same story WITHOUT repeating previous scenes: write a deep-dive epilogue interlude of 2300-2800 words:
- The night before the storm trial (flashback, sensory suspense)
- What happened to the city between parts (compressed progression scenes with suspense)
- The day AFTER the Hidden Throne falls (the silence, the empty throne, one last lantern)
- Then restate the moral EXPLICITLY and powerfully (last line is the moral)
- Same style: Devanagari Hindi mixed with English technical words. NO double quotes, NO backslashes inside dialogue. Hindi quotes 「 」 or single quotes only.
- Never summarize. Keep pace slow, tension high, absolutely no scenes from before the current ending.

Return ONLY JSON: {{"part": 8, "narration": "..."}}"""
        extra = _generate(ext_prompt, f"extension {ext + 1}", min_words=1800)
        narration = narration.rstrip() + "\n\n" + extra.strip()
        total_words = len(narration.split())
        log(f"after extension: {total_words} words")
    else:
        log("WARNING: after 3 extensions video is still under 2h")

    log("=== IMAGES (32) ===")
    image_paths, seed0 = [], random.randint(1000, 999999)
    for i, p in enumerate(IMAGE_PROMPTS):
        dest = WORK / f"img_{i:02d}.png"
        if cf_image(p, dest, seed0 + i):
            image_paths.append(dest)
        time.sleep(1)
    if len(image_paths) < 12:
        sys.exit(f"only {len(image_paths)} images - aborting")

    log("=== THUMB ===")
    thumb_dest = WORK / "thumb.png"
    thumb = thumb_dest if cf_image(THUMB_PROMPT, thumb_dest, seed0 + 999) else None

    # TTS already produced/validated by the extension loop above (narration.txt tracked it)
    txt = WORK / "narration.txt"
    mp3, srt = WORK / "narration.mp3", WORK / "narration.srt"
    log(f"=== continuing with validated TTS: {media_duration(mp3):.1f}s ===")

    log("=== RENDER ===")
    mixed = mix_bgm(mp3)
    total = media_duration(mixed)
    per = total / len(image_paths)
    segs = []
    for i, img in enumerate(image_paths):
        seg = WORK / f"seg_{i:02d}.mp4"
        make_segment(img, seg, per, zoom_in=(i % 2 == 0))
        segs.append(seg)
        log(f"segment {i + 1}/{len(image_paths)} ({per:.1f}s)")

    list_file = WORK / "concat.txt"
    list_file.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs))
    concat = WORK / "concat.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                    "-c", "copy", str(concat)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    sub_style = ("FontName=Noto Sans Devanagari,FontSize=17,Bold=-1,"
                 "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=4,Outline=2,Shadow=0,MarginV=24")
    out_mp4 = OUT / f"mega_{EPISODE_ID}.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(concat), "-i", str(mixed),
                    "-vf", f"subtitles={srt.as_posix()}:force_style='{sub_style}'",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "27",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("video ready:", out_mp4)

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ["https://www.googleapis.com/auth/youtube.upload",
                          "https://www.googleapis.com/auth/youtube"])
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    body = {
        "snippet": {"title": TITLE, "description": DESCRIPTION, "tags": TAGS,
                    "categoryId": "24", "defaultLanguage": "hi"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(out_mp4), chunksize=16 * 1024 * 1024,
                            resumable=True, mimetype="video/mp4")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            log(f"upload {int(status.progress() * 100)}%")
    vid = resp["id"]
    log(f"uploaded: https://youtu.be/{vid}")

    if thumb:
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
            log("thumbnail set")
        except Exception as e:
            log("thumbnail skipped:", e)

    # add to Chinese Animation Recaps playlist
    try:
        yt.playlistItems().insert(part="snippet",
            body={"snippet": {"playlistId": "PLJ8DOidoftZM",
                               "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
        log("added to CN playlist")
    except Exception as e:
        log("playlist add failed:", e)
    print("MEGA_URL=https://youtu.be/" + vid)

if __name__ == "__main__":
    main()
