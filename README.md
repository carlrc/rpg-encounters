<p align="center">
    <a href="frontend/public/logo.png">
        <img src="frontend/public/logo.png" alt="rpg encounters logo" width="20%"/>
    </a>
</p>

<h2 align="center">
    <p>RPG Encounters</p>
</h2>

<div align="center">

[**Setup**](#-setup) | [**Getting started**](#-getting-started)

</div>

RPG Encounters is a program for adding AI characters into your in-person tabletop sessions. It is designed for DMs to easily create characters with biases, memories, trust based secrets that players can interact with.

It is designed to replace encounters where the DM does not want to impersonate characters and instead introduce some variability, and free-form role play.

## 🚀 Getting Started

1. Read the [game instructions](./frontend/public/instructions.md) and [features](#-core-features) to understand the mechanics.
2. Follow the [setup guide](#-setup) and [usage instructions](#-usage) or use the [hosted version](https://rpg-encounters.com).
3. Talk to some characters in the [default scenario](./frontend/public/instructions.md#the-captains-secret-crate)!

## ✨ Core Features

| | |
|---|---|
| <img src="frontend/public/landing/assets/images/home/encounters-screen.png" alt="Encounters screen" width="220" /> | **Visually manage encounters**<br/>Assign characters and players to encounters that match the board in front of you. |
| <img src="frontend/public/landing/assets/images/home/encounter-popup.png" alt="Encounter popup" width="220" /> | **Secrets that are unlocked with influence or ability checks**<br/>Players can choose to free-form role play to gain influence or challenge characters with a charisma based ability check. |
| <img src="frontend/public/landing/assets/images/home/player-screen.png" alt="Player popup" width="220" /> | **Players can speak through their phone**<br/>Generate login links for players and let them control the conversation. |
| <img src="frontend/public/landing/assets/images/home/character-screen.png" alt="Character screen" width="220" /> | **Characters with personality**<br/>Create characters with biases, motivations and trust based secrets, which dictate how they respond. |

## 🔌 Setup

- Follow `backend` [setup guide](./backend/README.md)
- Follow `frontend` [setup guide](./frontend/README.md)

## 💻 Usage

Launch frontend

```bash
npm run dev
```

Launch backend services

```bash
docker compose -f backend/docker-compose.yml -f backend/docker-compose.dev.yml up
```

### Microphone

Locally you need to use a shared microphone, where the DM initiates conversations from the `/encounters` screen. A conference microphone is best, so the table can share in the experience, but something you can pass around also works. In the hosted version players can use their personal phones.

### Login

Because the application uses magic links in production, locally you need to:

- Set `LOG_MAGIC_LINK=true` in `backend/.env`
- [Seed the database](./backend/README.md) with a user and email
- Request login link
- Copy login link from backend service logs, which looks something like: `test1@example.com login link: http://localhost:3001/auth?token=e-e6Cs6paxa6H0fmC0gYfrwfLElxWwkeSF0Jb6ck-XY`
- Paste login link into the same browser used to request it

### Avoiding Token Checks

You can avoid token billing checks by either:

- Setting `BILLING_IGNORE_BALANCE_CHECK=true` in `backend/.env`.
- Adjusting token balances with the script in `backend/tests/scripts/set_billing_state.py`:

```python
docker exec rpg-encounters-backend /app/.venv/bin/python tests/scripts/set_billing_state.py --email test1@example.com --available 1000000 --last-used 0
```

### Avoiding Moderation

You can skip moderation by setting `SKIP_MODERATION=true` in `backend/.env`.

### Changing Models

You can switch models by setting the appropriate API keys in your `backend/.env` and adjusting `src/core/backend/app/agents/base_agent.py` following the [Pydantic docs](https://ai.pydantic.dev/models/overview/).

### Changing TTS Provider

Provider availability is based on which API keys are set in `backend/.env`:

- ElevenLabs `ELEVENLABS_TTS_API_KEY`
- Google `GOOGLE_CLOUD_TTS_API_KEY`

The default provider is set by `DEFAULT_TTS_PROVIDER`.

## Support

There are many ways to support:

- Use it! Write about it! Star it!
- Sponsor my work at <https://www.buymeacoffee.com/carlrcr>

<a href="https://www.buymeacoffee.com/carlrcr" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>
