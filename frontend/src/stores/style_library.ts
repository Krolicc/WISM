
import { ref } from 'vue';
import { defineStore } from 'pinia';
import type { StylePattern } from '../types/style-pattern';

// Имитируем API, чтобы не трогать основной файл api.ts на этом этапе
const fakeApi = {
  async analyzeStyle(text: string): Promise<StylePattern[]> {
    console.log('Отправка текста на анализ:', text.substring(0, 100) + '...');
    await new Promise(resolve => setTimeout(resolve, 1500)); // Имитация задержки сети

    // Моковые (тестовые) данные, которые вернет бэкенд
    const mockData: StylePattern[] = [
      {
        id: 'pattern-1',
        function: 'Описание персонажа через действие',
        text: 'Он вошел в комнату, не постучав, и сбросил мокрое пальто на стул, даже не взглянув на присутствующих.'
      },
      {
        id: 'pattern-2',
        function: 'Создание атмосферы через детали',
        text: 'Пылинки танцевали в единственном луче света, пробивавшемся сквозь грязное окно. В воздухе пахло старой бумагой и чем-то сладковатым, почти приторным.'
      },
      {
        id: 'pattern-3',
        function: 'Внутренний монолог с рефлексией',
        text: '"И зачем я только сюда пришел?" - подумал он, чувствуя, как знакомое раздражение подступает к горлу. Каждый раз одно и то же.'
      }
    ];

    console.log('Получен результат анализа:', mockData);
    return mockData;
  }
};

export const useStyleLibraryStore = defineStore('style_library', () => {
  const patterns = ref<StylePattern[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Отправляет текст на анализ и сохраняет полученные паттерны.
   */
  const analyzeText = async (text: string) => {
    if (!text.trim()) {
      error.value = 'Текст для анализа не может быть пустым.';
      return;
    }

    isLoading.value = true;
    error.value = null;
    try {
      const result = await fakeApi.analyzeStyle(text);
      patterns.value = result;
    } catch (e) {
      console.error(e);
      error.value = 'Произошла ошибка при анализе текста.';
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Очищает текущие проанализированные паттерны.
   */
  const clearAnalyzedPatterns = () => {
    patterns.value = [];
    error.value = null;
  };

  return {
    patterns,
    isLoading,
    error,
    analyzeText,
    clearAnalyzedPatterns,
  };
});
