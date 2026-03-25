<template>
  <div class="stat-card page-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-extra">{{ extra }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  extra: string
}>()
</script>

<style scoped>
.stat-card {
  padding: 20px;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.stat-value {
  margin-top: 12px;
  font-size: 32px;
  font-weight: 700;
}

.stat-extra {
  margin-top: 8px;
  color: var(--brand);
  font-size: 13px;
}
</style>
