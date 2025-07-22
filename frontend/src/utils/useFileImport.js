import { ref } from 'vue'

export function useFileImport(entityType) {
  const importing = ref(false)

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target.result)
      reader.onerror = (e) => reject(new Error('Failed to read file'))
      reader.readAsText(file)
    })
  }

  const parseMarkdownEntities = (content) => {
    const entities = []

    // Split by main headers (# or ## followed by any text)
    const sections = content.split(/^#\s+/m).filter((section) => section.trim())

    for (const section of sections) {
      try {
        const entity = parseEntitySection(section)
        if (entity) {
          entities.push(entity)
        }
      } catch (err) {
        console.warn('Failed to parse entity section:', err.message)
      }
    }

    return entities
  }

  const parseEntitySection = (section) => {
    const lines = section.split('\n')
    const entity = {
      name: '',
      appearance: '',
      race: '',
      class_name: '',
      size: '',
      alignment: '',
      tags: [],
    }

    let currentField = null
    let currentContent = []

    for (const line of lines) {
      const trimmedLine = line.trim()

      // Check for field headers
      if (trimmedLine.match(/^##\s*name/i)) {
        currentField = 'name'
        currentContent = []
      } else if (trimmedLine.match(/^##\s*appearance/i)) {
        currentField = 'appearance'
        currentContent = []
      } else if (trimmedLine.match(/^##\s*race/i)) {
        currentField = 'race'
        currentContent = []
      } else if (trimmedLine.match(/^##\s*class/i)) {
        currentField = 'class_name'
        currentContent = []
      } else if (trimmedLine.match(/^##\s*size/i)) {
        currentField = 'size'
        currentContent = []
      } else if (trimmedLine.match(/^##\s*alignment/i)) {
        currentField = 'alignment'
        currentContent = []
      } else if (trimmedLine.match(/^##\s*(tags|groups)/i)) {
        currentField = 'tags'
        currentContent = []
      } else if (trimmedLine.startsWith('##')) {
        // Unknown field, stop processing current field
        currentField = null
        currentContent = []
      } else if (currentField && trimmedLine) {
        // Add content to current field
        if (currentField === 'tags') {
          // Parse bullet points for tags
          if (trimmedLine.match(/^[-*]\s+(.+)/)) {
            const tagName = trimmedLine.replace(/^[-*]\s+/, '').trim()
            if (tagName) {
              currentContent.push(tagName)
            }
          }
        } else {
          currentContent.push(trimmedLine)
        }
      } else if (currentField && currentContent.length > 0) {
        // End of field content, save it
        if (currentField === 'tags') {
          entity[currentField] = currentContent
        } else {
          entity[currentField] = currentContent.join(' ').trim()
        }
        currentField = null
        currentContent = []
      }
    }

    // Handle any remaining content
    if (currentField && currentContent.length > 0) {
      if (currentField === 'tags') {
        entity[currentField] = currentContent
      } else {
        entity[currentField] = currentContent.join(' ').trim()
      }
    }

    // Validate required fields - size and alignment are now required
    if (
      !entity.name ||
      !entity.appearance ||
      !entity.race ||
      !entity.class_name ||
      !entity.size ||
      !entity.alignment
    ) {
      throw new Error(
        `Missing required fields for ${entityType.toLowerCase()}: ${entity.name || 'Unknown'}`
      )
    }

    return entity
  }

  const importEntitiesFromMarkdown = async (parsedEntities, createEntityFn) => {
    let successCount = 0
    const errors = []

    for (const entityData of parsedEntities) {
      try {
        await createEntityFn(entityData)
        successCount++
      } catch (err) {
        // Extract more detailed error information
        let errorMessage = `Failed to create ${entityData.name || `Unknown ${entityType}`}`

        if (err.response && err.response.data) {
          // Handle API validation errors
          if (err.response.data.detail) {
            if (Array.isArray(err.response.data.detail)) {
              // Pydantic validation errors
              const validationErrors = err.response.data.detail
                .map((detail) => {
                  const field = detail.loc ? detail.loc.join('.') : 'unknown field'
                  return `${field}: ${detail.msg}`
                })
                .join(', ')
              errorMessage += ` - Validation errors: ${validationErrors}`
            } else {
              errorMessage += ` - ${err.response.data.detail}`
            }
          } else {
            errorMessage += ` - ${JSON.stringify(err.response.data)}`
          }
        } else if (err.message) {
          errorMessage += ` - ${err.message}`
        } else {
          errorMessage += ' - Unknown error occurred'
        }

        errors.push(errorMessage)
        console.error(`Failed to create ${entityType.toLowerCase()} ${entityData.name}:`, err)
      }
    }

    return { successCount, errors }
  }

  const handleImportFile = async (event, createEntityFn, onSuccess, onError) => {
    const file = event.target.files[0]
    if (!file) return

    try {
      importing.value = true

      const content = await readFileContent(file)
      const parsedEntities = parseMarkdownEntities(content)

      if (parsedEntities.length === 0) {
        onError(`No valid ${entityType.toLowerCase()}s found in the markdown file`)
        return
      }

      const { successCount, errors } = await importEntitiesFromMarkdown(
        parsedEntities,
        createEntityFn
      )

      // Reset file input
      event.target.value = ''

      // Show results with detailed error information
      if (successCount > 0) {
        const message = `Successfully imported ${successCount} ${entityType.toLowerCase()}${successCount > 1 ? 's' : ''}`
        if (errors.length > 0) {
          onError(
            `${message}. However, ${errors.length} ${entityType.toLowerCase()}${errors.length > 1 ? 's' : ''} failed to import:\n\n${errors.join('\n\n')}`
          )
        } else {
          onSuccess(message)
        }
      } else {
        onError(
          `Import failed - no ${entityType.toLowerCase()}s were successfully imported:\n\n${errors.join('\n\n')}`
        )
      }
    } catch (err) {
      onError(`Import failed: ${err.message}`)
      console.error('Import error:', err)
    } finally {
      importing.value = false
    }
  }

  return {
    importing,
    handleImportFile,
  }
}
