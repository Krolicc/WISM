<template>
  <div class="toc-tree-view-container content-block">
    <ul class="toc-list">
      <TocNode 
        v-for="block in blocks"
        :key="block.id"
        :block="block"
        :depth="0"
        :target-id="targetId"
        :active-action="activeAction"
        @set-target="(id) => emit('set-target', id)"
        @execute="(e) => emit('execute', e)"
      />
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { Block } from '@/types/preprocessing';
import TocNode from './TocNode.vue';

defineProps<{
  blocks: Block[];
  targetId: string | null;
  activeAction: 'move' | 'merge' | null;
}>();

const emit = defineEmits<{
  (e: 'set-target', id: string | null): void
  (e: 'execute', payload: { position: 'before' | 'after' | 'prepend' | 'append' }): void
}>();

</script>

<style scoped>
.toc-tree-view-container {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 15px;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
</style>
