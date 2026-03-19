<template>
    <div class="prompt-editor-main">
        <div v-for="(item, key) in modelValue" :key="key.toString()">
        <!-- Render as a Section -->
        <div v-if="isSection(item)" class="section">
          <div class="section-header" @click="toggleSection(item)">
            <span class="section-title">{{ formatKey(key.toString()) }}</span>
            <div class="header-actions">
              <button v-if="item.user_actions" @click.stop="deleteItem(key)" class="delete-btn">&times;</button>
              <span class="toggle-icon">{{ item.isExpanded ? '&#9660;' : '&#9658;' }}</span>
            </div>
          </div>
          <div v-if="item.isExpanded" class="section-content">
            <!-- Recursive Component -->
            <prompt-editor :modelValue="item.fields" @update:modelValue="updateNested($event, key)" />
          </div>
        </div>
  
        <!-- Render as a Field -->
        <div v-else class="field">
          <label :for="key.toString()">{{ formatKey(key.toString()) }}</label>
          <div class="field-container">
            <textarea 
                :value="item.value" 
                @input="updateField(item, $event)" 
                :placeholder="item.placeholder"
                :class="getFieldClass(item)"
            ></textarea>
            <button v-if="item.user_actions" @click="deleteItem(key)" class="delete-btn field-delete-btn">&times;</button>
          </div>
        </div>
      </div>
      <div class="add-new-field">
        <input v-model="newItemName" @keyup.enter="addNewItem" placeholder="Enter new field or section name" />
        <button @click="addNewItem">Add Field</button>
        <button @click="addNewSection">Add Section</button>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, defineProps, defineEmits } from 'vue';
  import type { PromptSection, PromptField, PromptObject } from '../lib/prompt-templates';
  
  const props = defineProps<{
    modelValue: PromptObject;
  }>();
  
  const emit = defineEmits(['update:modelValue']);
  
  const newItemName = ref('');
  
  const isSection = (item: any): item is PromptSection => 'fields' in item;
  
  const formatKey = (key: string) => key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
  const toggleSection = (section: PromptSection) => {
    section.isExpanded = !section.isExpanded;
  };
  
  const getFieldClass = (field: PromptField) => {
    if (field.isModified && field.value === '') return 'empty';
    if (field.isModified) return 'modified';
    return '';
  };

  const updateField = (field: PromptField, event: Event) => {
    const target = event.target as HTMLTextAreaElement;
    field.value = target.value;
    if (!field.isModified) {
      field.isModified = true; 
    }
    // Inform the parent about the change
    emit('update:modelValue', { ...props.modelValue });
  };
  
  const updateNested = (newValue: any, key: string | number) => {
    const updatedModel = { ...props.modelValue };
    const section = updatedModel[key];
    if (isSection(section)) {
        section.fields = newValue;
        emit('update:modelValue', updatedModel);
    }
  };
  
  const deleteItem = (key: string | number) => {
    const updatedModel = { ...props.modelValue };
    delete updatedModel[key];
    emit('update:modelValue', updatedModel);
  };
  
  const addNewItem = () => {
    if (newItemName.value.trim() === '') return;
    const key = newItemName.value.trim();
    const newField: PromptField = {
        value: '',
        placeholder: 'Enter value',
        user_actions: true,
        isModified: true
    };
    const updatedModel = { ...props.modelValue, [key]: newField };
    emit('update:modelValue', updatedModel);
    newItemName.value = '';
  };
  
  const addNewSection = () => {
    if (newItemName.value.trim() === '') return;
    const key = newItemName.value.trim();
    const newSection: PromptSection = {
        fields: {},
        user_actions: true,
        isExpanded: true
    };
    const updatedModel = { ...props.modelValue, [key]: newSection };
    emit('update:modelValue', updatedModel);
    newItemName.value = '';
    };
</script>

<script lang="ts">
export default {
  name: 'PromptEditor' // Necessary for recursion
}
</script>
  
<style scoped>
  .section {
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
    background-color: var(--container-bg-duller);
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    cursor: pointer;
    user-select: none;
  }
  
  .section-header:hover {
    background-color: var(--hover-bg-color);
  }
  
  .section-title { font-weight: 600; }
.header-actions { display: flex; align-items: center; gap: 1rem; }
.toggle-icon { font-size: 0.8rem; color: var(--sub-color); }

  
  .section-content {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
  }
  
  .field { margin-bottom: 1rem; }
.field label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: var(--sub-color); }
.field-container { display: flex; gap: 0.5rem; }

  
  .field textarea {
    width: 100%;
    min-height: 80px;
    background-color: var(--bg-color);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-color);
    font-family: monospace;
    font-size: 0.9rem;
    padding: 0.75rem;
    resize: vertical;
    transition: border-color 0.2s, border-left 0.2s;
    border-left: 3px solid transparent;
  }
  
  .field textarea:focus { outline: none; border-color: var(--main-color); }
.field textarea.modified { border-left-color: var(--main-color-green); }
.field textarea.empty { border-left-color: var(--main-color-red); }

  
  .delete-btn {
      background: none;
      border: 1px solid var(--border-color);
      color: var(--main-color-red);
      border-radius: var(--border-radius);
      cursor: pointer;
  }
  
  .field-delete-btn { align-self: flex-start; height: 30px; width: 30px; }

  
  .add-new-field {
      display: flex;
      gap: .5rem;
      margin-top: 1.5rem;
      border-top: 1px solid var(--border-color);
    padding-top: 1.5rem;
  }
  
  .add-new-field input {
      flex-grow: 1;
      background-color: var(--bg-color);
      border: 1px solid var(--border-color);
      color: var(--text-color);
      padding: 0.5rem;
      border-radius: var(--border-radius);
  }

  .add-new-field button {
    background-color: var(--container-bg-lighter);
    border: 1px solid var(--border-color);
    color: var(--text-color);
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    cursor: pointer;
}
  </style>
  