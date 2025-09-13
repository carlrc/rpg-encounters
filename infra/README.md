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

## Deploying

- As defined in `main.ts`, the two SSL certs (CloudFront & ALB) are manually created and referenced by their `arn`
