import { showActionHint, hideActionHint } from '../stores/actionHint';
import type { Action } from '../stores/actionHint';

export const actionHintDirective = {
  mounted(el: HTMLElement, binding: { value: Action[] }) {
    const show = () => {
      if (binding.value && binding.value.length > 0) {
        showActionHint(binding.value);
      }
    };

    const hide = () => {
      hideActionHint();
    };

    el.addEventListener('mouseenter', show);
    el.addEventListener('mouseleave', hide);

    // Store handlers on the element to be able to remove them in unmounted
    el.__actionHintHandlers = { show, hide };
  },
  unmounted(el: HTMLElement) {
    if (el.__actionHintHandlers) {
      el.removeEventListener('mouseenter', el.__actionHintHandlers.show);
      el.removeEventListener('mouseleave', el.__actionHintHandlers.hide);
    }
  }
};

// Custom property on HTMLElement to store handlers
declare global {
  interface HTMLElement {
    __actionHintHandlers?: { 
      show: () => void;
      hide: () => void;
    };
  }
}
