import { ref } from 'vue'
import { describe, expect, it } from 'vitest'
import { useEncounterGraphOps } from '../../src/composables/encounters/useEncounterGraphOps.js'

const countPlayerAssignments = (elements) => {
  const counts = new Map()

  for (const element of elements) {
    if (element.type !== 'encounter') continue

    for (const player of element.data?.players || []) {
      counts.set(player.id, (counts.get(player.id) || 0) + 1)
    }
  }

  return counts
}

describe('useEncounterGraphOps', () => {
  it('Iterating adjusted encounters keeps each player assigned to at most one encounter', () => {
    const players = ref([
      { id: 1, name: 'Player One' },
      { id: 2, name: 'Player Two' },
      { id: 3, name: 'Player Three' },
    ])

    const characters = ref([])
    const elements = ref([
      {
        id: '1',
        type: 'encounter',
        data: {
          players: [players.value[0], players.value[1]],
        },
      },
      {
        id: '2',
        type: 'encounter',
        data: {
          players: [players.value[1], players.value[2]],
        },
      },
      {
        id: '3',
        type: 'encounter',
        data: {
          players: [players.value[0]],
        },
      },
    ])

    const { addPlayerToEncounter } = useEncounterGraphOps({ elements, characters, players })

    // DM-style adjustments that should normalize duplicates by reassignment.
    addPlayerToEncounter('3', 2)
    addPlayerToEncounter('2', 1)

    const counts = countPlayerAssignments(elements.value)
    for (const count of counts.values()) {
      expect(count).toBeLessThanOrEqual(1)
    }

    const encounterOne = elements.value.find((element) => element.id === '1')
    const encounterTwo = elements.value.find((element) => element.id === '2')
    const encounterThree = elements.value.find((element) => element.id === '3')

    expect(encounterOne.data.players.map((player) => player.id)).toEqual([])
    expect(encounterTwo.data.players.map((player) => player.id)).toEqual([3, 1])
    expect(encounterThree.data.players.map((player) => player.id)).toEqual([2])
  })
})
