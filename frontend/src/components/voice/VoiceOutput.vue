<!-- VoiceOutput.vue - 语音播放按钮 -->
<template>
  <el-tooltip :content="playing ? '播放中...' : '朗读此条消息'" placement="top">
    <button :class="['voice-play-btn', { playing }]" :disabled="!text" @click="play">
      <el-icon :size="14"><component :is="playing ? Loading : Microphone" /></el-icon>
    </button>
  </el-tooltip>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone, Loading } from '@element-plus/icons-vue'

const props = defineProps({ text: { type: String, default: '' } })
const playing = ref(false)

async function play() {
  if (!props.text || playing.value) return
  playing.value = true

  // 浏览器内置 TTS（无需 API Key，优先使用）
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(props.text.slice(0, 300))
    u.lang = 'zh-CN'
    u.rate = 1.0
    u.onend = () => { playing.value = false }
    u.onerror = () => { playing.value = false; ElMessage.error('语音播放失败') }
    window.speechSynthesis.speak(u)
    return
  }

  // 后端 TTS（需要阿里云 API Key）
  try {
    const { synthesizeSpeech } = await import('@/api/audio')
    const res = await synthesizeSpeech(props.text.slice(0, 300))
    const b64 = res.data?.data?.audio_base64
    if (!b64) { playing.value = false; ElMessage.warning('语音合成失败'); return }
    const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0))
    const blob = new Blob([bytes], { type: 'audio/mp3' })
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    audio.onended = () => { playing.value = false; URL.revokeObjectURL(url) }
    audio.onerror = () => { playing.value = false; URL.revokeObjectURL(url) }
    await audio.play()
  } catch (e) {
    playing.value = false
    ElMessage.error('语音播放失败')
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.voice-play-btn {
  width: 28px; height: 28px; border-radius: 50%; border: 1px solid $gold-border;
  background: transparent; cursor: pointer; display: inline-flex; align-items: center;
  justify-content: center; color: $gold-dark; transition: all 0.2s;
  &:hover { border-color: $gold; color: $gold; }
  &.playing { border-color: $vermilion; color: $vermilion; animation: playPulse 1s infinite; }
  &:disabled { opacity: 0.3; cursor: default; }
}
@keyframes playPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
