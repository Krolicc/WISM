export interface GenerationFlag {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export const GENERATION_FLAGS: GenerationFlag[] = [
  {
    id: 'regenerate',
    name: 'Перегенерировать',
    description: 'Создать совершенно новую версию этой сцены на основе того же промта.',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11A8.1 8.1 0 0 0 4.5 9M4 5v4h4"/><path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"/></svg>`
  },
  {
    id: 'deepen_details',
    name: 'Углубить Детали',
    description: 'Обогатить текст сенсорными ощущениями, описаниями окружения и внутренними монологами, не меняя сюжета.',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-6-6m2-5a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z"/><line x1="10" x2="10" y1="7" y2="13"/><line x1="7" x2="13" y1="10" y2="10"/></svg>`
  },
  {
    id: 'increase_pace',
    name: 'Сократить / Ускорить Темп',
    description: 'Уплотнить текст, оставив только ключевые действия и диалоги для ускорения повествования.',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 19 22 12 13 5 13 19"/><polygon points="2 19 11 12 2 5 2 19"/></svg>`
  },
  {
    id: 'change_tone',
    name: 'Изменить Тон',
    description: 'Переписать сцену, изменив ее эмоциональный окрас (напряженный, юмористический, мрачный и т.д.).',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22C6.5 22 2 17.5 2 12S6.5 2 12 2s10 4.5 10 10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>`
  },
  {
    id: 'expand_dialogue',
    name: 'Добавить / Расширить Диалог',
    description: 'Превратить повествование в живой диалог между персонажами для лучшего раскрытия их характеров.',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`
  },
  {
    id: 'alternative_development',
    name: 'Альтернативное Развитие',
    description: 'Создать сюжетную ветку, сгенерировав новый вариант развития событий с этой точки.',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v10a2 2 0 0 0 2 2h8"/><path d="M10 15l-4 4 4 4"/><path d="M18 9a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v10"/></svg>`
  }
];
