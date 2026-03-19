<template>
  <div class="flag-panel-container">
    <!-- Absolutely positioned block for flags BEFORE the active one -->
    <Transition name="slide-up">
      <div v-if="isExpanded" class="flags-before">
        <FlagButton
          v-for="flag in flagsBefore"
          :key="flag.id"
          :flag="flag"
          :is-active="false"
          @click="selectFlag(flag.id)"
        />
      </div>
    </Transition>

    <!-- The always-visible active flag -->
    <FlagButton
      v-if="activeFlag"
      class="active-flag-button"
      :flag="activeFlag"
      :is-active="true"
      @click="toggleExpand"
    />

    <!-- Absolutely positioned block for flags AFTER the active one -->
    <Transition name="slide-down">
      <div v-if="isExpanded" class="flags-after">
        <FlagButton
          v-for="flag in flagsAfter"
          :key="flag.id"
          :flag="flag"
          :is-active="false"
          @click="selectFlag(flag.id)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { GENERATION_FLAGS as flags } from '../../lib/generation-flags';
import FlagButton from './FlagButton.vue';

const props = defineProps<{ modelValue: string }>();

const emit = defineEmits<{
  (e: 'update:model-value', flagId: string): void, // Event to update the flag
}>();

const isExpanded = ref(false);

const activeFlagIndex = computed(() => flags.findIndex(f => f.id === props.modelValue));
const activeFlag = computed(() => flags[activeFlagIndex.value]);

const flagsBefore = computed(() => flags.slice(0, activeFlagIndex.value));
const flagsAfter = computed(() => flags.slice(activeFlagIndex.value + 1));

function selectFlag(flagId: string) {
  emit('update:model-value', flagId);
  isExpanded.value = false; // Collapse after selection
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}
</script>

<style scoped>
.flag-panel-container {
  position: relative; /* This is the positioning context for the absolute children */
  width: var(--button-size);
  height: var(--button-size);
  z-index: 10; /* Ensure the panel is above other timeline items */
  --gap: 8px;
  --button-size: 40px;
}

.active-flag-button {
  /* The active button is always visible and in the flow */
}

.flags-before,
.flags-after {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: var(--gap);
  width: var(--button-size);
  z-index: -1; /* Positioned behind the active button to not intercept clicks when hidden */
}

.flags-before {
  /* Positioned above the active button */
  bottom: calc(100% + var(--gap));
  flex-direction: column; /* This is the key change: stack items upwards */
}

.flags-after {
  /* Positioned below the active button */
  top: calc(100% + var(--gap));
  flex-direction: column;
}

/* --- Transitions --- */

.slide-up-enter-active,
.slide-up-leave-active,
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease-out;
}

/* SLIDE UP */
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

/* SLIDE DOWN */
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}
</style>
