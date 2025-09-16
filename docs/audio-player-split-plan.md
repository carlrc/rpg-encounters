Title: Split Plan for HTTP vs WebSocket Audio Players with Simplified Usage

Objective
- Split the current audio handling into two focused modules with explicit and minimal APIs.
- Make WebSocket streaming usage linear and predictable:
  init with first chunk -> append chunks -> play -> end (audio complete) or stop (force stop).
- Keep HTTP response playback separate and simple (buffered Blob playback).
- Remove ambiguous maybe* behaviors from component usage; any internal queuing remains encapsulated.

Why this change
- Current implementation in [useAudioPlayer()](frontend/src/composables/useAudioPlayer.js:1) mixes concerns and exposes internals through activeAudio, leading to complex component code such as [processAudioChunk](frontend/src/components/CharacterEncounterPopup.vue:438-448) and [CONTROL.AUDIO_COMPLETE](frontend/src/components/CharacterEncounterPopup.vue:353-362).
- This split clarifies responsibilities and simplifies component usage while retaining progressive playback performance.

Deliverables
- New modules:
  - [frontend/src/composables/audio/WebSocketStreamPlayer.js](frontend/src/composables/audio/WebSocketStreamPlayer.js)
  - [frontend/src/composables/audio/HttpAudioPlayer.js](frontend/src/composables/audio/HttpAudioPlayer.js)
- Updates to components:
  - [CharacterEncounterPopup.vue](frontend/src/components/CharacterEncounterPopup.vue)
  - [VoiceSelector.vue](frontend/src/components/VoiceSelector.vue)
  - [CharacterCard.vue](frontend/src/components/CharacterCard.vue)
- Optional: make [useAudioPlayer()](frontend/src/composables/useAudioPlayer.js:1) a thin wrapper with deprecations.

Module APIs

