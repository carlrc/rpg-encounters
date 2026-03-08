import type { paths } from './_generated/openapi'

export type RequestMagicLinkRequest =
  paths['/api/auth/request']['post']['requestBody']['content']['application/json']

export type AuthCheckResponse =
  paths['/api/auth/check']['get']['responses']['200']['content']['application/json']
