"""
Test des différentes configurations de zoom pour mobile
Serveur: http://localhost:8055

3 graphes côte à côte pour comparer :
1. dragmode='pan' (actuel)
2. dragmode='zoom'
3. dragmode='pan' + instructions
"""
import dash
from dash import dcc, html
import plotly.graph_objects as go

app = dash.Dash(__name__)

# Données de test simples
x_data = list(range(1, 11))
y_data1 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
y_data2 = [1, 4, 2, 5, 3, 7, 4, 8, 5, 9]

app.layout = html.Div([
    html.H1("🔍 Test Mobile Zoom - 3 Configurations", style={
        'textAlign': 'center',
        'padding': '20px',
        'backgroundColor': '#667eea',
        'color': 'white',
        'margin': '0'
    }),
    
    html.Div("Testez sur votre téléphone mobile :", style={
        'textAlign': 'center',
        'padding': '10px',
        'backgroundColor': '#f0f0f0',
        'fontWeight': 'bold'
    }),
    
    # Version 1 : dragmode='pan' (ACTUEL)
    html.Div([
        html.H3("1️⃣ Mode PAN (actuel)", style={'textAlign': 'center', 'color': '#667eea'}),
        html.P([
            "🖱️ Desktop: Click-drag = déplacer",
            html.Br(),
            "📱 Mobile: 1 doigt = déplacer | 2 doigts scroll ↕️ = zoom ?",
            html.Br(),
            "🔘 Boutons: Cliquer + ou - pour zoomer"
        ], style={'textAlign': 'center', 'fontSize': '12px', 'color': '#666', 'margin': '10px'}),
        
        html.Div([
            dcc.Graph(
                id='graph-pan',
                figure=go.Figure(
                    data=[
                        go.Scatter(x=x_data, y=y_data1, mode='markers+lines', 
                                   marker=dict(size=15, color='#667eea'), name='Serie 1'),
                        go.Scatter(x=x_data, y=y_data2, mode='markers+lines', 
                                   marker=dict(size=15, color='#f093fb'), name='Serie 2')
                    ],
                    layout=go.Layout(
                        title='dragmode=pan',
                        dragmode='pan',  # ← MODE ACTUEL
                        xaxis=dict(range=[0, 11]),
                        yaxis=dict(range=[0, 35]),
                        height=300,
                        showlegend=False
                    )
                ),
                config={
                    'displayModeBar': 'hover',
                    'scrollZoom': True,  # ← Scroll 2 doigts
                    'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'resetScale2d'],
                    'displaylogo': False
                }
            ),
        ], style={'position': 'relative', 'padding': '10px'}),
        
    ], style={'width': '100%', 'display': 'inline-block', 'border': '2px solid #667eea', 'borderRadius': '10px', 'margin': '10px 0'}),
    
    # Version 2 : dragmode='zoom'
    html.Div([
        html.H3("2️⃣ Mode ZOOM", style={'textAlign': 'center', 'color': '#f093fb'}),
        html.P([
            "🖱️ Desktop: Click-drag = dessiner zone → zoom",
            html.Br(),
            "📱 Mobile: 1 doigt drag = dessiner zone → zoom",
            html.Br(),
            "🔘 Boutons: Cliquer + ou - pour zoomer"
        ], style={'textAlign': 'center', 'fontSize': '12px', 'color': '#666', 'margin': '10px'}),
        
        html.Div([
            dcc.Graph(
                id='graph-zoom',
                figure=go.Figure(
                    data=[
                        go.Scatter(x=x_data, y=y_data1, mode='markers+lines', 
                                   marker=dict(size=15, color='#667eea'), name='Serie 1'),
                        go.Scatter(x=x_data, y=y_data2, mode='markers+lines', 
                                   marker=dict(size=15, color='#f093fb'), name='Serie 2')
                    ],
                    layout=go.Layout(
                        title='dragmode=zoom',
                        dragmode='zoom',  # ← MODE ZOOM
                        xaxis=dict(range=[0, 11]),
                        yaxis=dict(range=[0, 35]),
                        height=300,
                        showlegend=False
                    )
                ),
                config={
                    'displayModeBar': 'hover',
                    'scrollZoom': True,
                    'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'resetScale2d', 'pan2d'],  # Ajouter pan
                    'displaylogo': False
                }
            ),
        ], style={'position': 'relative', 'padding': '10px'}),
        
    ], style={'width': '100%', 'display': 'inline-block', 'border': '2px solid #f093fb', 'borderRadius': '10px', 'margin': '10px 0'}),
    
    # Version 3 : dragmode='pan' + gros boutons + instructions
    html.Div([
        html.H3("3️⃣ Mode PAN + GROS BOUTONS", style={'textAlign': 'center', 'color': '#20c997'}),
        html.P([
            "💡 ASTUCE: Glissez 2 doigts ↕️ pour zoomer",
            html.Br(),
            "📱 Ou utilisez les GROS boutons + et -",
            html.Br(),
            "🖱️ Desktop: Molette souris = zoom"
        ], style={'textAlign': 'center', 'fontSize': '12px', 'color': '#666', 'margin': '10px', 'backgroundColor': '#fff3cd', 'padding': '10px', 'borderRadius': '5px'}),
        
        html.Div([
            dcc.Graph(
                id='graph-pan-big-buttons',
                figure=go.Figure(
                    data=[
                        go.Scatter(x=x_data, y=y_data1, mode='markers+lines', 
                                   marker=dict(size=15, color='#667eea'), name='Serie 1'),
                        go.Scatter(x=x_data, y=y_data2, mode='markers+lines', 
                                   marker=dict(size=15, color='#f093fb'), name='Serie 2')
                    ],
                    layout=go.Layout(
                        title='dragmode=pan + instructions',
                        dragmode='pan',
                        xaxis=dict(range=[0, 11]),
                        yaxis=dict(range=[0, 35]),
                        height=300,
                        showlegend=False
                    )
                ),
                config={
                    'displayModeBar': True,  # Toujours visible
                    'scrollZoom': True,
                    'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'resetScale2d'],
                    'displaylogo': False
                }
            ),
            
            # GROS boutons custom
            html.Button("➕", id='big-zoom-in', style={
                'position': 'absolute',
                'bottom': '80px',
                'right': '20px',
                'width': '60px',
                'height': '60px',
                'fontSize': '32px',
                'backgroundColor': '#667eea',
                'color': 'white',
                'border': 'none',
                'borderRadius': '50%',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
                'cursor': 'pointer',
                'zIndex': '1000'
            }),
            html.Button("➖", id='big-zoom-out', style={
                'position': 'absolute',
                'bottom': '15px',
                'right': '20px',
                'width': '60px',
                'height': '60px',
                'fontSize': '32px',
                'backgroundColor': '#f093fb',
                'color': 'white',
                'border': 'none',
                'borderRadius': '50%',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
                'cursor': 'pointer',
                'zIndex': '1000'
            }),
        ], style={'position': 'relative', 'padding': '10px'}),
        
    ], style={'width': '100%', 'display': 'inline-block', 'border': '2px solid #20c997', 'borderRadius': '10px', 'margin': '10px 0'}),
    
    # Instructions finales
    html.Div([
        html.H4("📝 RAPPORT DE TEST", style={'color': '#667eea'}),
        html.P([
            "Testez chaque configuration et notez :",
            html.Br(),
            "✅ Config 1 (PAN) : 2 doigts scroll ↕️ = zoom ? Oui / Non",
            html.Br(),
            "✅ Config 2 (ZOOM) : Touch-drag zone = zoom ? Oui / Non",
            html.Br(),
            "✅ Config 3 (PAN + BIG) : Plus facile ? Oui / Non",
            html.Br(),
            html.Br(),
            "🚨 RAPPEL : Le pinch (écarter doigts) NE MARCHERA JAMAIS (limitation Plotly)"
        ], style={'fontSize': '14px', 'lineHeight': '1.8'})
    ], style={
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'margin': '20px 10px',
        'borderRadius': '10px',
        'border': '2px solid #e0e0e0'
    }),
    
], style={'maxWidth': '600px', 'margin': '0 auto', 'fontFamily': 'Arial, sans-serif'})

