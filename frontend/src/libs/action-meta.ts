
import { AppAction } from '../types/actions';

export interface ActionParameterBase {
    label: string;
    required?: boolean;
}

export interface BooleanParameter extends ActionParameterBase {
    type: 'boolean';
    defaultValue?: boolean;
}

export interface TextParameter extends ActionParameterBase {
    type: 'text';
    defaultValue?: string;
}

export interface NumberParameter extends ActionParameterBase {
    type: 'number';
    defaultValue?: number;
}

export interface SelectOption {
    value: string | number;
    label: string;
}
export interface SelectParameter extends ActionParameterBase {
    type: 'select';
    options: SelectOption[];
    defaultValue?: string | number;
}

export type ActionParameter = BooleanParameter | TextParameter | NumberParameter | SelectParameter;

export interface ActionFlag {
    id: string;
    name: string;
    description: string;
    icon: string;

    parameters?: Record<string, ActionParameter>;

    meta?: {
        isHidden?: boolean;
    }
}

export type ActionFlagsMap = Record<string, ActionFlag>;

interface ActionMeta {
    name: string;
    icon: string;
    helperIcon?: string;
    category: 'create' | 'modify' | 'delete' | 'move' | 'update' | 'exp';
    flags?: ActionFlagsMap; 
}

const CONTENT_ACTIONS = {
    manual: `
        <svg width="10" height="48" viewBox="0 -9 5 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M3.41211 8C3.41211 7.44772 2.96439 7 2.41211 7C1.85982 7 1.41211 7.44772 1.41211 8V23C1.41211 23.5523 1.85982 24 2.41211 24C2.96439 24 3.41211 23.5523 3.41211 23V8ZM2.07878 21.6667C2.07878 21.8508 2.22801 22 2.41211 22C2.5962 22 2.74544 21.8508 2.74544 21.6667V9.74447C2.74544 9.56037 2.5962 9.41113 2.41211 9.41113C2.22801 9.41113 2.07878 9.56037 2.07878 9.74447V21.6667Z" fill="currentColor"/>
            <path d="M2.41211 0.5L4.25683 3.69522C4.35192 3.85993 4.34534 4.06433 4.23983 4.22257L3.56054 5.24146C3.46781 5.38055 3.3117 5.4641 3.14452 5.4641H1.67969C1.51252 5.4641 1.35641 5.38055 1.26368 5.24146L0.584384 4.22257C0.478882 4.06433 0.472294 3.85993 0.567388 3.69522L2.41211 0.5ZM2.41211 0.5V3.46387" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    `,
    generate: `
        <svg width="14" height="50" viewBox="0 -9 7 25" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M4.54004 8.04004C4.54004 7.48775 4.09232 7.04004 3.54004 7.04004C2.98775 7.04004 2.54004 7.48775 2.54004 8.04004L2.54004 23.04C2.54004 23.5923 2.98775 24.04 3.54004 24.04C4.09232 24.04 4.54004 23.5923 4.54004 23.04L4.54004 8.04004ZM3.20671 21.7067C3.20671 21.8908 3.35594 22.04 3.54004 22.04C3.72413 22.04 3.87337 21.8908 3.87337 21.7067L3.87337 9.37337C3.87337 9.18928 3.72413 9.04004 3.54004 9.04004C3.35594 9.04004 3.20671 9.18928 3.20671 9.37337L3.20671 21.7067Z" fill="currentColor"/>
            <path d="M3.91113 2.32617C3.99696 2.57309 4.2279 2.74077 4.48926 2.74609L5.74219 2.77051L4.74316 3.52832C4.5349 3.68626 4.44677 3.95782 4.52246 4.20801L4.88574 5.40723L3.85742 4.69141L3.77344 4.64258C3.57225 4.54462 3.33031 4.56077 3.14258 4.69141L2.11328 5.40723L2.47754 4.20801C2.55323 3.95782 2.4651 3.68626 2.25684 3.52832L1.25684 2.77051L2.51074 2.74609C2.7721 2.74077 3.00304 2.57309 3.08887 2.32617L3.5 1.14258L3.91113 2.32617Z" stroke="currentColor" stroke-width="0.75" stroke-linejoin="round"/>
        </svg>
    `,
    skeleton: `
        <svg width="20" height="18" viewBox="0 0 20 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C12 3.10457 11.1046 4 10 4C8.89543 4 8 3.10457 8 2C8 0.895431 8.89543 0 10 0C11.1046 0 12 0.895431 12 2Z" fill="currentColor"/>
            <path d="M4 16C4 17.1046 3.10457 18 2 18C0.895431 18 0 17.1046 0 16C0 14.8954 0.895431 14 2 14C3.10457 14 4 14.8954 4 16Z" fill="currentColor"/>
            <path d="M20 16C20 17.1046 19.1046 18 18 18C16.8954 18 16 17.1046 16 16C16 14.8954 16.8954 14 18 14C19.1046 14 20 14.8954 20 16Z" fill="currentColor"/>
            <path d="M17 11C17 11 16.9813 8.81304 15.4444 8.33309C13.9076 7.85313 12.7797 8.83779 11.5556 8.33309C10.3314 7.82839 10 7 10 7C10 7 9.75447 7.90348 8.44444 8.33378C7.13442 8.76407 6.03206 7.93217 4.55556 8.33378C3.07905 8.73538 3 11 3 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>

    `
};

