
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

export interface AcitonMeta {
  
}

export interface ActionItem {
  id: string;
  type: 'generate_entity_image';
  isSelected: boolean;
  payload: any;
  meta: any;
}

export interface Actions {[key: string]: ActionItem}

export const useActionQueueStore = defineStore('actionQueue', () => {
  // --- STATE ---
  const actions = ref<Actions>({});
  const isMenuOpened = ref<boolean>(false);

  /// --- COMPUTED ---
  const isAnySelected = computed(() => {
    return Object.values(actions.value).some(action => action.isSelected);
  })
  const count = computed(() => Object.keys(actions.value).length);

  // --- ACTIONS ---
  const addAction = (obj_id: string, type: 'generate_entity_image', payload: any, meta: any) => {
    const newAction: ActionItem = {
      id: crypto.randomUUID(),
      type,
      payload,
      meta,
      isSelected: true,
    };
    actions.value[obj_id] = newAction;
  };

  const discardSelected = () => {
    const remainingActions = Object.fromEntries(
      Object.entries(actions.value).filter(([id, action]) => !action.isSelected)
    );

    actions.value = remainingActions;
  }

  const toggleSelection = (actionId: string) => {
    const action = actions.value[actionId];
    if (action) {
      action.isSelected = !action.isSelected;
    }
  };

  const confirmAndProcessSelected = () => {
    const selectedActions = Object.values(actions.value).filter(action => action.isSelected);
    const remainingActions = Object.fromEntries(
      Object.entries(actions.value).filter(([id, action]) => action.isSelected)
    );

    const imageGenerationJobs = selectedActions
      .filter(action => action.type === 'generate_entity_image')
      .map(action => action.payload);

    if (imageGenerationJobs.length > 0) {
      console.log('--- Confirming and processing jobs ---');
      console.log(imageGenerationJobs);
      console.log('------------------------------------');
    }

    actions.value = remainingActions;

    return imageGenerationJobs;
  };

  const toggleMenuOpen = (force?: boolean) => isMenuOpened.value = force ?? !isMenuOpened.value;;

  return {
    count,
    isAnySelected,
    actions,
    isMenuOpened,
    addAction,
    discardSelected,
    toggleSelection,
    confirmAndProcessSelected,
    toggleMenuOpen,
  };
});
