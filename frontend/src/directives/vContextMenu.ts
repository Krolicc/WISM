
import type { Directive, DirectiveBinding } from 'vue';
import { useContextMenuStore, type ContextMenuItem, type Placement } from '../stores/context_menu';

// --- Types ---

// The directive can accept a simple array of items...
type DirectiveValueSimple = ContextMenuItem[];

// ...or a detailed configuration object.
interface DirectiveValueObject {
  items: ContextMenuItem[] | (() => ContextMenuItem[]);
  placement?: Placement;
  strategy?: 'mouse' | 'element'; // The positioning strategy
}

type DirectiveValue = DirectiveValueSimple | DirectiveValueObject;

// --- Event Handler ---

function handleContextMenu(event: MouseEvent, el: HTMLElement, binding: DirectiveBinding<DirectiveValue>) {
  event.preventDefault();
  event.stopPropagation();

  const store = useContextMenuStore();
  const value = binding.value;

  // --- Normalize Configuration ---
  let items: ContextMenuItem[];
  const placement: Placement = (typeof value === 'object' && value.placement) ? value.placement : 'bottom-start';
  const strategy: 'mouse' | 'element' = (typeof value === 'object' && value.strategy) ? value.strategy : 'mouse';

  // Resolve items if they are provided as a function
  if (typeof value === 'object' && typeof value.items === 'function') {
    items = value.items();
  } else if (typeof value === 'object') {
    items = value.items as ContextMenuItem[];
  } else {
    items = value;
  }

  if (!items || items.length === 0) {
    console.warn('v-context-menu: No items provided.');
    return;
  }

  // --- Calculate Position based on Strategy ---
  let position = { x: 0, y: 0 };

  if (strategy === 'mouse') {
    // Strategy 1: Position relative to the mouse cursor
    position = { x: event.clientX, y: event.clientY };
  } else {
    // Strategy 2: Position relative to the element itself
    const rect = el.getBoundingClientRect();
    switch (placement) {
      case 'top-start':    position = { x: rect.left, y: rect.top }; break;
      case 'top-end':      position = { x: rect.right, y: rect.top }; break;
      case 'bottom-start': position = { x: rect.left, y: rect.bottom }; break;
      case 'bottom-end':   position = { x: rect.right, y: rect.bottom }; break;
      case 'left-start':   position = { x: rect.left, y: rect.top }; break;
      case 'left-end':     position = { x: rect.left, y: rect.bottom }; break;
      case 'right-start':  position = { x: rect.right, y: rect.top }; break;
      case 'right-end':    position = { x: rect.right, y: rect.bottom }; break;
    }
  }

  // --- Open The Menu ---
  store.open({
    items,
    position,
    placement
  });
}

// --- Directive Definition ---

export const vContextMenu: Directive<HTMLElement, DirectiveValue> = {
  mounted(el, binding) {
    const handler = (e: MouseEvent) => handleContextMenu(e, el, binding);
    el.addEventListener('contextmenu', handler);
    // Store the handler on the element so we can remove it later
    (el as any).__vContextMenuHandler = handler;
  },

  unmounted(el) {
    const handler = (el as any).__vContextMenuHandler;
    if (handler) {
      el.removeEventListener('contextmenu', handler);
      delete (el as any).__vContextMenuHandler;
    }
  },
  
  // In case the items or config change
  updated(el, binding) {
    const oldHandler = (el as any).__vContextMenuHandler;
    if (oldHandler) {
        el.removeEventListener('contextmenu', oldHandler);
    }
    const newHandler = (e: MouseEvent) => handleContextMenu(e, el, binding);
    el.addEventListener('contextmenu', newHandler);
    (el as any).__vContextMenuHandler = newHandler;
  }
};
