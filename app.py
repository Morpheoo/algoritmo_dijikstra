import streamlit as st
import graphviz
from dijkstra_logic import DijkstraSolver
import pandas as pd

# Page Config
st.set_page_config(page_title="Dijkstra Visualizer Pro", layout="wide")

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background-color: #007bff;
        color: white;
    }
    .metric-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .log-container {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        height: 200px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to parse graph input
def parse_graph(input_text):
    graph = {}
    edges = []
    try:
        # Expected format: A-B:5, B-C:3
        parts = [p.strip() for p in input_text.split(",")]
        for p in parts:
            if not p: continue
            edge_info, weight = p.split(":")
            u, v = edge_info.split("-")
            u, v = u.strip(), v.strip()
            weight = float(weight)
            
            if u not in graph: graph[u] = {}
            if v not in graph: graph[v] = {}
            
            graph[u][v] = weight
            # Assuming undirected for a better visual graph if chosen, 
            # but Dijkstra works for directed. We'll stick to directed as per standard input.
            edges.append((u, v, weight))
        return graph, edges
    except Exception as e:
        return None, f"Error al parsear: {e}"

# Initialization of Session State
if 'current_step_idx' not in st.session_state:
    st.session_state.current_step_idx = 0
if 'simulation_steps' not in st.session_state:
    st.session_state.simulation_steps = []
if 'graph_dict' not in st.session_state:
    st.session_state.graph_dict = {}

# Sidebar
with st.sidebar:
    st.title("🛠 Configuración")
    st.markdown("---")
    
    default_graph = "A-B:4, A-C:2, B-C:1, B-D:5, C-D:8, C-E:10, D-E:2, D-Z:6, E-Z:3"
    input_text = st.text_area("🔧 Definir Grafo (u-v:peso, ...)", value=default_graph, height=150)
    
    graph_dict, edges = parse_graph(input_text)
    
    if graph_dict:
        st.session_state.graph_dict = graph_dict
        nodes = sorted(list(graph_dict.keys()))
        col1, col2 = st.columns(2)
        with col1:
            start_node = st.selectbox("Origen", nodes, index=0)
        with col2:
            dest_node = st.selectbox("Destino", nodes, index=len(nodes)-1)
            
        if st.button("🚀 Calcular Algoritmo"):
            solver = DijkstraSolver(graph_dict)
            st.session_state.simulation_steps = solver.solve(start_node, dest_node)
            st.session_state.current_step_idx = 0
    else:
        st.error(edges) # edges contains error msg in this case

# Main Header
st.title("Dijkstra Algoritmo")

if st.session_state.simulation_steps:
    steps = st.session_state.simulation_steps
    curr_idx = st.session_state.current_step_idx
    curr_state = steps[curr_idx]
    
    # Metrics Bar
    dist_val = curr_state['distances'].get(dest_node, float('inf'))
    dist_str = "INF" if dist_val == float('inf') else f"{dist_val:.1f}"
    
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Paso Actual", f"{curr_idx + 1} / {len(steps)}")
    with m_col2:
        st.metric("Distancia al Destino", dist_str)
    with m_col3:
        status_msg = "En proceso..." if curr_idx < len(steps)-1 else "Finalizado"
        st.metric("Estado", status_msg)
        
    st.markdown("---")
    
    # Content Area
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.subheader("Visualización del Grafo")
        
        # Create Graphviz object
        dot = graphviz.Digraph(engine='dot') # Switched to 'dot' for better default hierarchy scaling
        dot.attr(rankdir='LR', size='4,3!', ratio='fill') # Added '!' to force size and fill ratio
        
        # Consistent node styling
        dot.attr('node', shape='circle', fixedsize='true', width='0.5', height='0.5', fontsize='10')
        dot.attr('edge', fontsize='10')
        
        # Determine Path nodes (only if final step)
        final_path = curr_state.get('final_path', [])
        path_edges = []
        if final_path:
            for i in range(len(final_path)-1):
                path_edges.append((final_path[i], final_path[i+1]))

        # Add Nodes
        for node in st.session_state.graph_dict:
            color = "#E0E0E0" # Gray
            penwidth = "1"
            
            if node == curr_state['current_node']:
                color = "#FFD700" if curr_state['evaluation'] else "#90EE90" # Yellow if evaluation, Green if just finished
            elif node in curr_state['visited']:
                color = "#90EE90" # Green
            elif node in curr_state['frontier']:
                color = "#ADD8E6" # Light Blue
            
            # Highlight final path nodes
            if node in final_path:
                penwidth = "3"
                if node == start_node or node == dest_node:
                    font_color = "red"
                else:
                    font_color = "black"
            else:
                font_color = "black"

            dot.node(node, style='filled', fillcolor=color, penwidth=penwidth, fontcolor=font_color)

        # Add Edges
        for u, v_dict in st.session_state.graph_dict.items():
            for v, w in v_dict.items():
                edge_color = "black"
                penwidth = "1"
                
                # Highlight path edges
                if (u, v) in path_edges:
                    edge_color = "red"
                    penwidth = "3"
                
                dot.edge(u, v, label=str(w), color=edge_color, penwidth=penwidth)
        
        st.graphviz_chart(dot, use_container_width=True)
        
        # Navigation Buttons
        c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1.5]) # Added one more column and adjusted ratios
        with c1:
            if st.button("⬅ Anterior") and curr_idx > 0:
                st.session_state.current_step_idx -= 1
                st.rerun()
        with c2:
            if st.button("Siguiente ➡") and curr_idx < len(steps) - 1:
                st.session_state.current_step_idx += 1
                st.rerun()
        with c3:
            if st.button("🎯 Ver Solución"):
                st.session_state.current_step_idx = len(steps) - 1
                st.rerun()
        with c5:
            if st.button("🔄 Reiniciar"):
                st.session_state.current_step_idx = 0
                st.rerun()

    with right_col:
        st.subheader("Estado & Logs")
        
        # Log Box
        st.markdown(f'<div class="log-container">> {curr_state["message"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Table of distances
        st.subheader("Tabla de Distancias")
        d_data = []
        for n, d in curr_state['distances'].items():
            prev = curr_state['previous'].get(n, "-")
            d_str = "∞" if d == float('inf') else str(d)
            status = "Visitado" if n in curr_state['visited'] else ("Frontera" if n in curr_state['frontier'] else "Pendiente")
            if n == curr_state['current_node']: status = "ACTUAL"
            
            d_data.append({"Nodo": n, "Dist.": d_str, "Previo": prev, "Estado": status})
        
        df = pd.DataFrame(d_data).sort_values(by="Nodo")
        st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("Configura el grafo en el sidebar y presiona 'Calcular Algoritmo' para comenzar.")
    
    # Placeholder aesthetic
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/57/Dijkstra_Animation.gif", caption="Ejemplo del algoritmo de Dijkstra")
