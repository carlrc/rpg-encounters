type EncounterStatusTextOptions = {
  isRecording: boolean
  isChallengeMode: boolean
  hasSelectedSkill: boolean
}

export const getEncounterStatusText = (options: EncounterStatusTextOptions) => {
  const { isRecording, isChallengeMode, hasSelectedSkill } = options

  if (isRecording) return 'Listening... Tap Stop when done'
  if (isChallengeMode && !hasSelectedSkill) return 'Select a skill for challenge'
  if (isChallengeMode) return 'Tap Speak to start challenge'
  return 'Tap Speak to start conversation'
}
