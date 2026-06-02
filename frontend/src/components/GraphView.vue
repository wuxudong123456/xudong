<template>
  <div class="graph-container">
    <div ref="chartRef" class="graph-chart"></div>
    <div v-if="selectedNode" class="node-info">
      <h4>{{ selectedNode.name }}</h4>
      <p>{{ selectedNode.value }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({ nodes: [], links: [], categories: [] })
  }
})

const chartRef = ref(null)
const selectedNode = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'node') {
          return `${params.data.name}<br/>${params.data.value || ''}`
        }
        return `${params.data.relation}`
      }
    },
    legend: {
      data: props.data.categories.map(c => c.name),
      top: 10,
      left: 10
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: props.data.nodes,
        links: props.data.links,
        categories: props.data.categories,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        force: {
          repulsion: 300,
          edgeLength: 100,
          gravity: 0.1
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4
          }
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        },
        edgeLabel: {
          show: true,
          formatter: (x) => x.data.relation,
          fontSize: 10
        }
      }
    ]
  }

  chart.setOption(option)

  // 点击事件
  chart.on('click', (params) => {
    if (params.dataType === 'node') {
      selectedNode.value = params.data
    }
  })
}

const handleResize = () => {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})

watch(() => props.data, () => {
  if (chart) {
    chart.dispose()
    initChart()
  }
}, { deep: true })
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 600px;
  position: relative;
}

.graph-chart {
  width: 100%;
  height: 100%;
}

.node-info {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(245, 230, 200, 0.95);
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #D4BE8A;
  box-shadow: 0 2px 12px rgba(26, 26, 28, 0.1);
  max-width: 250px;
}

.node-info h4 {
  margin: 0 0 8px 0;
  color: #C43B3B;
  font-family: 'KaiTi', 'STKaiti', serif;
  letter-spacing: 2px;
}

.node-info p {
  margin: 0;
  color: #555;
  font-size: 14px;
}
</style>
