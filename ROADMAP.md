# Roadmap - Motion Draft Studio

## Done (Week of 2026-11-09)
- 100+ episode master list (Chinese + Japanese interleaved)
- Daily 6 episode schedule (3 Chinese + 3 Japanese), 5 AM / 9 AM / 1 PM / 5 PM / 9 PM / 1 AM PKT
- Series-specific playlists:
  - Chinese Animation Recaps (6 videos)
  - Japanese 2D Anime Recaps (4 videos)
  - Chinese Animation Shorts (2 videos)
  - Japanese 2D Anime Shorts (1 video)
- Phone verified YouTube channel — long uploads allowed
- Background music synthesized (epic ambient, 7-minute loop)
- 15-minute cap eliminated via phone verify
- State reconcile done
- First subscriber + tribute video (public thank-you) - https://youtu.be/xkqKR_cJF-w
- Milestone tribute automation: tribute video at 50 / 100 / 500 / 1000 and every 5K thereafter (4h cron)
- Shorts W7-W11 (5 new poll hooks) + auto-playlist routing
- 40-min episode target: >=5000-word narration enforced with expand-retry (ep14 came out 38:04)

## Next week (Week of 2026-11-16)
- Video length: 25-30 minutes -> 45-50 minutes per episode
- Chapters per episode (3-4 chapter split) for free LLM limits
- 16 images + 50s per image (image generation: 8-16 images x 45s each)
- Add 2 more Shorts schedule (total: 6/week shorts)
- Verify playback: 45-min episode retention check
- Try: Custom thumbnail per episode (CF FLUX generates polished)

## Capacity references (planning)
- GitHub Actions free minutes: 2000/month private (currently ~30 min × 6/day × 30 days = huge)
- Cloudflare Workers AI free tier: 10,000 neurons/day (≈ 13 images/day at current style)
- OpenRouter free models: ~50-100 req/day (will need fallbacks)
- Upload quota: 1600 units per upload, 10,000/day (limit: 6 uploads/day)

## Channel KPI baseline
- Subscribers: <10 (starting)
- Videos public: 11 (incl. 3 shorts)
- Watch-time: very low (let algorithm learn)
- Monetization: Not possible yet (need 1000 subs + 4000 hours)
- ETA to monetization: ~3-5 months with 6 videos/day
