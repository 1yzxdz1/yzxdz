<template>
  <div class="page-card chart-wrap">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <p>{{ subtitle }}</p>
    </div>
    <div ref="chartRef" class="chart-box"></div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  title: string
  subtitle: string
  option: echarts.EChartsCoreOption
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const renderChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  chart.setOption(props.option)
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', renderChart)
})

watch(
  () => props.option,
  () => renderChart(),
  { deep: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderChart)
  chart?.dispose()
})
</script>

<style scoped>
.chart-wrap {
  padding: 22px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
}

.chart-header p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.chart-box {
  height: 320px;
  margin-top: 18px;
}
</style>
