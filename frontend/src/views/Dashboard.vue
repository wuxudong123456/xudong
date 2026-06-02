<!--
  Dashboard.vue - 数据看板
  展示学生人数统计、成绩分布、班级数据可视化图表
-->
<template>
  <div class="dashboard">
    <!-- 概览统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="stat in statsList" :key="stat.label">
        <el-card shadow="hover" class="stat-card">
          <el-statistic :value="stat.value" :title="stat.label">
            <template #prefix>
              <el-icon :color="stat.color" :size="24"><component :is="stat.icon" /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card header="班级学生分布">
          <div ref="classChart" style="height:320px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="成绩趋势">
          <div ref="scoreChart" style="height:320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card header="各班就业情况">
          <div ref="employChart" style="height:320px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="成绩分数段分布">
          <div ref="distChart" style="height:320px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import { User, School, DataBoard, Medal, TrendCharts } from '@element-plus/icons-vue'
import { getOverview, getClassDistribution, getScoreTrend, getEmploymentRate, getScoreDistribution } from '@/api/dashboard'

// 统计数据 — 古典色彩
const statsList = ref([
  { label: '学生总数', value: 0, icon: User, color: '#2C3E6B' },
  { label: '班级数量', value: 0, icon: School, color: '#5D8A5D' },
  { label: '教师人数', value: 0, icon: DataBoard, color: '#C9A96E' },
  { label: '平均成绩', value: 0, icon: Medal, color: '#C43B3B' },
  { label: '就业率(%)', value: 0, icon: TrendCharts, color: '#4A6B8A' },
])

// ECharts 古典色板
const CLASSICAL_COLORS = ['#C43B3B', '#2C3E6B', '#5D8A5D', '#C9A96E', '#4A6B8A', '#D4A0A0', '#8B1A1A', '#B8943D']

// 图表容器
const classChart = ref(null)
const scoreChart = ref(null)
const employChart = ref(null)
const distChart = ref(null)
let charts = []

/** 初始化ECharts实例 */
function initChart(refEl) {
  if (!refEl.value) return null
  const chart = echarts.init(refEl.value)
  charts.push(chart)
  return chart
}

/** 加载仪表盘数据 */
async function loadData() {
  try {
    // 概览数据
    const res = await getOverview()
    const d = res.data.data
    statsList.value[0].value = d.total_students
    statsList.value[1].value = d.total_classes
    statsList.value[2].value = d.total_teachers
    statsList.value[3].value = d.avg_score
    statsList.value[4].value = d.employment_rate

    // 班级分布饼图
    const distRes = await getClassDistribution()
    const pieChart = initChart(classChart)
    pieChart?.setOption({
      color: CLASSICAL_COLORS,
      tooltip: { trigger: 'item' },
      series: [{ type: 'pie', radius: ['40%', '70%'], data: distRes.data.data, emphasis: { itemStyle: { shadowBlur: 10 } } }]
    })

    // 成绩趋势折线图
    const trendRes = await getScoreTrend()
    const lineChart = initChart(scoreChart)
    const trendData = trendRes.data.data
    lineChart?.setOption({
      color: CLASSICAL_COLORS,
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: trendData.map(t => t.exam_order) },
      yAxis: { type: 'value', name: '平均分' },
      series: [{ type: 'line', data: trendData.map(t => t.avg_score), smooth: true }]
    })

    // 就业情况柱状图
    const employRes = await getEmploymentRate()
    const barChart = initChart(employChart)
    const employData = employRes.data.data
    barChart?.setOption({
      color: CLASSICAL_COLORS,
      tooltip: { trigger: 'axis' },
      legend: { data: ['就业人数', '平均薪资'] },
      xAxis: { type: 'category', data: employData.map(e => e.class_name), axisLabel: { rotate: 30 } },
      yAxis: [{ type: 'value', name: '人数' }, { type: 'value', name: '薪资(元)' }],
      series: [
        { name: '就业人数', type: 'bar', data: employData.map(e => e.employed_count) },
        { name: '平均薪资', type: 'line', yAxisIndex: 1, data: employData.map(e => e.avg_salary) },
      ]
    })

    // 成绩分布饼图
    const scoreDistRes = await getScoreDistribution()
    const pieChart2 = initChart(distChart)
    pieChart2?.setOption({
      color: CLASSICAL_COLORS,
      tooltip: { trigger: 'item' },
      series: [{ type: 'pie', radius: '70%',
        data: scoreDistRes.data.data.map(d => ({ name: d.range, value: d.count })),
        label: { formatter: '{b}: {c}人 ({d}%)' } }]
    })
  } catch (e) { /* error handled by interceptor */ }
}

onMounted(() => loadData())

// 监听窗口resize，自动调整图表大小
const resizeHandler = () => charts.forEach(c => c.resize())
window.addEventListener('resize', resizeHandler)
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler)
  charts.forEach(c => c.dispose())
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.dashboard { padding: 0; }
.stats-row { margin-bottom: 16px; }

.stat-card {
  text-align: center;
  background: $rice-paper;
  border: 2px solid $gold-border;
  border-radius: $border-radius-base;
  transition: all $transition-base;
  &:hover {
    box-shadow: 0 4px 16px rgba($gold, 0.25);
    border-color: $gold;
    transform: translateY(-2px);
  }
}

:deep(.el-statistic__head) {
  color: $ink-secondary;
  font-family: $font-family-title;
  letter-spacing: 2px;
}
:deep(.el-statistic__number) {
  color: $ink-black;
  font-family: $font-family-title;
  font-size: 28px;
}
:deep(.el-card__header) {
  font-family: $font-family-title;
  letter-spacing: 2px;
  color: $ink-black;
  border-bottom-color: $gold-border;
}
</style>
