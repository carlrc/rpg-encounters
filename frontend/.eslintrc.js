module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2022: true,
  },
  extends: ['eslint:recommended', 'plugin:vue/vue3-essential', '@vue/prettier'],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
}
