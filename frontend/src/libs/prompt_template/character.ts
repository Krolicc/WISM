
import { PromptObject } from '../../types/prompt';

// The main template object for generating characters
export const CHARACTER_PROMPT_TEMPLATE: PromptObject = {
  "negative_prompt": {
    "id": "c2e0986f-0405-46e6-b75d-ffbc37f4caad",
    "value": "",
    "placeholder": "ugly, deformed, extra fingers, bad anatomy, watermark, text",
  },
  "general": {
    "id": "be8c9816-2d33-48d8-84ec-7fe5c9d550d7",
    "fields": {
      "age": {
        "id": "87cee14f-a2d6-4f01-9932-7d2f1a32ef8f",
        "value": "",
        "placeholder": "25-30"
      },
      "gender": {
        "id": "9760f974-f7a9-4392-ba31-fadffc04773e",
        "value": "",
        "placeholder": "Мужчина | Женщина | Неопределенный"
      },
      "role": {
        "id": "969e64fc-cea8-49e7-852b-ad002643fae2",
        "value": "",
        "placeholder": "Главный герой | Злодей | Помощник"
      }
    },
  },
  "appearance": {
    "id": "c977606d-57fd-438a-b769-b78fdfa3db97",
    "fields": {
      "body_type": {
        "id": "85b2766a-ddd8-4245-a083-6c42184751a9",
        "value": "",
        "placeholder": "Атлетическое | Худощавое | Плотное"
      },
      "height": {
        "id": "e37ddf40-1fbb-430d-831b-7ef1c54b4ed0",
        "value": "",
        "placeholder": "Высокий | Средний | Низкий"
      },
      "skin_tone": {
        "id": "61b06689-e0fa-4409-833f-4a3648353e3c",
        "value": "",
        "placeholder": "Светлая | Смуглая | Фантастический цвет"
      },
      "hair": {
        "id": "01576204-95ac-43e5-8b47-b824ff5c122a",
        "value": "",
        "placeholder": "Короткие темные волосы | Длинные светлые косы"
      },
      "eyes": {
        "id": "7cdbe2b7-84f0-4c8b-a8ec-0fefd1abd42b",
        "value": "",
        "placeholder": "Голубые | Карие | Светящиеся"
      },
      "distinguishing_features": {
        "id": "a8384437-f95b-4a34-8388-3e4708f6bb5a",
        "value": "",
        "placeholder": "Татуировка дракона на шее, шрам над бровью"
      }
    },
  },
  "clothing": {
    "id": "05766ee5-f42d-421e-a5a2-7e7f50663e9c",
    "fields": {
      "style": {
        "id": "a8384437-f95b-4a34-8388-3e4708f6bb5a",
        "value": "",
        "placeholder": "Современная городская | Фэнтезийная броня | Киберпанк"
      },
      "primary_color": {
        "id": "43f58565-f1b6-43f9-ae26-2a3d6a0e3174",
        "value": "",
        "placeholder": "Темно-синий | Ярко-красный"
      },
      "items": {
        "id": "bbd86bad-4307-4887-8711-8f2eb7c1b351",
        "value": "",
        "placeholder": "Кожаная куртка | Джинсы | Высокие ботинки"
      },
      "details": {
        "id": "5e4529d9-9b4c-40c4-b4a1-fdbd68dccdd1",
        "value": "",
        "placeholder": "Потрепанная, со множеством карманов"
      }
    },
  },
  "personality_and_pose": {
    "id": "4a2be33e-fae0-4906-98b4-f2b9d8be6593",
    "fields": {
      "emotion": {
        "id": "ff9c274a-d8ce-487a-81b1-1db393e7341e",
        "value": "",
        "placeholder": "Спокойствие | Гнев | Радость | Задумчивость"
      },
      "pose": {
        "id": "e71eafd0-76c9-4296-8aac-b55cc96dd569",
        "value": "",
        "placeholder": "Стоит, скрестив руки | Сидит в кресле | Бежит"
      },
      "key_traits": {
        "id": "f1060b5f-0c7a-4fa8-abcb-d211a7b87a72",
        "value": "",
        "placeholder": "Смелый | Саркастичный | Добрый"
      }
    },
  },
  "style": {
    "id": "b193b6c8-849a-4e47-97e0-cfe8f444df5f",
    "fields": {
      "medium": {
        "id": "7ca1400a-3698-4024-80fe-5d7ec24fabb0",
        "value": "", 
        "placeholder": "Цифровая живопись | 3D рендер | Аниме"
      },
      "reference_artists": {
        "id": "5abbcb49-151e-487f-9a69-4d55b2d37c1f",
        "value": "",
        "placeholder": "Artgerm | Greg Rutkowski"
      },
      "general_style": {
        "id": "00053a25-ce0d-4c5c-92ef-8c31b7b3ea6a",
        "value": "",
        "placeholder": "Реализм | Стилизация | Нуар"
      },
      "color_palette": {
        "id": "1234a912-2132-40b6-a654-85b5fd0ba8ff",
        "fields": {
          "primary_colors": {
            "id": "fb2e4a8e-64a1-4361-a2dd-1fbfc0c6307e",
            "value": "",
            "placeholder": "#FF0000 | #0000FF"
          },
          "mood": {
            "id": "06f793af-3e2a-4407-adf4-b939dbb3a37b",
            "value": "",
            "placeholder": "Яркая и насыщенная | Мрачная и приглушенная"
          }
        },
      },
      "quality_tags": {
        "id": "336abb2f-06d4-497b-abb3-08ae3bee4548",
        "value": "masterpiece, 8k, detailed",
        "placeholder": "masterpiece, 8k, cinematic"
      }
    },
  }
};
