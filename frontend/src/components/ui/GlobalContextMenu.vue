
<template>
  <ListComponent
    :isOpen="store.isOpen"
    :items="resolvedItems"
    :x="store.position.x"
    :y="store.position.y"
    :placement="store.placement"
    :onItemClick="onItemClick"
    @close="store.close()"
  />
</template>

<script setup lang="ts">
import { computed, isRef, watch } from 'vue';
import { useContextMenuStore, type ContextMenuItem } from '../../stores/context_menu';
import { useKeyboardStateStore } from '../../stores/keyboard_state';
import ListComponent from './ListComponent.vue';

const store = useContextMenuStore();
const keyboardStore = useKeyboardStateStore();

const resolvedItems = computed((): ContextMenuItem[] => {
  const itemsSource = store.items;
  if (typeof itemsSource === 'function') {
    return itemsSource();
  } else if (isRef(itemsSource)) {
    return itemsSource.value;
  } else if (Array.isArray(itemsSource)) {
    return itemsSource;
  }
  return [];
});

function onItemClick(item: ContextMenuItem) {
  store.selectItem(item);
}

watch(() => keyboardStore.escapePressed, (isEscapedPressed) => {
  if (isEscapedPressed) {
    store.close();
  }
});

</script>
