
<template>
  <div 
    class="timeline-item" 
    @mouseover="isHovered = true" 
    @mouseleave="isHovered = false"
  >
    <div class="timeline-node">
      <div 
        class="timeline-circle"
        :class="{ active: isModifyActionActive }"
        :title="circleTitle"
        @click.stop="handleCircleClick"
        @dblclick.stop="handleDblClick"
      >
        <div class="icon"
          v-html="activeModifyActionIcon"
        ></div>
        <div class="category-icon"
          v-html="activeModifyActionCategoryIcon"  
        ></div>
      </div>
      
      <!-- Pop-up для выбора типа действия -->
      <div v-if="isActionPickerOpen" class="action-picker-wrapper">
        <ActionTypePicker 
          :actions="modifyActionsForPicker"
          :model-value="currentModifyType"
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
      <div v-if="isModifyActionActive" class="action-controls">
        <FlagPanel 
          v-if="canShowHelperFlags" 
          :owner-id="item.id"
          :activeFlag="currentHelperFlag"
          :flags="helperFlags" 
          @update:model-value="handleHelperFlagUpdate" 
        />

        <button 
          v-if="hasParameters" 
          @click="showParameterForm = !showParameterForm" 
          class="icon-btn"
        >
        <svg width="16.5" height="18" viewBox="0 0 22 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M11.7848 0C12.8239 0 13.7167 0.715478 13.9122 1.70497L13.9991 2.14497C14.3408 3.87444 16.1859 4.90724 17.9016 4.32942L18.3383 4.18235C19.3199 3.85177 20.4054 4.2436 20.9249 5.11607L21.7097 6.43388C22.2293 7.30638 22.0365 8.41368 21.2504 9.07255L20.9008 9.36557C19.5267 10.5172 19.5267 12.5828 20.9008 13.7344L21.2504 14.0274C22.0365 14.6863 22.2293 15.7936 21.7097 16.6661L20.925 17.9839C20.4054 18.8564 19.3199 19.2482 18.3382 18.9176L17.9017 18.7705C16.1859 18.1926 14.3408 19.2254 13.9991 20.955L13.9122 21.395C13.7167 22.3845 12.8239 23.1 11.7848 23.1H10.2152C9.1761 23.1 8.28331 22.3845 8.08781 21.3951L8.00082 20.9548C7.65909 19.2254 5.81395 18.1926 4.09822 18.7705L3.66179 18.9175C2.68016 19.2482 1.59465 18.8563 1.07505 17.9838L0.2903 16.6661C-0.229281 15.7936 -0.0365542 14.6863 0.74956 14.0274L1.09922 13.7344C2.47324 12.5827 2.47324 10.5172 1.09922 9.36562L0.74956 9.07256C-0.0365542 8.41368 -0.22928 7.3064 0.2903 6.43392L1.07508 5.1161C1.59466 4.24361 2.68014 3.85178 3.66176 4.18238L4.09831 4.32941C5.81401 4.90724 7.65909 3.87451 8.00082 2.14508L8.0878 1.70489C8.28331 0.715438 9.176 0 10.2152 0H11.7848ZM11 15.55C13.2091 15.55 15 13.7592 15 11.55C15 9.34089 13.2091 7.55005 11 7.55005C8.79087 7.55005 7.00002 9.34089 7 11.55C6.99998 13.7592 8.79085 15.55 11 15.55Z" fill="currentColor"/>
        </svg>

        </button>

        <button v-else @click="executeSimpleAction" class="apply-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </button>
      </div>
      
      <button 
        v-if="canShowDeleteButton"
        @click.stop="handleDeleteClick" 
        class="delete-item-btn" 
        :class="{ active: isDeleteActionActive }"
        title="Delete Item"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="delete-icon">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>

      <button 
        v-if="isHovered && !canShowDeleteButton"
        @click.stop="$emit('openContextMenu', $event)"
        class="context_menu-btn"
        title="Действия"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="1"></circle>
          <circle cx="12" cy="5" r="1"></circle>
          <circle cx="12" cy="19" r="1"></circle>
        </svg>
      </button>
    </div>

    <InsertionForm 
      v-if="showParameterForm"
      :parameters="currentHelperFlag?.parameters"
      :initial-data="item.actionState?.parameters"
      @update:data="handleFormUpdate"
      @submit="handleFormSubmit"
      @cancel="showParameterForm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, PropType } from 'vue';
import { useVerticalNavigationStore } from '../../stores/vertical_navigation';
import { useContentManageStore } from '../../stores/content_manage';
import { useOrchestrationManageStore, ActionState } from '../../stores/orchestration_manage';
import { useKeyboardStateStore } from '../../stores/keyboard_state';
import { ACTION_META, getModifyActions, ActionType } from '../../lib/action-meta';
import type { StoryNode } from '../../types';

import ActionTypePicker from '../ui/ActionTypePicker.vue';
import FlagPanel from '../ui/FlagPanel.vue';
import InsertionForm from './InsertionForm.vue'; 

// --- PROPS ---
const props = defineProps({
  item: { 
    type: Object as PropType<StoryNode & { actionState?: ActionState }>,
    required: true 
  }
});

const emits = defineEmits<{
  (e: 'openContextMenu', event: MouseEvent): void,
}>()

// --- STORES ---
const vertNavStore = useVerticalNavigationStore();
const contentStore = useContentManageStore();
const orchStore = useOrchestrationManageStore();
const keyboardStore = useKeyboardStateStore();

// --- LOCAL UI STATE ---
const isHovered = ref(false);
const isActionPickerOpen = ref(false);
const showParameterForm = ref(false);
const DEFAULT_ACTION_TYPE: ActionType = 'rewrite';

// --- COMPUTED (Derived directly from props.item.actionState) ---

