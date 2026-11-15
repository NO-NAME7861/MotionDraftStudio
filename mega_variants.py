"""
mega_variants.py - story definitions for the MEGA 2h+ Devanagari-Hindi recap builder.
Variants: M001 (betrayal -> Silent Thriller King, CN), M002 (disgraced ronin -> Silent Samurai, JP), M003 (20yr earthen god revenge, CN)
Each variant: TITLE, MORAL, CONTEXT (hero summary injected into part prompts), PARTS (7 beats),
DESCRIPTION, TAGS, IMAGE_PROMPTS (32), THUMB_PROMPT
"""

M001 = {
    "TITLE": "Betrayal Ke Baad Wapas Aaya — Silent Thriller King [Chinese Animation Recap Hindi]",
    "MORAL": "Betrayal ka jawaab gussa nahi, sabar aur strategy hai — patience is the greatest weapon.",
    "CONTEXT": (
        "Hero: CHEN YIRANG (चेन यिरांग), 19-year-old genius, betrayed on the mountain trial by elder brother चेन लूहांग, "
        "mentor मास्टर कियानमो, friend बैतुआन, fiancée लेयूया. Plunge, presumed dead. Rescued by Obsidian Fang syndicate "
        "under KUWEN DAMUN (कुवेन दामून). Trained as a shadow operative. Returns to Baolinghe as the silent \"Shadow King\". "
        "He methodically dismantles each betrayer with cold precision, then leaks the \"Hidden Throne\" cabal that runs the sect, "
        "bringing the entire system down by exposure, not war. Moral at the very end of part 7 only."
    ),
    "PARTS": [
        {"part": 1, "slug": "pratibha", "beat": (
            "Azure Heaven Pavilion's most gifted disciple CHEN YIRANG (चेन यिरांग), 19, wins the Celestial Trials, "
            "catches the mentor MASTER QIANMO's (मास्टर कियानमो) secret: the sect hierarchy crushes talent for clan politics. "
            "His fiancée लेयूया seems glowing, his best friend बैतुआन loyal, his elder brother चेन लूहांग jealous. "
            "Set the city BAOLINGHE (बोलिंगहे) with neon crime towers, sect tower, rain, market noise. "
            "Yirang is naive-honest, believes in the system. Show the festival, the banners, the tests. End part 1 with him hearing a whisper: 'The Trials are not what they seem.'"
        )},
        {"part": 2, "slug": "vishwasghat", "beat": (
            "The Betrayal Night. The final trial on Thunder Crag during the storm. Elder brother Luhang (लूहांग) cuts the rope during the ascension climb; "
            "mentor Qianmo watches and says nothing; best friend बैतुआन holds the gate and refuses to help; fiancée लेयूया runs to the brother's side. "
            "Yirang plummets into the river/cliff, presumed dead. Qianmo orders silence. The sect announces 'a tragic accident'. "
            "Flashbacks of earlier promises make the pain sharper. End: his body broken, he opens his eyes to red lanterns in the rain: the SECOND CITY below."
        )},
        {"part": 3, "slug": "chhayayon", "beat": (
            "The underworld city Baolinghe. Found by the OBSIDIAN FANG syndicate (ऑब्सीडियन फेंग) and its kingpin KUWEN DAMUN (कुवेन दामून), a dying crime emperor, "
            "who runs a shadow auction: information, blackmail, disappeared men. Yirang apprenticeship: ledgers, ciphers, surveillance, silence, interrogation, tasting fear. "
            "He gains back his body + mind, sees how clean the sect looks from outside vs the rot beneath. "
            "He finds his own name in an auction record: sold as 'asset #041' by his own sect. He does not rage; he laughs softly - the pivot moment. End: 'अब पूरा खेल मेरे rules पर चलेगा।'"
        )},
        {"part": 4, "slug": "badla1", "beat": (
            "Part 4 - RETURN and THE BROTHER'S FALL. Under a new face/name, Yirang the Shadow King moves into Baolinghe's elite circles; buys his brother Luhang's debts; engineers his promotion ceremony to blow up on live display "
            "(leaked forged evidence: the rope, the bribed judge, the audio of the storm night). Crowd mood flips. Luhang spends the night in the same cells he put Yirang in. Thriller beats: chase in the rain, a calm negotiation vs a panic, the silent smile, the reveal. "
            "Yirang shows mercy ONLY as strategy: he makes Luhang sign the entire secret ledger rather than kill him. End part 4: brother's hands tremble as he signs."
        )},
        {"part": 5, "slug": "master_girvat", "beat": (
            "Part 5 - THE MENTOR'S COLLAPSE. Qianmo senses danger, travels to Baolinghe undercover, meets the new 'Shadow King' unknowing of who he is. "
            "Yirang plays chess/cold hospitality: tells him stories of fallen sects. Twist reveal: Qianmo's own hidden slave-ledger (asset contracts, #041) is presented to the court as 'unknown evidence'. "
            "Qianmo's students turn; the verdict happens at the Pavilion's 900th anniversary ceremony on stage - the mentor bows and never rises again (metaphorically buried: publicly stripped). "
            "Thriller beats: the mask of reverence, the smile, the ledger on a silver plate, the silence in the hall. End: Yirang walks out as the crowd whispers 'Shadow King.'"
        )},
        {"part": 6, "slug": "dost_prem", "beat": (
            "Part 6 - THE FRIEND AND THE FIANCEE. बैतुआन, the guilt-eaten gatekeeper, is offered a 'ticket out' to exile; he exposes EVERYTHING in exchange. "
            "Fiancée लेयूया comes begging, pretending love; Yirang replays her storm-night words in a recorded auction of memory; she understands she sold him for a seat at the sect table; she is ruined publicly not by violence but by truth. "
            "Yirang offers one chance: confess on court, name everyone. She chooses silence - and he lets the world do the rest. "
            "Beat: the auction hall of truth, the crowd's faces, the soft delivery of the final line: 'मैं जीतने नहीं आया ... मैं पूरा खेल दिखाने आया हूँ।' End: the city empties before his one signal."
        )},
        {"part": 7, "slug": "hidden_throne", "beat": (
            "Part 7 - THE HIDDEN THRONE AND THE WORLD FLIP. The final reveal: the betrayals were orchestrated by the EMPEROR'S secret cabal 'Hidden Throne' (हिडन थ्रोन) which runs the Pavilion as a beta-test lab for removing inconvenient geniuses. "
            "Yirang, with Obsidian Fang's 200 shadow agents and Qianmo's ledger, doesn't storm any palace - he leaks EVERYTHING simultaneously: every court, every guild, every sect, every ledger page - one night, one hour, one command. "
            "The system collapses not by battle, but by exposure. KUWEN DAMUN dies satisfied in Yirang's arms: 'बेटा, सरकार... अब दुनिया तुम्हारा शहर है।' "
            "Epilogue 2 years later: 'Silent Emperor' legend, shrine streets empty, festivals renamed. End with the moral, slowly, explicitly: betrayal ka jawaab sabar aur strategy hai - gussa nahi. Patience crushes everyone."
        )},
    ],
    "DESCRIPTION": (
        "आज की सबसे गहरी कहानी — एक लड़का जिसे भाइयों, मास्टर, दोस्त और हबीब सबने धोखा दिया, वो कभी वापस आया ही नहीं... "
        "बल्कि एक परछाईं बन गया जिसने पूरे सिस्टम को धूल में मिला दिया। Betrayal → Silence → Strategy → Total Domination.\n\n"
        "⚠️ This video features AI-generated visuals and AI narration.\n\n"
        "Moral: Betrayal ka jawaab gussa nahi, sabar aur strategy hai.\n\n"
        "Subscribe for a new recap EVERY DAY: https://www.youtube.com/@MotionDraftStudio\n\n"
        "#HindiAnimationRecap #BetrayalRecap #ChineseAnimationRecapHindi #MotionDraftStudio #ThrillerHindi"
    ),
    "TAGS": [
        "hindi recap", "betrayal recap", "chinese animation recap hindi", "thriller recap",
        "motion draft studio", "revenge recap", "shady recap", "recap hindi", "animation recap hindi",
        "xianxia hindi", "डोंघुआ recap", "motivation hindi",
    ],
    "IMAGE_PROMPTS": [
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
    ],
    "THUMB_PROMPT": (
        "youtube thumbnail, cinematic chinese animation style, close-up of a young man soaked in rain with one glowing amber eye, "
        "broken prayer bead in his fist, red lantern light from below, world-ending mood, dramatic lighting, no text"
    ),
}

