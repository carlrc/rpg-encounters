Title: Refactor Plan for Progressive Audio Composable

Scope
This plan proposes targeted refactors to improve maintainability, clarity, and robustness of progressive audio playback in [useAudioPlayer()](frontend/src/composables/useAudioPlayer.js:7). It focuses on:
- Separating concerns between transport, buffering, and playback
- Replacing polling loops with event-driven flow control
- Unifying WebSocket and REST streaming semantics
- Tightening lifecycle and session invalidation
- Simplifying the public API used by components consuming this composable

Current Pain Points Observed
1) Mixed concerns and implicit state coupling
- The composable mixes: session management, MediaSource wiring, Audio element lifecycle, buffer control, and consumer-facing API. This makes it harder to reason about responsibilities and failure modes.
  - Example: [supportsMediaSource()](frontend/src/composables/useAudioPlayer.js:23), [playWebSocketAudio()](frontend/src/composables/useAudioPlayer.js:51), [playStreamingResponse()](frontend/src/composables/useAudioPlayer.js:436), [cleanup()](frontend/src/composables/useAudioPlayer.js:500).
- A nested player class [MediaSourceAudioPlayer](frontend/src/composables/useAudioPlayer.js:90) is tightly coupled to composable state via session checks and callbacks. The class is good encapsulation, but it still reaches back into composable semantics.

2) Polling loops for readiness cause busy waiting and complexity
- Functions like [appendChunk()](frontend/src/composables/useAudioPlayer.js:266) spin on while loops for readiness checks:
  - Waiting for MediaSource to open and SourceBuffer to be available
  - Waiting for sourceBuffer.updating to be false
- This increases complexity, introduces timing hazards, and can waste CPU on slower devices.

3) End-of-stream and finalization timing is spread out
- End-of-stream signaling is split across [markStreamComplete()](frontend/src/composables/useAudioPlayer.js:292), [checkAndEndStream()](frontend/src/composables/useAudioPlayer.js:218), and [finalizeMediaSource()](frontend/src/composables/useAudioPlayer.js:340). This distribution makes it harder to see when the stream is actually done and under what conditions.

4) Public API exposes internal player implementation details through state.activeAudio
- Consumers write chunks via [activeAudio.appendChunk](frontend/src/composables/useAudioPlayer.js:423) and call [activeAudio.endStream](frontend/src/composables/useAudioPlayer.js:424) directly, effectively exposing internals. It would be clearer to return a dedicated, typed stream handle rather than mutating a shared state object.

5) Two distinct code paths for REST vs WebSocket with different mental models
- WebSocket path is progressive via MediaSource.
- REST path buffers the entire response as a Blob before playing, which is fine for short voice samples but creates a different API surface and lifecycle.
- Consumers in [CharacterEncounterPopup.vue](frontend/src/components/CharacterEncounterPopup.vue:438-448), [VoiceSelector.vue](frontend/src/components/VoiceSelector.vue:338-350), and [CharacterCard.vue](frontend/src/components/CharacterCard.vue:648-661) handle these differently.

6) Session invalidation spread across multiple places
- Use of currentSessionId UUID checks is sound, but enforcement is embedded across callbacks and methods. Centralizing invalidation through an AbortController-like mechanism would reduce conditionals sprinkled throughout.

Target Architecture: Three-Layer Model
- Transport: Responsible for receiving audio data as chunks from any source (WebSocket, fetch ReadableStream, other).
- Buffer Controller: Owns MediaSource, SourceBuffer, chunk queue, and flow control; exposes a simple sink interface to write chunks and signal end.
- Player: Owns the Audio element, playback state, and high-level lifecycle; coordinates with the Buffer Controller and exposes a minimal public API to the app.

Proposed Public API
Provide a single progressive streaming API and a simple sample-play API:

- Progressive path (WebSocket or any chunked source)
  const { createProgressiveStream, stop, state } = useAudioPlayer()
  const stream = await createProgressiveStream({
    id: string, // logical stream id for the UI
    mimeType?: string, // default audio/mp4; codecs=mp4a.40.2
    autostart?: boolean, // default true, start playback when first chunk committed
    audioElement?: HTMLAudioElement, // optional injection for testing or special cases
  })
  // Feed chunks
  await stream.write(arrayBuffer) // enqueue chunk
  // Signal no more chunks
  await stream.end()
  // Optional abort
  stream.abort(reason?)

