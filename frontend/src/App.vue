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
    const audioQueue = ref([])
    const isPlaying = ref(false)

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
        const data = JSON.parse(event.data)
        
        if (data.type === 'audio_chunk') {
          // Receive audio response chunks and queue them for playback
          audioQueue.value.push(data.audio)
          if (!isPlaying.value) {
            playNextAudioChunk()
          }
        } else if (data.type === 'transcription') {
          console.log('Transcription:', data.text)
        } else if (data.type === 'response_complete') {
          isProcessing.value = false
        }
      }
      
      websocket.value.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      websocket.value.onclose = () => {
        console.log('WebSocket disconnected')
      }
    }

    const playNextAudioChunk = async () => {
      if (audioQueue.value.length === 0) {
        isPlaying.value = false
        return
      }
      
      isPlaying.value = true
      const audioData = audioQueue.value.shift()
      
      try {
        // Convert base64 audio data to blob and play
        const audioBlob = new Blob([Uint8Array.from(atob(audioData), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl)
          playNextAudioChunk()
        }
        
        await audio.play()
      } catch (error) {
        console.error('Error playing audio:', error)
        playNextAudioChunk()
      }
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
      
      // Send END signal to backend before closing WebSocket
      if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
        websocket.value.send("END")
        // Give a small delay to ensure the message is sent before closing
        setTimeout(() => {
          if (websocket.value) {
            websocket.value.close()
            websocket.value = null
          }
        }, 100)
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
