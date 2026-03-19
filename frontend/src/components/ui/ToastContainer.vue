<template>
  <div class="toast-container">
    <transition-group name="toast-slide" tag="div">
      <Toast v-for="toast in toasts" :key="toast.id" :toast="toast" />
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { useToasts } from '../../stores/toast';
import Toast from './Toast.vue';

const { toasts } = useToasts();
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1001;
  width: 320px;
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-slide-move {
  transition: transform 0.4s ease;
}
</style>
