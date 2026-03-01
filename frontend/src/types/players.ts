import type { paths } from './_generated/openapi'

export type GetPlayersResponse =
  paths['/api/players']['get']['responses']['200']['content']['application/json']

export type Player = GetPlayersResponse[number]

export type GetPlayerResponse =
  paths['/api/players/{player_id}']['get']['responses']['200']['content']['application/json']

export type CreatePlayerRequest =
  paths['/api/players']['post']['requestBody']['content']['application/json']
export type CreatePlayerResponse =
  paths['/api/players']['post']['responses']['200']['content']['application/json']

export type UpdatePlayerRequest =
  paths['/api/players/{player_id}']['put']['requestBody']['content']['application/json']
export type UpdatePlayerResponse =
  paths['/api/players/{player_id}']['put']['responses']['200']['content']['application/json']

export type CreatePlayerLoginLinkResponse =
  paths['/api/players/{player_id}/login']['post']['responses']['200']['content']['application/json']

export type GetPlayerEncounterResponse =
  paths['/api/players/{player_id}/encounter']['get']['responses']['200']['content']['application/json']
