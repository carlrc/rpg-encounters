export const createContextRegistry = () => {
  return []
}

export const trackContext = (registry, context) => {
  registry.push(context)
  return context
}

export const closeTrackedContexts = async (registry) => {
  while (registry.length > 0) {
    const context = registry.pop()
    try {
      await context.close()
    } catch {
      // Ignore close failures so cleanup can proceed for remaining contexts.
    }
  }
}