const CONTENT_ACTION_HELPERS = {
    regenerate: `
        <svg width="24" height="24" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="6" r="6" fill="var(--container-bg)"/>
            <path d="M8.62402 6.00781C8.62402 6.21492 8.79192 6.38281 8.99902 6.38281C9.20613 6.38281 9.37402 6.21492 9.37402 6.00781H8.99902H8.62402ZM3.37402 4.50781H2.99902C2.99902 4.71492 3.16692 4.88281 3.37402 4.88281V4.50781ZM3.74902 3.19531C3.74902 2.98821 3.58113 2.82031 3.37402 2.82031C3.16692 2.82031 2.99902 2.98821 2.99902 3.19531H3.37402H3.74902ZM4.49902 4.88281C4.70613 4.88281 4.87402 4.71492 4.87402 4.50781C4.87402 4.30071 4.70613 4.13281 4.49902 4.13281V4.50781V4.88281ZM5.99902 3.00781V3.38281C7.47942 3.38281 8.62402 4.52742 8.62402 6.00781H8.99902H9.37402C9.37402 4.11321 7.89363 2.63281 5.99902 2.63281V3.00781ZM3.37402 4.50781L3.7007 4.69196C4.14353 3.90639 4.99653 3.38281 5.99902 3.38281V3.00781V2.63281C4.72816 2.63281 3.62426 3.30024 3.04735 4.32366L3.37402 4.50781ZM3.37402 4.50781H3.74902V3.19531H3.37402H2.99902V4.50781H3.37402ZM3.37402 4.50781V4.88281H4.49902V4.50781V4.13281H3.37402V4.50781Z" fill="currentColor"/>
            <path d="M3.37402 6.00781C3.37402 5.80071 3.20613 5.63281 2.99902 5.63281C2.79192 5.63281 2.62402 5.80071 2.62402 6.00781H2.99902H3.37402ZM8.62402 7.50781H8.99902C8.99902 7.30071 8.83113 7.13281 8.62402 7.13281V7.50781ZM8.24902 8.82031C8.24902 9.02742 8.41692 9.19531 8.62402 9.19531C8.83113 9.19531 8.99902 9.02742 8.99902 8.82031H8.62402H8.24902ZM7.49902 7.13281C7.29192 7.13281 7.12402 7.30071 7.12402 7.50781C7.12402 7.71492 7.29192 7.88281 7.49902 7.88281V7.50781V7.13281ZM5.99902 9.00781V8.63281C4.51863 8.63281 3.37402 7.48821 3.37402 6.00781H2.99902H2.62402C2.62402 7.90242 4.10442 9.38281 5.99902 9.38281V9.00781ZM8.62402 7.50781L8.29735 7.32366C7.85452 8.10923 7.00152 8.63281 5.99902 8.63281V9.00781V9.38281C7.26988 9.38281 8.37378 8.71538 8.9507 7.69196L8.62402 7.50781ZM8.62402 7.50781H8.24902V8.82031H8.62402H8.99902V7.50781H8.62402ZM8.62402 7.50781V7.13281H7.49902V7.50781V7.88281H8.62402V7.50781Z" fill="currentColor"/>
            <path d="M7.18319 5.88277C7.29201 5.92304 7.29201 6.07696 7.18319 6.11723L6.45904 6.38519C6.42483 6.39785 6.39785 6.42483 6.38519 6.45904L6.11723 7.18319C6.07696 7.29201 5.92304 7.29201 5.88277 7.18319L5.61481 6.45904C5.60215 6.42483 5.57517 6.39785 5.54096 6.38519L4.81681 6.11723C4.70799 6.07696 4.70799 5.92304 4.81681 5.88277L5.54096 5.61481C5.57517 5.60215 5.60215 5.57517 5.61481 5.54096L5.88277 4.81681C5.92304 4.70799 6.07696 4.70799 6.11723 4.81681L6.38519 5.54096C6.39785 5.57517 6.42483 5.60215 6.45904 5.61481L7.18319 5.88277Z" fill="currentColor"/>
        </svg>
    `,
    generate: `
        <svg width="24" height="24" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="6" r="6" fill="var(--container-bg)"/>
            <path d="M8.87484 7.20179C8.98027 7.15331 9.08911 7.26215 9.04063 7.36758L8.71806 8.0691C8.70281 8.10225 8.70281 8.1404 8.71805 8.17354L9.04063 8.87506C9.08911 8.98049 8.98027 9.08933 8.87484 9.04085L8.17332 8.71828C8.14017 8.70304 8.10202 8.70304 8.06887 8.71828L7.36735 9.04085C7.26192 9.08933 7.15308 8.98049 7.20156 8.87506L7.52413 8.17354C7.53937 8.1404 7.53937 8.10225 7.52413 8.0691L7.20156 7.36758C7.15308 7.26215 7.26192 7.15331 7.36735 7.20179L8.06887 7.52436C8.10202 7.5396 8.14017 7.5396 8.17331 7.52436L8.87484 7.20179Z" fill="currentColor"/>
            <path d="M8.03402 2.92151C8.13945 2.87303 8.24829 2.98188 8.19981 3.0873L8.00611 3.50855C7.99087 3.5417 7.99087 3.57985 8.00611 3.61299L8.19981 4.03424C8.24829 4.13967 8.13945 4.24851 8.03402 4.20003L7.61277 4.00634C7.57962 3.9911 7.54147 3.9911 7.50833 4.00634L7.08708 4.20003C6.98165 4.24851 6.87281 4.13967 6.92129 4.03424L7.11498 3.61299C7.13023 3.57985 7.13023 3.5417 7.11498 3.50855L6.92129 3.0873C6.87281 2.98187 6.98165 2.87303 7.08708 2.92151L7.50833 3.11521C7.54147 3.13045 7.57962 3.13045 7.61277 3.11521L8.03402 2.92151Z" fill="currentColor"/>
            <path d="M5.28402 4.67151C5.38945 4.62303 5.49829 4.73188 5.44981 4.8373L4.91125 6.00855C4.896 6.0417 4.896 6.07985 4.91125 6.11299L5.44981 7.28424C5.49829 7.38967 5.38945 7.49851 5.28402 7.45003L4.11277 6.91147C4.07962 6.89623 4.04147 6.89623 4.00833 6.91147L2.83708 7.45003C2.73165 7.49851 2.62281 7.38967 2.67129 7.28424L3.20985 6.11299C3.22509 6.07985 3.22509 6.0417 3.20985 6.00855L2.67129 4.8373C2.62281 4.73188 2.73165 4.62303 2.83708 4.67151L4.00833 5.21007C4.04147 5.22532 4.07962 5.22532 4.11277 5.21007L5.28402 4.67151Z" fill="currentColor"/>
        </svg>
    `
};

