
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { Frame } from '../types';
import { useContentManageStore } from './content_manage';
import { useOrchestrationFrameManagerStore } from './orchestration_frame_manager';
import mockData from '../example_jsons/story-structure.json';

export const useFrameStore = defineStore('frame', () => {
  // --- STATE ---
  // Это "реальные" данные, которые мы считаем неизменной основой (из mock-файла)
  const baseFrames = ref<Map<string, Frame>>(new Map(Object.entries(mockData.frames)));
  const isLoading = ref(false);

  // Подключаем наш новый оркестратор
  const orchestrationStore = useOrchestrationFrameManagerStore();

  // --- COMPUTED PROPERTIES (Включая виртуальное состояние) ---

  /**
   * Главное вычисляемое свойство, которое объединяет реальные данные с "виртуальными"
   * изменениями из оркестратора.
   */
  const virtualFrames = computed(() => {
    const plan = orchestrationStore.executablePlan;
    const framesCopy = new Map(baseFrames.value);

    for (const action of plan) {
      switch (action.type) {
        case 'create_frame':
          // Создаем виртуальный объект Frame
          const newFrame: Frame = {
            id: action.params.id,
            type: 'frame',
            source_text_range: action.params.source_text_range,
            // --- Значения по умолчанию для нового виртуального кадра ---
            title: action.params.prompt.substring(0, 30), // Для примера
            use_detailed_prompt: false,
            detailed_prompt: {},
            image_url: undefined,
            width: 1024, // Стандартные размеры
            height: 576,
            common_description: ''
          };
          framesCopy.set(action.params.id, newFrame);
          break;

        case 'update_frame':
          const frameToUpdate = framesCopy.get(action.params.id);
          if (frameToUpdate) {
            // Применяем изменения поверх существующего кадра
            const updatedFrame = { ...frameToUpdate, ...action.params.content };
            framesCopy.set(action.params.id, updatedFrame);
          }
          break;

        case 'delete':
          framesCopy.delete(action.params.id);
          break;
      }
    }
    return framesCopy;
  });

  // --- GETTERS ---

  /**
   * Этот геттер теперь работает с "виртуальными" кадрами, всегда показывая актуальное состояние.
   */
  const getFramesForScene = computed(() => {
    const contentStore = useContentManageStore();
    
    return (sceneId: string): Frame[] => {
      // ВАЖНО: contentStore должен также работать с виртуальным состоянием, 
      // чтобы получить актуальный `childrenIds`.
      const scene = contentStore.getNode(sceneId);
      if (!scene || !scene.childrenIds) {
        return [];
      }
      
      return scene.childrenIds
        .map(frameId => virtualFrames.value.get(frameId))
        .filter((frame): frame is Frame => !!frame)
        .sort((a, b) => (a.source_text_range?.start || 0) - (b.source_text_range?.start || 0));
    };
  });

  function getFrame(frameId: string): Frame | undefined {
    return virtualFrames.value.get(frameId);
  }

  // --- ACTIONS (Остаются только для чтения, вся логика записи в оркестраторе) ---

  return { 
    isLoading,
    virtualFrames, // Предоставляем доступ к виртуальным кадрам для отладки
    getFramesForScene,
    getFrame,
  };
});
