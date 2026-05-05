
<template>
    <InsertionPoint 
        v-if="!isFormVisible" 
        @add="isFormVisible = true"
    />
    <InsertionForm 
        v-else
        :target-id="props.id"
        :relation="props.isBefore ? 'before' : 'after'"
        @remove="isFormVisible = false"
    />
</template>

<script setup lang="ts">
import { ref, defineAsyncComponent } from 'vue';

// --- Components ---
const InsertionPoint = defineAsyncComponent(() => import('./InsertionPoint.vue'));
const InsertionForm = defineAsyncComponent(() => import('./InsertionForm.vue'));

// --- Props ---
const props = defineProps<{ 
    id: string;
    isBefore: boolean;
    // parentId: string;
    // level: string; 
}>();

// --- State ---
const isFormVisible = ref(false);

</script>
