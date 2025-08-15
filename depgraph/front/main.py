import networkx as nx
import plotly.graph_objects as go
import typer

from .. import back

app = typer.Typer()

@app.command()
def main(path: str):

    G = back.api.generate_graph(path)

    visualize_graph_plotly_clear(G, "dependencies_plotly.html")


def visualize_graph_plotly_clear(G: nx.Graph, filename=None):
    """
    Визуализирует граф зависимостей с помощью Plotly без наложений.
    Пакеты и модули окрашены по-разному.
    """
    # Разносим узлы — scale побольше, k побольше (отталкивание сильнее)
    pos = nx.spring_layout(G, seed=42, k=1.5, iterations=200, scale=5)
    nx.set_node_attributes(G, pos, "pos")

    # Рёбра
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.8, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Узлы
    node_x, node_y, node_text, node_color = [], [], [], []
    for node, data in G.nodes(data=True):
        x, y = data['pos']
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node} ({data.get('type', 'module')})")
        node_color.append('#FFD700' if data.get('type') == 'package' else '#87CEFA')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[n for n in G.nodes()],
        textposition="bottom center",  # подписи под узлами
        textfont=dict(size=10),
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            color=node_color,
            size=14,
            line_width=2
        )
    )

    # Фигура
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title="Dependency Graph",
                        title_x=0.5,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=20, r=20, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))

    if filename:
        fig.write_html(filename)
        print(f"Plotly visualization saved to {filename}")
    else:
        fig.show()

if __name__ == "__main__":
    app()
