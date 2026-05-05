<template>
  <div 
    v-if="isOpen"
    class="list-component-container"
    :style="menuStyle"
    ref="listRef"
    role="menu"
    @scroll.stop
  >
    <div class="list-header" v-if="$slots.header">
      <slot name="header"></slot>
    </div>
    <div class="list-items-container" v-if="items.length > 0">
      <button
        v-for="item in items" :key="item.id"
        class="list-item"
        :disabled="item.disabled"
        @click.stop="onItemClick(item)"
        role="menuitem"
      >
        {{ item.text }}
      </button>
    </div>
    <div class="list-footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, type PropType, computed, nextTick } from 'vue';
import type { ContextMenuItem } from '../../stores/context_menu';

const props = defineProps({
  isOpen: Boolean,
  items: {
    type: Array as PropType<ContextMenuItem[]>,
    required: true
  },
  x: { type: Number, required: true },
  y: { type: Number, required: true },
  placement: { type: String, default: 'bottom-start' },
  onItemClick: {
    type: Function as PropType<(item: ContextMenuItem) => void>,
    required: true
  }
});

const emit = defineEmits(['close']);

const listRef = ref<HTMLElement | null>(null);
const menuWidth = ref(0);
const menuHeight = ref(0);

const menuStyle = computed(() => {
  let left = props.x;
  let top = props.y;

  // Basic placement logic from GlobalContextMenu
  let transform = '';
  if (props.placement.includes('bottom')) transform += `translateY(0%) `;
  if (props.placement.includes('top')) transform += `translateY(-100%) `;
  if (props.placement.includes('right')) transform += `translateX(0%) `;
  if (props.placement.includes('left')) transform += `translateX(-100%) `;
  if (props.placement.endsWith('-end')) {
    if (props.placement.startsWith('bottom') || props.placement.startsWith('top')) {
      transform += 'translateX(-100%)';
    }
    if (props.placement.startsWith('left') || props.placement.startsWith('right')) {
      transform += 'translateY(-100%)';
    }
  }

  // Viewport collision detection
  if (listRef.value) {
      if (left + menuWidth.value > window.innerWidth) {
          left = window.innerWidth - menuWidth.value - 5;
      }
      if (top + menuHeight.value > window.innerHeight) {
          top = window.innerHeight - menuHeight.value - 5;
      }
      if (left < 0) left = 5;
      if (top < 0) top = 5;
  }

  return {
    top: `${top}px`,
    left: `${left}px`,
    transform: transform.trim(),
  };
});

const handleOutsideClick = (event: MouseEvent) => {
  if (listRef.value && !listRef.value.contains(event.target as Node)) {
    emit('close');
  }
};

const handleScroll = (event: Event) => {
  if (listRef.value && event.target && listRef.value.contains(event.target as Node)) {
    return;
  }
  emit('close');
};

const measureMenu = () => {
    if (listRef.value) {
        menuWidth.value = listRef.value.offsetWidth;
        menuHeight.value = listRef.value.offsetHeight;
    }
};

const stopWatching = watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    nextTick(measureMenu);
    setTimeout(() => {
      document.addEventListener('click', handleOutsideClick);
      window.addEventListener('scroll', handleScroll, true);
    }, 0);
  } else {
    document.removeEventListener('click', handleOutsideClick);
    window.removeEventListener('scroll', handleScroll, true);
  }
});

onMounted(() => {
    if (props.isOpen) {
        measureMenu();
    }
});

onUnmounted(() => {
  stopWatching();
  document.removeEventListener('click', handleOutsideClick);
  window.removeEventListener('scroll', handleScroll, true);
});

</script>

<style scoped>
.list-component-container {
  position: fixed;
  min-width: 180px;
  background-color: var(--container-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: .5rem;
  z-index: 9999;
  max-height: 400px;
  overflow-y: auto;
  padding: .5rem;
}

.list-items-container {
  overflow-y: auto;
  overflow-x: hidden;
}

.list-header, .list-footer {
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.list-item {
  display: block;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-color);
  border-radius: var(--border-radius, 4px);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.list-item:hover:not(:disabled) {
  background-color: var(--main-color);
  color: white;
}

.list-item:disabled {
  color: var(--sub-color);
  cursor: not-allowed;
  background-color: transparent;
}
</style>
