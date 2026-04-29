<template>
  <div class="creator-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>小红书文案生成</h2>
        </div>
      </template>

      <el-form :model="form" label-width="100px">
        <el-form-item label="主题">
          <el-input
            v-model="form.topic"
            placeholder="输入要生成的主题，如：护肤品推荐、穿搭分享"
          />
        </el-form-item>

        <el-form-item label="风格">
          <el-select v-model="form.style" placeholder="选择风格">
            <el-option label="经验分享" value="经验分享" />
            <el-option label="产品测评" value="产品测评" />
            <el-option label="情感共鸣" value="情感共鸣" />
            <el-option label="教程" value="教程" />
            <el-option label="合集" value="合集" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-select
            v-model="form.keywords"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入关键词后按回车"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="额外要求">
          <el-input
            v-model="form.extra"
            type="textarea"
            :rows="3"
            placeholder="额外要求（可选），如：突出性价比、适合学生党"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="generate" :loading="loading">
            生成文案
          </el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <h3>生成结果</h3>
          <el-button size="small" @click="copyContent">复制文案</el-button>
        </div>
      </template>

      <div class="result-section">
        <h2 class="title">{{ result.title }}</h2>
        <div class="content">{{ result.content }}</div>
        <div class="hashtags">
          <el-tag
            v-for="tag in result.hashtags"
            :key="tag"
            size="default"
            class="hashtag"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { generateContent } from '@/api/creator'

const form = reactive({
  topic: '',
  style: '经验分享',
  keywords: [] as string[],
  extra: ''
})

const loading = ref(false)
const result = ref<any>(null)

const generate = async () => {
  if (!form.topic) {
    ElMessage.warning('请输入主题')
    return
  }

  loading.value = true
  try {
    const response = await generateContent({
      topic: form.topic,
      style: form.style,
      keywords: form.keywords.length > 0 ? form.keywords : undefined,
      extra: form.extra || undefined
    })
    result.value = response.result
    ElMessage.success('生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    loading.value = false
  }
}

const reset = () => {
  form.topic = ''
  form.style = '经验分享'
  form.keywords = []
  form.extra = ''
  result.value = null
}

const copyContent = async () => {
  if (!result.value) return
  const text = `${result.value.title}\n\n${result.value.content}\n\n${result.value.hashtags.join(' ')}`
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.creator-view {
  max-width: 800px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2,
.card-header h3 {
  margin: 0;
}

.result-card {
  margin-top: 20px;
}

.result-section {
  padding: 10px 0;
}

.title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #303133;
}

.content {
  font-size: 16px;
  line-height: 1.8;
  white-space: pre-wrap;
  margin-bottom: 20px;
  color: #606266;
}

.hashtags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hashtag {
  background: #f0f9ff;
  border: none;
  color: #409eff;
}
</style>
