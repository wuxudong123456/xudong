<!-- SocialAssistant.vue - 社交助手页面（社交僚机 / 话术生成 / 情书代写 / 聊天辅助） -->
<template>
  <div class="social-assistant">
    <el-card class="sa-header" shadow="never">
      <el-row align="middle">
        <el-col :span="2" style="text-align:center"><span style="font-size:40px">💘</span></el-col>
        <el-col :span="22">
          <h3 style="margin:0 0 4px">八戒社交僚机</h3>
          <p style="color:#909399;font-size:13px;margin:0">
            俺老猪在高老庄那也是情场老手！帮你出谋划策、代写情书、聊天助攻，包你桃花运旺！
          </p>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" style="flex:1">
      <!-- 话术生成 -->
      <el-col :span="12">
        <el-card shadow="never" class="sa-card">
          <template #header><span><el-icon><ChatLineSquare /></el-icon> 聊天话术生成</span></template>
          <el-form label-width="90px">
            <el-form-item label="场景">
              <el-select v-model="scenario" style="width:100%">
                <el-option label="初次搭讪" value="first_meet" />
                <el-option label="暧昧升温" value="flirt" />
                <el-option label="道歉求和" value="apologize" />
                <el-option label="日常关心" value="care" />
                <el-option label="约会邀约" value="invite" />
                <el-option label="表白心意" value="confess" />
              </el-select>
            </el-form-item>
            <el-form-item label="对方性格">
              <el-select v-model="personality" style="width:100%">
                <el-option label="活泼开朗" value="outgoing" />
                <el-option label="文静内敛" value="shy" />
                <el-option label="独立强势" value="independent" />
                <el-option label="温柔体贴" value="gentle" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注信息">
              <el-input v-model="extraInfo" type="textarea" :rows="2" placeholder="对方的兴趣爱好、你们的关系等..." />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="generateLines" :loading="generating" style="width:100%">
                🐷 八戒帮我想话术</el-button>
            </el-form-item>
          </el-form>
          <div v-if="generatedLines" class="generated-result">
            <el-divider />
            <h4>俺老猪给你支几招：</h4>
            <div v-for="(line, i) in generatedLines" :key="i" class="line-item">
              <p>{{ line }}</p>
              <el-button link size="small" @click="copyText(line)">复制</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      <!-- 情书代写 -->
      <el-col :span="12">
        <el-card shadow="never" class="sa-card">
          <template #header><span><el-icon><Postcard /></el-icon> 情书代写</span></template>
          <el-form label-width="90px">
            <el-form-item label="对方昵称">
              <el-input v-model="loveLetter.to" placeholder="如: 小芳" />
            </el-form-item>
            <el-form-item label="风格">
              <el-radio-group v-model="loveLetter.style">
                <el-radio value="romantic">浪漫文艺</el-radio>
                <el-radio value="humorous">幽默风趣</el-radio>
                <el-radio value="sincere">朴实真诚</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="关键回忆">
              <el-input v-model="loveLetter.memory" type="textarea" :rows="2" placeholder="你们之间难忘的事..." />
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="writeLetter" :loading="writing" style="width:100%">
                ❤️ 八戒帮我写情书</el-button>
            </el-form-item>
          </el-form>
          <div v-if="writtenLetter" class="generated-result letter-result">
            <el-divider />
            <div class="letter-content">{{ writtenLetter }}</div>
            <el-button size="small" type="primary" @click="copyText(writtenLetter)" style="margin-top:8px">复制全文</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatLineSquare, Postcard } from '@element-plus/icons-vue'
import { generateChatLines, writeLoveLetter } from '@/api/bajie'

// ===== 话术生成 =====
const scenario = ref('first_meet')
const personality = ref('outgoing')
const extraInfo = ref('')
const generating = ref(false)
const generatedLines = ref(null)

async function generateLines() {
  generating.value = true
  try {
    const res = await generateChatLines({
      scenario: scenario.value,
      personality: personality.value,
      extra_info: extraInfo.value,
    })
    generatedLines.value = res.data.data.lines
  } catch (e) {
    ElMessage.error('生成话术失败')
  } finally {
    generating.value = false
  }
}

// ===== 情书代写 =====
const loveLetter = reactive({ to: '', style: 'romantic', memory: '' })
const writing = ref(false)
const writtenLetter = ref('')

async function writeLetter() {
  writing.value = true
  try {
    const res = await writeLoveLetter({
      to: loveLetter.to,
      style: loveLetter.style,
      memory: loveLetter.memory,
    })
    writtenLetter.value = res.data.data.letter
  } catch (e) {
    ElMessage.error('生成情书失败')
  } finally {
    writing.value = false
  }
}

/** 复制文本 */
function copyText(text) {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.social-assistant { height: calc(100vh - 140px); display: flex; flex-direction: column; gap: 12px; }
.sa-header { flex-shrink: 0; }
.sa-card { height: 100%;
  :deep(.el-card__header) { font-family: $font-family-title; letter-spacing: 2px; }
}
.generated-result { margin-top: 8px;
  h4 { font-family: $font-family-title; color: $vermilion; }
  .line-item {
    margin-bottom: 10px;
    background: $rice-paper;
    padding: 10px;
    border-radius: $border-radius-base;
    border-left: 4px solid $vermilion;
    p { margin: 0 0 4px; line-height: 1.7; color: $ink-black; font-family: $font-family-classic; }
  }
}
.letter-result .letter-content {
  white-space: pre-wrap;
  line-height: 2.2;
  color: $ink-black;
  font-size: 15px;
  font-family: $font-family-classic;
  background: $lotus-bg;
  padding: 16px;
  border-radius: $border-radius-base;
  border-left: 4px solid $vermilion;
}

:deep(.el-radio__input.is-checked .el-radio__inner) {
  background: $vermilion;
  border-color: $vermilion;
}
</style>