A) WebSocket progressive streaming player
- File: [WebSocketStreamPlayer.js](frontend/src/composables/audio/WebSocketStreamPlayer.js)
- Purpose: Progressive playback of MPEG-4 AAC chunks over MediaSource with explicit control.
- Public API (no implicit auto-start, no maybe* methods):
  - [WebSocketStreamPlayer.constructor()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - Options: { mimeType = 'audio/mp4; codecs=mp4a.40.2', onError, onLoadedData, onEnded, onPlaybackStart }
  - [WebSocketStreamPlayer.initWithFirstChunk()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - Initializes MediaSource and SourceBuffer and appends the first chunk. Accepts ArrayBuffer or Blob.
  - [WebSocketStreamPlayer.append()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - Appends subsequent chunks in order (encapsulates any internal queuing).
  - [WebSocketStreamPlayer.play()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - Explicitly starts playback once the first chunk is in the buffer.
  - [WebSocketStreamPlayer.end()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - Indicates no more data; drains any queued chunks, then finalizes the MediaSource.
  - [WebSocketStreamPlayer.stop()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - Force stop and cleanup immediately (used when user navigates away, closes popup, etc.).
- Notes:
  - The component decides when to call play() and end() versus stop().
  - Internals may use updateend-driven appends, but this complexity is not exposed.

B) HTTP buffered audio player
- File: [HttpAudioPlayer.js](frontend/src/composables/audio/HttpAudioPlayer.js)
- Purpose: Buffered playback of small/short audio assets such as voice preview samples.
- Public API:
  - [HttpAudioPlayer.constructor()](frontend/src/composables/audio/HttpAudioPlayer.js)
    - Options: { onError, onLoadedData, onEnded, onPlaybackStart }
  - [HttpAudioPlayer.playResponse()](frontend/src/composables/audio/HttpAudioPlayer.js)
    - Takes a Fetch Response, converts to Blob, creates an object URL, and plays via an Audio element.
  - [HttpAudioPlayer.playBlob()](frontend/src/composables/audio/HttpAudioPlayer.js)
    - Plays a provided Blob directly.
  - [HttpAudioPlayer.stop()](frontend/src/composables/audio/HttpAudioPlayer.js)
    - Stops playback and revokes the object URL. Safe to call multiple times.

Component Migrations

1) CharacterEncounterPopup (WebSocket progressive)
- File: [CharacterEncounterPopup.vue](frontend/src/components/CharacterEncounterPopup.vue)
- Replace usage of [useAudioPlayer()](frontend/src/composables/useAudioPlayer.js:1) and activeAudio with a local WebSocketStreamPlayer instance.
- New usage pattern:
  - On first audio chunk (currently handled in [processAudioChunk](frontend/src/components/CharacterEncounterPopup.vue:438-448)):
    - if (!player) player = new [WebSocketStreamPlayer.constructor()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - await [WebSocketStreamPlayer.initWithFirstChunk()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
    - await [WebSocketStreamPlayer.play()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
  - On subsequent chunks:
    - await [WebSocketStreamPlayer.append()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
  - On AUDIO_COMPLETE control token (currently handled in [CONTROL.AUDIO_COMPLETE](frontend/src/components/CharacterEncounterPopup.vue:353-362)):
    - await [WebSocketStreamPlayer.end()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
  - On popup close or unmount (currently stops audio in [onUnmounted](frontend/src/components/CharacterEncounterPopup.vue:665-674)):
    - await [WebSocketStreamPlayer.stop()](frontend/src/composables/audio/WebSocketStreamPlayer.js)
- Outcome: linear and explicit flow; no reliance on maybeAppend or internal appendChunk exposure.

2) VoiceSelector and CharacterCard (HTTP buffered)
- Files:
  - [VoiceSelector.vue](frontend/src/components/VoiceSelector.vue)
  - [CharacterCard.vue](frontend/src/components/CharacterCard.vue)
- Replace composable usage with a local HttpAudioPlayer instance:
  - Before playing a new sample:
    - await [HttpAudioPlayer.stop()](frontend/src/composables/audio/HttpAudioPlayer.js)
  - Play:
    - const response = await getVoiceSample(...)
    - await [HttpAudioPlayer.playResponse()](frontend/src/composables/audio/HttpAudioPlayer.js)
  - On unmount:
    - await [HttpAudioPlayer.stop()](frontend/src/composables/audio/HttpAudioPlayer.js)
- This mirrors existing behavior but removes dependency on the mixed composable.

3) useAudioPlayer composable
- File: [useAudioPlayer.js](frontend/src/composables/useAudioPlayer.js)
- Make this optional convenience (thin wrapper or re-exports) and mark legacy methods as deprecated in comments.
- Provide factory helpers to construct the new players if we still want a single import point.

Sequence Diagrams

WebSocket progressive path
sequenceDiagram
  participant WS as WebSocket
  participant CMP as Component
  participant WSP as WebSocketStreamPlayer
  participant AUD as Audio

  WS -> CMP: first Blob chunk
  CMP -> WSP: initWithFirstChunk
  CMP -> WSP: play
  loop chunks
    WS -> CMP: next Blob chunk
    CMP -> WSP: append
  end
  WS -> CMP: AUDIO_COMPLETE
  CMP -> WSP: end
  AUD -> CMP: ended

  CMP -> WSP: stop (on user dismiss)

HTTP buffered path
sequenceDiagram
  participant API as HTTP
  participant CMP as Component
  participant HAP as HttpAudioPlayer
  participant AUD as Audio

  CMP -> API: getVoiceSample
  API --> CMP: Response
  CMP -> HAP: playResponse
  AUD -> CMP: onLoadedData, onPlaybackStart
  AUD -> CMP: ended
  CMP -> HAP: stop (on unmount or next preview)

Acceptance Criteria
- CharacterEncounterPopup uses an explicit linear sequence:
  initWithFirstChunk -> append -> play -> end -> stop.
- Voice previews use a small, independent HTTP player with stop-before-play and unmount cleanup.
- No maybeAppend/maybePlay/maybeStop decisions leak to components; they call explicit methods.
- Browsers without MediaSource still allow HTTP previews; WebSocket path throws a clear error via onError.
- Code is split into the two new files and components are migrated without regressions.

Implementation Steps
1) Add [WebSocketStreamPlayer.js](frontend/src/composables/audio/WebSocketStreamPlayer.js) with the explicit API.
2) Add [HttpAudioPlayer.js](frontend/src/composables/audio/HttpAudioPlayer.js) with playResponse, playBlob, stop.
3) Migrate [CharacterEncounterPopup.vue](frontend/src/components/CharacterEncounterPopup.vue) to use WebSocketStreamPlayer with the linear pattern.
4) Migrate [VoiceSelector.vue](frontend/src/components/VoiceSelector.vue) and [CharacterCard.vue](frontend/src/components/CharacterCard.vue) to use HttpAudioPlayer.
5) Convert [useAudioPlayer()](frontend/src/composables/useAudioPlayer.js:1) into a thin wrapper or re-exports; mark legacy methods deprecated.
6) Smoke test progressive playback, end vs stop behavior, and preview playback lifecycle.

Migration Notes and Touchpoints
- Replace progressive flow in [processAudioChunk](frontend/src/components/CharacterEncounterPopup.vue:438-448) and [CONTROL.AUDIO_COMPLETE](frontend/src/components/CharacterEncounterPopup.vue:353-362) with WebSocketStreamPlayer calls.
- Replace preview playback in:
  - [VoiceSelector.vue playSample](frontend/src/components/VoiceSelector.vue:338-358)
  - [CharacterCard.vue playCharacterVoiceSample](frontend/src/components/CharacterCard.vue:648-661)
- Keep the current user experience while simplifying the code paths.

Post-Implementation Cleanup
- Remove any now-unused legacy fields and methods from [useAudioPlayer()](frontend/src/composables/useAudioPlayer.js:1) after verifying all call sites are migrated.
- Update inline comments to reflect the new flow and responsibilities.

Request for Approval
- Confirm this plan. Upon approval, proceed to:
  - Create the two new files.
  - Update the three components.
  - Simplify [useAudioPlayer.js](frontend/src/composables/useAudioPlayer.js) as a thin layer with deprecations.