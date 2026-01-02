import heapq
from typing import Dict, List, Optional, Tuple, Any

class DijkstraSolver:
    def __init__(self, graph: Dict[str, Dict[str, float]]):
        """
        Initialize with a graph in adjacency list format:
        {
            'A': {'B': 5, 'C': 2},
            'B': {'D': 4},
            ...
        }
        """
        self.graph = graph
        self.nodes = list(graph.keys())

    def solve(self, start_node: str, end_node: str) -> List[Dict[str, Any]]:
        """
        Runs Dijkstra and returns a list of dictionaries representing the state at each step.
        """
        # Distances: node -> distance
        distances = {node: float('inf') for node in self.graph}
        distances[start_node] = 0
        
        # Previous nodes for path reconstruction
        previous = {node: None for node in self.graph}
        
        # Priority Queue: (distance, node)
        pq = [(0, start_node)]
        
        # State tracking sets
        visited = set()
        steps = []
        
        def capture_state(current_node: Optional[str] = None, message: str = "", evaluation: bool = False):
            # We copy all dynamic structures to avoid reference issues
            steps.append({
                "distances": distances.copy(),
                "previous": previous.copy(),
                "visited": list(visited),
                "frontier": [node for _, node in pq],
                "current_node": current_node,
                "message": message,
                "evaluation": evaluation  # If True, node is being evaluated (yellow/orange)
            })

        # Initial state
        capture_state(message=f"Preparando búsqueda desde {start_node} hacia {end_node}...")

        while pq:
            curr_dist, curr_node = heapq.heappop(pq)
            
            # Step: Evaluating current node
            capture_state(
                current_node=curr_node, 
                message=f"Evaluando el nodo {curr_node} (distancia actual: {curr_dist}).",
                evaluation=True
            )

            if curr_node in visited:
                continue
                
            if curr_node == end_node:
                visited.add(curr_node)
                capture_state(
                    current_node=curr_node, 
                    message=f"¡Destino {end_node} alcanzado!",
                    evaluation=False
                )
                break

            visited.add(curr_node)

            for neighbor, weight in self.graph[curr_node].items():
                if neighbor in visited:
                    continue
                    
                new_dist = curr_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = curr_node
                    heapq.heappush(pq, (new_dist, neighbor))
                    
                    capture_state(
                        current_node=curr_node,
                        message=f"Mejorando distancia a {neighbor}: {new_dist} (vía {curr_node}).",
                        evaluation=True
                    )

            # Step: Node processing finished
            capture_state(
                current_node=curr_node, 
                message=f"Nodo {curr_node} procesado completamente.",
                evaluation=False
            )

        # Final state: Shortest path reconstruction
        path = []
        if distances[end_node] != float('inf'):
            temp = end_node
            while temp:
                path.append(temp)
                temp = previous[temp]
            path.reverse()

        steps.append({
            "distances": distances.copy(),
            "previous": previous.copy(),
            "visited": list(visited),
            "frontier": [],
            "current_node": None,
            "message": f"Algoritmo finalizado.{' Caminito encontrado!' if path else ' No se encontró camino.'}",
            "evaluation": False,
            "final_path": path
        })

        return steps
