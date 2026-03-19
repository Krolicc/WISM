<template>
  <div class="insertion-form-wrapper">
    <!-- Timeline Node -->
    <div class="timeline-node" @click="emit('remove')" title="Remove">
        <div class="timeline-line"></div>
        <div class="timeline-circle new-item-node">#</div>
    </div>
    <!-- Form -->
    <div class="form-content">
        <input 
            type="number" 
            class="count-input"
            v-model="action.params.count"
            min="1"
            />
            <textarea 
            class="description-input"
            v-model="action.params.idea"
            placeholder="Description if necessary..."
        ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GenerateAction } from '../../stores/orchestration';

const props = defineProps<{ 
    action: GenerateAction
}>();

const emit = defineEmits<{
    (e: 'remove'): void,
}>();

</script>

<style scoped>
.insertion-form-wrapper {
    position: relative;
    padding-left: 60px; /* Space for the timeline node */
    margin: 10px 0;
    display: flex;
    align-items: center; /* This will help center the node */
}

.timeline-node {
    position: absolute;
    left: 0;
    top: 0;
    width: 40px;
    height: 100%;
    display: flex;
    align-items: center; /* Center the circle vertically */
    justify-content: center;
    z-index: 2;
    cursor: pointer;
}

.timeline-line {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 19px; /* (40px - 2px) / 2 */
    width: 2px;
    background-color: var(--main-color);
}

.timeline-circle.new-item-node {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background-color: var(--main-color);
    border: 2px solid var(--main-color);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1rem;
    z-index: 3;
    flex-shrink: 0; /* Prevent shrinking */
    transition: background-color 0.2s, border-color 0.2s;
}

.timeline-node:hover .timeline-circle.new-item-node {
    background-color: #d32f2f; /* Red */
    border-color: #d32f2f; /* Red */
}

.timeline-node:hover .timeline-line {
    background-color: #d32f2f;
}


.form-content {
    background-color: var(--container-bg);
    display: flex;
    gap: 0.75rem;
    width: 100%;
}

.count-input {
    font-size: 0.9rem;
    width: 50px;
    height: fit-content;
    padding: .5rem;
    text-align: center;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background-color: var(--bg-color);
    color: var(--text-color);
}

.description-input {
    flex-grow: 1;
    min-height: 40px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background-color: var(--bg-color);
    color: var(--text-color);
    padding: 0.5rem;
    resize: vertical;
}
</style>
