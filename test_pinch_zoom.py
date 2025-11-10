"""
Test du pinch-to-zoom custom sur mobile
Serveur: http://localhost:8056

Cette version utilise Plotly.relayout() directement sans attendre graphDiv.data
"""
import dash
from dash import dcc, html
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>Test Pinch-to-Zoom</title>
    {%favicon%}
    {%css%}
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
        .container { width: 100vw; height: 100vh; position: relative; }
        #instructions {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(102, 126, 234, 0.95);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            z-index: 2000;
            text-align: center;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
    </style>
    <script>
        // ============================================================================
        // PINCH-TO-ZOOM POUR MOBILE (Solution robuste v2)
        // ============================================================================
        
        (function() {
            console.log('🔧 Pinch-to-zoom initializing...');
            
            var pinchState = {
                active: false,
                initialDistance: 0,
                initialCenter: null,
                initialRanges: null,
                lastUpdate: 0
            };
            
            function getDistance(touch1, touch2) {
                var dx = touch1.clientX - touch2.clientX;
                var dy = touch1.clientY - touch2.clientY;
                return Math.sqrt(dx * dx + dy * dy);
            }
            
            function getCenter(touch1, touch2) {
                return {
                    x: (touch1.clientX + touch2.clientX) / 2,
                    y: (touch1.clientY + touch2.clientY) / 2
                };
            }
            
            function screenToGraph(graphDiv, screenX, screenY) {
                try {
                    var layout = graphDiv.layout || {};
                    var xaxis = layout.xaxis || {};
                    var yaxis = layout.yaxis || {};
                    
                    if (!xaxis.range || !yaxis.range) {
                        return null;
                    }
                    
                    var bbox = graphDiv.getBoundingClientRect();
                    var relX = (screenX - bbox.left) / bbox.width;
                    var relY = (screenY - bbox.top) / bbox.height;
                    
                    var xRange = xaxis.range;
                    var yRange = yaxis.range;
                    
                    return {
                        x: xRange[0] + relX * (xRange[1] - xRange[0]),
                        y: yRange[1] - relY * (yRange[1] - yRange[0])
                    };
                } catch(e) {
                    console.error('screenToGraph error:', e);
                    return null;
                }
            }
            
            function handleTouchStart(e) {
                if (e.touches.length !== 2) {
                    pinchState.active = false;
                    return;
                }
                
                var graphDiv = document.getElementById('test-graph');
                if (!graphDiv) return;
                
                console.log('🔵 Pinch START');
                
                pinchState.active = true;
                pinchState.initialDistance = getDistance(e.touches[0], e.touches[1]);
                pinchState.initialCenter = getCenter(e.touches[0], e.touches[1]);
                
                var currentLayout = graphDiv.layout || {};
                var xaxis = currentLayout.xaxis || {};
                var yaxis = currentLayout.yaxis || {};
                
                if (xaxis.range && yaxis.range) {
                    pinchState.initialRanges = {
                        x: [xaxis.range[0], xaxis.range[1]],
                        y: [yaxis.range[0], yaxis.range[1]]
                    };
                    console.log('✅ Initial ranges:', pinchState.initialRanges);
                } else {
                    console.log('⚠️ No ranges yet, waiting...');
                    pinchState.active = false;
                    return;
                }
                
                var centerGraph = screenToGraph(graphDiv, pinchState.initialCenter.x, pinchState.initialCenter.y);
                if (centerGraph) {
                    pinchState.initialCenter.graphX = centerGraph.x;
                    pinchState.initialCenter.graphY = centerGraph.y;
                }
                
                pinchState.lastUpdate = Date.now();
                e.preventDefault();
                e.stopPropagation();
            }
            
            function handleTouchMove(e) {
                if (!pinchState.active || e.touches.length !== 2) return;
                if (!pinchState.initialRanges) return;
                
                var now = Date.now();
                if (now - pinchState.lastUpdate < 33) return;
                pinchState.lastUpdate = now;
                
                var currentDistance = getDistance(e.touches[0], e.touches[1]);
                if (currentDistance === 0 || pinchState.initialDistance === 0) return;
                
                var scale = pinchState.initialDistance / currentDistance;
                if (scale < 0.1) scale = 0.1;
                if (scale > 10) scale = 10;
                
                var graphDiv = document.getElementById('test-graph');
                if (!graphDiv || !window.Plotly) return;
                
                var xCenter = pinchState.initialCenter.graphX || 
                              (pinchState.initialRanges.x[0] + pinchState.initialRanges.x[1]) / 2;
                var yCenter = pinchState.initialCenter.graphY || 
                              (pinchState.initialRanges.y[0] + pinchState.initialRanges.y[1]) / 2;
                
                var xSpan = (pinchState.initialRanges.x[1] - pinchState.initialRanges.x[0]) / 2 * scale;
                var ySpan = (pinchState.initialRanges.y[1] - pinchState.initialRanges.y[0]) / 2 * scale;
                
                var newXRange = [xCenter - xSpan, xCenter + xSpan];
                var newYRange = [yCenter - ySpan, yCenter + ySpan];
                
                console.log('🔍 Scale:', scale.toFixed(2), 'X:', newXRange.map(x => x.toFixed(1)), 'Y:', newYRange.map(y => y.toFixed(1)));
                
                try {
                    window.Plotly.relayout(graphDiv, {
                        'xaxis.range': newXRange,
                        'yaxis.range': newYRange
                    });
                } catch (err) {
                    console.error('❌ Error:', err);
                }
                
                e.preventDefault();
                e.stopPropagation();
            }
            
            function handleTouchEnd(e) {
                if (e.touches.length < 2) {
                    if (pinchState.active) {
                        console.log('🔵 Pinch END');
                    }
                    pinchState.active = false;
                }
            }
            
            function attachPinchListeners() {
                var graphDiv = document.getElementById('test-graph');
                if (!graphDiv) {
                    setTimeout(attachPinchListeners, 100);
                    return;
                }
                
                console.log('✅ Pinch-to-zoom attached!');
                
                graphDiv.addEventListener('touchstart', handleTouchStart, {
                    capture: true,
                    passive: false
                });
                graphDiv.addEventListener('touchmove', handleTouchMove, {
                    capture: true,
                    passive: false
                });
                graphDiv.addEventListener('touchend', handleTouchEnd, {
                    capture: true,
                    passive: false
                });
            }
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', attachPinchListeners);
            } else {
                attachPinchListeners();
            }
        })();
    </script>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
