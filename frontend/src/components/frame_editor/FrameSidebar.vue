
<template>
  <div class="scene-sidebar-wrapper" tabindex="-1">
    <div class="sidebar-header">
        <h3>{{ title }}</h3>
        <button @click="showSettings = !showSettings" class="settings-btn" title="Settings">⚙️</button>

        <div v-if="showSettings" class="settings-panel">
            <label>
                <input type="checkbox" v-model="strictBoundaries" />
                Auto-expand to whole words
            </label>
            <label>
                <input type="checkbox" v-model="validateSegments" />
                Validate content quality
            </label>
        </div>
    </div>

    <div class="scene-description-content">
      <div 
        v-if="description"
        ref="interactiveTextArea"
        class="interactive-text-area" 
        @mouseup="handleTextSelection"
      >
        <p>
          <span
            v-for="(segment, index) in textSegments"
            :key="index"
            :class="{
                'reserved-text': segment.isReserved,
                'invalid-segment': validateSegments && !segment.isReserved && !segment.isValid
            }"
            @dblclick="handleFrameDoubleClick(segment.frameId)"
          >
            {{ segment.text }}
          </span>
        </p>
      </div>
      
      <div v-if="selectedText" class="selection-tooltip" :class="{ 'is-invalid': !isSelectionValid }">
        <p v-if="selectionWarning" class="selection-warning">{{ selectionWarning }}</p>
        <p>"{{ selectedText }}"</p>
        <button @click="createFrame" :disabled="!isSelectionValid">+ Create Frame</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import type { Frame } from '../../types';

const props = defineProps<{
  title: string | null;
  description: string | null;
  frames: Frame[];
}>();

const emit = defineEmits<{
  (e: 'create-frame-from-text', textRange: { start: number; end: number }): void;
  (e: 'select-frame', frameId: number): void;
}>();

// --- State ---
const selectedText = ref('');
const selectionRange = ref<{ start: number; end: number } | null>(null);
const interactiveTextArea = ref<HTMLElement | null>(null);
const showSettings = ref(false);
const strictBoundaries = ref(true);
const validateSegments = ref(true);
const isSelectionValid = ref(false);
const selectionWarning = ref('');