M002 = {
    "TITLE": "The Ronin Betrayed by His Clan — Silent Samurai's Patient Revenge [Japanese 2D Anime Recap Hindi]",
    "MORAL": "Giratach ni morche log baja'an ho, patience se jeeta sab — the stillest blade always wins the war.",
    "CONTEXT": (
        "Hero: SHINJIRO TAIGA (शिंजीरो ताइगा), 19-year-old prodigious sword student of the KURODA CLAN (कुरोदा वंश) under SENSEI HANTSU (हंतु). "
        "Rival clan SOMA (सोमा वंश), led by elderly SAKURAI TOSHINAGA (साकुराइ तोशिनागा), framed the Kuroda for a tax-massacre, butchered the clan, "
        "took their land and water rights. Shinjiro survives with a back scar and a dying grip. Seven years as wanderer. "
        "He settles in a nameless plague village AKEBONO (अकेबोनो) as 'TAKUMI', the cheapest worker, and waits. "
        "Through the years he quietly guards the village, trains at dawn in secret, collects the truth of the betrayal, and builds a quiet web of allies. "
        "He never draws first; he draws once, clean, and it is always the right swing. The SOMA heir KEI eventually arrives to kill the legend. "
        "Moral at the very end of part 7 only."
    ),
    "PARTS": [
        {"part": 1, "slug": "guruji", "beat": (
            "Set AKEBONO (अकेबोनो) and the KURODA CLAN in SHINJIRO (शिंजीरो)'s memory: the mountain dōjō, the waterfall kata, master HANTSU's silence, "
            "the sakura tree at dawn. Shinjiro at 19, youngest ever to earn the black belt stripe. Show class tension: SOMA envoys visit with 'friendly' paper maps of the valley; "
            "the master laughs softly and changes the subject. A farmer messenger disappears from the road. Whispers of a tax revolt plot. "
            "End part 1: during the evening tea, a letter arrives with a red seal — and the master's face goes white."
        )},
        {"part": 2, "slug": "katl_raat", "beat": (
            "The massacre. Night rain. SOMA assassins dressed as tax collectors enter the clan estate. The killing is efficient, masked, polite — "
            "the stylings of a 'legitimate collection'. HANTSU draws for the last time at the koi pond; dies facing west. Shinjiro, 19, takes two slashes across the back, "
            "drops into the reedbeds, hears the estate burn. A fake edict is unrolled at dawn: 'KURODA CLAN — ATTEMPTED TREASON. SEIZED BY EMPEROR'S ORDER.' "
            "Shinjiro wakes in the river, dragging a broken sword with one hand. End: he walks away, leaving no name behind, no eyes on him — the world already forgets him."
        )},
        {"part": 3, "slug": "wandering", "beat": (
            "Seven years of wandering. Shinjiro (शिंजीरो) road-waits, fights the desperate man's wage, drinks standing, sleeps in straw shrines. "
            "He reaches AKEBONO (अकेबोनो), a dying village: plague bells, empty shrines, a headman with thick bandaged hands. He claims no name — 'TAKUMI'. "
            "He works the rice paddies first, smells the sickness, digs graves. He does not draw on a robber even at machete point — he yields, he waits. "
            "In the rain, he meets the village's last midwife, OTOHISA (ओतोहिसा), who says: 'जो हर लड़ाई जीतना हो, वो पहले हर हार सहना सीखता है।' "
            "End: that night he finds the masked figure in the old shrine — the same mask from the massacre. Someone has been here. Recently."
        )},
        {"part": 4, "slug": "vigil", "beat": (
            "Part 4 - THE VIGIL. Shinjiro lives two masks: day — the paddy labourer others ignore; night — the shrine. He learns from the abandoned fishermen's rites, "
            "guards the village plague wards, catches the SOMA informant (NEGORO (नेगोरो), the new travelling medicine seller) and takes him alive. "
            "From interrogation, the whole plan surfaces: the massacre was ordered two years before by TOSHINAGA, and 'plague' is a military weapon baked into the valley's well-rights. "
            "Shinjiro deals with Negoro without killing him — he maims the man's pride, not the man, and sends him back as a witness to the wrong men. "
            "End: Negoro kneels in the SOMA hall with blood on his knees and tells it all, word for word."
        )},
        {"part": 5, "slug": "challenger", "beat": (
            "Part 5 - THE SOMA HEIR KEI (केइ) ARRIVES. Young, golden, arrogant — he comes to AKEBONO hunting the legend. "
            "Before anyone can stop him, he destroys the village gate, challenges Shinjiro in the mud arena, and MOCKS the 'clown in rice-farmer rags'. "
            "Three matches: first — Shinjiro yields the mud-throwing; second — the sword-vs-sword at the cliff's edge, Shinjiro disarms him and breaks the rival's sword; "
            "third — no fight at all, Shinjiro shows him the MASTER'S LETTER — the real order, written by his own father. "
            "Kei breaks down on the mud, says the world has lied to him his whole life. Shinjiro doesn't kill him. He WITS him instead — Kei joins the village, mortified, relearning everything. "
            "End: the village bells ring — not for a death, for Kei's surrender to the truth."
        )},
        {"part": 6, "slug": "flood", "beat": (
            "Part 6 - THE FLOOD. The SOMA clan learns that AKEBONO now has a champion; TOSHINAGA empties the valley with a well-poisoning. "
            "Shinjiro (शिंजीरो) moves with Kei and OTOHISA: a dam broken at night, a river rerouted, SOMA's granary drowned, their army's supply lines cut — "
            "all without a single drawn blade. This is war by engineering, by silence, by patience. "
            "NEGORO returns with a price-ledger that SHOCKED the Imperial Court itself — the Emperor learns the massacre was never 'rebellion', it was a land-deal. "
            "The Court declares the SOMA clan dissolved. But TOSHINAGA'S son above, SAKURAI JUGO (साकुराइ जुगो), sends one final mask: the mask of his father — to challenge Shinjiro honestly. "
            "End: the duel at sunrise over the rice paddy — the classic image of the recap: two still eyes, one long breath."
        )},
        {"part": 7, "slug": "mask_down", "beat": (
            "Part 7 - THE MASK FALLS. Jugo, the SOMA son, is not a villain — he's a son holding onto loyalty to a dead man. "
            "The duel is brief: Jugo's first cut grazes Shinjiro's old scar; Shinjiro's still one move. Jugo is disarmed. "
            "Shinjiro walks with Jugo to the ruined Kuroda estate at dusk. He shows the ruins: the koi pond, the master's sword spot, the sakura tree now blooming unattended from the rain. "
            "Jugo orders the mask burned. He returns the land titles to the village. The plague bells finally stop. "
            "Epilogue: AKEBONO grows rice again; the shrine at the cliff edge is rebuilt with a sword-pillar for 'TAKUMI THE STILL SHADOW'. "
            "End with the moral, slowly and explicitly: sabse sakht blade patience hai - koi mask, kuch vachan sab gir jate hain. Patience wins without a war."
        )},
    ],
    "DESCRIPTION": (
        "सबसे बड़ी betrayal — और सबसे बड़ी patience की कहानी। शिंजीरो ताइगा को उसके अपने clan ने मरवा डाला... "
        "उसने सात साल paddy, graves और silence में बिताए, और एक ऐसा war जीता जो तलवार से नहीं हुआ। Sword, Honor, Plague, Patience, Silence.\n\n"
        "⚠️ This video features AI-generated visuals and AI narration.\n\n"
        "Moral: Sabse sakht blade patience hai - patience wins without a war.\n\n"
        "Subscribe for a new recap EVERY DAY: https://www.youtube.com/@MotionDraftStudio\n\n"
        "#HindiAnimationRecap #Japanese2DAnimeRecapHindi #MotionDraftStudio #SamuraiRecapHindi #BetrayalRecap"
    ),
    "TAGS": [
        "hindi recap", "japanese 2D anime recap hindi", "samurai recap", "betrayal recap hindi",
        "motion draft studio", "ronin recap", "revenge recap", "recap hindi", "animation recap hindi",
        "anime hindi recap", "patience motivation", "motivation hindi",
    ],
    "IMAGE_PROMPTS": [
        "japanese 2D anime key visual, a 19 year old sword student with wooden sword under a sakura tree at dawn, dōjō, dramatic cel shading, no text",
        "japanese 2D anime, a mountain dojo above waterfalls in morning mist, sword training hall, cel shaded, no text",
        "japanese 2D anime, SOMA clan's black-lacquered castle on the valley, banners with crescent emblem, cel shaded, dramatic, no text",
        "japanese 2D anime, three samurai envoys in black arriving at the Kuroda gate with a red-sealed scroll, cel shaded, no text",
        "japanese 2D anime, night rain on a clan estate, masked assassins with paper lantern masks, cel shaded, dramatic, no text",
        "japanese 2D anime, an old master dying at the koi pond facing west, last light, cel shaded, cinematic, no text",
        "japanese 2D anime, a young man dragging himself through river reeds and storm, broken sword, cel shaded, no text",
        "japanese 2D anime, a dying plague village at the edge of a paddy, plague bells, empty shrines, cel shaded, no text",
        "japanese 2D anime, a farmer working rice paddies at dawn, face hidden under straw hat, cel shaded, quiet, no text",
        "japanese 2D anime, an abandoned shrine overgrown with weeds, an old masked mask on the altar, cel shaded, no text",
        "japanese 2D anime, a dying midwife sitting under plum blossoms, kind deep eyes, cel shaded, no text",
        "japanese 2D anime, a medicine seller with a snake in his sleeve entering the village, cel shaded, suspicious, no text",
        "japanese 2D anime, a masked figure breaking into the village shrine at midnight, cel shaded, tense, no text",
        "japanese 2D anime, a hidden dojo behind a waterfall behind a plague ward, cel shaded, secret, no text",
        "japanese 2D anime, an interrogated smuggler kneeling with blood on his knees, cel shaded, dramatic, no text",
        "japanese 2D anime, a village children's dragon-dance at dusk under paper lanterns, cel shaded, warm, no text",
        "japanese 2D anime, the SOMA heir Kei standing in the mud arena destroyed, rage on his face, cel shaded, no text",
        "japanese 2D anime, a father-son sword duel on a cliff over the paddy at sunrise, cel shaded, no text",
        "japanese 2D anime, a golden mask held by a father-son confrontation, sparks, cel shaded, no text",
        "japanese 2D anime, an Imperial courier crossing the flooded river valley with SOMA dissolution orders, cel shaded, no text",
        "japanese 2D anime, the SOMA granary flooded with lanterns floating on water, cel shaded, dramatic, no text",
        "japanese 2D anime, a midwife delivering a baby under plum blossoms, dawn, cel shaded, hope, no text",
        "japanese 2D anime, Jugo standing before the ruined Kuroda estate at dusk, palanquin discarded, cel shaded, no text",
        "japanese 2D anime, the sakura tree blooming alone over the ruins, cel shaded, poetic, no text",
        "japanese 2D anime, an old stone sword-pillar in the rebuilt shrine, cel shaded, quiet, no text",
        "japanese 2D anime, the village bell ringing at sunset, cel shaded, peaceful, no text",
        "japanese 2D anime, the mask burning in a bronze bowl, sparks, cel shaded, symbolic, no text",
        "japanese 2D anime, rice harvest with hundreds of villagers singing, cel shaded, joy, no text",
        "japanese 2D anime, an empty dojo floor with one black belt on a pillar, cel shaded, no text",
        "japanese 2D anime, a final wide shot of the valley reborn, fields and school roof, cel shaded, cinematic, no text",
        "japanese 2D anime, the word 'patience' glowing behind still closed eyes, dreamlike cel shaded, no text",
        "japanese 2D anime, the shrouded silhouette leaving the village into the mountains, cel shaded, legend, no text",
    ],
    "THUMB_PROMPT": (
        "youtube thumbnail, cinematic japanese 2D anime style, close-up of a ronin's half-lit face with a single scar and a worn katana hilt, "
        "rain, washed iris reflection of sakura petals, world-ending drama, no text"
    ),
}

