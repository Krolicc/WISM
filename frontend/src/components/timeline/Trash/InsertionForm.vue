
<template>
  <div class="insertion-form-wrapper unselect">
    <!-- 1. Узел с выбором иконки -->
    <div class="timeline-node" title="Click to change action type">
      <div 
        class="timeline-circle new-item-node"
        title="Double-click to remove"
        @click="isPickerOpen = !isPickerOpen" 
        @dblclick="$emit('remove')"
        v-html="currentActionMeta.icon">
      </div>
      <!-- 2. Меню выбора действия (Picker) -->
      <div v-if="isPickerOpen" class="action-picker">
        <div 
          v-for="action in availableCreateActions" 
          :key="action.type" 
          class="picker-item" 
          :class="{active: selectedActionType == action.type}"
          :title="action.meta.name"
          @click="selectAction(action.type)"
          v-html="action.meta.icon">
        </div>
      </div>
    </div>

    <!-- 3. Условное содержимое формы -->
    <div class="form-content">
      <!-- Форма для 'create_generate' -->
      <template v-if="selectedActionType === 'create_generate'">
        <input 
            type="number" 
            class="count-input"
            v-model="count"
            @input="debouncedDispatch"
            min="1" />
        <textarea 
            ref="textareaRef" 
            class="description-input"
            v-model="idea"
            @input="debouncedDispatch"
            placeholder="Description if necessary..." />
      </template>

      <!-- Форма для 'create_manual' -->
      <template v-if="selectedActionType === 'create_manual'">
        <textarea 
            ref="textareaRef" 
            class="description-input full-width"
            v-model="manualContent"
            @input="debouncedDispatch"
            placeholder="Enter content..." />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { useOrchestrationManageStore } from '../../stores/orchestration_manage';
import type { CreateGenerateAction, CreateManualAction } from '../../types/actions';
import { ACTION_META } from '../../lib/action-meta';
import { debounce } from '../../lib/utils';

// --- PROPS & EMITS ---
const emit = defineEmits<{ (e: 'remove'): void }>();
const props = defineProps<{ 
    targetId: string;
    relation: 'before' | 'after';
}>();

// --- STATE ---
const orchestrationStore = useOrchestrationManageStore();
const textareaRef = ref<HTMLTextAreaElement | null>(null);
const entryId = ref<string | null>(null);

// State для выбора действия
const selectedActionType = ref<'create_manual' | 'create_generate'>('create_generate');
const isPickerOpen = ref(false);

// State для полей форм
const idea = ref('');
const count = ref(1);
const manualContent = ref('');

// --- COMPUTED --- 
const availableCreateActions = computed(() => [
  { type: 'create_generate', meta: ACTION_META['create_generate'] },
  { type: 'create_manual', meta: ACTION_META['create_manual'] },
]);

const currentActionMeta = computed(() => ACTION_META[selectedActionType.value]);

// --- METHODS ---
const selectAction = (type: 'create_manual' | 'create_generate') => {
  selectedActionType.value = type;
  isPickerOpen.value = false;
  dispatchUpdate(); // Сразу отправляем новое действие, т.к. тип изменился
  nextTick(() => textareaRef.value?.focus()); // Переводим фокус
}

const dispatchUpdate = () => {
  if (entryId.value) {
    orchestrationStore.cancelAction(entryId.value);
  }

  let action: CreateGenerateAction | CreateManualAction;
  if (selectedActionType.value === 'create_generate') {
    action = {
        type: 'create_generate',
        params: {
            idea: idea.value,
            count: count.value,
            target_id: props.targetId,
            relation: props.relation
        }
    };
  } else {
    action = {
        type: 'create_manual',
        params: {
            content: manualContent.value,
            target_id: props.targetId,
            relation: props.relation
        }
    };
  }
  
  entryId.value = orchestrationStore.dispatchAction(action);
};

const debouncedDispatch = debounce(dispatchUpdate, 300);

// --- LIFECYCLE ---
onMounted(() => {
    dispatchUpdate();
    nextTick(() => textareaRef.value?.focus());
});

onUnmounted(() => {
    if (entryId.value) {
        orchestrationStore.cancelAction(entryId.value);
    }
});
</script>

<style scoped>
/* Стили не изменены, как вы и просили */
.insertion-form-wrapper { position: relative; margin: 20px 0; display: flex; align-items: start; gap: 2rem; }
.timeline-node { height: 100%; display: flex; flex-direction: column; align-items: center; z-index: 2; }
.timeline-circle.new-item-node { width: 28px; height: 28px; border-radius: 50%; background-color: var(--main-color); border: 2px solid var(--main-color); cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--container-bg); overflow: hidden; }
.form-content { background-color: var(--container-bg); display: flex; gap: 0.75rem; width: 100%; }
.count-input { font-size: 0.9rem; width: 50px; height: fit-content; padding: .5rem; text-align: center; border: 1px solid var(--border-color); border-radius: var(--border-radius); background-color: var(--bg-color); color: var(--text-color); }
.description-input { flex-grow: 1; min-height: 150px; border: 1px solid var(--border-color); border-radius: var(--border-radius); background-color: var(--bg-color); color: var(--text-color); padding: 0.5rem; resize: vertical; }
.description-input.full-width { width: 100%; }

/* Новые классы для стилизации */
.action-picker { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.picker-item { 
  width: 28px; 
  height: 28px; 
  overflow: hidden; 
  border: 2px solid var(--border-color); 
  border-radius: 50%; 
  cursor: pointer; color: var(--sub-color); 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  transition: color .2s, border-color .2s;
}
.picker-item.active { 
  opacity: .25;
  pointer-events: none;
}
.picker-item:hover { 
  border-color: var(--main-color); 
  color: var(--main-color); 
}
</style>
