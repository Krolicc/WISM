
import { PromptObject } from '../../types/prompt';

// The main template object, typed to enforce the new structure
export const FRAME_PROMPT_TEMPLATE: PromptObject = {
  "negative_prompt": {
    value: "",
    placeholder: "ugly, deformed, extra fingers, bad anatomy, watermark, text",
  },
  "scene_metadata": {
    fields: {
      "scene_id": { value: "", placeholder: "001" },
      "aspect_ratio": { value: "", placeholder: "16:9 | 9:16 | 1:1 | 2:3" },
      "time_period": { value: "", placeholder: "Современность | Киберпанк | Викторианская эпоха | Фэнтези" }
    },
  },
  "setting": {
    fields: {
      "location_type": { value: "", placeholder: "Экстерьер (на улице) | Интерьер (внутри)" },
      "description": { value: "", placeholder: "Детальное описание окружения..." },
      "time_of_day": { value: "", placeholder: "Утро | Полдень | Золотой час | Сумерки..." },
      "weather": { value: "", placeholder: "Ясно | Проливной дождь | Густой туман..." },
      "key_objects": { value: "", placeholder: "Объект 1 | Объект 2" },
      "background_details": { value: "", placeholder: "Что происходит на самом дальнем плане..." }
    },
  },
  "camera": {
    fields: {
      "angle": { value: "", placeholder: "На уровне глаз | Низкий ракурс..." },
      "shot_type": { value: "", placeholder: "Сверхдальний план | Дальний план..." },
      "lens_type": { value: "", placeholder: "Широкоугольный (Fisheye/14mm) | Стандартный (50mm)..." },
      "focus": { value: "", placeholder: "Глубокий (все в фокусе) | Мелкий (фон размыт)" },
      "motion_blur": { value: "", placeholder: "Отсутствует | Смаз от быстрого движения" }
    },
  },
  "lighting": {
    fields: {
      "style": { value: "", placeholder: "Высокий ключ (яркое) | Низкий ключ (темное)..." },
      "sources": { value: "", placeholder: "Солнце из окна | Неоновая вывеска" },
      "color_temperature": { value: "", placeholder: "Теплый (желтый) | Холодный (синий)..." },
      "description": { value: "", placeholder: "Заметки о тенях и атмосфере..." }
    },
  },
    "vfx_and_atmosphere": {
    fields: {
      "particles": { value: "", placeholder: "Пылинки в лучах света | Искры от костра..." },
      "smoke_and_fog": { value: "", placeholder: "Стелющийся по полу туман | Густой дым" },
      "special_effects": { value: "", placeholder: "Магическое свечение | Голограммы | Блики" }
    },
  },
  "sfx_and_text": {
    fields: {
      "text": { value: "", placeholder: "БАМ!" },
      "style": { value: "", placeholder: "Рваный, 'взрывной' шрифт | Готический" },
      "placement": { value: "", placeholder: "В правом верхнем углу | Перекрывает сцену" }
    },
  },
  "composition": {
    fields: {
      "rule": { value: "", placeholder: "Правило третей | Золотое сечение | Симметрия" },
      "leading_lines": { value: "", placeholder: "Рельсы ведут взгляд к персонажу" },
      "notes": { value: "", placeholder: "Общие заметки о балансе кадра" }
    },
  },
  "style": {
    fields: {
      "medium": { value: "", placeholder: "Цифровая живопись | 3D рендер | Фотореализм" },
      "reference_artists": { value: "", placeholder: "Имя художника 1 | Имя художника 2" },
      "general_style": { value: "", placeholder: "Аниме в стиле Ghibli | Город грехов" },
      "color_palette": {
        fields: {
          "primary_colors": { value: "", placeholder: "Красный | Глубокий черный" },
          "mood": { value: "", placeholder: "Пастельные тона | Неоновый киберпанк | Монохром" }
        },
      },
      "quality_tags": { value: "", placeholder: "masterpiece, 8k, cinematic" }
    },
  }
};
