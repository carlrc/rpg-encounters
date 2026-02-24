/**
 * Sanitizes display names to plain text tokens only.
 * Allowed: letters, numbers, spaces, apostrophes, hyphens.
 */
export const sanitizeDisplayName = (name) => {
  if (typeof name !== 'string') return ''

  return name
    .normalize('NFKC')
    .replace(/[^\p{L}\p{N}\s'-]+/gu, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}
