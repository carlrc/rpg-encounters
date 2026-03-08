import type { paths } from './_generated/openapi'

export type GetCanvasResponse =
  paths['/api/canvas']['get']['responses']['200']['content']['application/json']

export type SaveCanvasRequest =
  paths['/api/canvas']['post']['requestBody']['content']['application/json']
export type SaveCanvasResponse =
  paths['/api/canvas']['post']['responses']['200']['content']['application/json']

export type CanvasResponse = GetCanvasResponse
