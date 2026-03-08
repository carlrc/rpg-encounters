# Content Moderation System

## Overview
The platform implements a two-layer content moderation system to maintain a safe environment while preserving creative expression in RPG storytelling.

## How It Works
1. **Initial Screening**: Curated word lists flag potentially problematic content
   - [LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words) blocklist (`./ldnoobw_words.text`)
   - [CMU Research](https://www.cs.cmu.edu/~biglou/resources/) word list (`./luis_von_ahn_bad_words.txt`)
   - Lists sanitized to remove false positives (nationalities, colors, emotions, legal terms, profanity etc.)

2. **AI Analysis**: Flagged content is analyzed by [OpenAI's Moderation API](https://platform.openai.com/docs/guides/moderation)
   - Multi-category assessment (harassment, hate, violence, sexual content)
   - Zero tolerance for content involving minors or self-harm
   - Conservative thresholds (0.4 general, 0.1 for minors)

## What's Protected
All user-generated text: character names, backgrounds, motivations, personality and dialogue.

## Privacy & Security
- Fail-secure design: blocks content if moderation unavailable

## Configuration
```bash
SKIP_MODERATION=true              # Disable moderation (development only)
OPEN_AI_MODERATION_THRESHOLD=0.4  # Adjust sensitivity (0.0-1.0)
```