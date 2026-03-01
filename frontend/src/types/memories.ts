import type { paths } from './_generated/openapi'

export type GetMemoriesResponse =
  paths['/api/memories']['get']['responses']['200']['content']['application/json']

export type Memory = GetMemoriesResponse[number]

export type GetMemoryResponse =
  paths['/api/memories/{memory_id}']['get']['responses']['200']['content']['application/json']

export type CreateMemoryRequest =
  paths['/api/memories']['post']['requestBody']['content']['application/json']
export type CreateMemoryResponse =
  paths['/api/memories']['post']['responses']['200']['content']['application/json']

export type UpdateMemoryRequest =
  paths['/api/memories/{memory_id}']['put']['requestBody']['content']['application/json']
export type UpdateMemoryResponse =
  paths['/api/memories/{memory_id}']['put']['responses']['200']['content']['application/json']
