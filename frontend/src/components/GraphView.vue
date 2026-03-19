<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { api } from './../services/api';
import { vTooltipHelper } from './../directives/tooltip-helper';
import { findPath } from './../composables/useAStarRouter';
import type { GraphNode, GraphRelationship } from '@/types';
import ActionHint from './ui/ActionHint.vue';

// --- Component State ---
const nodes = ref<GraphNode[]>([]);
const relationships = ref<GraphRelationship[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// --- Grid and Layout Settings ---
const grid = {
  size: 20, // A finer grid for the router
  nodeWidthCells: 6,
  nodeHeightCells: 2,
};

// --- Pan and Zoom ---
const transform = ref({ x: 0, y: 0, k: 1 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });

const canvasStyle = computed(() => ({
  transform: `translate(${transform.value.x}px, ${transform.value.y}px) scale(${transform.value.k})`,
}));

// --- Layout Algorithm ---
const nodePositions = computed(() => {
  const positions = new Map<string, { x: number; y: number }>();
  const occupied = new Set<string>();
  let col = 0, row = 0;

  nodes.value.forEach(node => {
    while(occupied.has(`${col},${row}`)) {
      col++;
    }
    positions.set(node.element_id, {
      x: col * (grid.nodeWidthCells + 2), // Position in grid cells
      y: row * (grid.nodeHeightCells + 2),
    });
    occupied.add(`${col},${row}`);
    
    if (col > 3) { 
      col = 0;
      row++;
    } else {
      col++;
    }
  });

  return positions;
});

const relationshipPaths = computed(() => {
    const gridSize = grid.size;
    const positions = nodePositions.value;
    if (positions.size === 0) return [];

    // 1. Create Routing Grid
    const maxX = Math.max(...Array.from(positions.values()).map(p => p.x)) + grid.nodeWidthCells;
    const maxY = Math.max(...Array.from(positions.values()).map(p => p.y)) + grid.nodeHeightCells;
    const routingGrid = Array.from({ length: maxY + 5 }, () => Array(maxX + 5).fill(0));

    // 2. Mark Obstacles
    nodes.value.forEach(node => {
        const pos = positions.get(node.element_id);
        if (!pos) return;
        for (let r = 0; r < grid.nodeHeightCells; r++) {
            for (let c = 0; c < grid.nodeWidthCells; c++) {
                if (routingGrid[pos.y + r] && routingGrid[pos.y + r][pos.x + c] !== undefined) {
                  routingGrid[pos.y + r][pos.x + c] = 1; // Mark as obstacle
                }
            }
        }
    });

    // 3. Find and Build Paths
    return relationships.value.map(rel => {
        const startNodePos = positions.get(rel.source);
        const endNodePos = positions.get(rel.target);
        if (!startNodePos || !endNodePos) return null;

        const startPoint = { x: startNodePos.x + Math.floor(grid.nodeWidthCells / 2), y: startNodePos.y - 1 };
        const endPoint = { x: endNodePos.x + Math.floor(grid.nodeWidthCells / 2), y: endNodePos.y - 1 };

        const path = findPath(routingGrid, startPoint, endPoint);

        if (!path) return null;

        // 4. Convert path to SVG string
        let d = `M ${path[0].x * gridSize} ${path[0].y * gridSize}`;
        for (let i = 1; i < path.length; i++) {
            d += ` L ${path[i].x * gridSize} ${path[i].y * gridSize}`;
        }
        
        return { d, rel };
    }).filter(p => p !== null);
});

// --- Lifecycle Hook ---
onMounted(async () => {
  try {
    isLoading.value = true;
    const response = await api.getFullGraph();
    nodes.value = response.nodes;
    relationships.value = response.relationships;
    error.value = null;
  } catch (err) {
    console.error('Failed to fetch graph data:', err);
    error.value = 'Failed to load graph data. Please try again later.';
  } finally {
    isLoading.value = false;
  }
});

// --- UI Methods & Event Handlers (mostly unchanged) ---
const getNodeColor = (labels: string[]) => {
  if (!labels) return '#333333';
  if (labels.includes('Character')) return '#60237B'; 
  if (labels.includes('Location')) return '#005B8A'; 
  if (labels.includes('Item')) return '#006A4E';   
  if (labels.includes('Event')) return '#8C1D40';    
  return '#333333';
};

const getTooltipContent = (element: GraphNode | GraphRelationship) => {
  let content = '';
  if (element.labels)
    content += `<strong>Labels:</strong> ${element.labels.join(', ')}<hr>`;
  for (const [key, value] of Object.entries(element.properties)) {
    content += `<strong>${key}:</strong> ${value}\n`;
  }
  return content;
};

const graphActions = [{ keys: [['Click', '&', 'Drag']], description: 'Pan View' }, { keys: [['Scroll']], description: 'Zoom View' }];

function startPan(event: MouseEvent) {
  isPanning.value = true;
  panStart.value = { x: event.clientX - transform.value.x, y: event.clientY - transform.value.y };
  (event.currentTarget as HTMLElement)?.classList.add('grabbing');
}
function doPan(event: MouseEvent) {
  if (!isPanning.value) return;
  transform.value.x = event.clientX - panStart.value.x;
  transform.value.y = event.clientY - panStart.value.y;
}
function endPan(event: MouseEvent) {
  isPanning.value = false;
  (event.currentTarget as HTMLElement)?.classList.remove('grabbing');
}
function handleWheel(event: WheelEvent) {
  event.preventDefault();
  const scaleAmount = 0.1;
  const newScale = transform.value.k * (1 - Math.sign(event.deltaY) * scaleAmount);
  transform.value.k = Math.max(0.1, Math.min(newScale, 5));
}
</script>

<template>
  <div 
    class="graph-view-container" 
    v-action-hint="graphActions"
    @wheel="handleWheel"
  >
    <div v-if="isLoading" class="loading-indicator">Loading Graph...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div 
      v-else
      class="graph-canvas"
      @mousedown.left="startPan"
      @mousemove="doPan"
      @mouseup.left="endPan"
      @mouseleave="endPan"
    >
      <svg width="100%" height="100%">
        <defs>
          <pattern id="grid" :width="grid.size" :height="grid.size" patternUnits="userSpaceOnUse">
            <path :d="`M ${grid.size} 0 L 0 0 0 ${grid.size}`" fill="none" stroke="var(--color-background-mute)" stroke-width="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" :style="canvasStyle"/>

        <g :style="canvasStyle">
          <!-- Relationships -->
          <g class="relationships">
            <path
              v-for="path, id in relationshipPaths"
              :key="id"
              :d="path.d!"
              fill="none"
              stroke="#999"
              stroke-width="2"
              v-tooltip-helper="getTooltipContent(path.rel)"
            />
          </g>
          
          <!-- Nodes -->
          <g class="nodes">
            <g 
              v-for="node in nodes"
              :key="node.element_id" 
              :transform="`translate(${nodePositions.get(node.element_id)?.x * grid.size || 0}, ${nodePositions.get(node.element_id)?.y * grid.size || 0})`"
            >
              <rect
                :width="grid.nodeWidthCells * grid.size"
                :height="grid.nodeHeightCells * grid.size"
                rx="10" 
                :fill="getNodeColor(node.labels)"
                stroke="#fff"
                stroke-width="2"
                v-tooltip-helper="getTooltipContent(node)"
              />
              <text
                fill="#FFFFFF"
                font-size="12"
                font-weight="bold"
                text-anchor="middle"
                :x="(grid.nodeWidthCells * grid.size) / 2"
                :y="(grid.nodeHeightCells * grid.size) / 2"
                dy=".3em"
              >
                {{ node.properties.name }}
              </text>
            </g>
          </g>
        </g>
      </svg>
    </div>
    <ActionHint />
  </div>
</template>

<style scoped>
/* Styles remain largely the same, but added a few for clarity */
.graph-view-container {
  width: 100%;
  height: 100%;
  background-color: var(--color-background-soft);
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}
.loading-indicator,
.error-message {
  font-size: 1.2rem;
  color: var(--color-text);
}
.error-message {
  color: var(--color-danger);
}
.graph-canvas {
  width: 100%;
  height: 100%;
  cursor: grab;
}
.graph-canvas.grabbing {
  cursor: grabbing;
}
.nodes text {
  pointer-events: none;
  user-select: none;
}
</style>
