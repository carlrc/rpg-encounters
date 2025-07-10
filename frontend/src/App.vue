<template>
  <div class="container">
    <h1 class="title">D&D AI Character</h1>
    
    <div class="audio-visualizer" v-if="isRecording">
      <div 
        v-for="i in 20" 
        :key="i" 
        class="audio-bar" 
        :style="{ height: audioLevels[i] || '4px' }"
      ></div>
    </div>
    
    <button 
      @click="toggleRecording" 
      :class="['start-button', { recording: isRecording }]"
      :disabled="isProcessing"
    >
      {{ buttonText }}
    </button>
    
    <div :class="['status', { recording: isRecording, processing: isProcessing }]">
      {{ statusText }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const isRecording = ref(false)
    const isProcessing = ref(false)
    const websocket = ref(null)
    const mediaRecorder = ref(null)
    const audioContext = ref(null)
    const analyser = ref(null)
    const audioLevels = ref(Array(20).fill('4px'))
    const audioChunks = ref([])

    const buttonText = computed(() => {
      if (isProcessing.value) return 'Processing...'
      return isRecording.value ? 'Stop' : 'Start'
    })

    const statusText = computed(() => {
      if (isProcessing.value) return 'Processing your message...'
      if (isRecording.value) return 'Listening... Click Stop when done'
      return 'Click Start to begin conversation'
    })

    const connectWebSocket = () => {
      // Connect to backend websocket (adjust URL as needed)
      websocket.value = new WebSocket('ws://localhost:8000/ws')
      
      websocket.value.onopen = () => {
        console.log('WebSocket connected')
      }
      
      websocket.value.onmessage = (event) => {
        if (event.data instanceof Blob) {
          // Received binary audio chunk
          console.log('Received audio chunk:', event.data.size, 'bytes')
          processAudioChunk(event.data)
        } else if (typeof event.data === 'string') {
          // Received text message
          if (event.data === 'AUDIO_COMPLETE') {
            console.log('Audio streaming complete')
            playAccumulatedAudio()
            isProcessing.value = false
            // Close WebSocket after receiving completion signal
            if (websocket.value) {
              websocket.value.close()
              websocket.value = null
            }
          } else {
            console.log('Received text message:', event.data)
          }
        }
      }
      
      websocket.value.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      websocket.value.onclose = () => {
        console.log('WebSocket disconnected')
      }
    }

    const processAudioChunk = (audioBlob) => {
      // Simply collect audio chunks
      audioChunks.value.push(audioBlob)
      console.log('Collected audio chunk:', audioBlob.size, 'bytes')
    }

    const playAccumulatedAudio = () => {
      if (audioChunks.value.length === 0) {
        console.log('No audio chunks to play')
        return
      }
      
      try {
        // Combine all chunks into single blob
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/mpeg' })
        console.log('Playing combined audio:', audioBlob.size, 'bytes')
        
        // Create object URL and play with Audio element
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl)
          console.log('Audio playback completed')
        }
        
        audio.onerror = (error) => {
          console.error('Audio playback error:', error)
          URL.revokeObjectURL(audioUrl)
        }
        
        audio.play().catch(error => {
          console.error('Failed to play audio:', error)
          URL.revokeObjectURL(audioUrl)
        })
        
      } catch (error) {
        console.error('Error creating audio blob:', error)
      }
      
      // Clear chunks for next response
      audioChunks.value = []
    }

    const startRecording = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
          } 
        })
        
        // Set up audio visualization
        audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
        analyser.value = audioContext.value.createAnalyser()
        const source = audioContext.value.createMediaStreamSource(stream)
        source.connect(analyser.value)
        
        analyser.value.fftSize = 64
        const bufferLength = analyser.value.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        
        const updateVisualization = () => {
          if (!isRecording.value) return
          
          analyser.value.getByteFrequencyData(dataArray)
          const levels = []
          
          for (let i = 0; i < 20; i++) {
            const value = dataArray[Math.floor(i * bufferLength / 20)]
            const height = Math.max(4, (value / 255) * 60)
            levels.push(`${height}px`)
          }
          
          audioLevels.value = levels
          requestAnimationFrame(updateVisualization)
        }
        
        updateVisualization()
        
        // Set up media recorder to send audio chunks
        mediaRecorder.value = new MediaRecorder(stream, {
          mimeType: 'audio/webm;codecs=opus'
        })
        
        mediaRecorder.value.ondataavailable = (event) => {
          if (event.data.size > 0 && websocket.value?.readyState === WebSocket.OPEN) {
            // Send raw binary audio data directly
            websocket.value.send(event.data)
          }
        }
        
        // Send audio chunks every 250ms for real-time processing
        mediaRecorder.value.start(250)
        isRecording.value = true
        
      } catch (error) {
        console.error('Error starting recording:', error)
        alert('Could not access microphone. Please check permissions.')
      }
    }

    const stopRecording = () => {
      if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
        mediaRecorder.value.stop()
        mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
      }
      
      if (audioContext.value) {
        audioContext.value.close()
      }
      
      isRecording.value = false
      isProcessing.value = true
      
      // Let the backend close it after streaming is complete
      if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
        websocket.value.send("END")
      }
    }

    const toggleRecording = () => {
      if (isRecording.value) {
        stopRecording()
      } else {
        // Connect WebSocket before starting recording
        if (!websocket.value) {
          connectWebSocket()
        }
        startRecording()
      }
    }

    onMounted(() => {
      connectWebSocket()
    })

    onUnmounted(() => {
      if (websocket.value) {
        websocket.value.close()
      }
      if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
        mediaRecorder.value.stop()
      }
      if (audioContext.value) {
        audioContext.value.close()
      }
      // Clear any remaining audio chunks
      audioChunks.value = []
    })

    return {
      isRecording,
      isProcessing,
      buttonText,
      statusText,
      audioLevels,
      toggleRecording
    }
  }
}
</script>
