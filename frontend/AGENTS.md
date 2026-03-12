# Frontend Agents File

## Overview

- Keep behavior, flows, and layout structure unchanged unless explicitly requested.

## Style Guide

### Sources Of Truth

- `src/styles/tokens.css`
- `src/styles/components.css`
- `src/styles/landing.css`

### Visual Direction

- Neutral, minimal, developer-tool look.
- Flat surfaces + borders; avoid heavy shadows and gradients.
- Keep backgrounds light/white; avoid purple accents and dark-theme drift.
- Keep transitions subtle and consistent.

### Canonical Button Mapping

- `shared-btn-primary`: black primary in-app actions (`Save`, `Create`, `Edit`).
- `shared-btn-secondary`: gray secondary actions (`Features`, `Demos`, `GitHub`, `Login`, `Cancel`, `Close`, `Profile`, `Instructions`).
- `shared-btn-danger`: red destructive actions (`Delete`).

### Guardrails

- Prefer shared button variants over page-specific button color overrides.
- Add new visual tokens in `tokens.css`; consume in shared styles first.
- Keep one-off component styles scoped and minimal.

### Quick Acceptance Checklist

- Landing and app headers use consistent button styling.
- Primary/secondary/danger intent is consistent across CRUD cards/forms.
- No ad-hoc button color drift outside shared variants.
