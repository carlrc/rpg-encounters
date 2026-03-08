import type { paths } from './_generated/openapi'

export type GetWorldsResponse =
  paths['/api/worlds']['get']['responses']['200']['content']['application/json']

export type World = GetWorldsResponse[number]

export type CreateWorldResponse =
  paths['/api/worlds']['post']['responses']['200']['content']['application/json']