- Buffered sample path (short voice previews)
  await playSampleResponse(response, id)

Notes:
- createProgressiveStream returns a handle with methods: write, end, abort, and a readonly id.
- Internally, state.activeStream is the current stream handle; avoid exposing internal player instance.
- For voice previews, keep the simple buffered flow, but consider using the same player/cleanup lifecycle for consistency.

Key Refactors

A) Replace polling with event-driven queue in Buffer Controller
- Introduce a FIFO queue of ArrayBuffer chunks, and only append when SourceBuffer is not updating.
- Drive the queue on sourcebuffer.updateend rather than spinning with setTimeout.
- Pseudocode:
  - on sourceopen: create SourceBuffer and attach events
  - on write: enqueue chunk, if not updating and not busy, append
  - on updateend: if queue not empty, append next; else if streamEnded is true, endOfStream
- Impacted areas: [appendChunk()](frontend/src/composables/useAudioPlayer.js:266), [setupSourceBufferEvents()](frontend/src/composables/useAudioPlayer.js:187), [finalizeMediaSource()](frontend/src/composables/useAudioPlayer.js:340), [markStreamComplete()](frontend/src/composables/useAudioPlayer.js:292).
- Benefit: avoids busy-wait, clearer backpressure handling, and deterministic finalization when queue is empty and streamEnded is set.

B) Isolate a reusable MediaSourceBufferController
- Extract logic from [MediaSourceAudioPlayer](frontend/src/composables/useAudioPlayer.js:90) into a standalone controller that:
  - Owns mediaSource, sourceBuffer, chunk queue, and end-of-stream
  - Exposes async write(chunk), end(), abort()
  - Emits events: onReady, onError, onEmptyQueueEnd
- The Player wraps this controller, creates the Audio element, and handles play() start, onended, errors, and cleanup.

C) Centralize session invalidation with AbortController-like token
- Replace scattered [isSessionValid()](frontend/src/composables/useAudioPlayer.js:32) checks with a token passed to the controller and player.
- On stop or cleanup, invalidate the token; all operations early-return if token is aborted.
- Maintain a monotonically increasing generation counter to avoid UUID lookups at hot paths; increment on each new createProgressiveStream.

D) Simplify lifecycle and cleanup with a single disposal path
- Expose a dispose() method on the internal Player that:
  - Pauses audio, detaches src, and calls mediaSource.endOfStream if needed
  - Revokes Object URLs safely after a microtask or slight delay (to avoid Empty src errors)
  - Clears event handlers
- The composable calls dispose() exactly once from stop() and from onUnmounted in the composable.
- Impacted areas: [invalidate()](frontend/src/composables/useAudioPlayer.js:314), [cleanup()](frontend/src/composables/useAudioPlayer.js:500), [stopAudio()](frontend/src/composables/useAudioPlayer.js:488).

E) Unify consumer semantics and method names
- Replace current pattern where components write through [activeAudio.appendChunk](frontend/src/composables/useAudioPlayer.js:423) and end via [activeAudio.endStream](frontend/src/composables/useAudioPlayer.js:424).
- New model:
  - useAudioPlayer exposes createProgressiveStream; returns stream handle
  - Store the handle locally in the component (not in reactive global state)
  - Component calls handle.write(chunk) and handle.end()
- Benefits:
  - Eliminates reliance on a mutable [activeAudio](frontend/src/composables/useAudioPlayer.js:573) bag object
  - Encourages clear ownership of playback lifecycle in the component using it
  - Reduces coupling and implicit state

F) Keep REST sample playback simple but make it consistent
- Keep buffering the entire blob for voice previews via a dedicated playSampleResponse(response, id) to keep it reliable and simple (small files).
- Still route Audio element creation and cleanup through the same Player disposal path so the lifecycle is unified.

G) Improve type safety and surface area
- Add JSDoc typedefs to document the StreamHandle shape and Player options clearly
- Optionally migrate composable to TypeScript for safer event-driven controller design

H) Observability hooks
- Add optional debug flag to emit metrics: chunks enqueued, appended, dropped, updateend count, and endOfStream called
- Log session generation transitions to diagnose races

Detailed Change Map and Migration Notes

Composable internal changes
1) Extract Buffer Controller
- New internal module: docs only in this plan; implementation would move core logic out of the class [MediaSourceAudioPlayer](frontend/src/composables/useAudioPlayer.js:90) into a MediaSourceBufferController with:
  - constructor(options: { mimeType, token, onReady, onError, onUpdateEnd })
  - async write(chunk)
  - async end()
  - abort()
