
import { defineStore } from 'pinia';
import { ref, readonly } from 'vue';

export const useKeyboardStateStore = defineStore('keyboardState', () => {
  // --- State ---
  const ctrlPressed = ref(false);
  const shiftPressed = ref(false);
  const altPressed = ref(false);
  const escapePressed = ref(false);

  // --- Private Methods ---

  /**
   * Updates the state based on a KeyboardEvent.
   * This works for both keydown and keyup.
   */
  const updateKeyState = (event: KeyboardEvent) => {
    ctrlPressed.value = event.ctrlKey;
    shiftPressed.value = event.shiftKey;
    altPressed.value = event.altKey;
    escapePressed.value = event.key == "Escape";
  };

  /**
   * Resets the state to false.
   * Crucial for when the user navigates away from the window.
   */
  const resetKeyState = () => {
    ctrlPressed.value = false;
    shiftPressed.value = false;
    altPressed.value = false;
    escapePressed.value = false;
  };

  // --- Lifecycle ---

  // This code runs only once when the store is first instantiated.
  // We check for `window` to ensure it only runs in the browser.
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', updateKeyState);
    window.addEventListener('keyup', updateKeyState);

    // If the user clicks away or tabs out, reset the state.
    window.addEventListener('blur', resetKeyState);
  }

  // --- Public API ---

  return {
    // We expose the state as `readonly` to prevent direct mutation from components.
    // The state can only be changed by the event listeners within this store.
    ctrlPressed: readonly(ctrlPressed),
    shiftPressed: readonly(shiftPressed),
    altPressed: readonly(altPressed),
    escapePressed: readonly(escapePressed),
  };
});
