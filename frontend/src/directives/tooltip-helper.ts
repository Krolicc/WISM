
import { useTooltipStore } from './../stores/tooltip';
import type { DirectiveBinding } from 'vue';

export const vTooltipHelper = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string>) {
    const tooltipStore = useTooltipStore();

    const text = binding.value;
    if (!text) return;

    const showTooltip = () => {
      if (binding.value) {
        tooltipStore.show(binding.value, el.getBoundingClientRect());
      }
    };
    const hideTooltip = () => {
      tooltipStore.hide();
    };

    el.addEventListener('mouseenter', showTooltip);
    el.addEventListener('mouseleave', hideTooltip);

    // Store handlers to remove them on unmount
    el.__tooltipHandlers = { showTooltip, hideTooltip };
  },
  beforeUnmount(el: HTMLElement) {
    if (el.__tooltipHandlers) {
      el.removeEventListener('mouseenter', el.__tooltipHandlers.showTooltip);
      el.removeEventListener('mouseleave', el.__tooltipHandlers.hideTooltip);
    }
  },
};

// Augment the HTMLElement type to include our custom property
declare global {
  interface HTMLElement {
    __tooltipHandlers?: {
      showTooltip: () => void;
      hideTooltip: () => void;
    };
  }
}
