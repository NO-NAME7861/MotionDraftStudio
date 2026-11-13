import asyncio
import edge_tts
import sys
sys.stdout.reconfigure(encoding='utf-8')

TEXT = "Listen carefully, my friend. In this world of cultivation, there is no greater honor than carrying your promises into battle."

async def t():
    for voice in ["en-IN-NeerjaExpressiveNeural", "hi-IN-SwaraNeural", "ur-PK-UzmaNeural"]:
        try:
            out = f"C:\\Users\\Park-Edge\\Desktop\\voice-test-{voice}.mp3"
            c = edge_tts.Communicate(TEXT, voice)
            await c.save(out)
            print("OK", voice, out)
        except Exception as e:
            print("FAIL", voice, e)

asyncio.run(t())