// --- Validation & Expansion Helpers ---
const isBoundaryChar = (char: string) => !char || /^\s$|[.,!?;:()"-]/.test(char);

function validateFreeSegment(text: string): boolean {
    // Use Unicode property escapes to detect letters and numbers from any language.
    return /[\p{L}\p{N}]/u.test(text);
}

function expandRangeToWords(range: Range): Range {
    if (range.startContainer.nodeType !== 3) return range;
    const text = range.startContainer.textContent || '';
    let start = range.startOffset;
    let end = range.endOffset;

    while (start > 0 && !isBoundaryChar(text[start - 1])) {
        start--;
    }
    while (end < text.length && !isBoundaryChar(text[end])) {
        end++;
    }
    // Smart punctuation capture
    if (end < text.length && /[.,!?;:]/.test(text[end])) {
        end++;
    }

    range.setStart(range.startContainer, start);
    range.setEnd(range.endContainer, end);
    return range;
}

function calculateGlobalRange(range: Range): { start: number; end: number } | null {
  const container = interactiveTextArea.value;
    if (!container || !container.contains(range.startContainer)) return null;
    try {
        const preSelectionRange = document.createRange();
        preSelectionRange.selectNodeContents(container);
        preSelectionRange.setEnd(range.startContainer, range.startOffset);
        
        const start = preSelectionRange.toString().length;
        const end = start + range.toString().length;
        return { start, end };
    } catch (e) {
        console.error("Error calculating range:", e);
        return null;
    }
}

// --- Core Logic ---
function handleTextSelection() {
  const selection = window.getSelection();
  
  if (!selection || selection.rangeCount === 0 || selection.toString().trim() === '') {
    selectedText.value = '';
    selectionRange.value = null;
    return;
  }

  let range = selection.getRangeAt(0);

  // Auto-expand selection if enabled (only for single-node selections)
  if (strictBoundaries.value && range.startContainer === range.endContainer) {
    range = expandRangeToWords(range);
    selection.removeAllRanges();
    selection.addRange(range);
  }

  const selectedString = selection.toString();
  selectedText.value = selectedString;

  // --- Validation Checks ---
  const reservedSpans = interactiveTextArea.value?.querySelectorAll('.reserved-text');
  let intersectsReserved = false;
  if (reservedSpans) {
    for (const span of reservedSpans) {
        if (range.intersectsNode(span)) {
            intersectsReserved = true;
            break;
        }
    }
  }

  if (intersectsReserved) {
    isSelectionValid.value = false;
    selectionWarning.value = 'Selection cannot include reserved text.';
    return;
  }

  if (validateSegments.value && !validateFreeSegment(selectedString)) {
      isSelectionValid.value = false;
      selectionWarning.value = 'Selection does not contain valid content.';
      return;
  }

  const globalRange = calculateGlobalRange(range);
  if (!globalRange) {
      isSelectionValid.value = false;
      selectionWarning.value = 'Could not determine selection range.';
      return;
  }

  // All checks passed
  isSelectionValid.value = true;
  selectionWarning.value = '';
  selectionRange.value = globalRange;
}

const textSegments = computed(() => {
  const desc = props.description;
  if (!desc) return [];
  const sortedFrames = [...props.frames]
      .filter(f => f.source_text_range && f.source_text_range.start < f.source_text_range.end)
      .sort((a, b) => a.source_text_range!.start - b.source_text_range!.start);

  const segments: { text: string; isReserved: boolean; frameId: string | null; isValid: boolean; }[] = [];
  let lastIndex = 0;

  for (const frame of sortedFrames) {
    const range = frame.source_text_range!;
    if (range.start > lastIndex) {
      const text = desc.substring(lastIndex, range.start);
      segments.push({ text, isReserved: false, frameId: null, isValid: validateFreeSegment(text) });
    }
    const reservedText = desc.substring(range.start, range.end);
    segments.push({ text: reservedText, isReserved: true, frameId: frame.id, isValid: true });
    lastIndex = range.end;
  }

  if (lastIndex < desc.length) {
    const text = desc.substring(lastIndex);
    segments.push({ text, isReserved: false, frameId: null, isValid: validateFreeSegment(text) });
  }
  return segments;
});

function createFrame() {
  if (isSelectionValid.value && selectionRange.value) {
    emit('create-frame-from-text', selectionRange.value);
  }
  selectedText.value = '';
  selectionRange.value = null;
  window.getSelection()?.removeAllRanges();
}

function handleFrameDoubleClick(frameId: string | null) {
  if (frameId) {
    emit('select-frame', props.frames.findIndex(f => f.id === frameId));
  }
}

// --- Global Event Handlers ---
const handleKeyDown = (event: KeyboardEvent) => {
  
  if (event.ctrlKey && event.key.toLowerCase() === 'a') {
    event.preventDefault();
    const area = interactiveTextArea.value;
    if (!area) return;
    const pElement = area.querySelector('p');
    if (pElement) {
      const selection = window.getSelection();
      if (!selection) return;
      const range = document.createRange();
      range.selectNodeContents(pElement);
      selection.removeAllRanges();
      selection.addRange(range);
      handleTextSelection();
    }
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown, true); // Use capture phase
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown, true);
});

</script>

<style scoped>
.scene-sidebar-wrapper {
  position: absolute;
  left: 2rem;
  bottom: 0;
  transform: translateY(100%);
  width: 350px;
  padding: 1.5rem;
  background-color: var(--container-bg);
  z-index: 100;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
  border-radius: var(--border-radius);
  outline: none;
}

.sidebar-header {
    position: relative; /* For settings panel positioning */
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.settings-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
}

.settings-panel {
    position: absolute;
    right: 0;
    top: 100%;
    z-index: 10;
    width: max-content;
    padding: 0.75rem 1rem;
    background-color: var(--container-bg-duller);
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-small);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.settings-panel label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
}

.scene-description-content, .interactive-text-area {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.interactive-text-area {
  overflow-y: auto;
  white-space: pre-wrap;
  font-size: 1rem;
  line-height: 1.7;
  color: var(--sub-color);
}

.reserved-text {
  background-color: color-mix(in srgb, var(--main-color) 25%, transparent);
  cursor: pointer;
  user-select: none;
}

.invalid-segment {
    color: color-mix(in srgb, var(--sub-color) 50%, transparent);
    user-select: none;
}

.selection-tooltip {
  border: 1px solid var(--border-color);
  margin-top: 1rem;
  background-color: var(--container-bg);
  padding: 1rem;
  border-radius: var(--border-radius);
}

.selection-tooltip.is-invalid { border-color: var(--danger-color); }
.selection-warning { color: var(--danger-color); font-size: 0.9rem; margin-bottom: 0.5rem; }
.selection-tooltip p { font-style: italic; margin: 0 0 1rem 0; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); }
.selection-tooltip p:first-of-type { margin-top: 0; }
.selection-tooltip p:last-of-type { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }

.selection-tooltip button {
    width: 100%;
    background-color: var(--main-color);
    color: white;
    padding: 0.75rem;
    border-radius: var(--border-radius);
    cursor: pointer;
    margin-top: 1rem;
}
.selection-tooltip button:disabled {
    background-color: var(--sub-color);
    cursor: not-allowed;
}

</style>
