
import { ref, watch, type Ref } from 'vue';
import { cloneDeep } from 'lodash-es';
import { Frame } from '../types';
import { useFrameStore } from '../stores/frame_store';

import type { PromptObject, PromptSection, PromptField } from '../types/prompt';
import { FRAME_PROMPT_TEMPLATE } from '../libs/prompt_template/frame';

// The new StoryNode is generic, so we define a local, more specific type for frames.

// Type guards
const isField = (item: any): item is PromptField => 'value' in item && 'placeholder' in item;
const isSection = (item: any): item is PromptSection => 'fields' in item;

// Core logic functions
function mergeWithTemplate(data: any, template: PromptObject): PromptObject {
    const merged = cloneDeep(template);
    for (const key in merged) {
        const templateItem = merged[key];
        const dataItem = data ? data[key] : undefined;

        if (isField(templateItem) && dataItem !== undefined) {
            templateItem.value = dataItem.value ?? '';
            templateItem.isModified = dataItem.value !== '';
        } else if (isSection(templateItem) && dataItem) {
            templateItem.fields = mergeWithTemplate(dataItem.fields, templateItem.fields as PromptObject);
        }
    }
    for (const key in data) {
        if (!merged[key]) {
            merged[key] = cloneDeep(data[key]);
        }
    }
    return merged;
}

function cleanForSave(prompt: PromptObject): any {
    const cleaned: any = {};
    for (const key in prompt) {
        const item = prompt[key];
        if (isField(item)) {
            if (item.value && item.value !== '') {
                cleaned[key] = { value: item.value, user_actions: item.user_actions };
            }
        } else if (isSection(item)) {
            const cleanedFields = cleanForSave(item.fields as PromptObject);
            if (Object.keys(cleanedFields).length > 0) {
                cleaned[key] = { fields: cleanedFields, user_actions: item.user_actions };
            }
        }
    }
    return cleaned;
}

// The Composable function
export function usePromptManager(activeFrame: Ref<Frame | null>) {
    const frameStore = useFrameStore();
    const editablePrompt = ref<PromptObject | null>(null);

    watch(activeFrame, (newFrame) => {
        if (newFrame) {
            const savedPrompt = newFrame.detailed_prompt || {};
            editablePrompt.value = mergeWithTemplate(savedPrompt, FRAME_PROMPT_TEMPLATE);
        } else {
            editablePrompt.value = null;
        }
    }, { immediate: true, deep: true });

    function handlePromptUpdate(newValue: PromptObject) {
        editablePrompt.value = newValue;
    }

    async function saveDetailedPrompt() {
        if (!activeFrame.value || !editablePrompt.value) {
            throw new Error('No active frame or prompt to save.');
        }
        const cleanedData = cleanForSave(editablePrompt.value);
        await frameStore.updateFrame(activeFrame.value.id, { detailed_prompt: cleanedData });
    }

    return {
        editablePrompt,
        handlePromptUpdate,
        saveDetailedPrompt
    };
}
