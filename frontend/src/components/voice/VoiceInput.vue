<!-- VoiceInput.vue - 语音输入录音按钮 -->
<template>
  <el-tooltip :content="!supported ? '浏览器不支持录音' : (recording ? '点击停止录音' : '点击开始录音')" placement="top">
    <button :class="['voice-btn', { recording, disabled: disabled || !supported }]" :disabled="disabled || !supported" @click="toggle">
      <el-icon :size="18"><Microphone /></el-icon>
      <span v-if="recording" class="recording-text">{{ countdown }}s</span>
    </button>
  </el-tooltip>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone } from '@element-plus/icons-vue'
import { recognizeSpeech } from '@/api/audio'

const props = defineProps({ disabled: Boolean })
const emit = defineEmits(['recognized'])

const supported = !!((window.MediaRecorder || window.webkitMediaRecorder) && navigator.mediaDevices?.getUserMedia)
const recording = ref(false)
const countdown = ref(15)
let mediaRecorder = null
let chunks = []
let timer = null

async function toggle() {
  if (recording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const MR = window.MediaRecorder || window.webkitMediaRecorder
    mediaRecorder = new MR(stream, { mimeType: 'audio/webm' })
    chunks = []

    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data) }
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop())
      const blob = new Blob(chunks, { type: 'audio/webm' })
      const file = new File([blob], 'recording.webm', { type: 'audio/webm' })
      try {
        const res = await recognizeSpeech(file)
        const text = res.data?.data?.text || ''
        if (text) {
          emit('recognized', { text })
        } else {
          ElMessage.warning('未识别到语音内容')
        }
      } catch (e) {
        ElMessage.error('语音识别失败')
      }
    }

    mediaRecorder.start()
    recording.value = true
    countdown.value = 15
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) stopRecording()
    }, 1000)
  } catch (e) {
    ElMessage.error('无法访问麦克风')
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  recording.value = false
  clearInterval(timer)
}

onUnmounted(() => {
  clearInterval(timer)
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.voice-btn {
  width: 40px; height: 40px; border-radius: 50%; border: 2px solid $gold-border;
  background: $rice-paper; cursor: pointer; display: flex; flex-direction: column;
  align-items: center; justify-content: center; position: relative; transition: all 0.3s;
  color: $gold-dark;
  &:hover:not(.disabled) { border-color: $gold; box-shadow: 0 0 12px rgba($gold, 0.2); }
  &.recording {
    border-color: $vermilion; background: $vermilion-bg; color: $vermilion;
    animation: pulse 1.2s infinite;
  }
  &.disabled { opacity: 0.4; cursor: not-allowed; }
  .recording-text { font-size: 10px; line-height: 1; }
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba($vermilion, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba($vermilion, 0); }
}
</style>
