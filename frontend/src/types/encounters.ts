import type { paths } from './_generated/openapi'

export type GetEncounterResponse =
  paths['/api/encounters/{encounter_id}']['get']['responses']['200']['content']['application/json']

export type Encounter = GetEncounterResponse

export type CreateEncounterRequest =
  paths['/api/encounters/']['post']['requestBody']['content']['application/json']
export type CreateEncounterResponse =
  paths['/api/encounters/']['post']['responses']['200']['content']['application/json']

export type UpdateEncounterRequest =
  paths['/api/encounters/{encounter_id}']['put']['requestBody']['content']['application/json']
export type UpdateEncounterResponse =
  paths['/api/encounters/{encounter_id}']['put']['responses']['200']['content']['application/json']

export type CreateConnectionResponse =
  paths['/api/encounters/connections']['post']['responses']['200']['content']['application/json']

export type Connection = CreateConnectionResponse

export type UpdateConnectionResponse =
  paths['/api/encounters/connections/{connection_id}']['put']['responses']['200']['content']['application/json']

export type GetEncounterConnectionsResponse =
  paths['/api/encounters/{encounter_id}/connections']['get']['responses']['200']['content']['application/json']

export type GetConversationDataResponse =
  paths['/api/encounters/{encounter_id}/conversation/{player_id}/{character_id}']['get']['responses']['200']['content']['application/json']

export type DeleteConversationHistoryResponse =
  paths['/api/encounters/{encounter_id}/conversation/{player_id}/{character_id}']['delete']['responses']['204']
