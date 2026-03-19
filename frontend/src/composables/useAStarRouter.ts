interface PathNode {
  x: number;
  y: number;
  g: number; // Cost from start
  h: number; // Heuristic cost to end
  f: number; // g + h
  parent: PathNode | null;
}

function manhattanDistance(pos0: {x: number, y: number}, pos1: {x: number, y: number}): number {
  const d1 = Math.abs(pos1.x - pos0.x);
  const d2 = Math.abs(pos1.y - pos0.y);
  return d1 + d2;
}

export function findPath(grid: number[][], start: {x: number, y: number}, end: {x: number, y: number}): {x: number, y: number}[] | null {
    if (!grid || grid.length === 0 || !grid[0] || grid[0].length === 0) {
        return null; // Invalid grid
    }

    const openSet: PathNode[] = [];
    const closedSet = new Set<string>();

    const startNode: PathNode = { x: start.x, y: start.y, g: 0, h: manhattanDistance(start, end), f: manhattanDistance(start, end), parent: null };
    openSet.push(startNode);

    while (openSet.length > 0) {
        let lowestFIndex = 0;
        for (let i = 1; i < openSet.length; i++) {
            if (openSet[i].f < openSet[lowestFIndex].f) {
                lowestFIndex = i;
            }
        }
        const currentNode = openSet[lowestFIndex];

        if (currentNode.x === end.x && currentNode.y === end.y) {
            const path = [];
            let temp: PathNode | null = currentNode;
            while (temp) {
                path.push({ x: temp.x, y: temp.y });
                temp = temp.parent;
            }
            return path.reverse();
        }

        openSet.splice(lowestFIndex, 1);
        closedSet.add(`${currentNode.x},${currentNode.y}`);

        const neighbors = [];
        const { x, y } = currentNode;

        // Corrected and safe neighbor checking
        // Up
        if (grid[y - 1] && grid[y - 1][x] === 0) neighbors.push({x, y: y - 1});
        // Down
        if (grid[y + 1] && grid[y + 1][x] === 0) neighbors.push({x, y: y + 1});
        // Left
        if (grid[y] && grid[y][x - 1] === 0) neighbors.push({x: x - 1, y});
        // Right
        if (grid[y] && grid[y][x + 1] === 0) neighbors.push({x: x + 1, y});

        for (const neighborPos of neighbors) {
            const neighborKey = `${neighborPos.x},${neighborPos.y}`;
            if (closedSet.has(neighborKey)) {
                continue;
            }

            const gScore = currentNode.g + 1;

            let neighborNode = openSet.find(node => node.x === neighborPos.x && node.y === neighborPos.y);

            if (!neighborNode) {
                neighborNode = {
                    x: neighborPos.x,
                    y: neighborPos.y,
                    g: gScore,
                    h: manhattanDistance(neighborPos, end),
                    f: gScore + manhattanDistance(neighborPos, end),
                    parent: currentNode
                };
                openSet.push(neighborNode);
            } else if (gScore >= neighborNode.g) {
                continue;
            } else {
                neighborNode.parent = currentNode;
                neighborNode.g = gScore;
                neighborNode.f = neighborNode.g + neighborNode.h;
            }
        }
    }

    return null; // No path found
}