'''

app.layout = html.Div([
    html.Div([
        html.H2("📱 Test Pinch-to-Zoom", style={'margin': '0', 'color': 'white'}),
        html.P("Écartez 2 doigts pour zoomer | Rapprochez pour dézoomer", style={'margin': '5px 0 0 0', 'fontSize': '12px'})
    ], id='instructions'),
    
    html.Div([
        dcc.Graph(
            id='test-graph',
            figure=go.Figure(
                data=[
                    go.Scatter(
                        x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        y=[2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
                        mode='markers+lines',
                        marker=dict(size=20, color='#667eea'),
                        line=dict(width=3, color='#667eea')
                    ),
                    go.Scatter(
                        x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        y=[1, 4, 2, 5, 3, 7, 4, 8, 5, 9],
                        mode='markers+lines',
                        marker=dict(size=20, color='#f093fb'),
                        line=dict(width=3, color='#f093fb')
                    )
                ],
                layout=go.Layout(
                    title='Pinch pour zoomer!',
                    xaxis=dict(range=[0, 11]),
                    yaxis=dict(range=[0, 35]),
                    height=600,
                    dragmode='pan',
                    showlegend=False
                )
            ),
            config={
                'displayModeBar': 'hover',
                'scrollZoom': True,
                'displaylogo': False
            }
        ),
    ], className='container'),
], style={'height': '100vh'})

if __name__ == '__main__':
    print("="*60)
    print("🚀 TEST PINCH-TO-ZOOM")
    print("="*60)
    print("📱 Ouvrir sur mobile : http://[VOTRE_IP]:8056")
    print("🖥️  Ou desktop : http://localhost:8056")
    print("")
    print("🤏 Testez :")
    print("   ✅ Écartez 2 doigts → Zoom IN")
    print("   ✅ Rapprochez 2 doigts → Zoom OUT")
    print("   ✅ Centre du zoom = position des doigts")
    print("")
    print("🔍 Ouvrez la console (F12) pour voir les logs")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=8056)
