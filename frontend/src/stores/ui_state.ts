import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useUIStateStore = defineStore('ui_state', () => {
    const expandedFlagPanelOwnerId = ref<string | null>(null);

    function setExpandedFlagPanel(ownerId: string | null) {
        expandedFlagPanelOwnerId.value = ownerId;
    }

    return {
        expandedFlagPanelOwnerId,
        setExpandedFlagPanel,
    };
});
