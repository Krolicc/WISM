<template>
  <div class="actions-panel content-block">
    <!-- Main action selection -->
    <div v-if="!activeAction">
      <button @click="emit('clear-selection')" :disabled="!isAnythingSelected" class="action-btn clear-btn">
        Очистить
      </button>
      <div class="status-container">
         <p v-if="isValidSelection" class="status-valid">Выделение валидно</p>
         <p v-else-if="isAnythingSelected" class="status-invalid">Нельзя перемещать вместе</p>
      </div>
      <div class="main-actions">
        <button @click="emit('start-action', 'move')" :disabled="!isValidSelection" class="action-btn">Переместить</button>
        <button @click="emit('start-action', 'merge')" :disabled="!isValidSelection" class="action-btn">Объединить</button>
      </div>
    </div>

    <!-- Action mode active -->
    <div v-else>
      <div class="transformation-rules">
        <h5>Правило трансформации:</h5>
        <p>{{ transformationRule }}</p>
      </div>

      <div v-if="targetBlock" class="context-actions">
        <template v-if="activeAction === 'move'">
          <button v-if="targetBlock.type !== 'Scene'" @click="emit('execute', { position: 'prepend' })" class="context-btn wide-btn">Вложить в начало</button>
          <button @click="emit('execute', { position: 'before' })" class="context-btn">Вставить до</button>
          <button @click="emit('execute', { position: 'after' })" class="context-btn">Вставить после</button>
          <button v-if="targetBlock.type !== 'Scene'" @click="emit('execute', { position: 'append' })" class="context-btn wide-btn">Вложить в конец</button>
        </template>
        <template v-if="activeAction === 'merge'">
          <button @click="emit('execute', { position: 'prepend' })" class="context-btn">В начало</button>
          <button @click="emit('execute', { position: 'append' })" class="context-btn">В конец</button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Block, BlockType } from '@/types/preprocessing';
import { HIERARCHY } from '/src/stores/story-structuring';

const props = defineProps<{
  activeAction: 'move' | 'merge' | null;
  isAnythingSelected: boolean;
  isValidSelection: boolean;
  targetBlock: Block | null;
  sourceType: BlockType | null;
}>();

const emit = defineEmits<{
  (e: 'clear-selection'): void
  (e: 'start-action', action: 'move' | 'merge'): void
  (e: 'cancel-action'): void
  (e: 'execute', payload: { position: 'before' | 'after' | 'prepend' | 'append' }): void
}>();

const transformationRule = computed(() => {
  if (!props.activeAction || !props.targetBlock || !props.sourceType) return "";

  const targetType = props.targetBlock.type;
  const targetLevel = HIERARCHY[targetType];
  const sourceLevel = HIERARCHY[props.sourceType];

  if (props.activeAction === 'move') {
      if (sourceLevel <= targetLevel) return `Перемещение на тот же уровень (${props.sourceType}). Структура сохранится.`;
      
      const levelsToDrop = sourceLevel - targetLevel;
      if (levelsToDrop === 1) return `Блок типа «${props.sourceType}» будет понижен до «${targetType}».`;
      
      return `Блок «${props.sourceType}» будет «сплющен» в простой текстовый блок типа «Scene».`;
  }
  if (props.activeAction === 'merge') {
    return `Весь текст из выделенных блоков будет добавлен в блок «${props.targetBlock.text}». Исходные блоки будут удалены.`
  }
  return "";
});

</script>

<style scoped>
.actions-panel { flex-shrink: 0; padding: 15px; }
.action-btn { background-color: #4a5162; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; width: 100%; margin-bottom: 10px; font-size: 1em; }
.action-btn:disabled { background-color: #383838; color: #777; cursor: not-allowed; }
.clear-btn { background-color: #5a3e3e; }
.back-btn { background-color: #6c757d; margin-bottom: 15px; }
.main-actions { display: flex; gap: 10px; margin-top: 10px; }
.status-container { min-height: 20px; text-align: center; margin-bottom: 10px; }
.status-valid { color: #81C784; font-weight: 500; }
.status-invalid { color: #E57373; font-weight: 500; }
.action-title { text-align: center; color: #fff; margin-bottom: 10px; }
.action-placeholder, .transformation-rules p { font-size: 0.9em; color: #aaa; text-align: center; line-height: 1.4; }
.transformation-rules h5 { text-align: center; color: #ddd; margin-bottom: 5px; }

.context-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}
.context-btn {
  border: none;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  background-color: #3c4c3c;
  color: white;
  flex-grow: 1;
}
.wide-btn {
  flex-basis: 100%;
}
</style>