export const ACTION_META: Record<AppAction['type'], ActionMeta> = {
    // --- Create Actions ---
    'create_manual': {
        name: 'Ручное создание',
        icon: CONTENT_ACTIONS.manual,
        category: 'create',
    },
    'create_generate': {
        name: 'Генеративное создание',
        icon: CONTENT_ACTIONS.generate,
        helperIcon: CONTENT_ACTION_HELPERS.generate,
        category: 'modify',
        flags: {
            regenerate: {
                id: 'generate',
                name: '',
                description: '',
                icon: ``,
            
                parameters: {
                    count: {
                        type: 'number',
                        label: 'Кол-во дочерних узлов',
                        defaultValue: 1,
                        required: true
                    },

                    prompt: {
                        type: 'text',
                        label: 'Пользовательский промпт',
                        defaultValue: "",
                        required: true
                    }
                },

                meta: {
                    isHidden: true,
                },
            }
        }
    },
    // --- Re-Actions ---
    'regenerate': {
        name: 'Перегенерация',
        icon: CONTENT_ACTIONS.generate,
        helperIcon: CONTENT_ACTION_HELPERS.regenerate,
        category: 'modify',
        flags: {
            regenerate: {
                id: 'regenerate',
                name: 'Перегенерировать',
                description: 'Создать совершенно новую версию этой сцены на основе того же промта.',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11A8.1 8.1 0 0 0 4.5 9M4 5v4h4"/><path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"/></svg>`,
            }
        }
    },
    'rewrite': {
        name: 'Переписывание',
        icon: CONTENT_ACTIONS.manual,
        helperIcon: CONTENT_ACTION_HELPERS.regenerate,
        category: 'modify',
        flags: {
            deepen_details: {
                id: 'deepen_details',
                name: 'Углубить Детали',
                description: 'Обогатить текст сенсорными ощущениями, описаниями окружения и внутренними монологами, не меняя сюжета.',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-6-6m2-5a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z"/><line x1="10" x2="10" y1="7" y2="13"/><line x1="7" x2="13" y1="10" y2="10"/></svg>`
            },
            increase_pace: {
                id: 'increase_pace',
                name: 'Сократить / Ускорить Темп',
                description: 'Уплотнить текст, оставив только ключевые действия и диалоги для ускорения повествования.',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 19 22 12 13 5 13 19"/><polygon points="2 19 11 12 2 5 2 19"/></svg>`
            },
            change_tone: {
                id: 'change_tone',
                name: 'Изменить Тон',
                description: 'Переписать сцену, изменив ее эмоциональный окрас (напряженный, юмористический, мрачный и т.д.).',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22C6.5 22 2 17.5 2 12S6.5 2 12 2s10 4.5 10 10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>`
            },
            expand_dialogue: {
                id: 'expand_dialogue',
                name: 'Добавить / Расширить Диалог',
                description: 'Превратить повествование в живой диалог между персонажами для лучшего раскрытия их характеров.',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`
            },
            alternative_development: {
                id: 'alternative_development',
                name: 'Альтернативное Развитие',
                description: 'Создать сюжетную ветку, сгенерировав новый вариант развития событий с этой точки.',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v10a2 2 0 0 0 2 2h8"/><path d="M10 15l-4 4 4 4"/><path d="M18 9a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v10"/></svg>`
            }
        }
    },
    'alternate_node': {
        name: 'Создать альтеранивный узел',
        icon: '',
        category: 'exp',
    },

    'generate_skeleton': {
        name: 'Генерация скелета',
        icon: CONTENT_ACTIONS.skeleton,
        helperIcon: CONTENT_ACTION_HELPERS.generate,

        category: 'modify',
    },
    'regenerate_skeleton': {
        name: 'Перегенерация скелета',
        icon: CONTENT_ACTIONS.skeleton,
        helperIcon: CONTENT_ACTION_HELPERS.regenerate,
        category: 'modify',
        flags: {
            regenerate: {
                id: 'regenerate',
                name: 'Перегенерировать',
                description: 'Создать совершенно новую версию этой сцены на основе того же промта.',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11A8.1 8.1 0 0 0 4.5 9M4 5v4h4"/><path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"/></svg>`
            }
        }
    },

    // --- Другие действия ---
    'delete': {
        name: 'Удаление',
        icon: `<svg><!-- иконка корзины --></svg>`,
        category: 'delete',
    },
    'move': {
        name: 'Перемещение',
        icon: `<svg><!-- иконка перемещения --></svg>`,
        category: 'delete',
    },
    'update': {
        name: 'Обновление',
        icon: `<svg><!-- иконка редактирования --></svg>`,
        category: 'update',
    }
};

export type ActionType = keyof typeof ACTION_META;

export function getModifyActions() {
    return (Object.entries(ACTION_META) as [ActionType, typeof ACTION_META[ActionType]][])
        .filter(([, meta]) => meta.category === 'modify')
        .map(([type, meta]) => ({ type, meta }));
}

export function getCreateActions() {
    return (Object.entries(ACTION_META) as [ActionType, typeof ACTION_META[ActionType]][])
        .filter(([, meta]) => meta.category === 'create')
        .map(([type, meta]) => ({ type, meta }));
}

export function getExpActions() {
    return (Object.entries(ACTION_META) as [ActionType, typeof ACTION_META[ActionType]][])
        .filter(([, meta]) => meta.category === 'exp')
        .map(([type, meta]) => ({ type, meta }));
}