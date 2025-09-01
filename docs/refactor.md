# Frontend Code Review & Refactor Prompt (Vue 3, No TypeScript)

You are a senior Vue 3 frontend architect. Perform a full code review and produce a refactor plan and code patches. Testing is ignored. Look at ONLY the frontend code for review.

---

## Output format

1. Executive summary: top improvements.  
2. Project-wide refactor plan.  
3. Proposed folder tree.  
4. Example code patches (Vue SFCs, services, styles).  
5. Shared style tokens and usage.  
6. Shared composables and services list with signatures.  
7. Per-feature migration notes.  
8. ESLint rules snippet.  
9. Post-refactor checklist.  

---

## Global rules

- All functions declared as `const fn = (args) => {}`.  
- No `var`. Use `const` or `let`.  
- Arrow functions everywhere.  
- Named exports preferred.  
- Immutability: do not mutate props or state directly.  
- Use async/await only. AbortController for cancellation.  
- Use optional chaining and nullish coalescing.  
- No side effects at module top level.  
- Sanitize any use of `v-html`.  
- Accessibility: semantic HTML, keyboard support, visible focus.  

---

## Vue Single File Components

- `<script setup>` only.  
- `defineProps`, `defineEmits`, `defineModel` for bindings.  
- Move logic out of templates into computed.  
- Local styles via `<style module>` or CSS Modules. No raw hex or ad-hoc spacing.  

**Example header**:

```vue
<script setup>
const props = defineProps({ title: String })
const emit = defineEmits(['save'])
const onClick = () => { emit('save') }
</script>

<template>
  <AppButton @click="onClick">{{ props.title }}</AppButton>
</template>

<style module>
.root { padding: var(--space-4) }
</style>
```

## State

- Use Pinia (or composables if store unnecessary).

- One store per domain.

- No HTTP in components. Move to services.

**Example store**:

`export const useInventory = defineStore('inventory', {   state: () => ({ items: [] }),   getters: { count: (s) => s.items.length },   actions: {     async load(signal) {       this.items = await api.items.list({ signal })     }   } })`

## Routing

- Vue Router 4.

- Route-level code splitting.

- Use `meta` for layout/auth.

---

## Folder Structure (feature-first)

`src/   app/                 # main.js, App.vue, plugins   assets/   components/     base/              # Base* components (form, button, modal)     app/               # App shell, navigation   features/     <feature>/       pages/       components/       store/       services/       composables/       routes.js   composables/   services/   styles/     tokens.css     index.css   utils/   router/   stores/   directives/   types/`

## Shared Styles

File: `src/styles/tokens.css`

`:root {   --color-bg: #0b0b0c;   --color-fg: #e7e7ea;   --space-1: 0.25rem; --space-2: 0.5rem; --space-3: 0.75rem; --space-4: 1rem;   --radius-2: .375rem; --radius-3: .5rem;   --font-sans: ui-sans-serif, system-ui, sans-serif; }`

Import once in `main.js`.

## Shared Functionality

- **services/http.js**: fetch wrapper with base URL, interceptors, Abort support.

- **composables/useAsync.js**: `pending`, `error`, `execute` pattern.

- **composables/useI18nPath.js**: locale-aware routing helper.

- **utils/format.js**: dates, currency, numbers.

**http.js example**:

`const request = async (method, url, body, { signal } = {}) => {   const res = await fetch(import.meta.env.VITE_API_URL + url, {     method, signal,     headers: { 'content-type': 'application/json', ...authHeader() },     body: body ? JSON.stringify(body) : undefined,   })   if (!res.ok) throw await normalizeError(res)   return res.json() }  export const http = {   get: (url, opts) => request('GET', url, undefined, opts),   post: (url, body, opts) => request('POST', url, body, opts), }`

## Modern JS Practices

- Use destructuring.

- Use `Object.hasOwn`, `structuredClone`, `Array.at`.

- Boolean vars should be positive (`isActive`, not `notInactive`).

- Avoid magic numbers.

- Prefer small pure functions.

---

## Forms & UX

- Use native `<form @submit.prevent>`.

- Centralize Base components for inputs.

- Debounce inputs for API calls.

- Provide skeletons and empty states.

---

## Performance

- Lazy load routes and components.

- Virtualize long lists.

- Use `v-memo` for memoization.

- Optimize images (size, lazy loading).

---

## Error Handling

- Global `app.config.errorHandler`.

- Per-feature error mappers.

- `onErrorCaptured` for fallback UI.

---

## Lint & Formatting

ESLint + Prettier.

**Example rules**:

`export default [   { rules: {     'func-style': ['error', 'expression'],     'no-var': 'error',     'prefer-const': 'error',     'vue/no-mutating-props': 'error',     'vue/script-setup-uses-vars': 'error'   }} ]`

---

## Post-refactor Checklist

- All functions are `const` arrows.

- No duplicate styles.

- No direct HTTP in components.

- No dead code or TODOs.

- Props/emits explicit.

- All pages route-split.

- Shared tokens only.
