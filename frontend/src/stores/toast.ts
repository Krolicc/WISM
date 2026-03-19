
import { reactive } from 'vue';

export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

let nextId = 0;

const toasts = reactive<Toast[]>([]);

export function useToasts() {
  const showToast = (message: string, type: Toast['type'] = 'success', duration: number = 3000) => {
    const id = nextId++;
    toasts.push({ id, message, type });

    setTimeout(() => {
      removeToast(id);
    }, duration);
  };

  const removeToast = (id: number) => {
    const index = toasts.findIndex(toast => toast.id === id);
    if (index !== -1) {
      toasts.splice(index, 1);
    }
  };

  return { toasts, showToast, removeToast };
}
