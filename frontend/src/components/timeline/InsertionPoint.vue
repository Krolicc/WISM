
<template>
  <div class="insertion-point-wrapper unselect">
    <button class="add-btn" @click.stop="emit('add');">
      +
    </button>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{(e: 'add'): void }>();
</script>

<style scoped>
.insertion-point-wrapper {
  position: relative;
  height: 40px;
  padding: 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-btn {
  width: 21px;
  height: 21px;
  border-radius: 50%;
  background-color: var(--main-color);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: end; 
  justify-content: center;
  font-size: 16px;
  z-index: 3;
  box-shadow: 0 0 10px 2px var(--bg-color);
  opacity: 0;
  transition: opacity .3s ease-out;
}

.insertion-point-wrapper:hover .add-btn {
  opacity: 1;
}
</style>
