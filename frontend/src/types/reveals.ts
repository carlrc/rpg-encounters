import type { paths } from './_generated/openapi'

export type GetRevealsResponse =
  paths['/api/reveals']['get']['responses']['200']['content']['application/json']

export type Reveal = GetRevealsResponse[number]

export type GetRevealResponse =
  paths['/api/reveals/{reveal_id}']['get']['responses']['200']['content']['application/json']

export type CreateRevealRequest =
  paths['/api/reveals']['post']['requestBody']['content']['application/json']
export type CreateRevealResponse =
  paths['/api/reveals']['post']['responses']['200']['content']['application/json']

export type UpdateRevealRequest =
  paths['/api/reveals/{reveal_id}']['put']['requestBody']['content']['application/json']
export type UpdateRevealResponse =
  paths['/api/reveals/{reveal_id}']['put']['responses']['200']['content']['application/json']

export type GetRevealsForCharacterResponse =
  paths['/api/reveals/character/{character_id}']['get']['responses']['200']['content']['application/json']
