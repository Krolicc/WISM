import { reactive } from 'vue';

// Interface for a single action hint
export interface Action {
  keys: string[][]; // Changed from string[] to string[][]
  description: string;
}

// The state holds visibility and the list of actions to display
export const actionHintState = reactive({
  visible: false,
  actions: [] as Action[],
});

// Function to show the hint with specific actions
export function showActionHint(actions: Action[]) {
  actionHintState.actions = actions;
  actionHintState.visible = true;
}

// Function to hide the hint
export function hideActionHint() {
  actionHintState.visible = false;
  // Optional: clear actions after a delay to prevent flickering on quick mouse-out/in
  setTimeout(() => {
    if (!actionHintState.visible) {
        actionHintState.actions = [];
    }
  }, 200);
}
