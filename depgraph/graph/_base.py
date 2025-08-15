from pyvis.network import Network
import networkx as nx

def visualize_graph_pyvis(G: nx.Graph, filename="dependencies.html"):
    """
    Визуализирует граф зависимостей G с помощью pyvis и сохраняет в HTML.
    """
    net = Network(height="1000px", width="100%", directed=True, notebook=False)
    
    # Добавляем узлы с цветами по типу
    for node, data in G.nodes(data=True):
        node_type = data.get("type", "module")
        color = "#FFCC00" if node_type == "package" else "#66CCFF"
        net.add_node(node, label=node, title=f"{node} ({node_type})", color=color)
    
    # Добавляем ребра
    for source, target in G.edges():
        net.add_edge(source, target)

    # Настройка физики (чтобы узлы не слипались)
    net.force_atlas_2based()
    
    # Сохраняем в HTML
    net.show(filename)
    print(f"Interactive visualization saved to {filename}")