- Replace [appendChunk()](frontend/src/composables/useAudioPlayer.js:266) and [markStreamComplete()](frontend/src/composables/useAudioPlayer.js:292) to delegate to controller.write and controller.end without polling.

2) Player rework
- Player owns:
  - Audio element, Object URL
  - MediaSourceBufferController instance
  - startPlayback semantics from [startPlayback()](frontend/src/composables/useAudioPlayer.js:230)
  - disposal path replacing [invalidate()](frontend/src/composables/useAudioPlayer.js:314) and parts of [cleanup()](frontend/src/composables/useAudioPlayer.js:500)
- A single onUpdateEnd handler triggers:
  - First-play attempt if not started
  - Finalization when controller reports streamEnded and queue is empty

3) Composable API
- Replace [playWebSocketAudio()](frontend/src/composables/useAudioPlayer.js:51) with:
  - createProgressiveStream({ id, mimeType?, autostart?, audioElement? })
    - Initializes Player and returns StreamHandle { id, write, end, abort }
- Keep [playStreamingResponse()](frontend/src/composables/useAudioPlayer.js:436) but rename to playSampleResponse for clarity and to indicate its buffered nature.
- Deprecate direct exposure of [activeAudio](frontend/src/composables/useAudioPlayer.js:573). Replace with a simple isActive boolean or activeStreamId string for UI state.

4) Session invalidation
- Replace [currentSessionId](frontend/src/composables/useAudioPlayer.js:15) UUID with a numeric generation counter. Store a token { generation, aborted } that is captured by Player and Controller.
- On stop(), increment generation and mark token.aborted = true to invalidate all in-flight operations without sprinkling isSessionValid checks everywhere.

Consumer changes

A) CharacterEncounterPopup.vue
- Current flow:
  - On first chunk: [processAudioChunk](frontend/src/components/CharacterEncounterPopup.vue:438-448) calls [playWebSocketAudio](frontend/src/components/CharacterEncounterPopup.vue:444), then uses [activeAudio.appendChunk](frontend/src/components/CharacterEncounterPopup.vue:447).
  - On control token AUDIO_COMPLETE: calls [activeAudio.endStream](frontend/src/components/CharacterEncounterPopup.vue:356-358).

- New flow:
  - Keep a local let streamHandle = null
  - On first chunk, if no streamHandle, streamHandle = await createProgressiveStream({ id: encounterId })
  - For each chunk: await streamHandle.write(arrayBuffer)
  - On AUDIO_COMPLETE: await streamHandle.end()
  - On popup close or unmount: call stop() from composable which disposes active playback

- Edit touchpoints:
  - Replace references to activeAudio.value?.appendChunk and activeAudio.value?.endStream with streamHandle.write and streamHandle.end
  - Locations: [processAudioChunk](frontend/src/components/CharacterEncounterPopup.vue:438-448) and [CONTROL.AUDIO_COMPLETE](frontend/src/components/CharacterEncounterPopup.vue:353-361)

B) VoiceSelector.vue and CharacterCard.vue
- These use [playStreamingResponse](frontend/src/components/VoiceSelector.vue:213-219) and [playStreamingResponse](frontend/src/components/CharacterCard.vue:413-415) for short previews.
- Rename usage to playSampleResponse but otherwise keep behavior.
- Locations to update:
  - [VoiceSelector.vue](frontend/src/components/VoiceSelector.vue:338-350)
  - [CharacterCard.vue](frontend/src/components/CharacterCard.vue:648-661)

Lifecycle and Cleanup Rules
- stop(): Disposes any active Player and Controller; revokes URLs; invalidates the token.
- onUnmounted of the composable: call stop() to ensure no leaks.
- Component-level unmount still calls composable.stop() as a safety net.

Error Handling Strategy
- Transport-level: Errors from WebSocket or fetch are handled by the component (transport). When ending early, call stream.abort(reason) or composable.stop()
- Buffer-level: Controller onError triggers composable setError and hard disposal
- Playback-level: Playback errors (audio.play) surface a clear user-facing error and disposal
- All errors funnel through a single onError(errorMessage) handler in the composable to maintain consistent state transitions

