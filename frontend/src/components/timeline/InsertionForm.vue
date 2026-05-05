
<template>
  <div class="insertion-form-container">
    <div class="form-header">
      <h4>{{ title || 'Parameters' }}</h4>
      <button @click="emit('cancel')" class="cancel-btn">&times;</button>
    </div>

    <div v-if="hasParameters" class="form-body">
      <div v-for="(row, rowIndex) in formLayout" :key="rowIndex" class="form-row">
        <div v-for="key in row" :key="key" class="form-field">
          <label :for="key.toString()">{{ parameters[key].label }}</label>
          
          <input
            v-if="parameters[key].type === 'number'"
            type="number"
            :id="key.toString()"
            v-model.number="formData[key]"
            :required="parameters[key].required"
          />
          
          <textarea
            v-else-if="parameters[key].type === 'text'"
            :id="key.toString()"
            v-model="formData[key]"
            :required="parameters[key].required"
            rows="3"
          ></textarea>

          <select
            v-else-if="parameters[key].type === 'select'"
            :id="key.toString()"
            v-model="formData[key]"
            :required="parameters[key].required"
          >
            <option 
              v-for="option in (parameters[key] as SelectParameter).options" 
              :key="option.value" 
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <div class="form-footer">
      <button @click="submitForm" class="submit-btn">{{ submitText || 'Apply' }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import type { ActionParameter, SelectParameter } from '../../lib/action-meta';

// --- Props ---
const props = defineProps<{
  parameters: Record<string, ActionParameter>;
  initialData?: Record<string, any>; // <-- NEW PROP
  title?: string;
  submitText?: string;
}>();

// --- Emits ---
const emit = defineEmits<{
  (e: 'update:data', data: Record<string, any>): void; 
  (e: 'submit', data: Record<string, any>): void;
  (e: 'cancel'): void;
}>();

// --- State ---
const formData = ref<Record<string, any>>({});
const debounceTimeout = ref<number | null>(null);
const hasInitialized = ref(false); // Gate to prevent emit on mount

// --- Computed ---
const hasParameters = computed(() => Object.keys(props.parameters).length > 0);

const formLayout = computed(() => {
  const rows: (keyof typeof props.parameters)[][] = [];
  let nonTextPair: (keyof typeof props.parameters)[] = [];
  
  const paramKeys = Object.keys(props.parameters);

  for (const key of paramKeys) {
    const param = props.parameters[key];
    if (param.type === 'text') {
      if (nonTextPair.length > 0) {
        rows.push(nonTextPair);
        nonTextPair = [];
      }
      rows.push([key]);
    } else {
      nonTextPair.push(key);
      if (nonTextPair.length === 2) {
        rows.push(nonTextPair);
        nonTextPair = [];
      }
    }
  }
  
  if (nonTextPair.length > 0) {
    rows.push(nonTextPair);
  }
  
  return rows;
});

// --- Watcher with Debounce ---
watch(formData, (newData) => {
  // Clear the previous timeout if it exists
  if (!hasInitialized.value) {
    return;
  }
  
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value);
  }
  // Set a new timeout
  debounceTimeout.value = window.setTimeout(() => {
    // Emit the update event after the delay
    emit('update:data', newData);
  }, 500); // 500ms debounce delay
}, { deep: true }); // Use deep watch for nested object changes

// --- Lifecycle ---
onMounted(() => {
  if (props.parameters) {
    for (const key in props.parameters) {
      if (props.initialData && props.initialData[key] !== undefined) {
        formData.value[key] = props.initialData[key];
      } else {
        formData.value[key] = props.parameters[key].defaultValue;
      }
    }
  }
  
  window.setTimeout(() => hasInitialized.value = true);
});

onUnmounted(() => {
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value);
    emit('update:data', formData.value);
  }
})

// --- Methods ---
function submitForm() {
  // When submitting, clear any pending debounce timeout
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value);
  }
  // And emit the final data immediately with the 'submit' event
  emit('submit', formData.value);
}

</script>

<style scoped>
/* Styles are unchanged, they are generic enough */
.insertion-form-container {
  position: absolute;
  bottom: -1rem;
  left: 0;
  transform: translateY(100%);
  z-index: 1;
  background-color: var(--container-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  margin: 0.5rem 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 100%;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.form-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.cancel-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--sub-color);
  line-height: 1;
}

.form-body {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
}

input, select, textarea {
  width: 100%;
  padding: 0.5rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  background-color: var(--bg-color);
  color: var(--text-color);
  font-size: 1rem;
  box-sizing: border-box;
}

textarea {
  resize: vertical;
}

.form-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  background-color: var(--main-color);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
}

.submit-btn:hover {
  opacity: 0.9;
}
</style>
