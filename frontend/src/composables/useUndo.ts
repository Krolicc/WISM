
import { onMounted, onUnmounted } from 'vue';
import { useHistoryStore } from '../stores/history_store';

export function useUndo() {
  const historyStore = useHistoryStore();

  const handleKeyDown = (event: KeyboardEvent) => {
    // Проверяем, нажаты ли Ctrl (или Cmd на Mac) и Z
    if ((event.ctrlKey || event.metaKey) && event.key === 'z') {
      event.preventDefault(); // Предотвращаем стандартное поведение браузера
      
      // TODO: Добавить проверку на Shift для Redo
      // if (event.shiftKey) {
      //   historyStore.redo();
      // } else {
      //   historyStore.undo();
      // }

      console.log('Ctrl+Z detected, calling history.undo()');
      historyStore.undo();
    }
  };

  // Добавляем слушатель, когда компонент, использующий этот composable, монтируется
  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown);
  });

  // Убираем слушатель, когда компонент размонтируется, чтобы избежать утечек памяти
  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown);
  });

  // Этот composable не возвращает ничего, так как он просто устанавливает глобальный слушатель
}
