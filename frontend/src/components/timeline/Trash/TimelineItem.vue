<template>
  <div 
    class="timeline-item" 
    @mouseover="showDelete = true" 
    @mouseleave="showDelete = false"
  >
    <div class="timeline-node">
      <div 
        class="timeline-circle"
        :class="{ active: !!activeModifyLogEntry }"
        :title="circleTitle"
        @click.stop="handleCircleClick"
        @dblclick.stop="handleDblClick"
        v-html="activeModifyActionIcon"
      ></div>
      
      <!-- Pop-up для выбора типа действия -->
      <div v-if="isActionPickerOpen" class="action-picker-wrapper">
        <ActionTypePicker 
          :actions="modifyActionsForPicker"
          :model-value="currentActionType"
          @update:model-value="handleActionTypeUpdate"
        />
      </div>
    </div>

    <!-- Item Content -->
    <div 
      class="item-block" 
      :class="{ 
        active: item.id === vertNavStore.activeNodeId,
        select: item.id === contentStore.selectedNodeId
      }"
      @click.stop="contentStore.selectNode(item.id)"
      @dblclick.stop="vertNavStore.drillDown(item.id)"
    >
        <h4 v-if="!isActionPickerOpen" class="item-title">{{ item.content.title }}</h4>
        <span v-if="item.isLoading" class="spinner">🌀</span>
    </div>

    <!-- Flag Panel or Delete Button -->
    <div class="controls-wrapper">
      <FlagPanel 
        v-if="canShowHelperFlags" 
        :owner-id="item.id"
        :activeFlag="currentHelperFlag"
        :flags="helperFlags" 
        @update:model-value="handleHelperFlagUpdate" 
      />
      
      <button 
        v-if="canShowDeleteButton"
        @click.stop="handleDeleteClick" 
        class="delete-item-btn" 
        :class="{ active: isDeleteActionQueued }"
        title="Delete Item"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="delete-icon">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, PropType } from 'vue';
import { useVerticalNavigationStore } from '../../stores/vertical_navigation';
import { useContentManageStore } from '../../stores/content_manage';
import { useOrchestrationManageStore, LogEntry } from '../../stores/orchestration_manage';
import { ACTION_META, getModifyActions, ActionType } from '../../lib/action-meta';
import type { BaseNode } from '../../types';

import ActionTypePicker from '../ui/ActionTypePicker.vue';
import FlagPanel from '../ui/FlagPanel.vue';

// --- PROPS --- (Now only the item itself)
const props = defineProps({
  item: { 
    type: Object as PropType<BaseNode>,
    required: true 
  },
});

// --- STORES ---
const vertNavStore = useVerticalNavigationStore();
const contentStore = useContentManageStore();
const orchStore = useOrchestrationManageStore();

// --- STATE ---
const showDelete = ref(false);
const isActionPickerOpen = ref(false);
const DEFAULT_ACTION_TYPE: ActionType = 'rewrite';
const MODIFY_ACTION_TYPES: ActionType[] = ['rewrite', 'regenerate', 'generate_skeleton', 'regenerate_skeleton'];
const DELETE_ACTION_TYPE: ActionType[] = ['delete'];

// --- COMPUTED: Основная логика --- 
const activeModifyLogEntry = computed<LogEntry | undefined>(() => {
  const action = orchStore.getFinalActionForIdByTypes(
    props.item.id, MODIFY_ACTION_TYPES, { includeCancelled: true }
  )

  return action == undefined || action.isCancelled ? undefined : action;
});

// Определяем текущий тип действия (Action Type)
const currentActionType = computed<ActionType | null>(() => activeModifyLogEntry.value?.action.type || null);

const modifyActionsForPicker = computed(() => {
  const allActions = getModifyActions();
  const hasChildren = props.item.children_ids && props.item.children_ids.length > 0;
  if (hasChildren) {
    return allActions.filter(action => action.type !== 'generate_skeleton');
  } else {
    return allActions.filter(action => action.type !== 'regenerate_skeleton');
  }
});

// Иконка для главного круга
const activeModifyActionIcon = computed(() => currentActionType.value ? ACTION_META[currentActionType.value].icon : '');

// Заголовок для главного круга
const circleTitle = computed(() => {
    if (currentActionType.value) return ACTION_META[currentActionType.value]?.name || 'Select Action';
    return 'Choose an action';
});

// Это действие типа 'delete'?
const activeDeleteLogEntry = computed(() => 
  orchStore.getFinalActionForIdByTypes(props.item.id, DELETE_ACTION_TYPE)
);