Backward Compatibility and Migration
- Provide a transitional shim:
  - Keep playWebSocketAudio deprecated; internally call createProgressiveStream and set state.activeStreamHandle for one release
  - Expose legacy adapters with the same shape as activeAudio.appendChunk and activeAudio.endStream to avoid breaking immediate callers
- Phase-out plan:
  1) Introduce createProgressiveStream and playSampleResponse, mark old APIs deprecated in JSDoc
  2) Update [CharacterEncounterPopup.vue](frontend/src/components/CharacterEncounterPopup.vue:438-448) to use the new StreamHandle
  3) Rename playStreamingResponse to playSampleResponse in [VoiceSelector.vue](frontend/src/components/VoiceSelector.vue:338-350) and [CharacterCard.vue](frontend/src/components/CharacterCard.vue:648-661)
  4) Remove legacy activeAudio accessors after downstream migration

Mermaid Sequence Diagram
sequenceDiagram
  participant WS as WS Transport
  participant CMP as Component
  participant COM as useAudioPlayer
  participant PLR as Player
  participant BUF as Buffer Controller
  participant AUD as Audio

  WS -> CMP: Blob chunk
  CMP -> COM: createProgressiveStream
  COM -> PLR: init Player with token
  PLR -> BUF: init MediaSource and queue
  BUF -> PLR: onReady

  loop for each chunk
    WS -> CMP: Blob chunk
    CMP -> COM: stream.write(ArrayBuffer)
    COM -> BUF: enqueue
    BUF -> BUF: append when not updating
    BUF -> PLR: updateend
    PLR -> AUD: try play once on first updateend
  end

  WS -> CMP: AUDIO_COMPLETE
  CMP -> COM: stream.end()
  COM -> BUF: mark streamEnded
  BUF -> BUF: when queue empty, endOfStream
  AUD -> PLR: onended
  PLR -> COM: disposal

Acceptance Criteria
- No polling loops remain in chunk ingestion path
- Progressive playback starts on first chunk reliably, without multiple play() calls
- endOfStream is called exactly once when streamEnded and queue is empty
- stop() disposes all resources and prevents further writes without errors
- CharacterEncounterPopup continues to progressively play as chunks arrive
- Voice previews work unchanged other than method rename
- Errors during any stage result in a consistent error state and proper cleanup

Test Strategy
- Unit tests (with fake MediaSource and SourceBuffer):
  - Enqueue many chunks quickly; ensure no busy-wait, all chunks appended in order
  - Call end() with non-empty queue; ensure endOfStream waits for queue to drain
  - Abort mid-stream; ensure no further appends and resources cleaned
  - Playback start called once upon first updateend
- Integration tests:
  - WebSocket simulated transport feeds chunks at varied pacing; verify continuous audio and correct end
  - REST sample remains functional and is cleaned up properly
- Race tests:
  - Start a second stream quickly after the first; ensure the first is invalidated and cannot write
  - Component unmount during streaming triggers stop and no leaks

Implementation Outline
- Step 1: Introduce the new API and internals
  - Create Buffer Controller class
  - Refactor Player to use queue and event-driven appends
  - Wire composable createProgressiveStream and playSampleResponse
- Step 2: Add shims for backward compatibility
  - Implement playWebSocketAudio in terms of the new API
  - Expose a temporary adapter on state for appendChunk and endStream if necessary
- Step 3: Migrate consumers
  - Update [CharacterEncounterPopup.vue](frontend/src/components/CharacterEncounterPopup.vue:438-448) to use StreamHandle
  - Rename playStreamingResponse to playSampleResponse in [VoiceSelector.vue](frontend/src/components/VoiceSelector.vue:338-350) and [CharacterCard.vue](frontend/src/components/CharacterCard.vue:648-661)
- Step 4: Remove deprecated paths, finalize types and docs

Risks and Mitigations
- Timing differences around endOfStream
  - Mitigate with strict condition: only when streamEnded and queue empty
- Browser quirks with MediaSource
  - Maintain the slight delay before URL revoke for MediaSource case; encapsulate in Player.dispose
- Complexity creep
  - Keep strict separation between Buffer Controller, Player, and Composable; small, documented interfaces

Summary
This refactor streamlines progressive playback by introducing a queue-driven, event-based buffer controller, clarifying ownership and lifecycle, and presenting a minimal, consistent API to components. It removes busy-wait loops, tightens session invalidation, and unifies cleanup to be robust and predictable, while keeping voice sample playback simple and reliable.