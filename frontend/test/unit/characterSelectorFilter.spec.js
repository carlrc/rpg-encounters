import { describe, expect, it } from 'vitest'
import {
  buildVisibleCharacterOptions,
  filterCharactersByAttributes,
  normalizeCharacterIds,
} from '../../src/utils/characterSelectorFilter.js'

const characters = [
  { id: 1, name: 'Aria', race: 'Elf', alignment: 'Chaotic Good' },
  { id: 2, name: 'Borin', race: 'Dwarf', alignment: 'Lawful Neutral' },
  { id: 3, name: 'Cade', race: 'Human', alignment: 'Chaotic Good' },
]

describe('characterSelectorFilter', () => {
  it('No filters returns all characters', () => {
    const result = filterCharactersByAttributes(characters, { race: [], alignment: [] })
    expect(result.map((c) => c.id)).toEqual([1, 2, 3])
  })

  it('Race filter hides nonmatching characters', () => {
    const result = filterCharactersByAttributes(characters, { race: ['Elf'], alignment: [] })
    expect(result.map((c) => c.id)).toEqual([1])
  })

  it('Alignment filter hides nonmatching characters', () => {
    const result = filterCharactersByAttributes(characters, {
      race: [],
      alignment: ['Lawful Neutral'],
    })
    expect(result.map((c) => c.id)).toEqual([2])
  })

  it('Race + alignment filters use AND behavior', () => {
    const result = filterCharactersByAttributes(characters, {
      race: ['Human', 'Elf'],
      alignment: ['Chaotic Good'],
    })
    expect(result.map((c) => c.id)).toEqual([1, 3])
  })

  it('Selected hidden IDs are preserved externally (no mutation)', () => {
    const selectedModelValue = [2]
    const before = [...selectedModelValue]

    const visibleOptions = buildVisibleCharacterOptions({
      characters,
      filters: { race: ['Elf'], alignment: [] },
      showNoCharactersOption: false,
    })

    expect(visibleOptions.map((o) => o.value)).toEqual([1])
    expect(selectedModelValue).toEqual(before)
  })

  it('Clearing filters restores previously hidden selected visibility', () => {
    const filteredOptions = buildVisibleCharacterOptions({
      characters,
      filters: { race: ['Elf'], alignment: [] },
    })
    expect(filteredOptions.map((o) => o.value)).toEqual([1])

    const clearedOptions = buildVisibleCharacterOptions({
      characters,
      filters: { race: [], alignment: [] },
    })
    expect(clearedOptions.map((o) => o.value)).toEqual([1, 2, 3])
  })

  it('normalizeCharacterIds normalizes mixed string/number IDs', () => {
    const result = normalizeCharacterIds([1, '2', 'no-characters', 'abc', 3])
    expect(result).toEqual([1, 2, 3])
  })

  it('Sentinel option is included when requested', () => {
    const options = buildVisibleCharacterOptions({
      characters,
      filters: { race: [], alignment: [] },
      showNoCharactersOption: true,
    })

    expect(options[0]).toEqual({
      label: 'NONE - Select items with no assignments',
      value: 'no-characters',
      excludeFromSelectAll: true,
    })
    expect(options.slice(1).map((o) => o.value)).toEqual([1, 2, 3])
  })
})