const isModifyActionActive = computed(() => props.item.actionState?.type === 'modify');
const isDeleteActionActive = computed(() => props.item.actionState?.type === 'delete');

const currentModifyType = computed<ActionType | null>(() => {
  return isModifyActionActive.value ? props.item.actionState?.modifyType || null : null;
});

const modifyActionsForPicker = computed(() => {
  const allActions = getModifyActions();
  const hasChildren = (props.item.children_ids || []).length > 0;
  if (hasChildren) {
    return allActions.filter(action => action.type !== 'generate_skeleton');
  } else {
    return allActions.filter(action => action.type !== 'regenerate_skeleton');
  }
});

const activeModifyActionIcon = computed(() => {
    return currentModifyType.value ? ACTION_META[currentModifyType.value].icon : '';
});

const activeModifyActionCategoryIcon = computed(() => {
    return currentModifyType.value ? ACTION_META[currentModifyType.value].helperIcon || '' : '';
});

const circleTitle = computed(() => {
    if (currentModifyType.value) return ACTION_META[currentModifyType.value]?.name || 'Select Action';
    return 'Choose an action';
});

// --- HELPER FLAGS ---
const helperFlags = computed(() => {
  return currentModifyType.value ? ACTION_META[currentModifyType.value]?.flags || {} : {}
});

const currentHelperFlag = computed(() => {
    if (isModifyActionActive.value && props.item.actionState?.flag) {
        return helperFlags.value[props.item.actionState.flag];
    }
    return undefined;
});

// --- UI VISIBILITY ---
const hasParameters = computed(() => !!currentHelperFlag.value?.parameters);
const canShowHelperFlags = computed(() => {
  const isHidden = currentHelperFlag.value?.meta?.isHidden || false;
  return isModifyActionActive.value && Object.keys(helperFlags.value).length > 0 && !isHidden;
});
const canShowDeleteButton = computed(() => (isHovered.value && keyboardStore.ctrlPressed && !isModifyActionActive.value) || isDeleteActionActive.value);

// --- METHODS (Immediate dispatch to orchestration store) ---

function handleCircleClick() {
  if (isModifyActionActive.value) {
    isActionPickerOpen.value = !isActionPickerOpen.value;
  }
}

function handleDblClick() {
  if (props.item.actionState && props.item.actionState.type == 'modify') {
    orchStore.clearAction(props.item.id);
  } else {
    orchStore.setAction(props.item.id, { type: 'modify', modifyType: DEFAULT_ACTION_TYPE });
  }
  isActionPickerOpen.value = false;
}

function handleDeleteClick() {
  if (isDeleteActionActive.value) {
    orchStore.clearAction(props.item.id);
  } else {
    orchStore.setAction(props.item.id, { type: 'delete' });
  }
  isActionPickerOpen.value = false;
}

function handleActionTypeUpdate(newType: ActionType) {
  const flags = ACTION_META[newType].flags;
  const active_flag = flags && Object.keys(flags).length > 0 ? Object.keys(flags)[0] : undefined;
  let initialParams = {};

  isActionPickerOpen.value = false;

  if (active_flag && flags?.[active_flag]?.parameters) {
    for (const key in flags[active_flag].parameters) {
      initialParams[key] = flags[active_flag].parameters[key].defaultValue;
    }
    showParameterForm.value = true;
  } else {
    showParameterForm.value = false;
  }

  orchStore.setAction(props.item.id, { 
    type: 'modify', 
    modifyType: newType, 
    flag: active_flag,
    parameters: initialParams
  });
}

function handleHelperFlagUpdate(flagId: string) {
  if (!isModifyActionActive.value) return

  const flag = ACTION_META[currentModifyType.value].flags?.[flagId] || null;

  if (flag == null) {
    orchStore.setAction(props.item.id, {
      type: 'modify',
      modifyType: currentModifyType.value,
      flag: flagId
    });

    return
  };

  let initialParams = {};

  if (flag.parameters) {
    for (const key in flag.parameters) {
      initialParams[key] = flag.parameters[key].defaultValue;
    }
    showParameterForm.value = true;
  } else {
    showParameterForm.value = false;
  }

  orchStore.setAction(props.item.id, { 
    type: 'modify', 
    modifyType: currentModifyType.value, 
    flag: flagId,
    parameters: initialParams
  });
}

function executeSimpleAction() {
  if (!currentModifyType.value) return;
  console.log(`Executing simple action: ${currentModifyType.value} for node ${props.item.id}`);
  // Here you would call the actual logic, e.g., a store action
  // orchStore.executeAction(props.item.id, currentModifyType.value, {});
  
  // Clear the action state afterwards
  orchStore.clearAction(props.item.id);
}

function handleFormUpdate(data: Record<string, any>) {
  if (!isModifyActionActive.value) return;
  
  // Update the action in the store with the latest parameters from the form.
  orchStore.setAction(props.item.id, {
    type: 'modify',
    modifyType: props.item.actionState?.modifyType,
    flag: props.item.actionState?.flag,
    parameters: data
  });
}

function handleFormSubmit(data: Record<string, any> ) {
  console.log(`Executing action with parameters: ${currentModifyType.value} for node ${props.item.id}`, data);
  // orchStore.executeAction(props.item.id, currentModifyType.value, data);
  showParameterForm.value = false;
  orchStore.clearAction(props.item.id);
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
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;

    position: relative;
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

.icon {
  overflow: hidden;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-icon {
  position: absolute;
  top: 0;
  left: 0;
  transform: translate(-50%, -50%);
  color: var(--main-color);

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

.action-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 4px;
}

.icon-btn, 
.apply-btn,
.context_menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  color: var(--sub-color);
  background: none;
}

.context_menu-btn {
  border: none;
}


.icon-btn, 
.apply-btn {
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
}

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