M003 = {
    "TITLE": "Bai Ya's 20-Year Revenge — The Earthen God Who Ate The Celestial Throne [Chinese Animation Recap Hindi]",
    "MORAL": "20 saal pressure cooker hai — sabse matlab hai inner maan maanega, sabar se sab kuch achieve hota hai.",
    "CONTEXT": (
        "Hero: BAI YA (बाई या), a 9-year-old village boy who dreams of the sword. His sister BAI LI (बाई ली) joins the HEAVENLY RIVER SECT (स्वर्ग नदी Sect) "
        "to pay off the family's debt. She returns dismembered, her marrow harvested for the sect elites' immortality pills. "
        "Bai Ya buries her with his own hands, finds her broken sword, and trains alone in the CLAY BARRIER MOUNTAINS (मिट्टी पहाड़) for 20 years. "
        "He eats dirt, sleeps in tombs, reads the sect's criminals' ledgers by candlelight for two decades. "
        "He returns during the GRAND AUCTION OF IMMORTALITY PILLS, starts as a nobody, rises through the sect from inside, dismantles its elite caste, "
        "founds an egalitarian sect of merit-alone promotion, and takes on the CELESTIAL THRONE (सेलेस्टियल थ्रोन) itself. Moral at the very end of part 7 only."
    ),
    "PARTS": [
        {"part": 1, "slug": "bai_ya", "beat": (
            "Set the village of MISTY CLAY FIELDS (मिष्टी क्ले फील्ड्स): BAI YA (बाई या) at nine, training with a bamboo sword at the edge of the paddy, "
            "dreaming of the sword to protect his sister. Sister BAI LI works the herb house for the family's debt. "
            "The HEAVENLY RIVER SECT (स्वर्ग नदी Sect) comes down to recruit: elite disciples in silver armour, the children line up — but only Bai Li is 'worthy'. "
            "Bai Ya growls at them; guards block him. Bai Li promises to come back. "
            "End: a year later the sect carts return — and only her body does, laid on the very straw mat she slept on."
        )},
        {"part": 2, "slug": "burial", "beat": (
            "The burial. Bai Ya (बाई या), nine years old, carries the body up the hill with his own strength. The sect attributes her death to 'Heaven's punishment for a debt-marked soul'. "
            "Her broken sword is thrown to him as a 'donation'. He refuses the money. He digs her grave with a garden sickle. "
            "In the coffin, her hand is missing its marrow fingers — the sign of the sect's 'Lotus Death' harvest. He understands: she was not punished, she was HARVESTED. "
            "The market-priest calls her karma 'bad luck' and offers an 'offering prayer'. Bai Ya spits at his feet. "
            "End: he wipes the blood off her sword and asks the mountain spirit for nothing but one thing — a body that will not break."
        )},
        {"part": 3, "slug": "training", "beat": (
            "Twenty years of training in CLAY BARRIER MOUNTAINS (मिट्टी पहाड़). Bai Ya eats dirt, loses teeth, loses weight, barely stays human. "
            "He trains in tombs of nameless swordsmen, memorizes the HEAVENLY RIVER SECT'S ledger by smuggling pages through a dying monk, "
            "trains in a waterfall of rotten pine needles, falls unconscious fifty times, stands back up every time. "
            "His skin turns grey from clay-stone grit; the locals call him 'मिट्टी का दैत्य' (the Clay Fiend). "
            "Nine tests to see the immortal flame — he fails four, endures five. Ten passes. "
            "End: on the 20th-year dawn, the mountain splits in two — and something in it wakes up."
        )},
        {"part": 4, "slug": "return", "beat": (
            "Part 4 - THE RETURN. The GRAND AUCTION OF IMMORTALITY PILLS begins at Heavenly River. "
            "Bai Ya (बाई या) arrives dirt-grey, selling dirt-bricks for 'foundation stones'. A guard questions him; he says, 'No strikes needed. I'll just sell bricks. And talk about the sect.' "
            "His bricks interest no one — except a dismissed servant, XIAO QIN (शियाओ छिन), who follows him and senses something. "
            "Bai Ya buys the cheapest pill and swallows it in front of everyone. The elite disciples laugh. Their laughter doesn't last: "
            "the pill's spiritual energy fails to reject him — no anger, no rage, nothing. The hall goes quiet. "
            "End: the auctioneer announces the final item — a pill of his sister's face. Bai Ya's eyes finally move."
        )},
        {"part": 5, "slug": "pill_auction", "beat": (
            "Part 5 - THE PILL AUCTION. The final item is unveiled: a medicine extracted from Bai Li's remains, for sale. "
            "Before any bid is made, Bai Ya (बाई या) stands up and reads the pill clean — with his dirt-starved body he analyzes it better than any cultivator alive. "
            "The entire auction stalls. The CROWN DISCIPLE BAOGLO (बाओग्लो) demands he prove the pills are fake — Bai Ya bites into one live, doesn't blink, "
            "and a hundred voices repeat his words: the sect's pills are dilute mud wrapped in gold. "
            "The whole auction collapses into revolt — bidders riot, demanding refunds. "
            "XIAO QIN (शियाओ छिन) escapes with the original list: EVERY BUYER OF LOTUS-DEATH-DERIVED PILLS IS ON THE LIST. "
            "End: the sect's High Elder Lians orders the guards to seize the dirt man. Bai Ya laughs — for the first time in 20 years."
        )},
        {"part": 6, "slug": "sect_fall", "beat": (
            "Part 6 - THE SECT FALLS. Bai Ya (बाई या), aided now by seething servants and ruined buyers, begins a quiet strike: "
            "nobody cooks, nobody rings the bell, nobody sells pills. The HEAVENLY RIVER SECT (स्वर्ग नदी Sect) runs on routine — and routine dies. "
            "Then the government sends a judicial inspection from the IMPERIAL COURT (सेलेस्टियल थ्रोन). "
            "Bai Ya's ledger arrives sealed, with Bai Li's original death entry — signed by all three High Elders. "
            "The Elders retreat to their mountain cave; the disciples open the gates; the caste hierarchy drops. "
            "XIAO QIN becomes architect-chancellor of the new egalitarian sect. "
            "End: the High Elders ride down into the Clay Barrier mountains to face the 'Fiend' — and what comes out of the mountain is no longer human."
        )},
        {"part": 7, "slug": "celestial_throne", "beat": (
            "Part 7 - THE CELESTIAL THRONE. The three High Elders descend to CLAY BARRIER MOUNTAINS (मिट्टी पहाड़) with the CELESTIAL THRONE'S golden warrant. "
            "Bai Ya faces them alone on a mud sea. Each Elder throws a mountain at him one by one — he absorbs the earth back into himself. "
            "They understand then: the mountain didn't build him — he IS the mountain. "
            "They kneel. The CELESTIAL THRONE sends its Advance team - arrests are made, the Imperial Court convenes. "
            "Bai Ya doesn't burn them. He dissolves the lotus-death economy altogether: no pills, no sect-caste, no debts, equal training paths, merit-educated cultivation for all. "
            "Epilogue: the village grows rice again, parents sell dirt to raise their children's futures. "
            "End with the moral, slowly and explicitly: 20 saal pressure cooker ho gaya — patience se sab kuch achieve hota hai."
        )},
    ],
    "DESCRIPTION": (
        "सबसे ज़्यादा betrayed लड़का — सबसे बड़ी जगह पहुंचने की कहानी। नौ साल का लड़का, 20 साल का इंतज़ार, मिट्टी में घुल गया, "
        "और फिर एक ऐसा war जीता जो उसने कभी चुनौती भी नहीं दी थी। Patience, Revenge, Cultivation, Sacrifice.\n\n"
        "⚠️ This video features AI-generated visuals and AI narration.\n\n"
        "Moral: 20 saal pressure cooker — sabar se sab kuch achieve hota hai.\n\n"
        "Subscribe for a new recap EVERY DAY: https://www.youtube.com/@MotionDraftStudio\n\n"
        "#HindiAnimationRecap #ChineseAnimationRecapHindi #MotionDraftStudio #CultivationRecapHindi #RevengeRecap"
    ),
    "TAGS": [
        "hindi recap", "chinese animation recap hindi", "cultivation recap", "betrayal recap hindi",
        "motion draft studio", "revenge recap", "donghua recap hindi", "xianxia hindi", "animation recap hindi",
        "patience motivation", "motivation hindi", "underdog revenge",
    ],
    "IMAGE_PROMPTS": [
        "chinese animation key visual, a 9-year-old boy training with a bamboo sword in a paddy field at dawn, village setting, cel art, no text",
        "chinese animation, a village of misty clay fields with tiled roofs and a herb house at dusk, cel art, no text",
        "chinese animation, three elite disciples in silver armour descending from a cloud platform to recruit children, cel art, no text",
        "chinese animation, a young girl boarding a sect caravan with a small bundle, village gate, cel art, no text",
        "chinese animation, a body of a young girl carried back in a straw cart at night, villagers mourning, cel art, no text",
        "chinese animation, a 9-year-old boy digging a grave with a garden sickle on a hill, rain beginning, cel art, no text",
        "chinese animation, a broken sword dropped on blood-stained straw in a village square, macro, cel art, no text",
        "chinese animation, a clay mountain range with monster-fog coiling around its peak, world painted mud and ochre, cel art, no text",
        "chinese animation, a dying monk passing stolen sect pages to a boy who resembles a demon, cel art, no text",
        "chinese animation, a waterfall made of pine needles rotten into black silt, a figure standing under it training, cel art, no text",
        "chinese animation, a 20-year-old face of a youth sculpted from hardened clay, focused eyes, cel art, no text",
        "chinese animation, the mountain splitting in two as a dark figure rises in the dust, cel art, cinematic, no text",
        "chinese animation, an auction of glowing immortality pills in a lotus-shaped hall, buyers in silk, cel art, no text",
        "chinese animation, a dirt-grey labourer selling bricks at the auction gate, two guards eying him, cel art, no text",
        "chinese animation, a titan-like man biting into a glowing pill without flinching, hall going silent, cel art, no text",
        "chinese animation, a runner carrying stolen auction paper lists across the city roofs at night, cel art, no text",
        "chinese animation, the Heavenly River Sect's main gate closing on rioting bidders, cel art, dramatic, no text",
        "chinese animation, a beheaded sect elder kneeling on black marble before Bai Li's blood-stained mat, cel art, no text",
        "chinese animation, the secret entrance into the clay barrier mountains closing behind the three High Elders' caravan, cel art, no text",
        "chinese animation, the monster-fog folding inward on the mountain peak, teeth-like stone pillars, cel art, no text",
        "chinese animation, Bai Ya's hand spread over a sea of clay as the mountain answers, cel art, no text",
        "chinese animation, three gold-armoured elders falling to their knees in the mud, horrified, cel art, no text",
        "chinese animation, an Imperial Font warrant floating above a golden courtroom, officials bowing, cel art, no text",
        "chinese animation, the collapsed lotus-garden left alone in the mist, petals scattered under grey rain, cel art, no text",
        "chinese animation, a free school with dirt-floor classrooms, children training with wooden swords, cel art, no text",
        "chinese animation, a mother selling dirt bricks with her daughter learning to count coins, cel art, no text",
        "chinese animation, the misty clay fields restored with cherry-planted seedlings and lion flags, cel art, no text",
        "chinese animation, a young disciple ascending the rebuilt Heavenly River gate alone, cel art, no text",
        "chinese animation, a final wide view of the sect's new public marketplace under golden banners, cel art, cinematic, no text",
        "chinese animation, the word 'patience' carved into stone glowing in rain, cel art, no text",
        "chinese animation, a dirt-grey figure walking into the sunset with a daughter holding a miniature sword, cel art, no text",
    ],
    "THUMB_PROMPT": (
        "youtube thumbnail, cinematic chinese animation style, close-up of a man's eyes under a dirt-grey cloak with a cursed sword raised against purple sky, "
        "clay storm behind him, world ending mood, dramatic lighting, no text"
    ),
}

VARIANTS = {
    "M001": M001,
    "M002": M002,
    "M003": M003,
}
