
// Defines the structure for a single editable property field
export interface PromptField {
  value: string | string[];
  placeholder: string | string[];
  user_actions: boolean;
  isModified?: boolean;
}

// Defines the structure for a section containing multiple fields
export interface PromptSection {
  fields: { [key: string]: PromptField | PromptSection }; // Can be nested
  user_actions: boolean;
  isExpanded?: boolean; // To control UI visibility
}

// Defines a generic object containing either fields or sections
export type PromptObject = { [key: string]: PromptField | PromptSection };

// The main template object, typed to enforce the new structure
export const DETAILED_PROMPT_TEMPLATE: PromptObject = {
  "negative_prompt": {
    value: "",
    placeholder: "ugly, deformed, extra fingers, bad anatomy, watermark, text",
    user_actions: false,
    isModified: false
  },
  "scene_metadata": {
    fields: {
      "scene_id": { value: "", placeholder: "001", user_actions: false, isModified: false },
      "aspect_ratio": { value: "", placeholder: "16:9 | 9:16 | 1:1 | 2:3", user_actions: false, isModified: false },
      "time_period": { value: "", placeholder: "Современность | Киберпанк | Викторианская эпоха | Фэнтези", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  },
  "setting": {
    fields: {
      "location_type": { value: "", placeholder: "Экстерьер (на улице) | Интерьер (внутри)", user_actions: false, isModified: false },
      "description": { value: "", placeholder: "Детальное описание окружения...", user_actions: false, isModified: false },
      "time_of_day": { value: "", placeholder: "Утро | Полдень | Золотой час | Сумерки...", user_actions: false, isModified: false },
      "weather": { value: "", placeholder: "Ясно | Проливной дождь | Густой туман...", user_actions: false, isModified: false },
      "key_objects": { value: [], placeholder: ["Объект 1", "Объект 2"], user_actions: false, isModified: false },
      "background_details": { value: "", placeholder: "Что происходит на самом дальнем плане...", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  },
  "camera": {
    fields: {
      "angle": { value: "", placeholder: "На уровне глаз | Низкий ракурс...", user_actions: false, isModified: false },
      "shot_type": { value: "", placeholder: "Сверхдальний план | Дальний план...", user_actions: false, isModified: false },
      "lens_type": { value: "", placeholder: "Широкоугольный (Fisheye/14mm) | Стандартный (50mm)...", user_actions: false, isModified: false },
      "focus": { value: "", placeholder: "Глубокий (все в фокусе) | Мелкий (фон размыт)", user_actions: false, isModified: false },
      "motion_blur": { value: "", placeholder: "Отсутствует | Смаз от быстрого движения", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  },
  "lighting": {
    fields: {
      "style": { value: "", placeholder: "Высокий ключ (яркое) | Низкий ключ (темное)...", user_actions: false, isModified: false },
      "sources": { value: [], placeholder: ["Солнце из окна", "Неоновая вывеска"], user_actions: false, isModified: false },
      "color_temperature": { value: "", placeholder: "Теплый (желтый) | Холодный (синий)...", user_actions: false, isModified: false },
      "description": { value: "", placeholder: "Заметки о тенях и атмосфере...", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  },
    "vfx_and_atmosphere": {
    fields: {
      "particles": { value: "", placeholder: "Пылинки в лучах света | Искры от костра...", user_actions: false, isModified: false },
      "smoke_and_fog": { value: "", placeholder: "Стелющийся по полу туман | Густой дым", user_actions: false, isModified: false },
      "special_effects": { value: "", placeholder: "Магическое свечение | Голограммы | Блики", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  },
  "sfx_and_text": {
    fields: {
      "text": { value: "", placeholder: "БАМ!", user_actions: false, isModified: false },
      "style": { value: "", placeholder: "Рваный, 'взрывной' шрифт | Готический", user_actions: false, isModified: false },
      "placement": { value: "", placeholder: "В правом верхнем углу | Перекрывает сцену", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  },
  "composition": {
    fields: {
      "rule": { value: "", placeholder: "Правило третей | Золотое сечение | Симметрия", user_actions: false, isModified: false },
      "leading_lines": { value: "", placeholder: "Рельсы ведут взгляд к персонажу", user_actions: false, isModified: false },
      "notes": { value: "", placeholder: "Общие заметки о балансе кадра", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  },
  "style": {
    fields: {
      "medium": { value: "", placeholder: "Цифровая живопись | 3D рендер | Фотореализм", user_actions: false, isModified: false },
      "reference_artists": { value: [], placeholder: ["Имя художника 1", "Имя художника 2"], user_actions: false, isModified: false },
      "general_style": { value: "", placeholder: "Аниме в стиле Ghibli | Город грехов", user_actions: false, isModified: false },
      "color_palette": {
        fields: {
          "primary_colors": { value: [], placeholder: ["Красный", "Глубокий черный"], user_actions: false, isModified: false },
          "mood": { value: "", placeholder: "Пастельные тона | Неоновый киберпанк | Монохром", user_actions: false, isModified: false }
        },
        user_actions: false,
        isExpanded: false
      },
      "quality_tags": { value: "", placeholder: "masterpiece, 8k, cinematic", user_actions: false, isModified: false }
    },
    user_actions: false,
    isExpanded: false
  }
};
