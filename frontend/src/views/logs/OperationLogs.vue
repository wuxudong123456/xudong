<!-- OperationLogs.vue - 操作日志页面 -->
<template>
  <div>
    <el-card class="search-card" shadow="never">
      <el-form inline>
        <el-form-item label="操作模块">
          <el-select v-model="search.module" clearable placeholder="全部" style="width:140px">
            <el-option label="学生管理" value="student" />
            <el-option label="班级管理" value="class" />
            <el-option label="成绩管理" value="score" />
            <el-option label="就业管理" value="employment" />
            <el-option label="课程管理" value="course" />
            <el-option label="用户管理" value="user" />
            <el-option label="认证" value="auth" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="search.action" clearable placeholder="全部" style="width:120px">
            <el-option label="查询" value="query" />
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
            start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">搜索</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="操作用户" width="120" />
        <el-table-column prop="module" label="模块" width="100" />
        <el-table-column prop="action" label="操作" width="80" />
        <el-table-column prop="target_type" label="目标类型" width="100" />
        <el-table-column prop="target_id" label="目标ID" width="80" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="create_time" label="操作时间" width="180" />
      </el-table>
      <el-pagination v-model:current-page="page" v-model:page-size="size" :total="total"
        layout="total, prev, pager, next" @current-change="fetchData" style="margin-top:16px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLogList } from '@/api/log'

const search = reactive({ module: '', action: '' })
const dateRange = ref(null)
const tableData = ref([]); const loading = ref(false)
const page = ref(1); const size = ref(20); const total = ref(0)

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, size: size.value, module: search.module || undefined, action: search.action || undefined }
    if (dateRange.value) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }
    const res = await getLogList(params)
    const d = res.data.data; tableData.value = d.items; total.value = d.total
  } finally { loading.value = false }
}
onMounted(fetchData)
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.search-card { margin-bottom: 16px; }

:deep(.el-table) {
  border-radius: $border-radius-base;
  overflow: hidden;
}
</style>
