<template>
  <div class="knowledge-view">
    <el-card>
      <template #header>
        <h2>知识库管理</h2>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="上传文档" name="upload">
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="false"
            :limit="10"
            multiple
            accept=".txt,.md,.pdf,.json"
            :file-list="fileList"
            @change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持 txt、md、pdf、json 格式</div>
            </template>
          </el-upload>
          <el-button type="primary" @click="submitUpload" :loading="uploading">
            上传到知识库
          </el-button>
        </el-tab-pane>

        <el-tab-pane label="搜索知识" name="search">
          <el-form :model="searchForm" inline>
            <el-form-item label="搜索内容">
              <el-input
                v-model="searchForm.query"
                placeholder="输入搜索关键词"
                style="width: 300px"
              />
            </el-form-item>
            <el-form-item label="返回数量">
              <el-input-number v-model="searchForm.k" :min="1" :max="20" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="doSearch" :loading="searching">
                搜索
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="searchResults.length > 0" class="search-results">
            <el-divider />
            <h3>搜索结果 ({{ searchResults.length }})</h3>
            <el-card
              v-for="(item, index) in searchResults"
              :key="index"
              class="result-item"
            >
              <div class="result-content">{{ item.content }}</div>
              <div class="result-meta" v-if="item.metadata">
                <el-tag size="small" v-if="item.metadata.source">
                  {{ item.metadata.source }}
                </el-tag>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane label="知识库统计" name="stats">
          <el-button @click="loadStats" :loading="loadingStats">
            刷新统计
          </el-button>
          <div v-if="stats" class="stats-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="文档块数量">
                {{ stats.total_chunks }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { addDocuments, searchKnowledge, listDocuments } from '@/api/knowledge'

const activeTab = ref('upload')
const uploadRef = ref()
const fileList = ref<any[]>([])
const uploading = ref(false)
const searching = ref(false)
const loadingStats = ref(false)

const searchForm = reactive({
  query: '',
  k: 5
})

const searchResults = ref<any[]>([])
const stats = ref<any>(null)

const handleFileChange = (file: any, files: any[]) => {
  fileList.value = files
}

const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  const files = fileList.value.map(f => f.raw)
  const dataTransfer = new DataTransfer()
  files.forEach(file => dataTransfer.items.add(file))
  const fileListNew = dataTransfer.files

  uploading.value = true
  try {
    const response = await addDocuments(fileListNew)
    ElMessage.success(`成功添加 ${response.total_files} 个文件，共 ${response.total_chunks} 个文档块`)
    fileList.value = []
  } catch (error: any) {
    ElMessage.error(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const doSearch = async () => {
  if (!searchForm.query) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  searching.value = true
  try {
    const response = await searchKnowledge(searchForm.query, searchForm.k)
    searchResults.value = response.results
    ElMessage.success(`找到 ${response.total} 条结果`)
  } catch (error: any) {
    ElMessage.error(error.message || '搜索失败')
  } finally {
    searching.value = false
  }
}

const loadStats = async () => {
  loadingStats.value = true
  try {
    const response = await listDocuments()
    stats.value = response.data[0]
  } catch (error: any) {
    ElMessage.error(error.message || '获取统计失败')
  } finally {
    loadingStats.value = false
  }
}
</script>

<style scoped>
.knowledge-view {
  max-width: 900px;
}

.el-upload {
  margin-bottom: 20px;
}

.search-results {
  margin-top: 20px;
}

.search-results h3 {
  margin: 16px 0;
}

.result-item {
  margin-bottom: 12px;
}

.result-content {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #606266;
}

.result-meta {
  margin-top: 8px;
}

.stats-info {
  margin-top: 20px;
}
</style>