# Callbacks pour les gros boutons (Config 3)
app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        var plotlyButton = document.querySelector('#graph-pan-big-buttons [data-title="Zoom in"]');
        if (plotlyButton) plotlyButton.click();
        return window.dash_clientside.no_update;
    }
    """,
    dash.dependencies.Output('big-zoom-in', 'n_clicks', allow_duplicate=True),
    dash.dependencies.Input('big-zoom-in', 'n_clicks'),
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        var plotlyButton = document.querySelector('#graph-pan-big-buttons [data-title="Zoom out"]');
        if (plotlyButton) plotlyButton.click();
        return window.dash_clientside.no_update;
    }
    """,
    dash.dependencies.Output('big-zoom-out', 'n_clicks', allow_duplicate=True),
    dash.dependencies.Input('big-zoom-out', 'n_clicks'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    print("="*60)
    print("🚀 SERVEUR TEST MOBILE ZOOM")
    print("="*60)
    print("📱 Ouvrir sur mobile : http://[VOTRE_IP_LOCAL]:8055")
    print("🖥️  Ou sur desktop : http://localhost:8055")
    print("")
    print("📝 Tester les 3 configurations et noter les résultats :")
    print("   1. Mode PAN (actuel)")
    print("   2. Mode ZOOM (alternatif)")
    print("   3. Mode PAN + GROS BOUTONS (optimisé)")
    print("")
    print("🔍 Ce qu'on teste :")
    print("   ✅ Two-finger scroll (↕️) = zoom ?")
    print("   ✅ Touch-drag zone = zoom ?")
    print("   ✅ Gros boutons plus faciles ?")
    print("   ❌ Pinch (écarter doigts) = NON SUPPORTÉ PAR PLOTLY")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=8055)
