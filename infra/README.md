# RPG Encounters Infra

## Setup

Install NPM dependencies

```bash
npm ci
```

Get TF dependencies

```bash
npm run get
```

Compile

```bash
npm run synth
```

## Deploying

- As defined in `main.ts`, the two SSL certs (CloudFront & ALB) are manually created and referenced by their `arn`

Login to AWS SSO. Replace with whatever profile is setup as Administrator in RPG Encounters AWS Account.

```bash
aws sso login --profile rpg-admin
```

Deploy application and DNS stacks

```bash
npm run deploy rpg-encounters-app rpg-encounters-dns -- --auto-approve
```

Destroy infra

```bash
npm run destroy rpg-encounters-app rpg-encounters-dns -- --auto-approve
```