const isDeleteActionQueued = computed(() => 
  activeDeleteLogEntry.value != undefined
);
// --- COMPUTED: "ФЛАГИ-ХЕЛПЕРЫ" (FlagPanel) ---
// Доступные флаги-хелперы для текущего действия
const helperFlags = computed(() => {
  return currentActionType.value ? ACTION_META[currentActionType.value]?.flags || {} : {}
});

const currentHelperFlag = computed(() => {
  return activeModifyLogEntry.value && activeModifyLogEntry.value?.action.params
    ? helperFlags.value[activeModifyLogEntry.value.action.params.flag] 
    : undefined
});

// --- COMPUTED: Видимость контролов --- 
const canShowHelperFlags = computed(() => !!activeModifyLogEntry.value && Object.values(helperFlags.value).length > 0);
const canShowDeleteButton = computed(() => (showDelete.value && !activeModifyLogEntry.value) || isDeleteActionQueued.value);

// --- METHODS  ---
function handleCircleClick() {
  if (activeModifyLogEntry.value) {
    isActionPickerOpen.value = !isActionPickerOpen.value;
  }
}

function handleDblClick() {
  if (activeModifyLogEntry.value) {
    orchStore.cancelAction(activeModifyLogEntry.value.id);
  } else {
    if (isDeleteActionQueued.value) orchStore.cancelAction(activeDeleteLogEntry.value!.id);
    const flags = ACTION_META[DEFAULT_ACTION_TYPE].flags
    const active_flag = flags && Object.keys(flags).length > 0 ? Object.keys(flags)[0] : ''
    orchStore.dispatchAction({ type: DEFAULT_ACTION_TYPE, params: { id: props.item.id, flag: active_flag }});
  }

  isActionPickerOpen.value = false;
}

function handleDeleteClick() {
  if (isDeleteActionQueued.value) {
    orchStore.cancelAction(activeDeleteLogEntry.value!.id);
  } else {
    if (activeModifyLogEntry.value) orchStore.cancelAction(activeModifyLogEntry.value.id);
    orchStore.dispatchAction({ type: 'delete', params: { id: props.item.id } });
  }
  isActionPickerOpen.value = false;
}
// Обновление "флага-действия" из ActionTypePicker
function handleActionTypeUpdate(newType: ActionType) {
  const flags = ACTION_META[newType].flags;
  const active_flag = flags && Object.keys(flags).length > 0 ? Object.keys(flags)[0] : undefined;
  
  const params: { id: string, flag?: string } = { id: props.item.id, flag: active_flag };
  orchStore.dispatchAction({ type: newType, params });
  isActionPickerOpen.value = false;
}

// Обновление "флага-хелпера" из FlagPanel
function handleHelperFlagUpdate(flagId: string) {
  const entry = activeModifyLogEntry.value;
  if (!entry) return;
  const lastEntryInLog = orchStore.lastLogEntry;
  if (entry.id === lastEntryInLog?.id) {
    orchStore.updateActionParams(entry.id, { flag: flagId });
  } else {
    const newAction = { ...entry.action, params: { ...entry.action.params, flag: flagId } };
    orchStore.dispatchAction(newAction);
  }
}


</script>

<style scoped>
.timeline-item {
    display: flex;
    align-items: center;
    gap: 2rem;
    position: relative; 
    min-height: 40px;
}

.timeline-node {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 32px;
    position: relative;
}

.timeline-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid var(--border-color);
    color: var(--sub-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
    overflow: hidden;
}
.timeline-circle.interactive, .timeline-circle:hover {
    border-color: var(--main-color);
}
.timeline-circle:hover { transform: scale(1.1); }
.timeline-circle.active {
    background-color: var(--main-color);
    border-color: var(--main-color);
    color: var(--bg-color);
}
.item-block {
  background-color: var(--container-bg);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: border-color 0.2s;
  flex: 1 1 auto;
  min-width: 0; 
}
.item-block.active { color: var(--main-color); }
.item-block.select { color: var(--main-color); }

.item-title { 
  font-size: 1rem; 
  font-weight: 600; 
  margin: 0; 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.controls-wrapper { flex-shrink: 0; }

.delete-item-btn {
  background: none;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}
.delete-item-btn:hover,
.delete-item-btn.active { background: var(--main-color-red); }
.delete-item-btn:hover .delete-icon,
.delete-item-btn.active .delete-icon{ color: var(--bg-color); }
.spinner { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.action-picker-wrapper { 
  position: absolute;
  top: 50%;
  transform: translate(100%, -50%);  
  right: -1rem; 
  z-index: 10; 
}

</style>
