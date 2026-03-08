import type { paths } from './_generated/openapi'

export type GetCharactersResponse =
  paths['/api/characters']['get']['responses']['200']['content']['application/json']

export type Character = GetCharactersResponse[number]

export type GetCharacterResponse =
  paths['/api/characters/{character_id}']['get']['responses']['200']['content']['application/json']

export type CreateCharacterRequest =
  paths['/api/characters']['post']['requestBody']['content']['application/json']
export type CreateCharacterResponse =
  paths['/api/characters']['post']['responses']['200']['content']['application/json']

export type UpdateCharacterRequest =
  paths['/api/characters/{character_id}']['put']['requestBody']['content']['application/json']
export type UpdateCharacterResponse =
  paths['/api/characters/{character_id}']['put']['responses']['200']['content']['application/json']
