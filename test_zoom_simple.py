"""Test simple du système de zoom - version événement Plotly"""
import os
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

import dash
from dash import dcc, html
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>Test Zoom</title>
    {%favicon%}
    {%css%}
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
        .container { width: 100vw; height: 100vh; position: relative; }
        #btn-zoom-in, #btn-zoom-out {
            position: absolute; width: 50px; height: 50px;
            background: rgba(47, 128, 237, 0.95); border: 2px solid white;
            border-radius: 8px; color: white; font-size: 24px;
            cursor: pointer; z-index: 1000;
            display: flex; align-items: center; justify-content: center;
        }
        #btn-zoom-in { bottom: 80px; right: 20px; }
        #btn-zoom-out { bottom: 20px; right: 20px; }
    </style>
    <script>
        // ============================================================================
        // RELIER LES BOUTONS CUSTOM AUX BOUTONS NATIFS PLOTLY
        // ============================================================================
        
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🔧 Linking custom buttons to native Plotly buttons...');
            
            // Fonction pour trouver et cliquer sur un bouton natif Plotly
            function clickPlotlyButton(buttonTitle) {
                var graphDiv = document.getElementById('test-graph');
                if (!graphDiv) {
                    console.log('❌ Graph not found');
                    return false;
                }
                
                // Trouver la toolbar Plotly
                var modebar = graphDiv.querySelector('.modebar');
                if (!modebar) {
                    console.log('⏳ Modebar not found yet, waiting...');
                    return false;
                }
                
                // Chercher le bouton avec le bon titre
                var buttons = modebar.querySelectorAll('[data-title]');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].getAttribute('data-title') === buttonTitle) {
                        console.log('✅ Found Plotly button:', buttonTitle);
                        buttons[i].click();
                        return true;
                    }
                }
                
                console.log('❌ Button not found:', buttonTitle);
                return false;
            }
            
            // Observer pour attacher les listeners quand les boutons sont créés
            var checkInterval = setInterval(function() {
                var zoomInBtn = document.getElementById('btn-zoom-in');
                var zoomOutBtn = document.getElementById('btn-zoom-out');
                
                if (zoomInBtn && zoomOutBtn && !zoomInBtn.dataset.linked) {
                    clearInterval(checkInterval);
                    console.log('✅ Custom buttons found, linking to Plotly...');
                    
                    zoomInBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('➕ Custom zoom in clicked');
                        clickPlotlyButton('Zoom in');
                    });
                    
                    zoomOutBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('➖ Custom zoom out clicked');
                        clickPlotlyButton('Zoom out');
                    });
                    
                    zoomInBtn.dataset.linked = 'true';
                    zoomOutBtn.dataset.linked = 'true';
                }
            }, 100);
        });
    </script>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
'''

app.layout = html.Div([
    html.H1("Test Zoom avec plotly_afterplot", style={'textAlign': 'center', 'padding': '20px'}),
    html.Div([
        dcc.Graph(
            id='test-graph',
            figure=go.Figure(
                data=[go.Scatter(x=[1, 2, 3, 4, 5], y=[1, 4, 2, 5, 3], mode='markers+lines', marker=dict(size=20))],
                layout=go.Layout(title='Testez les boutons Plotly natifs OU les boutons custom', xaxis=dict(range=[0, 6]), yaxis=dict(range=[0, 6]), height=600)
            ),
            config={
                'displayModeBar': 'hover',  # Afficher les boutons natifs Plotly !
                'scrollZoom': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'pan2d'],
                'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'resetScale2d'],
            }
        ),
        html.Button(html.I(className="fas fa-plus"), id='btn-zoom-in'),
        html.Button(html.I(className="fas fa-minus"), id='btn-zoom-out'),
    ], className='container'),
])

if __name__ == '__main__':
    print("🚀 Test server starting...")
    print("📱 Open http://localhost:8054")
    print("🔍 Open browser console (F12) to see logs")
    app.run(debug=True, port=8054)
