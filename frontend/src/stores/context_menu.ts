
import { defineStore } from 'pinia';
import { type Ref } from 'vue';

// --- Types ---

export interface ContextMenuItem {
  id: string;
  text: string;
  disabled?: boolean;
  action?: () => void; // ADDED: An optional callback function
}

export type Placement = 
  | 'top-start' | 'top-end' 
  | 'bottom-start' | 'bottom-end'
  | 'left-start' | 'left-end'
  | 'right-start' | 'right-end';

  export type ItemsSource = ContextMenuItem[] | (() => ContextMenuItem[]) | Ref<ContextMenuItem[]>;

interface ContextMenuState {
  isOpen: boolean;
  items: ItemsSource;
  position: { x: number; y: number };
  placement: Placement;
  // New state to hold the selected item for observation if needed
  selectedItemId: string | null;
}

interface OpenOptions {
  items: ItemsSource;
  position: { x: number; y: number };
  placement?: Placement;
}

// --- Store Definition ---

export const useContextMenuStore = defineStore('context_menu', {
  state: (): ContextMenuState => ({
    isOpen: false,
    items: [],
    position: { x: 0, y: 0 },
    placement: 'bottom-start',
    selectedItemId: null,
  }),

  actions: {
    open(options: OpenOptions) {
      this.isOpen = true;
      this.items = options.items;
      this.position = options.position;
      this.placement = options.placement || 'bottom-start';
      this.selectedItemId = null; 
    },

    close() {
      if (this.isOpen) {
        this.isOpen = false;
        this.items = [];
      }
    },
    
    /**
     * Called when a menu item is clicked.
     * It executes the item's action if it exists.
     */
    selectItem(item: ContextMenuItem) {
        if (item.disabled) return;

        this.selectedItemId = item.id;
        console.log(`Menu item selected: ${item}`);

        // The magic happens here!
        if (item.action) {
            item.action(); // Execute the associated function
        }

        // The menu should always close after an action.
        this.close();
    },

    handleContextEvent(event: MouseEvent, items: ItemsSource, placement: Placement = 'bottom-start') {
        event.preventDefault();
        event.stopPropagation();
        
        this.open({
            items,
            position: { x: event.clientX, y: event.clientY },
            placement,
        });
    }
  },
});
