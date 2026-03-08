// Simple in-memory storage for viewport state
let savedViewport = null

export const saveViewport = (viewport) => {
  savedViewport = viewport
}

export const getViewport = () => {
  return savedViewport
}
