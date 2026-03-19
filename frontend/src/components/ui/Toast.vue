<template>
  <div :class="['toast-message', `toast-${toast.type}`]">
    {{ toast.message }}
  </div>
</template>

<script setup lang="ts">
import type { Toast } from '../../stores/toast';

defineProps<{
  toast: Toast;
}>();
</script>

<style scoped>
.toast-message {
  padding: 1rem 1.5rem;
  border-radius: var(--border-radius);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  margin-bottom: 1rem;
}

.toast-success {
  background-color: var(--main-color-green);
}

.toast-error {
  background-color: var(--main-color-red);
}

.toast-info {
  background-color: var(--sub-color);
}
</style>
