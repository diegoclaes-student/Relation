#!/usr/bin/env python3
"""
Centrale Potins Maps - V2
Architecture 100% propre avec Services + Repositories
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, MATCH, ctx, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from flask import session

# Import UNIQUEMENT nouvelle architecture
from database.persons import person_repository
from database.relations import relation_repository
from services.symmetry import symmetry_manager
from services.graph_builder import graph_builder
from services.history import history_service
from utils.constants import RELATION_TYPES
from utils.validators import Validator

# Import graph utilities pour rendering
from graph import build_graph, compute_layout, make_figure

# Import système authentification V7
from database.users import user_repository, pending_account_repository
from database.pending_submissions import pending_submission_repository
from services.auth import auth_service
from services.activity_log import log_event
from components.auth_components import (
    create_login_modal, 
    create_register_modal,
    create_propose_relation_modal,
    create_public_header, 
    create_admin_header
)
from components.admin_panel import create_admin_panel_tab
from components.history_tab import create_history_tab
from components.user_management import create_user_management_tab

# ============================================================================
# CONFIGURATION APP
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v6.1.1/css/all.css"
    ],
    meta_tags=[{
        "name": "viewport", 
        "content": "width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes"
    }],
    suppress_callback_exceptions=True
)

app.title = "Centrale Potins Maps"

# Configuration Flask session pour authentification
server = app.server
server.secret_key = 'dev-secret-key-change-in-production-2024'  # TODO: Changer en production !

# ============================================================================
# CSS MODERNE
# ============================================================================

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        /* PALETTE PREMIUM : Bleu marine profond + Blanc cassé */
        :root {
            --primary-dark: #1a2332;
            --primary-medium: #2d3e50;
            --primary-light: #4a5f7f;
            --accent: #3a7bd5;
            --bg-light: #f8f9fa;
            --text-dark: #1a2332;
            --text-light: #f8f9fa;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --shadow-soft: rgba(26, 35, 50, 0.15);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background: #e8ecef;
            min-height: 100vh;
        }
        
        .main-container {
            padding: 20px;
            min-height: 100vh;
        }
        
        .header-bar {
            background: var(--primary-dark);
            border-radius: 12px;
            padding: 20px 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px var(--shadow-soft);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid var(--accent);
        }
        
        .header-bar h1 {
            color: var(--text-light);
            font-size: 28px;
            font-weight: 600;
            margin: 0;
            letter-spacing: -0.5px;
        }
        
        .header-badge {
            background: var(--primary-medium);
            color: var(--text-light);
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            border: 1px solid var(--border-subtle);
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .graph-panel {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 12px var(--shadow-soft);
            min-height: 600px;
            border: 1px solid #e0e4e8;
        }
        
        #network-graph {
            width: 100%;
            height: 600px;
        }
        
        #network-graph-admin {
            width: 100%;
            height: 600px;
        }
        
        .controls-panel {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 12px var(--shadow-soft);
            max-height: calc(100vh - 160px);
            overflow-y: auto;
            border: 1px solid #e0e4e8;
        }
        
        .controls-panel::-webkit-scrollbar { width: 6px; }
        .controls-panel::-webkit-scrollbar-track { background: #f8f9fa; border-radius: 10px; }
        .controls-panel::-webkit-scrollbar-thumb { background: var(--primary-light); border-radius: 10px; }
        
        .section-title {
            color: var(--text-dark);
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e0e4e8;
            letter-spacing: -0.3px;
        }
        
        .control-group { margin-bottom: 20px; }
        
        .control-label {
            display: block;
            color: var(--text-dark);
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        /* Boutons premium - Sans dégradé */
        .btn-primary {
            background: var(--primary-dark);
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            color: var(--text-light);
            box-shadow: 0 2px 8px var(--shadow-soft);
            transition: all 0.2s ease;
        }
        
        .btn-primary:hover {
            background: var(--primary-medium);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px var(--shadow-soft);
        }
        
        .btn-outline {
            border: 1px solid var(--primary-dark);
            background: transparent;
            color: var(--primary-dark);
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .btn-outline:hover {
            background: var(--primary-dark);
            color: var(--text-light);
        }
        
        .stats-card {
            background: var(--primary-dark);
            border-radius: 8px;
            padding: 20px;
            color: var(--text-light);
            box-shadow: 0 2px 8px var(--shadow-soft);
            margin-top: 20px;
            border-left: 3px solid var(--accent);
        }
        
        .stats-card h5 { font-size: 14px; margin-bottom: 12px; font-weight: 600; opacity: 0.9; }
        .stat-item { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; }
        .stat-value { font-weight: 600; font-size: 15px; color: var(--accent); }
        
        .action-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            border: 1px solid #e0e4e8;
        }
        
        .action-buttons {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        /* Modal styling */
        .modal-dialog {
            max-width: 600px;
        }
        
        .modal-content {
            border-radius: 16px;
            border: none;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .modal-header {
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            padding: 20px 25px;
        }
        
        .modal-title {
            font-weight: 700;
            font-size: 20px;
        }
        
        .modal-body {
            padding: 25px;
        }
        
        .modal-footer {
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            padding: 15px 25px;
        }
        
        /* Form controls styling */
        .Select-control, .dropdown, input[type="text"], input[type="number"], textarea, input[type="password"] {
            border-radius: 8px;
            border: 1px solid rgba(26, 35, 50, 0.2);
            padding: 10px 15px;
            font-size: 14px;
            background: rgba(248, 249, 250, 0.95);
        }
        
        input[type="text"]:focus, input[type="number"]:focus, textarea:focus, input[type="password"]:focus {
            border-color: #2d3e50;
            box-shadow: 0 0 0 3px rgba(45, 62, 80, 0.15);
            outline: none;
        }
        
        /* Dropdown improvements */
        .Select-menu-outer {
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }
        
        /* ============================================= */
        /* RESPONSIVE DESIGN - TABLETTE & MOBILE */
        /* ============================================= */
        
        /* Animations */
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Hamburger hover effect */
        #hamburger-btn-graph:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 24px rgba(26, 35, 50, 0.6);
        }
        
        /* Hamburger menu style */
        #hamburger-menu {
            max-height: calc(100vh - 100px);
            overflow-y: auto;
            overflow-x: hidden;
            -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
        }
        
        /* Zoom buttons hover effect */
        #btn-zoom-in:hover, #btn-zoom-out:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 16px rgba(47, 128, 237, 0.5);
        }
        
        /* Mobile: Ensure buttons are clickable above the graph */
        #btn-zoom-in, #btn-zoom-out, #btn-fullscreen, #hamburger-btn-graph {
            pointer-events: auto;
        }
        
        /* Tablette (< 1200px) */
        @media (max-width: 1200px) {
            .content-grid { 
                grid-template-columns: 1fr;
            }
            .controls-panel { 
                max-height: none;
                margin-bottom: 20px;
            }
        }
        
        /* Mobile Large (< 768px) */
        @media (max-width: 768px) {
            .main-container {
                padding: 10px;
            }
            
            .header-bar {
                padding: 15px 20px;
                flex-direction: column;
                gap: 10px;
                text-align: center;
            }
            
            .header-bar h1 {
                font-size: 22px;
            }
            
            .content-grid {
                gap: 15px;
            }
            
            .graph-panel {
                padding: 0;
                min-height: calc(100vh - 60px); /* Prend tout l'espace disponible */
                margin: 0;
                position: relative;
            }
            
            #network-graph {
                height: calc(100vh - 60px) !important; /* Tout l'espace moins le header */
                width: 100% !important;
            }
            
            .controls-panel {
                padding: 20px;
            }
            
            .section-title {
                font-size: 16px;
            }
            
            .stats-card {
                padding: 15px;
            }
            
            .btn-primary, .btn-outline {
                padding: 12px 16px;
                font-size: 14px;
            }
            
            /* Modal responsive */
            .modal-dialog {
                margin: 10px;
                max-width: calc(100vw - 20px);
            }
            
            .modal-title {
                font-size: 18px;
            }
            
            .modal-body {
                padding: 20px;
            }
        }
        
        /* Mobile Small (< 480px) */
        @media (max-width: 480px) {
            /* FIXE: Empêcher tout scroll de la page */
            html, body {
                overflow: hidden !important;
                position: fixed !important;
                width: 100% !important;
                height: 100% !important;
            }
            
            .main-container {
                padding: 5px;
                overflow: hidden !important;
                height: 100vh !important;
            }
            
            /* Header compact sur mobile */
            .header-bar {
                padding: 8px 12px !important;
                border-radius: 8px;
                min-height: 50px;
                margin-bottom: 8px;
            }
            
            .header-bar h1 {
                font-size: 16px !important;
                margin: 0;
            }
            
            .header-bar h1 i {
                font-size: 14px !important;
                margin-right: 6px !important;
            }
            
            /* Boutons auth compacts - cacher texte, garder icônes */
            .auth-header-btn {
                padding: 8px 12px !important;
                font-size: 12px !important;
                min-height: 36px !important;
            }
            
            .auth-btn-text {
                display: inline !important;
                font-size: 11px;
            }
            
            /* Pour très petit écran, cacher complètement le texte */
            @media (max-width: 360px) {
                .auth-btn-text {
                    display: none !important;
                }
                .auth-header-btn {
                    padding: 8px !important;
                    min-width: 36px;
                }
            }
            
            .header-badge {
                padding: 4px 10px;
                font-size: 10px;
            }
            
            .graph-panel {
                padding: 10px;
                min-height: calc(75vh - 70px); /* Plus bas : 75% au lieu de 66% */
                border-radius: 12px;
            }
            
            /* Menu hamburger responsive sur mobile */
            #hamburger-menu {
                max-height: calc(100vh - 120px) !important;
                max-width: calc(100vw - 30px);
                right: 10px !important;
                top: 60px !important;
                font-size: 11px;
            }
            
            #network-graph {
                height: calc(75vh - 70px) !important; /* Plus bas : 75% au lieu de 66% */
                width: 100% !important;
            }
            
            .controls-panel {
                padding: 15px;
                border-radius: 12px;
            }
            
            .section-title {
                font-size: 15px;
                margin-bottom: 12px;
            }
            
            .control-label {
                font-size: 12px;
            }
            
            .stats-card {
                padding: 12px;
                margin-top: 15px;
            }
            
            .stats-card h5 {
                font-size: 14px;
                margin-bottom: 10px;
            }
            
            .stat-item {
                font-size: 13px;
                margin-bottom: 8px;
            }
            
            .stat-value {
                font-size: 14px;
            }
            
            .btn-primary, .btn-outline {
                padding: 10px 14px;
                font-size: 13px;
            }
            
            .action-buttons {
                gap: 8px;
            }
            
            /* Modal responsive small */
            .modal-dialog {
                margin: 5px;
                max-width: calc(100vw - 10px);
            }
            
            .modal-header {
                padding: 15px 20px;
            }
            
            .modal-title {
                font-size: 16px;
            }
            
            .modal-body {
                padding: 15px;
            }
            
            .modal-footer {
                padding: 12px 20px;
            }
            
            .modal-footer button {
                padding: 10px 16px;
                font-size: 13px;
            }
        }
        
        /* Bouton plein écran */
        #btn-fullscreen {
            transition: all 0.3s ease;
        }
        
        #btn-fullscreen:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.3);
        }
        
        #btn-fullscreen:active {
            transform: scale(0.95);
        }
        
        /* Mode plein écran activé */
        .fullscreen-mode {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 9999 !important;
            background: white !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .fullscreen-mode .graph-panel {
            width: 100% !important;
            height: 100vh !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }
        
        .fullscreen-mode #network-graph {
            height: 100vh !important;
            width: 100vw !important;
        }
        
        /* Touch optimizations pour mobile */
        @media (hover: none) and (pointer: coarse) {
            .btn-primary, .btn-outline {
                min-height: 44px; /* Apple recommandation pour touch targets */
            }
            
            .controls-panel::-webkit-scrollbar {
                width: 10px;
            }
            
            /* Améliorer les zones de touch pour les dropdown */
            .Select-control {
                min-height: 44px;
                padding: 12px 15px;
            }
            
            /* Inputs plus grands pour mobile */
            input[type="text"], input[type="number"], textarea {
                min-height: 44px;
                font-size: 16px; /* Évite le zoom automatique sur iOS */
            }
            
            /* IMPORTANT : Laisser Plotly gérer les touches pour pinch-to-zoom */
            #network-graph {
                touch-action: auto !important; /* Permet tous les gestes natifs */
            }
            
            .graph-panel {
                touch-action: auto !important; /* Laisse Plotly gérer */
                overflow: hidden; /* Empêche le scroll du container */
            }
            
            /* Force Plotly à accepter les gestes tactiles */
            .js-plotly-plot, .plotly, .svg-container {
                touch-action: auto !important;
                -webkit-user-select: none;
                user-select: none;
            }
        }
        
        /* Landscape orientation sur mobile */
        @media (max-width: 768px) and (orientation: landscape) {
            .main-container {
                padding: 5px;
            }
            
            .header-bar {
                padding: 8px 15px;
            }
            
            .header-bar h1 {
                font-size: 16px;
            }
            
            .graph-panel {
                min-height: calc(85vh - 60px); /* Presque plein écran en landscape */
                padding: 10px;
            }
            
            #network-graph {
                height: calc(85vh - 60px) !important; /* Presque plein écran en landscape */
            }
            
            /* Menu hamburger en landscape - encore plus compact */
            #hamburger-menu {
                max-height: calc(100vh - 80px) !important;
                font-size: 10px;
            }
            
            /* Boutons en landscape - empilés verticalement */
            #btn-propose-relation {
                right: 10px !important;
                bottom: 80px !important;  /* Au-dessus des boutons zoom */
                top: auto !important;
                font-size: 11px !important;
                padding: 6px 12px !important;
            }
        }
        
        /* Portrait mode optimizations */
        @media (max-width: 768px) and (orientation: portrait) {
            .graph-panel {
                /* Graph prend 66% en portrait */
                position: relative;
            }
            
            #network-graph {
                /* Assurer que le graphe prend bien 2/3 de l'écran */
                min-height: 450px;
            }
            
            /* Menu hamburger en portrait - plus d'espace vertical */
            #hamburger-menu {
                max-height: calc(100vh - 140px) !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                right: 10px !important;
                top: 65px !important;
            }
            
            /* Standalone Proposer Relation button on mobile */
            #btn-propose-relation {
                right: 10px !important;
                bottom: 20px !important;  /* Déplacé en bas pour éviter le hamburger */
                top: auto !important;
                font-size: 12px !important;
                padding: 8px 14px !important;
                width: auto !important;
            }
            
            /* Hamburger button stays at top right */
            #hamburger-btn-graph {
                right: 10px !important;
                top: 10px !important;
            }
        }
    </style>
    <script>
        // ============================================================================
        // RELIER LES BOUTONS CUSTOM AUX BOUTONS NATIFS PLOTLY
        // ============================================================================
        
        // Attendre que le DOM soit prêt
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🔧 Linking custom buttons to native Plotly buttons...');
            
            // Fonction pour trouver et cliquer sur un bouton natif Plotly
            function clickPlotlyButton(buttonTitle) {
                var graphDiv = document.getElementById('network-graph');
                if (!graphDiv) {
                    console.log('❌ Graph not found');
                    return false;
                }
                
                // Trouver la toolbar Plotly
                var modebar = graphDiv.querySelector('.modebar');
                if (!modebar) {
                    console.log('❌ Modebar not found');
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
            var observer = new MutationObserver(function() {
                var zoomInBtn = document.getElementById('btn-zoom-in');
                var zoomOutBtn = document.getElementById('btn-zoom-out');
                
                if (zoomInBtn && !zoomInBtn.dataset.linked) {
                    console.log('🔗 Linking btn-zoom-in to Plotly Zoom in');
                    zoomInBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('➕ Custom zoom in clicked');
                        clickPlotlyButton('Zoom in');
                    });
                    // Touch pour mobile
                    zoomInBtn.addEventListener('touchstart', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('➕ Custom zoom in touched');
                        clickPlotlyButton('Zoom in');
                    }, {passive: false});
                    zoomInBtn.dataset.linked = 'true';
                }
                
                if (zoomOutBtn && !zoomOutBtn.dataset.linked) {
                    console.log('🔗 Linking btn-zoom-out to Plotly Zoom out');
                    zoomOutBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('➖ Custom zoom out clicked');
                        clickPlotlyButton('Zoom out');
                    });
                    // Touch pour mobile
                    zoomOutBtn.addEventListener('touchstart', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('➖ Custom zoom out touched');
                        clickPlotlyButton('Zoom out');
                    }, {passive: false});
                    zoomOutBtn.dataset.linked = 'true';
                }
            });
            
            // Observer le body pour détecter quand les boutons sont ajoutés
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    </script>
    <script>
        // ============================================================================
        // PINCH-TO-ZOOM POUR MOBILE (Solution robuste)
        // ============================================================================
        
        (function() {
            console.log('🔧 Pinch-to-zoom initializing...');
            
            // État du pinch
            var pinchState = {
                active: false,
                initialDistance: 0,
                initialCenter: null,
                initialRanges: null,
                lastUpdate: 0
            };
            
            // Calculer distance entre 2 touches
            function getDistance(touch1, touch2) {
                var dx = touch1.clientX - touch2.clientX;
                var dy = touch1.clientY - touch2.clientY;
                return Math.sqrt(dx * dx + dy * dy);
            }
            
            // Calculer centre entre 2 touches
            function getCenter(touch1, touch2) {
                return {
                    x: (touch1.clientX + touch2.clientX) / 2,
                    y: (touch1.clientY + touch2.clientY) / 2
                };
            }
            
            // Convertir coordonnées écran → graphe
            function screenToGraph(graphDiv, screenX, screenY) {
                try {
                    // Utiliser _fullLayout (Plotly interne) au lieu de layout
                    var layout = graphDiv._fullLayout || graphDiv.layout || {};
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
                        y: yRange[1] - relY * (yRange[1] - yRange[0])  // Y inversé
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
                
                // Ne pas intercepter si c'est sur un bouton
                var target = e.target;
                if (target.closest('#btn-zoom-in, #btn-zoom-out, #btn-fullscreen, #hamburger-btn-graph')) {
                    return;
                }
                
                var graphDiv = document.getElementById('network-graph');
                if (!graphDiv) return;
                
                console.log('🔵 Pinch START');
                
                // Sauvegarder état initial
                pinchState.active = true;
                pinchState.initialDistance = getDistance(e.touches[0], e.touches[1]);
                pinchState.initialCenter = getCenter(e.touches[0], e.touches[1]);
                
                // Récupérer les ranges actuels de _fullLayout (Plotly interne)
                var currentLayout = graphDiv._fullLayout || graphDiv.layout || {};
                var xaxis = currentLayout.xaxis || {};
                var yaxis = currentLayout.yaxis || {};
                
                if (xaxis.range && yaxis.range) {
                    pinchState.initialRanges = {
                        x: [xaxis.range[0], xaxis.range[1]],
                        y: [yaxis.range[0], yaxis.range[1]]
                    };
                    console.log('✅ Initial ranges saved:', pinchState.initialRanges);
                } else {
                    console.log('⚠️ No ranges available yet, trying to wait...');
                    // Attendre un peu que Plotly se charge
                    setTimeout(function() {
                        var layout2 = graphDiv._fullLayout || graphDiv.layout || {};
                        var xaxis2 = layout2.xaxis || {};
                        var yaxis2 = layout2.yaxis || {};
                        if (xaxis2.range && yaxis2.range) {
                            pinchState.initialRanges = {
                                x: [xaxis2.range[0], xaxis2.range[1]],
                                y: [yaxis2.range[0], yaxis2.range[1]]
                            };
                            console.log('✅ Ranges retrieved after delay:', pinchState.initialRanges);
                        }
                    }, 100);
                }
                
                // Calculer centre en coordonnées graphe
                var centerGraph = screenToGraph(graphDiv, pinchState.initialCenter.x, pinchState.initialCenter.y);
                if (centerGraph) {
                    pinchState.initialCenter.graphX = centerGraph.x;
                    pinchState.initialCenter.graphY = centerGraph.y;
                    console.log('📍 Pinch center (graph coords):', centerGraph);
                }
                
                pinchState.lastUpdate = Date.now();
                
                // Empêcher le comportement par défaut
                e.preventDefault();
                e.stopPropagation();
            }
            
            function handleTouchMove(e) {
                if (!pinchState.active || e.touches.length !== 2) return;
                if (!pinchState.initialRanges) return;
                
                // Throttle: max 30fps
                var now = Date.now();
                if (now - pinchState.lastUpdate < 33) return;
                pinchState.lastUpdate = now;
                
                var currentDistance = getDistance(e.touches[0], e.touches[1]);
                if (currentDistance === 0 || pinchState.initialDistance === 0) return;
                
                // Calculer le facteur de zoom (distance actuelle / distance initiale)
                // Plus les doigts s'écartent, plus scale est petit (zoom in)
                var scale = pinchState.initialDistance / currentDistance;
                
                // Limiter le zoom
                if (scale < 0.1) scale = 0.1;   // Max zoom out
                if (scale > 10) scale = 10;     // Max zoom in
                
                var graphDiv = document.getElementById('network-graph');
                if (!graphDiv || !window.Plotly) return;
                
                // Calculer nouvelles ranges centrées sur le point de pinch
                var xCenter = pinchState.initialCenter.graphX || 
                              (pinchState.initialRanges.x[0] + pinchState.initialRanges.x[1]) / 2;
                var yCenter = pinchState.initialCenter.graphY || 
                              (pinchState.initialRanges.y[0] + pinchState.initialRanges.y[1]) / 2;
                
                var xSpan = (pinchState.initialRanges.x[1] - pinchState.initialRanges.x[0]) / 2 * scale;
                var ySpan = (pinchState.initialRanges.y[1] - pinchState.initialRanges.y[0]) / 2 * scale;
                
                var newXRange = [xCenter - xSpan, xCenter + xSpan];
                var newYRange = [yCenter - ySpan, yCenter + ySpan];
                
                console.log('🔍 Pinch scale:', scale.toFixed(2), 'ranges:', newXRange.map(x => x.toFixed(1)), newYRange.map(y => y.toFixed(1)));
                
                try {
                    // Utiliser Plotly.relayout directement sur le div
                    window.Plotly.relayout(graphDiv, {
                        'xaxis.range': newXRange,
                        'yaxis.range': newYRange
                    });
                } catch (err) {
                    console.error('❌ Plotly.relayout error:', err);
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
                    pinchState.initialDistance = 0;
                    pinchState.initialRanges = null;
                }
            }
            
            // Attacher les listeners
            function attachPinchListeners() {
                var graphDiv = document.getElementById('network-graph');
                if (!graphDiv) {
                    setTimeout(attachPinchListeners, 100);
                    return;
                }
                
                console.log('✅ Attaching pinch-to-zoom listeners (capture mode)');
                
                // Capture mode pour intercepter AVANT Plotly
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
            
            // Initialiser quand le DOM est prêt
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

# ============================================================================
# FONCTIONS LAYOUTS (PUBLIC vs ADMIN)
# ============================================================================

def create_public_layout():
    """Vue publique (non-authentifié) : Graph + Propose + Login (simplifié)"""
    return html.Div([
        # Store et Interval already in main layout
        
        # Header public
        create_public_header(),
        
        # Main Content - Graph en lecture seule
        html.Div([
            # Graph Panel - Full width (pas de sidebar lourde)
            html.Div([
                dcc.Graph(
                    id='network-graph',
                    config={
                        'displayModeBar': 'hover',  # Afficher au survol (desktop) ou toujours (mobile)
                        'scrollZoom': True,  # Zoom avec molette/trackpad
                        'displaylogo': False,
                        'doubleClick': 'reset',
                        'responsive': True,
                        'showTips': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'pan2d'],
                        'modeBarButtonsToAdd': ['zoomIn2d', 'zoomOut2d', 'resetScale2d'],
                        'editable': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'network_graph',
                            'height': 1080,
                            'width': 1920,
                            'scale': 2
                        }
                    }
                ),
                
                # Boutons de contrôle superposés sur le graphe
                # Menu hamburger (en haut à DROITE)
                html.Button([
                    html.I(className="fas fa-bars", style={
                        'fontSize': '18px', 
                        'color': 'white',
                    })
                ], id='hamburger-btn-graph', n_clicks=0, style={
                    'position': 'absolute',
                    'top': '15px',
                    'right': '15px',
                    'width': '48px',
                    'height': '48px',
                    'background': 'var(--primary-dark)',
                    'borderRadius': '50%',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.2)',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease',
                    'zIndex': '1000',
                    'border': '2px solid white',
                }, title="Menu"),
                
                # Bouton Zoom + (à droite sous le hamburger)
                html.Button([
                    html.I(className="fas fa-plus", style={'fontSize': '18px', 'color': 'white'})
                ], id='btn-zoom-in', n_clicks=0, style={
                    'position': 'absolute',
                    'bottom': '75px',
                    'right': '15px',
                    'width': '40px',
                    'height': '40px',
                    'background': 'rgba(47, 128, 237, 0.95)',
                    'borderRadius': '8px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.2)',
                    'cursor': 'pointer',
                    'transition': 'all 0.2s ease',
                    'zIndex': '1000',
                    'border': '2px solid white',
                    'userSelect': 'none',
                    'touchAction': 'manipulation',
                    'WebkitTouchCallout': 'none',
                }, title="Zoom avant"),
                
                # Bouton Zoom - (sous le +)
                html.Button([
                    html.I(className="fas fa-minus", style={'fontSize': '18px', 'color': 'white'})
                ], id='btn-zoom-out', n_clicks=0, style={
                    'position': 'absolute',
                    'bottom': '25px',
                    'right': '15px',
                    'width': '40px',
                    'height': '40px',
                    'background': 'rgba(47, 128, 237, 0.95)',
                    'borderRadius': '8px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.2)',
                    'cursor': 'pointer',
                    'transition': 'all 0.2s ease',
                    'zIndex': '1000',
                    'border': '2px solid white',
                    'userSelect': 'none',
                    'touchAction': 'manipulation',
                    'WebkitTouchCallout': 'none',
                }, title="Zoom arrière"),
                
                # Bouton plein écran (en bas à GAUCHE)
                html.Button([
                    html.I(className="fas fa-expand", id='fullscreen-icon')
                ], id='btn-fullscreen', n_clicks=0, style={
                    'position': 'absolute',
                    'bottom': '15px',
                    'left': '15px',
                    'width': '48px',
                    'height': '48px',
                    'background': 'rgba(47, 128, 237, 0.95)',
                    'borderRadius': '50%',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.2)',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease',
                    'zIndex': '1000',
                    'color': 'white',
                    'fontSize': '20px',
                    'border': '2px solid white',
                }, title="Mode plein écran"),
                
                # Menu déroulant hamburger (DANS le graph-panel pour position: absolute)
                html.Div([
                    # Sélecteur de Layout
                    html.Div("🎨 Mode de Visualisation", style={
                        'fontSize': '12px', 
                        'fontWeight': '600', 
                        'marginBottom': '8px',
                        'color': 'var(--text-dark)',
                        'textAlign': 'left',
                    }),
                    dcc.Dropdown(
                        id='layout-selector',
                        options=[
                            {'label': '🌐 Communautés', 'value': 'community'},
                            {'label': '⭕ Circulaire', 'value': 'circular'},
                            {'label': '🌳 Hiérarchique', 'value': 'hierarchical'},
                            {'label': '🎯 Radial', 'value': 'radial'},
                            {'label': '🔀 Force-Directed', 'value': 'spring'},
                            {'label': '📊 Kamada-Kawai', 'value': 'kk'},
                            {'label': '✨ Spectral', 'value': 'spectral'},
                        ],
                        value='community',
                        style={
                            'width': '100%',
                            'padding': '6px',
                            'borderRadius': '4px',
                            'border': '1px solid #ddd',
                            'fontSize': '12px',
                            'marginBottom': '12px'
                        },
                        clearable=False
                    ),
                    html.Hr(style={'margin': '12px 0', 'borderColor': '#e0e4e8'}),
                    
                    html.Div("⚙️ Paramètres", style={
                        'fontSize': '12px', 
                        'fontWeight': '600', 
                        'marginBottom': '12px',
                        'color': 'var(--text-dark)',
                        'textAlign': 'left',
                    }),
                    
                    # 1. Rechercher personne
                    html.Div([
                        html.Label("🔍 Chercher une personne:", style={'fontSize': '11px', 'fontWeight': '500', 'marginBottom': '4px'}),
                        dcc.Dropdown(
                            id='search-person',
                            placeholder='Tapez un nom...',
                            searchable=True,
                            clearable=True,
                            value=None,
                            style={'fontSize': '12px'},
                        ),
                    ], style={'marginBottom': '12px'}),
                    
                    # 2. Taille des bulles
                    html.Div([
                        html.Label("📊 Taille des bulles:", style={'fontSize': '11px', 'fontWeight': '500', 'marginBottom': '4px'}),
                        dcc.Slider(
                            id='node-size-slider',
                            min=5,
                            max=30,
                            step=1,
                            value=15,
                            marks={5: '5', 10: '10', 15: '15', 20: '20', 30: '30'},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ], style={'marginBottom': '12px'}),
                    
                    # 3. Distance / Répulsion entre bulles
                    html.Div([
                        html.Label("📏 Distance / Répulsion:", style={'fontSize': '11px', 'fontWeight': '500', 'marginBottom': '4px'}),
                        dcc.Slider(
                            id='repulsion-slider',
                            min=0.5,
                            max=10.0,
                            step=0.1,
                            value=1.0,
                            marks={0.5: '0.5', 2.0: '2.0', 5.0: '5.0', 10.0: '10.0'},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ], style={'marginBottom': '12px'}),
                    
                    # 4. Force pour éviter croisement des liens
                    html.Div([
                        html.Label("⚡ Force anti-croisement:", style={'fontSize': '11px', 'fontWeight': '500', 'marginBottom': '4px'}),
                        dcc.Slider(
                            id='edge-tension-slider',
                            min=0.0,
                            max=1.0,
                            step=0.1,
                            value=0.5,
                            marks={0.0: 'Faible', 0.5: 'Moyen', 1.0: 'Fort'},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ], style={'marginBottom': '12px'}),
                    
                    # 5. Afficher tous les noms
                    html.Div([
                        dbc.Checklist(
                            id='show-all-names',
                            options=[
                                {'label': '👁️ Afficher tous les noms', 'value': 'show_all'}
                            ],
                            value=[],
                            switch=True,
                            style={'fontSize': '12px'}
                        ),
                    ], style={'marginBottom': '12px'}),
                    
                    html.Hr(style={'margin': '12px 0', 'borderColor': '#e0e4e8'}),
                ], id='hamburger-menu', style={
                    'position': 'absolute',
                    'top': '65px',
                    'right': '15px',
                    'background': 'white',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'boxShadow': '0 4px 20px rgba(0,0,0,0.3)',
                    'minWidth': '220px',
                    'maxHeight': 'calc(100vh - 120px)',  # Mobile scrolling fix
                    'overflowY': 'auto',  # Enable vertical scroll
                    'border': '2px solid white',
                    'display': 'none',  # Caché par défaut
                    'zIndex': '9999',  # Increased for fullscreen compatibility
                }),
                
                # Standalone Proposer Relation Button (outside hamburger menu)
                dbc.Button([
                    html.I(className="fas fa-link", style={'marginRight': '8px'}),
                    "Proposer une relation"
                ], id='btn-propose-relation', style={
                    'position': 'absolute',
                    'top': '15px',
                    'right': '70px',  # Leave space for hamburger icon
                    'zIndex': '10000',  # Higher than fullscreen overlay (9999)
                    'fontSize': '14px',
                    'padding': '10px 18px',
                    'background': 'var(--primary-dark)',
                    'border': 'none',
                    'borderRadius': '6px',
                    'color': 'white',
                    'fontWeight': '600',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.15)',
                    'transition': 'all 0.3s ease',
                }),
            ], className='graph-panel', style={'gridColumn': '1 / -1', 'position': 'relative'}),  # Full width
            
            # Dropdowns cachés pour compatibilité callbacks
            html.Div([
                dcc.Dropdown(id='layout-dropdown', value='community', style={'display': 'none'}),
                dcc.Dropdown(id='color-dropdown', value='community', style={'display': 'none'}),
                html.Div(id='stats-display', style={'display': 'none'}),
            ]),
            
        ], className='content-grid', style={'gridTemplateColumns': '1fr'}),  # 1 colonne
        
        # Modals auth
        create_login_modal(),
        create_register_modal(),
        create_propose_relation_modal(),
        
    ], className='main-container')


def create_admin_layout(user):
    """Vue admin (authentifié) : Toutes les fonctionnalités + Admin Panel"""
    username = user.get('username', 'User')
    is_admin = user.get('is_admin', False)
    
    return html.Div([
        # Store et Interval already in main layout
        
        # Header admin
        create_admin_header(username, is_admin),
        
        # Tabs pour organiser les sections
        dbc.Tabs([
            # Tab 1: Graph & Relations
            dbc.Tab(label="📊 Network", tab_id='tab-network', children=[
                html.Div([
                    # Graph Panel
                    html.Div([
                        dcc.Graph(
                            id='network-graph-admin',
                            config={
                                'displayModeBar': True,
                                'scrollZoom': True,
                                'displaylogo': False,
                                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                                'doubleClick': 'reset',
                                'modeBarButtonsToAdd': ['resetScale2d'],
                                'responsive': True,
                                'showTips': False,
                            }
                        )
                    ], className='graph-panel'),
                    
                    # Controls Panel
                    html.Div([
                        # Graph Controls
                        html.Div([
                            html.Div("🎨 Graph Settings", className='section-title'),
                            
                            html.Div([
                                html.Label("Layout Algorithm", className='control-label'),
                                dcc.Dropdown(
                                    id='layout-selector',
                                    options=[
                                        {'label': '🎯 Community Detection', 'value': 'community'},
                                        {'label': '🌸 Spring Force', 'value': 'spring'},
                                        {'label': '🔷 Kamada-Kawai', 'value': 'kk'},
                                        {'label': '⭐ Spectral', 'value': 'spectral'},
                                    ],
                                    value='community',
                                    clearable=False,
                                )
                            ], className='control-group'),
                            
                            html.Div([
                                html.Label("Color Scheme", className='control-label'),
                                dcc.Dropdown(
                                    id='color-dropdown',
                                    options=[
                                        {'label': '🎨 By Community', 'value': 'community'},
                                        {'label': '📈 By Connections', 'value': 'degree'},
                                    ],
                                    value='community',
                                    clearable=False,
                                )
                            ], className='control-group'),
                        ]),
                        
                        # Additional Graph Controls - Sliders and search
                        html.Hr(style={'margin': '15px 0'}),
                        
                        # Search person
                        html.Div([
                            html.Label("🔍 Search Person", className='control-label'),
                            dcc.Dropdown(
                                id='search-person',
                                placeholder='Find a person...',
                                searchable=True,
                                clearable=True,
                                value=None,
                                style={'fontSize': '12px'},
                            ),
                        ], className='control-group'),
                        
                        # Node size slider
                        html.Div([
                            html.Label("📊 Node Size", className='control-label'),
                            dcc.Slider(
                                id='node-size-slider',
                                min=5,
                                max=30,
                                step=1,
                                value=15,
                                marks={5: '5', 15: '15', 30: '30'},
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ], className='control-group'),
                        
                        # Repulsion slider
                        html.Div([
                            html.Label("📏 Repulsion", className='control-label'),
                            dcc.Slider(
                                id='repulsion-slider',
                                min=0.5,
                                max=10.0,
                                step=0.1,
                                value=1.0,
                                marks={0.5: '0.5', 5.0: '5.0', 10.0: '10.0'},
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ], className='control-group'),
                        
                        # Edge tension slider
                        html.Div([
                            html.Label("⚡ Edge Tension", className='control-label'),
                            dcc.Slider(
                                id='edge-tension-slider',
                                min=0.0,
                                max=1.0,
                                step=0.1,
                                value=0.5,
                                marks={0.0: 'Low', 0.5: 'Med', 1.0: 'High'},
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ], className='control-group'),
                        
                        # Stats Card
                        html.Div([
                            html.H5("📊 Network Statistics"),
                            html.Div(id='stats-display')
                        ], className='stats-card'),
                        
                    ], className='controls-panel'),
                    
                ], className='content-grid', style={'padding': '20px'}),
            ]),
            
            # Tab 2: Manage (Add, Edit, Delete)
            dbc.Tab(label="⚙️ Manage", tab_id='tab-manage', children=[
                html.Div([
                    html.Div("⚡ Actions", className='section-title', style={'marginBottom': '20px'}),
                    
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-link", style={'marginRight': '8px'}),
                            "Add Relation"
                        ], id='btn-add-relation', color='primary', size='lg', className='mb-3'),
                        
                        dbc.Button([
                            html.I(className="fas fa-sync-alt", style={'marginRight': '8px'}),
                            "Update Relation"
                        ], id='btn-update-relation', color='info', size='lg', className='mb-3'),
                        
                        dbc.Button([
                            html.I(className="fas fa-edit", style={'marginRight': '8px'}),
                            "Edit Person"
                        ], id='btn-edit-person', outline=True, color='primary', size='lg', className='mb-3'),
                        
                        dbc.Button([
                            html.I(className="fas fa-users", style={'marginRight': '8px'}),
                            "Merge Persons"
                        ], id='btn-merge-persons', outline=True, color='primary', size='lg', className='mb-3'),
                        
                        dbc.Button([
                            html.I(className="fas fa-trash", style={'marginRight': '8px'}),
                            "Delete Person"
                        ], id='btn-delete-person', outline=True, color='danger', size='lg', className='mb-3'),
                    ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px', 'maxWidth': '400px'}),
                    
                ], style={'padding': '30px'}),
            ]),
            
            # Tab 3: Admin Panel (si admin)
            dbc.Tab(
                label="👑 Admin Panel" if is_admin else "🚫 Admin Only",
                tab_id='tab-admin',
                disabled=not is_admin,
                children=[
                    create_admin_panel_tab() if is_admin else html.Div("Access Denied", style={'padding': '30px'})
                ]
            ),
            
            # Tab 4: History (si admin)
            dbc.Tab(
                label="📋 Historique" if is_admin else "🚫 History Only",
                tab_id='tab-history',
                disabled=not is_admin,
                children=[
                    create_history_tab() if is_admin else html.Div("Access Denied", style={'padding': '30px'})
                ]
            ),
            
            # Tab 5: User Management (si admin)
            dbc.Tab(
                label="👥 Utilisateurs" if is_admin else "🚫 Users Only",
                tab_id='tab-users',
                disabled=not is_admin,
                children=[
                    create_user_management_tab() if is_admin else html.Div("Access Denied", style={'padding': '30px'})
                ]
            ),
            
        ], id='main-tabs', active_tab='tab-network', style={'marginTop': '20px'}),
        
        # Tous les modals
        # Modal Add Person
        # Modal Edit Person
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("✏️ Edit Person")),
            dbc.ModalBody([
                # Search bar section
                html.Div([
                    html.Label([
                        html.I(className="fas fa-search", style={'marginRight': '8px'}),
                        "Search Person & Relations"
                    ], style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    dbc.Input(
                        id='input-search-person-relations',
                        type='text',
                        placeholder='🔍 Type a name to search...',
                        debounce=True,
                        style={'fontSize': '15px', 'marginBottom': '10px'}
                    ),
                    html.Div(id='search-results-relations', style={
                        'maxHeight': '200px',
                        'overflowY': 'auto',
                        'marginBottom': '15px',
                        'padding': '10px',
                        'backgroundColor': '#f8f9fa',
                        'borderRadius': '8px',
                        'minHeight': '50px'
                    })
                ], style={'marginBottom': '20px', 'padding': '15px', 'backgroundColor': '#f8f9ff', 'borderRadius': '8px'}),
                
                html.Hr(),
                
                # Original edit section
                html.Div([
                    html.Label("Select Person", className='control-label'),
                    dcc.Dropdown(id='dropdown-edit-person-select', placeholder='Select person to edit')
                ], className='control-group'),
                
                html.Div([
                    html.Label("New Name", className='control-label'),
                    dbc.Input(id='input-edit-person-name', type='text', placeholder='Enter new name')
                ], className='control-group'),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id='btn-cancel-edit-person', color='secondary'),
                dbc.Button("Save Changes", id='btn-submit-edit-person', color='primary')
            ])
        ], id='modal-edit-person', is_open=False, size='lg'),
        
        # Modal Merge Persons
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("🔀 Merge Persons")),
            dbc.ModalBody([
                html.Div([
                    html.Label("Source Person (will be deleted)", className='control-label'),
                    dcc.Dropdown(id='dropdown-merge-source', placeholder='Select source person')
                ], className='control-group'),
                
                html.Div([
                    html.Label("Target Person (will be kept)", className='control-label'),
                    dcc.Dropdown(id='dropdown-merge-target', placeholder='Select target person')
                ], className='control-group'),
                
                html.Div(id='merge-preview-info', style={'marginTop': '15px'}),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id='btn-cancel-merge-persons', color='secondary'),
                dbc.Button("Merge", id='btn-submit-merge-persons', color='warning')
            ])
        ], id='modal-merge-persons', is_open=False),
        
        # Modal Delete Person
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("🗑️ Delete Person")),
            dbc.ModalBody([
                html.Div([
                    html.Label("Select Person to Delete", className='control-label'),
                    dcc.Dropdown(id='dropdown-delete-person-select', placeholder='Select person')
                ], className='control-group'),
                
                html.Div(id='delete-person-info', style={'marginTop': '15px'}),
                
                html.Div([
                    dbc.Checkbox(
                        id='checkbox-delete-cascade',
                        label='Also delete all relations',
                        value=True
                    )
                ], style={'marginTop': '15px'}),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id='btn-cancel-delete-person', color='secondary'),
                dbc.Button("Delete", id='btn-submit-delete-person', color='danger')
            ])
        ], id='modal-delete-person', is_open=False),
        
        # Modal Add Relation - REDESIGNED FOR INTUITIVE UX
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("🔗 Add New Relation")),
            dbc.ModalBody([
                # Helper text - clear and simple
                dbc.Alert([
                    html.I(className="fas fa-magic", style={'marginRight': '8px'}),
                    html.Strong("Just type names! "),
                    "Existing persons will appear, or you can create new ones on the fly."
                ], color="info", style={'fontSize': '14px', 'padding': '10px 15px', 'marginBottom': '20px'}),
                
                # Person 1 - Smart Input
                html.Div([
                    html.Label([
                        html.I(className="fas fa-user", style={'marginRight': '8px', 'color': '#667eea'}),
                        "First Person"
                    ], style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    
                    dcc.Dropdown(
                        id='dropdown-add-rel-p1',
                        placeholder='🔍 Type a name... (existing or new)',
                        searchable=True,
                        clearable=True,
                        style={'fontSize': '15px'}
                    ),
                    
                    # Smart indicator
                    html.Div(id='person-1-indicator', style={'marginTop': '8px', 'minHeight': '24px'}),
                    
                ], style={'marginBottom': '25px', 'padding': '15px', 'backgroundColor': '#f8f9ff', 'borderRadius': '8px'}),
                
                # Person 2 - Smart Input
                html.Div([
                    html.Label([
                        html.I(className="fas fa-user", style={'marginRight': '8px', 'color': '#667eea'}),
                        "Second Person"
                    ], style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    
                    dcc.Dropdown(
                        id='dropdown-add-rel-p2',
                        placeholder='🔍 Type a name... (existing or new)',
                        searchable=True,
                        clearable=True,
                        style={'fontSize': '15px'}
                    ),
                    
                    # Smart indicator
                    html.Div(id='person-2-indicator', style={'marginTop': '8px', 'minHeight': '24px'}),
                    
                ], style={
                    'marginBottom': '25px',
                    'padding': '15px',
                    'backgroundColor': '#f8f9ff',
                    'borderRadius': '8px'
                }),
                
                # Relation Type - Smart Input
                html.Div([
                    html.Label([
                        html.I(className="fas fa-heart", style={'marginRight': '8px', 'color': '#e74c3c'}),
                        "Relation Type"
                    ], style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    
                    dcc.Dropdown(
                        id='dropdown-add-rel-type',
                        options=[{'label': RELATION_TYPES[k], 'value': k} for k in RELATION_TYPES.keys()],
                        placeholder='Select type... (💋 Bisou, 😴 Dodo, etc.)',
                        clearable=False,
                        style={'fontSize': '15px'}
                    ),
                    
                ], style={
                    'marginBottom': '20px',
                    'padding': '15px',
                    'backgroundColor': '#fff5f5',
                    'borderRadius': '8px'
                }),
                
                # Status display
                html.Div(id='add-relation-status', style={'marginTop': '10px'})
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id='btn-cancel-add-relation', color='secondary'),
                dbc.Button("Add Relation", id='btn-submit-add-relation', color='primary')
            ])
        ], id='modal-add-relation', is_open=False, size='lg'),
        
        # Modal Update/Delete Relation - REDESIGNED
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("🔧 Manage Relations")),
            dbc.ModalBody([
                # Helper text
                dbc.Alert([
                    html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                    html.Strong("All relations: "),
                    "Click on a relation type to edit it, or click the delete button to remove it."
                ], color="info", style={'fontSize': '14px', 'padding': '10px 15px', 'marginBottom': '20px'}),
                
                # Relations list (will be populated dynamically)
                html.Div(id='relations-list-container', style={'maxHeight': '500px', 'overflowY': 'auto'}),
                
                # Status message
                html.Div(id='manage-relation-status', style={'marginTop': '15px'})
            ]),
            dbc.ModalFooter([
                dbc.Button("Close", id='btn-close-update-relation', color='secondary')
            ])
        ], id='modal-update-relation', is_open=False, size='xl'),
        
        # Modal Edit Relation Type (appears when clicking a relation)
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("✏️ Edit Relation Type")),
            dbc.ModalBody([
                html.Div(id='edit-relation-info', style={'marginBottom': '20px'}),
                
                html.Div([
                    html.Label([
                        html.I(className="fas fa-heart", style={'marginRight': '8px', 'color': '#e74c3c'}),
                        "New Relation Type"
                    ], style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    
                    dcc.Dropdown(
                        id='dropdown-edit-relation-type',
                        options=[{'label': RELATION_TYPES[k], 'value': k} for k in RELATION_TYPES.keys()],
                        placeholder='Select new type...',
                        style={'fontSize': '15px'}
                    )
                ], style={
                    'padding': '15px',
                    'backgroundColor': '#fff5f5',
                    'borderRadius': '8px'
                }),
                
                html.Div(id='edit-relation-status', style={'marginTop': '15px'})
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id='btn-cancel-edit-relation', color='secondary'),
                dbc.Button("Save Changes", id='btn-submit-edit-relation', color='primary')
            ])
        ], id='modal-edit-relation', is_open=False),
        
        # Hidden store for selected relation to edit/delete
        dcc.Store(id='selected-relation-store', data=None),
        
        # Modals auth (needed for admin too!)
        create_propose_relation_modal(),
        
    ], className='main-container')


# ============================================================================
# LAYOUT PRINCIPAL (ROUTING CONDITIONNEL)
# ============================================================================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-session', storage_type='session'),
    dcc.Store(id='data-version', data=0),  # Global store for both public and admin
    dcc.Interval(id='auto-refresh', interval=300000, n_intervals=0, disabled=True),  # 5 min, disabled by default
    html.Div(id='page-content')
])

# ============================================================================
# CALLBACK ROUTING - Display page based on auth
# ============================================================================

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, user_session):
    """Route vers vue publique ou admin selon authentification"""
    # Récupérer user depuis Flask session
    user = session.get('user', None)
    log_event("navigation", "display_page", {
        "pathname": pathname,
        "authenticated": auth_service.is_authenticated(user)
    })
    
    if auth_service.is_authenticated(user):
        # User authentifié → Vue admin complète
        return create_admin_layout(user)
    else:
        # User non-authentifié → Vue publique
        return create_public_layout()


# ============================================================================
# CALLBACKS AUTHENTIFICATION
# ============================================================================

# Login
@app.callback(
    [Output('modal-login', 'is_open', allow_duplicate=True),
     Output('login-error', 'children'),
     Output('url', 'pathname', allow_duplicate=True)],
    Input('btn-submit-login', 'n_clicks'),
    [State('input-login-username', 'value'),
     State('input-login-password', 'value')],
    prevent_initial_call='initial_duplicate'
)
def handle_login(n_clicks, username, password):
    """Gérer la connexion utilisateur"""
    if not n_clicks or not ctx.triggered:
        return no_update, '', no_update
    
    print(f"✅ [PUBLIC] LOGIN ATTEMPT: {username}")
    
    log_event("auth", "login_attempt", {
        "username": username,
        "has_password": bool(password)
    })

    if not username or not password:
        return True, dbc.Alert("Please enter username and password", color='danger'), no_update
    
    # Tentative de connexion
    user = auth_service.login(username, password)
    
    if user:
        # Succès : stocker dans Flask session
        session['user'] = user
        session.permanent = True
        print(f"✅ [PUBLIC] LOGIN SUCCESS: {username}")
        log_event("auth", "login_success", {"username": username})
        return False, '', '/'  # Fermer modal, clear error, refresh page
    else:
        # Échec
        print(f"❌ [PUBLIC] LOGIN FAILED: {username}")
        log_event("auth", "login_failure", {"username": username})
        return True, dbc.Alert("Invalid username or password", color='danger'), no_update


# Logout
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('btn-logout', 'n_clicks'),
    prevent_initial_call='initial_duplicate'
)
def handle_logout(n_clicks):
    """Déconnecter l'utilisateur"""
    if not n_clicks or not ctx.triggered:
        return no_update
    
    # Supprimer user de Flask session
    print(f"✅ [PUBLIC] LOGOUT: {session.get('user', {}).get('username')}")
    log_event("auth", "logout", {
        "username": session.get('user', {}).get('username')
    })
    session.pop('user', None)
    return '/'  # Refresh page → affichera vue publique


# Register
@app.callback(
    [Output('modal-register', 'is_open', allow_duplicate=True),
     Output('register-error', 'children'),
     Output('register-success', 'children')],
    Input('btn-submit-register', 'n_clicks'),
    [State('input-register-username', 'value'),
     State('input-register-password', 'value'),
     State('input-register-confirm', 'value')],
    prevent_initial_call='initial_duplicate'
)
def handle_register(n_clicks, username, password, confirm):
    """Gérer la demande d'inscription"""
    if not n_clicks or not ctx.triggered:
        return no_update, '', ''
    
    print(f"✅ [PUBLIC] REGISTER ATTEMPT: {username}")
    
    log_event("auth", "register_attempt", {
        "username": username,
        "has_password": bool(password),
        "has_confirm": bool(confirm)
    })

    # Validation
    if not username or not password or not confirm:
        return True, dbc.Alert("Please fill all fields", color='danger'), ''
    
    if password != confirm:
        return True, dbc.Alert("Passwords don't match", color='danger'), ''
    
    if len(password) < 6:
        return True, dbc.Alert("Password must be at least 6 characters", color='danger'), ''
    
    # Demande d'inscription
    success, message = auth_service.register_request(username, password)
    
    if success:
        print(f"✅ [PUBLIC] REGISTER SUCCESS: {username}")
        log_event("auth", "register_request_success", {"username": username})
        return True, '', dbc.Alert(message, color='success')
    else:
        print(f"❌ [PUBLIC] REGISTER FAILED: {username} - {message}")
        log_event("auth", "register_request_failure", {
            "username": username,
            "message": message
        })
        return True, dbc.Alert(message, color='danger'), ''


# Toggle modals
@app.callback(
    Output('modal-login', 'is_open'),
    [Input('btn-open-login', 'n_clicks'),
     Input('btn-cancel-login', 'n_clicks')],
    State('modal-login', 'is_open'),
    prevent_initial_call=False
)
def toggle_login_modal(n_open, n_cancel, is_open):
    """Ouvrir/fermer modal login"""
    if not ctx.triggered:
        return is_open
    
    print(f"✅ [PUBLIC] Toggle login modal")
    
    log_event("ui", "toggle_login_modal", {
        "open_clicks": n_open,
        "cancel_clicks": n_cancel,
        "was_open": is_open
    })
    return not is_open


@app.callback(
    Output('modal-register', 'is_open'),
    [Input('btn-open-register', 'n_clicks'),
     Input('btn-cancel-register', 'n_clicks')],
    State('modal-register', 'is_open'),
    prevent_initial_call=False
)
def toggle_register_modal(n_open, n_cancel, is_open):
    """Ouvrir/fermer modal register"""
    if not ctx.triggered:
        return is_open
    
    print(f"✅ [PUBLIC] Toggle register modal")
    
    log_event("ui", "toggle_register_modal", {
        "open_clicks": n_open,
        "cancel_clicks": n_cancel,
        "was_open": is_open
    })
    return not is_open


@app.callback(
    Output('modal-propose-relation', 'is_open'),
    [Input('btn-propose-relation', 'n_clicks'),
     Input('btn-cancel-propose-relation', 'n_clicks'),
     Input('btn-submit-propose-relation', 'n_clicks')],
    State('modal-propose-relation', 'is_open'),
    prevent_initial_call=False
)
def toggle_propose_relation_modal(n_open, n_cancel, n_submit, is_open):
    """Ouvrir/fermer modal propose relation"""
    if not ctx.triggered:
        return is_open
    
    ctx_triggered = ctx.triggered_id
    print(f"✅ [PUBLIC] Toggle propose relation modal: {ctx_triggered}")
    
    log_event("ui", "toggle_propose_relation_modal", {
        "triggered": ctx_triggered,
        "open_clicks": n_open,
        "cancel_clicks": n_cancel,
        "submit_clicks": n_submit,
        "was_open": is_open
    })
    if ctx_triggered in ['btn-cancel-propose-relation', 'btn-submit-propose-relation']:
        return False
    return not is_open


# Propose person
@app.callback(
    [Output('propose-person-error', 'children'),
     Output('propose-person-success', 'children')],
    Input('btn-submit-propose-person', 'n_clicks'),
    [State('input-propose-person-name', 'value'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_propose_person(n_clicks, name, user_session):
    """Gérer la proposition d'une nouvelle personne"""
    if not n_clicks or not ctx.triggered:
        return '', ''
    
    print(f"✅ [PUBLIC] PROPOSE PERSON: n_clicks={n_clicks}, name={name}")
    
    user = session.get('user', None)
    submitted_by = user.get('username', 'anonymous') if user else 'anonymous'
    
    print(f"👤 Submitted by: {submitted_by}")
    
    if not name or not name.strip():
        print(f"❌ Validation error: empty name")
        return dbc.Alert("Please enter a name", color='danger'), ''
    
    try:
        submission_id = pending_submission_repository.submit_person(name.strip(), submitted_by)
        print(f"✅ Person submitted successfully with ID: {submission_id}")
        return '', dbc.Alert(f"✅ Person '{name}' proposed! Waiting for admin approval.", color='success')
    except Exception as e:
        print(f"❌ Error submitting person: {str(e)}")
        return dbc.Alert(f"Error: {str(e)}", color='danger'), ''


# Propose relation
@app.callback(
    [Output('propose-relation-error', 'children'),
     Output('propose-relation-success', 'children')],
    Input('btn-submit-propose-relation', 'n_clicks'),
    [State('dropdown-propose-rel-p1', 'value'),
     State('dropdown-propose-rel-p2', 'value'),
     State('dropdown-propose-rel-type', 'value'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def handle_propose_relation(n_clicks, person1, person2, rel_type, user_session):
    """Gérer la proposition d'une nouvelle relation (avec création de personnes si nécessaire)"""
    if not n_clicks or not ctx.triggered:
        return '', ''
    
    log_event("proposal", "propose_relation_start", {
        "n_clicks": n_clicks,
        "person1": person1,
        "person2": person2,
        "relation_type": rel_type
    })
    
    print(f"✅ [PUBLIC] PROPOSE RELATION: n_clicks={n_clicks}, person1={person1}, person2={person2}, rel_type={rel_type}")
    
    # Récupérer username depuis user_session ou mettre anonymous
    submitted_by = 'anonymous'
    if user_session and isinstance(user_session, dict):
        submitted_by = user_session.get('username', 'anonymous')
    
    print(f"👤 Submitted by: {submitted_by}")
    
    if not person1 or not person2 or rel_type is None:
        error_msg = "Veuillez sélectionner les deux personnes et un type de relation"
        print(f"❌ Validation error: {error_msg}")
        log_event("proposal", "propose_relation_validation_error", {"reason": "missing_fields"})
        return dbc.Alert(error_msg, color='danger'), ''
    
    # Extract real names from __CREATE__ prefix if present
    p1_name = person1.replace("__CREATE__", "") if str(person1).startswith("__CREATE__") else person1
    p2_name = person2.replace("__CREATE__", "") if str(person2).startswith("__CREATE__") else person2
    
    print(f"📝 Real names: p1={p1_name}, p2={p2_name}")
    
    if p1_name == p2_name:
        error_msg = "Impossible de créer une relation avec la même personne"
        print(f"❌ Same person error: {error_msg}")
        log_event("proposal", "propose_relation_validation_error", {"reason": "same_person"})
        return dbc.Alert(error_msg, color='danger'), ''
    
    try:
        # Create new persons if needed
        created_persons = []
        if str(person1).startswith("__CREATE__"):
            print(f"➕ Creating new person: {p1_name}")
            success, msg = person_repository.create(p1_name)
            if success:
                created_persons.append(p1_name)
                log_event("proposal", "create_person_inline", {"name": p1_name, "success": True})
                print(f"✅ Person created: {p1_name}")
            else:
                print(f"❌ Failed to create person {p1_name}: {msg}")
                log_event("proposal", "create_person_inline_failed", {"name": p1_name, "error": msg})
                return dbc.Alert(f"Erreur création personne '{p1_name}': {msg}", color='danger'), ''
        
        if str(person2).startswith("__CREATE__"):
            print(f"➕ Creating new person: {p2_name}")
            success, msg = person_repository.create(p2_name)
            if success:
                created_persons.append(p2_name)
                log_event("proposal", "create_person_inline", {"name": p2_name, "success": True})
                print(f"✅ Person created: {p2_name}")
            else:
                print(f"❌ Failed to create person {p2_name}: {msg}")
                log_event("proposal", "create_person_inline_failed", {"name": p2_name, "error": msg})
                return dbc.Alert(f"Erreur création personne '{p2_name}': {msg}", color='danger'), ''
        
        print(f"💾 Saving relation proposal: {p1_name} <-> {p2_name} (type={rel_type})")
        submission_id = pending_submission_repository.submit_relation(p1_name, p2_name, rel_type, submitted_by)
        
        log_event("proposal", "propose_relation_submitted", {
            "submission_id": submission_id,
            "person1": p1_name,
            "person2": p2_name,
            "relation_type": rel_type,
            "submitted_by": submitted_by,
            "created_persons": created_persons
        })
        
        success_msg = f"✅ Relation proposée ! En attente d'approbation admin."
        if created_persons:
            success_msg += f" Nouvelle(s) personne(s) créée(s): {', '.join(created_persons)}"
        
        print(f"✅ SUCCESS: {success_msg}")
        return '', dbc.Alert(success_msg, color='success')
    except Exception as e:
        error_msg = f"Erreur: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        log_event("proposal", "propose_relation_error", {"error": str(e)})
        return dbc.Alert(error_msg, color='danger'), ''


# SMART DROPDOWN OPTIONS - Propose Relation Person 1 (with "Create new" option)
@app.callback(
    Output('dropdown-propose-rel-p1', 'options'),
    [Input('dropdown-propose-rel-p1', 'search_value'),
     Input('modal-propose-relation', 'is_open')],
    [State('dropdown-propose-rel-p1', 'value')],
    prevent_initial_call=False
)
def populate_propose_p1_options(search_value, is_open, current_value):
    """Populate Person 1 dropdown with existing persons + 'Create new' option if needed"""
    if not is_open:
        raise PreventUpdate
    
    persons = person_repository.read_all()
    # Trier par ordre alphabétique
    options = [{'label': p['name'], 'value': p['name']} for p in sorted(persons, key=lambda x: x['name'].lower())]
    
    # If search value and no exact match → add "Create new" option
    if search_value and len(search_value.strip()) >= 2:
        existing_names = [p['name'].lower() for p in persons]
        if search_value.strip().lower() not in existing_names:
            options.insert(0, {
                'label': f"➕ Créer: {search_value.strip()}",
                'value': f"__CREATE__{search_value.strip()}"
            })
    
    # Keep __CREATE__ option visible after selection
    if current_value and str(current_value).startswith("__CREATE__"):
        name = str(current_value).replace("__CREATE__", "")
        if not any(opt['value'] == current_value for opt in options):
            options.insert(0, {
                'label': f"➕ Créer: {name}",
                'value': current_value
            })
    
    return options


# SMART DROPDOWN OPTIONS - Propose Relation Person 2 (with "Create new" option)
@app.callback(
    Output('dropdown-propose-rel-p2', 'options'),
    [Input('dropdown-propose-rel-p2', 'search_value'),
     Input('modal-propose-relation', 'is_open')],
    [State('dropdown-propose-rel-p2', 'value')],
    prevent_initial_call=False
)
def populate_propose_p2_options(search_value, is_open, current_value):
    """Populate Person 2 dropdown with existing persons + 'Create new' option if needed"""
    if not is_open:
        raise PreventUpdate
    
    persons = person_repository.read_all()
    # Trier par ordre alphabétique
    options = [{'label': p['name'], 'value': p['name']} for p in sorted(persons, key=lambda x: x['name'].lower())]
    
    # If search value and no exact match → add "Create new" option
    if search_value and len(search_value.strip()) >= 2:
        existing_names = [p['name'].lower() for p in persons]
        if search_value.strip().lower() not in existing_names:
            options.insert(0, {
                'label': f"➕ Créer: {search_value.strip()}",
                'value': f"__CREATE__{search_value.strip()}"
            })
    
    # Keep __CREATE__ option visible after selection
    if current_value and str(current_value).startswith("__CREATE__"):
        name = str(current_value).replace("__CREATE__", "")
        if not any(opt['value'] == current_value for opt in options):
            options.insert(0, {
                'label': f"➕ Créer: {name}",
                'value': current_value
            })
    
    return options


# ============================================================================
# CALLBACKS ADMIN PANEL
# ============================================================================

# Refresh admin panel - INITIAL LOAD
@app.callback(
    [Output('pending-accounts-list', 'children'),
     Output('pending-persons-list', 'children'),
     Output('pending-relations-list', 'children')],
    [Input('btn-refresh-admin', 'n_clicks'),
     Input('auto-refresh', 'n_intervals')],
    State('user-session', 'data'),
    prevent_initial_call=False
)
def refresh_admin_panel(n_clicks, n_intervals, user_session):
    """Rafraîchir les listes du panel admin - Initial Load + Auto-refresh"""
    print(f"🔄 REFRESH ADMIN PANEL called (initial/auto-refresh)")
    user = session.get('user', None)
    
    # Vérifier si admin
    if not auth_service.is_admin(user):
        print(f"❌ Access denied - user is not admin")
        return (
            html.P("Accès refusé", className='text-muted'),
            html.P("Accès refusé", className='text-muted'),
            html.P("Accès refusé", className='text-muted')
        )
    
    print(f"✅ User is admin, fetching pending submissions...")
    
    from components.admin_panel import (
        render_pending_accounts_list,
        render_pending_persons_list,
        render_pending_relations_list
    )
    
    # Récupérer les données
    accounts = pending_account_repository.get_pending_requests()
    persons = pending_submission_repository.get_pending_persons()
    relations = pending_submission_repository.get_pending_relations()
    
    print(f"📊 Admin panel data: accounts={len(accounts)}, persons={len(persons)}, relations={len(relations)}")
    
    return (
        render_pending_accounts_list(accounts),
        render_pending_persons_list(persons),
        render_pending_relations_list(relations)
    )


# Refresh admin panel - AFTER PERSON PROPOSED
@app.callback(
    [Output('pending-accounts-list', 'children', allow_duplicate=True),
     Output('pending-persons-list', 'children', allow_duplicate=True),
     Output('pending-relations-list', 'children', allow_duplicate=True)],
    Input('btn-submit-propose-person', 'n_clicks'),
    State('user-session', 'data'),
    prevent_initial_call='initial_duplicate'
)
def refresh_admin_panel_after_propose_person(n_clicks, user_session):
    """Rafraîchir après proposition d'une personne"""
    if not n_clicks or not ctx.triggered:
        return no_update, no_update, no_update
    
    print(f"✅ [ADMIN] REFRESH ADMIN PANEL - after propose person")
    user = session.get('user', None)
    
    if not auth_service.is_admin(user):
        print(f"❌ Access denied - not admin")
        return no_update, no_update, no_update
    
    from components.admin_panel import (
        render_pending_accounts_list,
        render_pending_persons_list,
        render_pending_relations_list
    )
    
    accounts = pending_account_repository.get_pending_requests()
    persons = pending_submission_repository.get_pending_persons()
    relations = pending_submission_repository.get_pending_relations()
    
    print(f"📊 Updated data: accounts={len(accounts)}, persons={len(persons)}, relations={len(relations)}")
    
    return (
        render_pending_accounts_list(accounts),
        render_pending_persons_list(persons),
        render_pending_relations_list(relations)
    )


# Refresh admin panel - AFTER RELATION PROPOSED
@app.callback(
    [Output('pending-accounts-list', 'children', allow_duplicate=True),
     Output('pending-persons-list', 'children', allow_duplicate=True),
     Output('pending-relations-list', 'children', allow_duplicate=True)],
    Input('btn-submit-propose-relation', 'n_clicks'),
    State('user-session', 'data'),
    prevent_initial_call='initial_duplicate'
)
def refresh_admin_panel_after_propose_relation(n_clicks, user_session):
    """Rafraîchir après proposition d'une relation"""
    if not n_clicks or not ctx.triggered:
        return no_update, no_update, no_update
    
    print(f"✅ [ADMIN] REFRESH ADMIN PANEL - after propose relation")
    user = session.get('user', None)
    
    if not auth_service.is_admin(user):
        print(f"❌ Access denied - not admin")
        return no_update, no_update, no_update
    
    from components.admin_panel import (
        render_pending_accounts_list,
        render_pending_persons_list,
        render_pending_relations_list
    )
    
    accounts = pending_account_repository.get_pending_requests()
    persons = pending_submission_repository.get_pending_persons()
    relations = pending_submission_repository.get_pending_relations()
    
    print(f"📊 Updated data: accounts={len(accounts)}, persons={len(persons)}, relations={len(relations)}")
    
    return (
        render_pending_accounts_list(accounts),
        render_pending_persons_list(persons),
        render_pending_relations_list(relations)
    )


# Approve/Reject Accounts (pattern matching)
@app.callback(
    Output('pending-accounts-list', 'children', allow_duplicate=True),
    [Input({'type': 'approve-account', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-account', 'index': ALL}, 'n_clicks')],
    State('user-session', 'data'),
    prevent_initial_call=True
)
def handle_account_approval(approve_clicks, reject_clicks, user_session):
    """Gérer l'approbation/rejet de comptes"""
    if not ctx.triggered:
        return no_update
    
    print(f"✅ [ADMIN] Handle account approval: {ctx.triggered_id}")
    
    user = session.get('user', None)
    
    if not auth_service.is_admin(user):
        return "Access Denied"
    
    ctx_triggered = ctx.triggered_id
    if not ctx_triggered:
        return no_update
    
    # Vérifier qu'au moins un bouton a vraiment été cliqué
    if all(c is None for c in approve_clicks) and all(c is None for c in reject_clicks):
        return no_update
    
    account_id = ctx_triggered['index']
    action_type = ctx_triggered['type']
    
    if action_type == 'approve-account':
        pending_account_repository.approve_request(account_id)
    elif action_type == 'reject-account':
        pending_account_repository.reject_request(account_id)
    
    # Rafraîchir la liste
    from components.admin_panel import render_pending_accounts_list
    accounts = pending_account_repository.get_pending_requests()
    return render_pending_accounts_list(accounts)


# Approve/Reject Persons (pattern matching)
@app.callback(
    Output('pending-persons-list', 'children', allow_duplicate=True),
    [Input({'type': 'approve-person', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-person', 'index': ALL}, 'n_clicks')],
    State('user-session', 'data'),
    prevent_initial_call=True
)
def handle_person_approval(approve_clicks, reject_clicks, user_session):
    """Gérer l'approbation/rejet de personnes"""
    if not ctx.triggered:
        return no_update
    
    print(f"✅ [ADMIN] PERSON APPROVAL: {ctx.triggered_id}")
    user = session.get('user', None)
    
    if not auth_service.is_admin(user):
        print(f"❌ Access denied - not admin")
        return "Access Denied"
    
    ctx_triggered = ctx.triggered_id
    
    if not ctx_triggered:
        return no_update
    
    # Vérifier qu'au moins un bouton a vraiment été cliqué
    if all(c is None for c in approve_clicks) and all(c is None for c in reject_clicks):
        print(f"⚠️ No real click detected - preventing update")
        return no_update
    
    person_id = ctx_triggered['index']
    action_type = ctx_triggered['type']
    
    print(f"📝 Action: {action_type} for person ID: {person_id}")
    
    if action_type == 'approve-person':
        result = pending_submission_repository.approve_person(person_id)
        print(f"✅ Approval result: {result}")
    elif action_type == 'reject-person':
        pending_submission_repository.reject_person(person_id)
    
    # Rafraîchir la liste
    from components.admin_panel import render_pending_persons_list
    persons = pending_submission_repository.get_pending_persons()
    return render_pending_persons_list(persons)


# Approve/Reject Relations (pattern matching)
@app.callback(
    Output('pending-relations-list', 'children', allow_duplicate=True),
    [Input({'type': 'approve-relation', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-relation', 'index': ALL}, 'n_clicks')],
    State('user-session', 'data'),
    prevent_initial_call=True
)
def handle_relation_approval(approve_clicks, reject_clicks, user_session):
    """Gérer l'approbation/rejet de relations"""
    if not ctx.triggered:
        return no_update
    
    if all(c is None for c in approve_clicks) and all(c is None for c in reject_clicks):
        return no_update
    
    print(f"✅ [ADMIN] Handle relation approval: {ctx.triggered_id}")
    
    log_event("admin", "relation_approval_callback", {
        "approve_clicks": approve_clicks,
        "reject_clicks": reject_clicks
    })
    
    user = session.get('user', None)
    
    if not auth_service.is_admin(user):
        log_event("admin", "relation_approval_denied", {"reason": "not_admin"})
        return "Access Denied"
    
    ctx_triggered = ctx.triggered_id
    if not ctx_triggered:
        log_event("admin", "relation_approval_no_trigger", {"reason": "no_triggered_id"})
        return no_update
    
    # Vérifier qu'au moins un bouton a vraiment été cliqué (pas juste None)
    # Si tous les clicks sont None, c'est que les boutons viennent d'apparaître
    if all(c is None for c in approve_clicks) and all(c is None for c in reject_clicks):
        log_event("admin", "relation_approval_no_real_click", {
            "approve_clicks": approve_clicks,
            "reject_clicks": reject_clicks
        })
        return no_update
    
    relation_id = ctx_triggered['index']
    action_type = ctx_triggered['type']
    
    log_event("admin", "relation_action", {
        "action": action_type,
        "relation_id": relation_id
    })
    
    if action_type == 'approve-relation':
        print(f"   ✅ Approving relation ID: {relation_id}")
        result = pending_submission_repository.approve_relation(relation_id)
        log_event("admin", "relation_approved", {
            "relation_id": relation_id,
            "success": result
        })
    elif action_type == 'reject-relation':
        print(f"   ✅ Rejecting relation ID: {relation_id}")
        result = pending_submission_repository.reject_relation(relation_id)
        log_event("admin", "relation_rejected", {
            "relation_id": relation_id,
            "success": result
        })
    
    # Rafraîchir la liste
    from components.admin_panel import render_pending_relations_list
    relations = pending_submission_repository.get_pending_relations()
    return render_pending_relations_list(relations)


# User Management (pattern matching)
@app.callback(
    [Output('active-users-list', 'children'),
     Output('pending-users-list', 'children'),
     Output('user-filter-state', 'data')],
    [Input('btn-refresh-users', 'n_clicks'),
     Input('filter-all-users', 'n_clicks'),
     Input('filter-admins', 'n_clicks'),
     Input('filter-users', 'n_clicks'),
     Input('filter-pending', 'n_clicks'),
     Input({'type': 'toggle-admin', 'index': ALL}, 'n_clicks'),
     Input({'type': 'delete-user', 'index': ALL}, 'n_clicks'),
     Input({'type': 'approve-pending-user', 'index': ALL}, 'n_clicks'),
     Input({'type': 'approve-pending-admin', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-pending-user', 'index': ALL}, 'n_clicks')],
    State('user-session', 'data'),
    prevent_initial_call=False
)
def handle_user_management(refresh_clicks, all_clicks, admin_clicks, user_clicks, pending_clicks,
                          toggle_admin_clicks, delete_clicks, approve_clicks, approve_admin_clicks, reject_clicks,
                          user_session):
    """Gère la liste des utilisateurs et les actions admin"""
    from components.user_management import render_active_users_list, render_pending_users_list
    from database.audit import AuditRepository
    
    # Vérifier les permissions admin
    user = session.get('user', None)
    if not auth_service.is_admin(user):
        error_div = html.Div("Access Denied", style={'color': 'red', 'padding': '10px'})
        return error_div, error_div, 'all'
    
    filter_type = 'all'
    
    # Initial load ou refresh
    if not ctx.triggered or ctx.triggered_id in ['btn-refresh-users', None]:
        active_users = user_repository.get_all_users()
        pending_users = user_repository.get_pending_users()
        return render_active_users_list(active_users, 'all'), render_pending_users_list(pending_users), 'all'
    
    triggered_id = ctx.triggered_id
    print(f"✅ [USER-MGMT] Triggered: {triggered_id}")
    
    # Handle filter buttons
    if triggered_id == 'filter-all-users':
        filter_type = 'all'
    elif triggered_id == 'filter-admins':
        filter_type = 'admins'
    elif triggered_id == 'filter-users':
        filter_type = 'users'
    elif triggered_id == 'filter-pending':
        filter_type = 'pending'
    
    # Handle user actions
    elif isinstance(triggered_id, dict):
        user_id = triggered_id.get('index')
        action_type = triggered_id.get('type')
        print(f"  Action: {action_type} on user {user_id}")
        
        if action_type == 'toggle-admin' and user_id:
            user_obj = user_repository.get_user_by_id(user_id)
            if user_obj:
                if user_obj.get('is_admin'):
                    user_repository.demote_from_admin(user_id)
                    print(f"  ✅ Demoted {user_obj['username']}")
                    AuditRepository.log_action(
                        action_type='demote',
                        entity_type='user',
                        entity_id=user_id,
                        entity_name=user_obj['username'],
                        performed_by=user.get('username', 'admin') if user else 'admin',
                        old_value='admin',
                        new_value='user'
                    )
                else:
                    user_repository.promote_to_admin(user_id)
                    print(f"  ✅ Promoted {user_obj['username']}")
                    AuditRepository.log_action(
                        action_type='promote',
                        entity_type='user',
                        entity_id=user_id,
                        entity_name=user_obj['username'],
                        performed_by=user.get('username', 'admin') if user else 'admin',
                        old_value='user',
                        new_value='admin'
                    )
        
        elif action_type == 'delete-user' and user_id:
            user_obj = user_repository.get_user_by_id(user_id)
            if user_obj:
                user_repository.delete_user(user_id)
                print(f"  ✅ Deleted {user_obj['username']}")
                AuditRepository.log_action(
                    action_type='delete',
                    entity_type='user',
                    entity_id=user_id,
                    entity_name=user_obj['username'],
                    performed_by=user.get('username', 'admin') if user else 'admin',
                    old_value=f"user:{user_obj.get('is_admin', False)}",
                    new_value='deleted'
                )
        
        elif action_type == 'approve-pending-user' and user_id:
            user_obj = user_repository.get_pending_user_by_id(user_id)
            if user_obj:
                user_repository.approve_pending_user(user_id, make_admin=False)
                print(f"  ✅ Approved {user_obj['username']} as user")
                AuditRepository.log_action(
                    action_type='approve',
                    entity_type='user',
                    entity_id=user_id,
                    entity_name=user_obj['username'],
                    performed_by=user.get('username', 'admin') if user else 'admin',
                    old_value='pending',
                    new_value='approved'
                )
        
        elif action_type == 'approve-pending-admin' and user_id:
            user_obj = user_repository.get_pending_user_by_id(user_id)
            if user_obj:
                user_repository.approve_pending_user(user_id, make_admin=True)
                print(f"  ✅ Approved {user_obj['username']} as admin")
                AuditRepository.log_action(
                    action_type='approve',
                    entity_type='user',
                    entity_id=user_id,
                    entity_name=user_obj['username'],
                    performed_by=user.get('username', 'admin') if user else 'admin',
                    old_value='pending',
                    new_value='approved_admin'
                )
        
        elif action_type == 'reject-pending-user' and user_id:
            user_obj = user_repository.get_pending_user_by_id(user_id)
            if user_obj:
                user_repository.reject_pending_user(user_id)
                print(f"  ✅ Rejected {user_obj['username']}")
                AuditRepository.log_action(
                    action_type='reject',
                    entity_type='user',
                    entity_id=user_id,
                    entity_name=user_obj['username'],
                    performed_by=user.get('username', 'admin') if user else 'admin',
                    old_value='pending',
                    new_value='rejected'
                )
    
    # Rafraîchir les listes
    active_users = user_repository.get_all_users()
    pending_users = user_repository.get_pending_users()
    
    return render_active_users_list(active_users, filter_type), render_pending_users_list(pending_users), filter_type


# ============================================================================
# CALLBACKS - GRAPH
# ============================================================================

@app.callback(
    Output('network-graph', 'figure'),
    [Input('layout-selector', 'value'),
     Input('color-dropdown', 'value'),
     Input('data-version', 'data'),  # Trigger refresh on data change
     Input('auto-refresh', 'n_intervals'),
     Input('node-size-slider', 'value'),
     Input('repulsion-slider', 'value'),
     Input('edge-tension-slider', 'value'),
     Input('search-person', 'value'),
     Input('show-all-names', 'value')],
    prevent_initial_call=False
)
def update_graph(layout_type, color_by, data_version, n_intervals, node_size, repulsion, edge_tension, search_person, show_all_names):
    """Build graph using repository + graph.py rendering with parameters"""
    try:
        # Get relations from repository (deduplicate pour éviter A→B et B→A)
        relations = relation_repository.read_all(deduplicate=True)
        
        if not relations:
            # Empty graph
            fig = go.Figure()
            fig.add_annotation(
                text="No relations to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color='#999')
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            return fig
        
        # Convert to dict format for build_graph
        relations_dict = {}
        for p1, p2, rel_type in relations:
            if p1 not in relations_dict:
                relations_dict[p1] = []
            relations_dict[p1].append((p2, rel_type))
        
        # Build NetworkX graph
        G = build_graph(relations_dict)
        
        # Compute layout with repulsion parameter
        pos = compute_layout(G, mode=layout_type, repulsion=repulsion)
        
        # Vérifier si la checkbox est cochée
        show_all = 'show_all' in (show_all_names or [])
        
        # Create figure with size, edge tension, and show_all_names parameters
        fig = make_figure(G, pos, size_factor=node_size/15.0, edge_width=1.0 + edge_tension, show_all_names=show_all)
        
        # If searching for a person, center and zoom on them
        if search_person:
            if search_person in pos:
                x_pos, y_pos = pos[search_person]
                # Center on the node and zoom
                fig.update_xaxes(range=[x_pos - 1, x_pos + 1])
                fig.update_yaxes(range=[y_pos - 1, y_pos + 1])
        
        return fig
        
    except Exception as e:
        # Error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='red')
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

# ============================================================================
# Admin Graph Callback - Same as public but for admin tab
# ============================================================================

@app.callback(
    Output('network-graph-admin', 'figure'),
    [Input('layout-selector', 'value'),
     Input('color-dropdown', 'value'),
     Input('data-version', 'data'),  # Trigger refresh on data change
     Input('auto-refresh', 'n_intervals'),
     Input('node-size-slider', 'value'),
     Input('repulsion-slider', 'value'),
     Input('edge-tension-slider', 'value'),
     Input('search-person', 'value'),
     Input('show-all-names', 'value')],
    prevent_initial_call=False
)
def update_graph_admin(layout_type, color_by, data_version, n_intervals, node_size, repulsion, edge_tension, search_person, show_all_names):
    """Build graph using repository + graph.py rendering with parameters (admin version)"""
    print(f"\n🔵 [ADMIN-GRAPH] Callback triggered!")
    print(f"  Layout: {layout_type}, Show all: {show_all_names}")
    try:
        # Get relations from repository (deduplicate pour éviter A→B et B→A)
        relations = relation_repository.read_all(deduplicate=True)
        print(f"  Relations retrieved: {len(relations)}")
        
        if not relations:
            # Empty graph
            fig = go.Figure()
            fig.add_annotation(
                text="No relations to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color='#999')
            )
            fig.update_layout(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            return fig
        
        # Convert to dict format for build_graph
        relations_dict = {}
        for p1, p2, rel_type in relations:
            if p1 not in relations_dict:
                relations_dict[p1] = []
            relations_dict[p1].append((p2, rel_type))
        
        # Build NetworkX graph
        G = build_graph(relations_dict)
        
        # Compute layout with repulsion parameter
        pos = compute_layout(G, mode=layout_type, repulsion=repulsion)
        
        # Vérifier si la checkbox est cochée
        show_all = 'show_all' in (show_all_names or [])
        
        # Create figure with size, edge tension, and show_all_names parameters
        fig = make_figure(G, pos, size_factor=node_size/15.0, edge_width=1.0 + edge_tension, show_all_names=show_all)
        
        # If searching for a person, center and zoom on them
        if search_person:
            if search_person in pos:
                x_pos, y_pos = pos[search_person]
                # Center on the node and zoom
                fig.update_xaxes(range=[x_pos - 1, x_pos + 1])
                fig.update_yaxes(range=[y_pos - 1, y_pos + 1])
        
        return fig
        
    except Exception as e:
        # Error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='red')
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

# ============================================================================
# CALLBACKS CLIENTSIDE - BOUTONS INTERACTIFS (Zoom, Fullscreen, Hamburger)
# ============================================================================

# Note: Les boutons zoom custom (btn-zoom-in, btn-zoom-out) sont reliés
# aux boutons natifs Plotly via JavaScript (voir index_string)

# Callback pour Hamburger Menu
app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        
        console.log('🍔 Hamburger clicked');
        
        var menu = document.getElementById('hamburger-menu');
        if (!menu) {
            console.error('Hamburger menu not found');
            return window.dash_clientside.no_update;
        }
        
        var currentDisplay = window.getComputedStyle(menu).display;
        var newDisplay = (currentDisplay === 'none') ? 'block' : 'none';
        menu.style.display = newDisplay;
        
        console.log('✅ Menu display:', newDisplay);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('hamburger-btn-graph', 'n_clicks', allow_duplicate=True),
    Input('hamburger-btn-graph', 'n_clicks'),
    prevent_initial_call=True
)

# Callback pour Fullscreen
app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        
        console.log('🖥️ Fullscreen clicked');
        
        var graphPanel = document.querySelector('.graph-panel');
        var icon = document.getElementById('fullscreen-icon');
        
        if (!graphPanel) {
            console.error('Graph panel not found');
            return window.dash_clientside.no_update;
        }
        
        var isFullscreen = graphPanel.classList.contains('fullscreen-mode');
        
        if (isFullscreen) {
            graphPanel.classList.remove('fullscreen-mode');
            if (icon) icon.className = 'fas fa-expand';
            console.log('✅ Exited fullscreen');
        } else {
            graphPanel.classList.add('fullscreen-mode');
            if (icon) icon.className = 'fas fa-compress';
            console.log('✅ Entered fullscreen');
        }
        
        // Resize Plotly graph après un court délai
        setTimeout(function() {
            var graphDiv = document.getElementById('network-graph');
            if (graphDiv && window.Plotly) {
                var plotlyDiv = graphDiv.querySelector('.js-plotly-plot') || graphDiv;
                Plotly.Plots.resize(plotlyDiv);
                console.log('✅ Graph resized');
            }
        }, 100);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('btn-fullscreen', 'n_clicks', allow_duplicate=True),
    Input('btn-fullscreen', 'n_clicks'),
    prevent_initial_call=True
)

# ============================================================================
# CALLBACKS - SEARCH & DROPDOWN OPTIONS
# ============================================================================

@app.callback(
    Output('search-person', 'options'),
    Input('data-version', 'data')
)
def update_person_options(data_version):
    """Update person search dropdown options"""
    try:
        persons = person_repository.read_all()
        options = [{'label': person['name'], 'value': person['name']} for person in persons if person.get('name') and not person['name'].startswith('#')]
        return sorted(options, key=lambda x: x['label'])
    except:
        return []

# ============================================================================
# CALLBACKS - STATS
# ============================================================================

@app.callback(
    Output('stats-display', 'children'),
    Input('auto-refresh', 'n_intervals')
)
def update_stats(n_intervals):
    """Update statistics display"""
    persons = person_repository.read_all()
    relations = relation_repository.read_all(deduplicate=True)
    
    # Relations déjà dédupliquées par le repository
    unique_relations = len(relations)
    
    return html.Div([
        html.Div([html.Span("Persons"), html.Span(f"{len(persons)}", className='stat-value')], className='stat-item'),
        html.Div([html.Span("Relations"), html.Span(f"{unique_relations}", className='stat-value')], className='stat-item'),
        html.Div([html.Span("Symmetry"), html.Span("✅ 100%", className='stat-value')], className='stat-item'),
    ])

# ============================================================================
# CALLBACKS - HISTORY
# ============================================================================

@app.callback(
    Output('history-list-recent', 'children'),
    [Input('btn-refresh-history-recent', 'n_clicks'),
     Input('auto-refresh', 'n_intervals'),
     Input('history-filter-type', 'value'),
     Input('history-filter-action', 'value')],
    prevent_initial_call=False
)
def update_history_recent(n_clicks, n_intervals, filter_type, filter_action):
    """Display recent ACTIVE actions from HistoryService"""
    print(f"✅ [HISTORY] update_history_recent called: n_clicks={n_clicks}, filter_type={filter_type}, filter_action={filter_action}")
    
    try:
        # Get ACTIVE history records from database
        recent = history_service.get_history(limit=50, status='active')
        print(f"   → Retrieved {len(recent)} active history records from database")
        
        if not recent:
            return html.P("Aucune modification récente", className='text-muted')
        
        # Import components for rendering
        from components.history_tab import render_history_item
        
        # Convert to UI format using the component renderer
        items = []
        for record in recent:
            # Enrich record with entity info if missing
            if not record.get('entity_type'):
                # Infer from action_type
                action_type = record.get('action_type', '')
                if 'PERSON' in action_type.upper():
                    record['entity_type'] = 'person'
                    record['entity_name'] = record.get('person1', 'N/A')
                elif 'RELATION' in action_type.upper():
                    record['entity_type'] = 'relation'
                    record['entity_name'] = f"{record.get('person1', '')} ↔ {record.get('person2', '')}"
                else:
                    record['entity_type'] = 'unknown'
                    record['entity_name'] = record.get('person1', 'N/A')
            
            items.append(render_history_item(record, show_cancel_button=True))
        
        print(f"   ✅ Returning {len(items)} formatted history items")
        return html.Div(items) if items else html.P("Aucune modification récente", className='text-muted')
        
    except Exception as e:
        print(f"   ❌ ERROR in update_history_recent: {e}")
        import traceback
        traceback.print_exc()
        return html.P(f"Erreur lors du chargement de l'historique: {str(e)}", className='text-danger')


@app.callback(
    Output('history-list-cancelled', 'children'),
    [Input('btn-refresh-history-cancelled', 'n_clicks'),
     Input('auto-refresh', 'n_intervals')],
    prevent_initial_call=False
)
def update_history_cancelled(n_clicks, n_intervals):
    """Display CANCELLED actions"""
    print(f"✅ [HISTORY] update_history_cancelled called: n_clicks={n_clicks}")
    
    try:
        # Get CANCELLED history records
        cancelled = history_service.get_history(limit=50, status='cancelled')
        print(f"   → Retrieved {len(cancelled)} cancelled records")
        
        if not cancelled:
            return html.P("Aucune modification annulée", className='text-muted')
        
        # Import components for rendering
        from components.history_tab import render_history_item
        
        # Convert to UI format
        items = []
        for record in cancelled:
            # Enrich record
            if not record.get('entity_type'):
                action_type = record.get('action_type', '')
                if 'PERSON' in action_type.upper():
                    record['entity_type'] = 'person'
                    record['entity_name'] = record.get('person1', 'N/A')
                elif 'RELATION' in action_type.upper():
                    record['entity_type'] = 'relation'
                    record['entity_name'] = f"{record.get('person1', '')} ↔ {record.get('person2', '')}"
                else:
                    record['entity_type'] = 'unknown'
                    record['entity_name'] = record.get('person1', 'N/A')
            
            items.append(render_history_item(record, show_cancel_button=False))
        
        return html.Div(items) if items else html.P("Aucune modification annulée", className='text-muted')
        
    except Exception as e:
        print(f"   ❌ ERROR in update_history_cancelled: {e}")
        import traceback
        traceback.print_exc()
        return html.P(f"Erreur: {str(e)}", className='text-danger')


# Clientside callback pour détecter le clic sur un bouton d'annulation
app.clientside_callback(
    """
    function(n_clicks_list) {
        console.log('🔍 [CLIENTSIDE] Cancel button detection triggered');
        console.log('   n_clicks_list:', n_clicks_list);
        
        // Find which button was clicked (look for the one that just incremented)
        if (!n_clicks_list || n_clicks_list.length === 0) {
            console.log('   ⚠️ No buttons detected');
            return window.dash_clientside.no_update;
        }
        
        // Get the triggered component ID from Dash context
        const triggered = window.dash_clientside.callback_context.triggered;
        console.log('   Triggered:', triggered);
        
        if (!triggered || triggered.length === 0) {
            return window.dash_clientside.no_update;
        }
        
        // Extract the action ID from the triggered prop_id
        const prop_id = triggered[0].prop_id;
        console.log('   prop_id:', prop_id);
        
        // Parse the JSON ID to get the index
        const match = prop_id.match(/"index":(\\d+)/);
        if (match && match[1]) {
            const action_id = parseInt(match[1]);
            console.log('   ✅ Detected cancel for action_id:', action_id);
            return {
                'action_id': action_id,
                'timestamp': Date.now()
            };
        }
        
        console.log('   ❌ Could not parse action_id from prop_id');
        return window.dash_clientside.no_update;
    }
    """,
    Output('cancel-action-store', 'data'),
    Input({'type': 'cancel-history', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)


# Callback pour annuler l'action stockée dans le Store
@app.callback(
    [Output('history-list-recent', 'children', allow_duplicate=True),
     Output('history-list-cancelled', 'children', allow_duplicate=True),
     Output('data-version', 'data', allow_duplicate=True),
     Output('cancel-action-store', 'data', allow_duplicate=True)],
    Input('cancel-action-store', 'data'),
    [State('data-version', 'data'),
     State('auth-data', 'data')],
    prevent_initial_call=True
)
def cancel_history_action(cancel_data, current_version, auth_data):
    """Cancel a history action based on the stored action ID"""
    print(f"🔍 [HISTORY-CANCEL] Callback triggered!")
    print(f"   cancel_data: {cancel_data}")
    
    if not cancel_data or not cancel_data.get('action_id'):
        print(f"   ⚠️ No action_id in cancel_data")
        return no_update, no_update, no_update, no_update
    
    action_id = cancel_data.get('action_id')
    
    # Check authentication
    if not auth_data or not auth_data.get('is_admin'):
        print("❌ [HISTORY] Unauthorized cancel attempt")
        return no_update, no_update, no_update, None
    
    print(f"✅ [HISTORY] Cancel action: action_id={action_id}")
    
    try:
        # Cancel the action
        username = auth_data.get('username', 'admin')
        success, message = history_service.cancel_action(action_id, cancelled_by=username)
        
        if success:
            print(f"   ✅ {message}")
            
            # Clear cache and increment version
            graph_builder.clear_cache()
            new_version = (current_version or 0) + 1
            print(f"   → Cache cleared, new version: {new_version}")
            
            # Refresh both lists
            # Get active actions
            recent = history_service.get_history(limit=50, status='active')
            from components.history_tab import render_history_item
            
            recent_items = []
            for record in recent:
                if not record.get('entity_type'):
                    action_type = record.get('action_type', '')
                    if 'PERSON' in action_type.upper():
                        record['entity_type'] = 'person'
                        record['entity_name'] = record.get('person1', 'N/A')
                    elif 'RELATION' in action_type.upper():
                        record['entity_type'] = 'relation'
                        record['entity_name'] = f"{record.get('person1', '')} ↔ {record.get('person2', '')}"
                    else:
                        record['entity_type'] = 'unknown'
                        record['entity_name'] = record.get('person1', 'N/A')
                
                recent_items.append(render_history_item(record, show_cancel_button=True))
            
            recent_display = html.Div(recent_items) if recent_items else html.P("Aucune modification récente", className='text-muted')
            
            # Get cancelled actions
            cancelled = history_service.get_history(limit=50, status='cancelled')
            cancelled_items = []
            for record in cancelled:
                if not record.get('entity_type'):
                    action_type = record.get('action_type', '')
                    if 'PERSON' in action_type.upper():
                        record['entity_type'] = 'person'
                        record['entity_name'] = record.get('person1', 'N/A')
                    elif 'RELATION' in action_type.upper():
                        record['entity_type'] = 'relation'
                        record['entity_name'] = f"{record.get('person1', '')} ↔ {record.get('person2', '')}"
                    else:
                        record['entity_type'] = 'unknown'
                        record['entity_name'] = record.get('person1', 'N/A')
                
                cancelled_items.append(render_history_item(record, show_cancel_button=False))
            
            cancelled_display = html.Div(cancelled_items) if cancelled_items else html.P("Aucune modification annulée", className='text-muted')
            
            # Clear the store and return updated lists
            return recent_display, cancelled_display, new_version, None
        else:
            print(f"   ❌ {message}")
            return no_update, no_update, no_update, None
            
    except Exception as e:
        print(f"   ❌ ERROR cancelling action: {e}")
        import traceback
        traceback.print_exc()
        return no_update, no_update, no_update, None

# ============================================================================
# CALLBACKS - MODALS ADD RELATION
# ============================================================================

@app.callback(
    [Output('modal-add-relation', 'is_open'),
     Output('dropdown-add-rel-p1', 'value'),
     Output('dropdown-add-rel-type', 'value'),
     Output('dropdown-add-rel-p2', 'value'),
     Output('add-relation-status', 'children'),
     Output('data-version', 'data', allow_duplicate=True)],
    [Input('btn-add-relation', 'n_clicks'),
     Input('btn-cancel-add-relation', 'n_clicks'),
     Input('btn-submit-add-relation', 'n_clicks')],
    [State('modal-add-relation', 'is_open'),
     State('dropdown-add-rel-p1', 'value'),
     State('dropdown-add-rel-type', 'value'),
     State('dropdown-add-rel-p2', 'value'),
     State('data-version', 'data')],
    prevent_initial_call=True
)
def toggle_and_submit_add_relation(open_clicks, cancel_clicks, submit_clicks, is_open, p1_id, rel_type, p2_id, current_version):
    """Toggle modal AND handle submit (with smart inline person creation)"""
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    triggered_id = ctx.triggered_id
    
    # Safety check: verify the button that triggered has actually been clicked (n_clicks > 0)
    if triggered_id == 'btn-add-relation' and (not open_clicks or open_clicks == 0):
        print(f"⚠️ [ADMIN] Spurious trigger on btn-add-relation (n_clicks={open_clicks})")
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    if triggered_id == 'btn-cancel-add-relation' and (not cancel_clicks or cancel_clicks == 0):
        print(f"⚠️ [ADMIN] Spurious trigger on btn-cancel-add-relation (n_clicks={cancel_clicks})")
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    if triggered_id == 'btn-submit-add-relation' and (not submit_clicks or submit_clicks == 0):
        print(f"⚠️ [ADMIN] Spurious trigger on btn-submit-add-relation (n_clicks={submit_clicks})")
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    print(f"✅ [ADMIN] ADD RELATION triggered: {triggered_id}")
    
    # Open modal
    if triggered_id == 'btn-add-relation':
        print(f"   → Opening modal")
        return True, None, None, None, None, no_update
    
    # Cancel
    if triggered_id == 'btn-cancel-add-relation':
        print(f"   → Canceling")
        return False, None, None, None, None, no_update
    
    # Submit
    if triggered_id == 'btn-submit-add-relation':
        print(f"   → Submitting: p1_id={p1_id}, rel_type={rel_type}, p2_id={p2_id}")
        
        try:
            # === ÉTAPE 1: Check if Person 1 needs to be created ===
            if p1_id and str(p1_id).startswith("__CREATE__"):
                raw_name = str(p1_id).replace("__CREATE__", "").strip()
                # Sanitize using the same rules as the repository so lookup matches
                clean_name = Validator.sanitize_name(raw_name)
                print(f"   → Creating new person 1: raw='{raw_name}' clean='{clean_name}'")

                try:
                    # Create using the cleaned name (repository will also sanitize/validate)
                    success, msg = person_repository.create(
                        name=clean_name,
                        gender=None,
                        sexual_orientation=None
                    )
                    if not success:
                        print(f"   ❌ Failed to create Person 1: {msg}")
                        return True, None, rel_type, p2_id, dbc.Alert(f"Error creating person '{clean_name}': {msg}", color='danger', duration=3000), no_update

                    print(f"   ✅ Person 1 created in database: {clean_name}")

                    # Get the created person's ID using read_by_name (exact match on sanitized name)
                    p1_obj = person_repository.read_by_name(clean_name)
                    if p1_obj:
                        p1_id = p1_obj['id']
                        print(f"   ✅ Person 1 retrieved with ID: {p1_id}")
                    else:
                        print(f"   ❌ ERROR: Person 1 was created but couldn't be retrieved (name mismatch)!")
                        return True, None, rel_type, p2_id, dbc.Alert(f"Error: Could not retrieve created person '{clean_name}'", color='danger', duration=3000), no_update
                except Exception as e:
                    print(f"   ❌ ERROR creating Person 1: {e}")
                    return True, None, rel_type, p2_id, dbc.Alert(f"Error creating person: {str(e)}", color='danger', duration=3000), no_update
            
            # === ÉTAPE 2: Check if Person 2 needs to be created ===
            if p2_id and str(p2_id).startswith("__CREATE__"):
                raw_name = str(p2_id).replace("__CREATE__", "").strip()
                clean_name = Validator.sanitize_name(raw_name)
                print(f"   → Creating new person 2: raw='{raw_name}' clean='{clean_name}'")

                try:
                    success, msg = person_repository.create(
                        name=clean_name,
                        gender=None,
                        sexual_orientation=None
                    )
                    if not success:
                        print(f"   ❌ Failed to create Person 2: {msg}")
                        return True, p1_id, rel_type, None, dbc.Alert(f"Error creating person '{clean_name}': {msg}", color='danger', duration=3000), no_update

                    print(f"   ✅ Person 2 created in database: {clean_name}")

                    p2_obj = person_repository.read_by_name(clean_name)
                    if p2_obj:
                        p2_id = p2_obj['id']
                        print(f"   ✅ Person 2 retrieved with ID: {p2_id}")
                    else:
                        print(f"   ❌ ERROR: Person 2 was created but couldn't be retrieved (name mismatch)!")
                        return True, p1_id, rel_type, None, dbc.Alert(f"Error: Could not retrieve created person '{clean_name}'", color='danger', duration=3000), no_update
                except Exception as e:
                    print(f"   ❌ ERROR creating Person 2: {e}")
                    return True, p1_id, rel_type, None, dbc.Alert(f"Error creating person: {str(e)}", color='danger', duration=3000), no_update
            
            # === ÉTAPE 3: Validation ===
            # Check if all required fields are present (None or empty, but 0 is valid!)
            if p1_id is None or p2_id is None or rel_type is None:
                missing = []
                if p1_id is None:
                    missing.append("Person 1")
                if p2_id is None:
                    missing.append("Person 2")
                if rel_type is None:
                    missing.append("Relation Type")
                print(f"   ❌ Missing fields: {missing}")
                return True, p1_id, rel_type, p2_id, dbc.Alert(f"Missing required fields: {', '.join(missing)}", color='warning', duration=4000), no_update
            
            if p1_id == p2_id:
                print(f"   ❌ Self-relation!")
                return True, p1_id, rel_type, p2_id, dbc.Alert("Cannot create self-relation", color='warning', duration=3000), no_update
            
            # === ÉTAPE 4: Récupérer les noms des personnes ===
            p1 = person_repository.read(p1_id)
            p2 = person_repository.read(p2_id)
            
            if not p1 or not p2:
                print(f"   ❌ Person not found!")
                return True, p1_id, rel_type, p2_id, dbc.Alert("Person not found", color='danger', duration=3000), no_update
            
            # === ÉTAPE 5: Créer la relation ===
            print(f"   → Creating relation: {p1['name']} - {p2['name']}")
            # Utilise RelationRepository.create() qui attend des NOMS (str), pas des IDs
            relation_repository.create(
                person1=p1['name'],
                person2=p2['name'],
                relation_type=rel_type
            )
            
            print(f"   → Recording history...")
            history_service.record_action(
                action_type='ADD',
                person1=p1['name'],
                person2=p2['name'],
                relation_type=rel_type
            )
            
            print(f"   → Invalidating cache...")
            graph_builder.clear_cache()
            
            # Bump version to trigger graph refresh
            new_version = (current_version or 0) + 1
            print(f"   ✅ Success! New data version: {new_version}")
            
            # Close modal and reset form
            return False, None, None, None, dbc.Alert("Relation added successfully!", color='success', duration=3000), new_version
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            return True, p1_id, rel_type, p2_id, dbc.Alert(f"Error: {str(e)}", color='danger', duration=3000), no_update
    
    # Fallback
    return False, None, None, None, None, no_update

# ============================================================================
# CALLBACKS - INITIALIZE DROPDOWN OPTIONS ON MODAL OPEN
# ============================================================================

# SUPPRIMÉ - Causait conflit avec les callbacks existants

# ============================================================================
# SMART DROPDOWN OPTIONS - Person 1 (with "Create new" option)
# ============================================================================
@app.callback(
    Output('dropdown-add-rel-p1', 'options'),
    [Input('dropdown-add-rel-p1', 'search_value'),
     Input('modal-add-relation', 'is_open')],
    [State('dropdown-add-rel-p1', 'value')],
    prevent_initial_call=False
)
def populate_p1_options(search_value, is_open, current_value):
    """Populate Person 1 dropdown with existing persons + 'Create new' option if needed"""
    if not is_open:
        raise PreventUpdate
    
    persons = person_repository.read_all()
    options = [{'label': p['name'], 'value': p['id']} for p in persons]
    
    # If search value and no exact match → add "Create new" option
    if search_value and len(search_value.strip()) >= 2:
        existing_names = [p['name'].lower() for p in persons]
        if search_value.strip().lower() not in existing_names:
            options.insert(0, {
                'label': f"➕ Create new: {search_value.strip()}",
                'value': f"__CREATE__{search_value.strip()}"
            })
    
    # IMPORTANT: If current_value starts with __CREATE__, keep it in options
    # This ensures the option stays visible after selection
    if current_value and str(current_value).startswith("__CREATE__"):
        name = str(current_value).replace("__CREATE__", "")
        # Check if this option is already in the list
        if not any(opt['value'] == current_value for opt in options):
            options.insert(0, {
                'label': f"➕ Create new: {name}",
                'value': current_value
            })
    
    return options

# Smart indicator for Person 1
@app.callback(
    Output('person-1-indicator', 'children'),
    Input('dropdown-add-rel-p1', 'value'),
    prevent_initial_call=True
)
def update_p1_indicator(value):
    """Show indicator based on Person 1 selection"""
    if not value:
        return None
    
    if str(value).startswith("__CREATE__"):
        name = str(value).replace("__CREATE__", "")
        return html.Div([
            html.I(className="fas fa-plus-circle", style={'color': '#28a745', 'marginRight': '5px'}),
            html.Span(f"Will create new person: {name}", style={'color': '#28a745', 'fontSize': '13px', 'fontWeight': '500'})
        ])
    else:
        return html.Div([
            html.I(className="fas fa-check-circle", style={'color': '#667eea', 'marginRight': '5px'}),
            html.Span("Existing person selected", style={'color': '#667eea', 'fontSize': '13px', 'fontWeight': '500'})
        ])

# ============================================================================
# SMART DROPDOWN OPTIONS - Person 2 (with "Create new" option)
# ============================================================================
@app.callback(
    Output('dropdown-add-rel-p2', 'options'),
    [Input('dropdown-add-rel-p2', 'search_value'),
     Input('modal-add-relation', 'is_open')],
    [State('dropdown-add-rel-p2', 'value')],
    prevent_initial_call=False
)
def populate_p2_options(search_value, is_open, current_value):
    """Populate Person 2 dropdown with existing persons + 'Create new' option if needed"""
    if not is_open:
        raise PreventUpdate
    
    persons = person_repository.read_all()
    options = [{'label': p['name'], 'value': p['id']} for p in persons]
    
    # If search value and no exact match → add "Create new" option
    if search_value and len(search_value.strip()) >= 2:
        existing_names = [p['name'].lower() for p in persons]
        if search_value.strip().lower() not in existing_names:
            options.insert(0, {
                'label': f"➕ Create new: {search_value.strip()}",
                'value': f"__CREATE__{search_value.strip()}"
            })
    
    # IMPORTANT: If current_value starts with __CREATE__, keep it in options
    # This ensures the option stays visible after selection
    if current_value and str(current_value).startswith("__CREATE__"):
        name = str(current_value).replace("__CREATE__", "")
        # Check if this option is already in the list
        if not any(opt['value'] == current_value for opt in options):
            options.insert(0, {
                'label': f"➕ Create new: {name}",
                'value': current_value
            })
    
    return options

# Smart indicator for Person 2
@app.callback(
    Output('person-2-indicator', 'children'),
    Input('dropdown-add-rel-p2', 'value'),
    prevent_initial_call=True
)
def update_p2_indicator(value):
    """Show indicator based on Person 2 selection"""
    if not value:
        return None
    
    if str(value).startswith("__CREATE__"):
        name = str(value).replace("__CREATE__", "")
        return html.Div([
            html.I(className="fas fa-plus-circle", style={'color': '#28a745', 'marginRight': '5px'}),
            html.Span(f"Will create new person: {name}", style={'color': '#28a745', 'fontSize': '13px', 'fontWeight': '500'})
        ])
    else:
        return html.Div([
            html.I(className="fas fa-check-circle", style={'color': '#667eea', 'marginRight': '5px'}),
            html.Span("Existing person selected", style={'color': '#667eea', 'fontSize': '13px', 'fontWeight': '500'})
        ])


# ============================================================================
# CALLBACKS - MANAGE RELATIONS (Update/Delete)
# ============================================================================

# Open/close Manage Relations modal + populate list
@app.callback(
    [Output('modal-update-relation', 'is_open'),
     Output('relations-list-container', 'children'),
     Output('manage-relation-status', 'children')],
    [Input('btn-update-relation', 'n_clicks'),
     Input('btn-close-update-relation', 'n_clicks'),
     Input('data-version', 'data')],  # Refresh when data changes
    State('modal-update-relation', 'is_open'),
    prevent_initial_call=True
)
def toggle_manage_relations_modal(n_open, n_close, data_version, is_open):
    """Handle Manage Relations modal"""
    triggered_id = ctx.triggered_id
    print(f"� [MANAGE RELATIONS] triggered_id={triggered_id}")
    
    # Close modal
    if triggered_id == 'btn-close-update-relation':
        print(f"   → Closing modal")
        return False, [], None
    
    # Open modal OR refresh list
    if triggered_id == 'btn-update-relation' or (triggered_id == 'data-version' and is_open):
        print(f"   → Opening/Refreshing modal")
        
        # Get all unique relations (deduplicated)
        # read_all returns List[Tuple[str, str, int]] = (person1, person2, relation_type)
        all_relations = relation_repository.read_all(deduplicate=False)
        
        # Deduplicate manually to keep only one direction
        seen = set()
        unique_relations = []
        for rel_tuple in all_relations:
            person1, person2, rel_type = rel_tuple  # Unpack tuple
            # Create a sorted tuple to identify unique pairs
            pair = tuple(sorted([person1, person2]))
            if pair not in seen:
                seen.add(pair)
                unique_relations.append({
                    'person1': person1,
                    'person2': person2,
                    'type': rel_type
                })
        
        print(f"   → Found {len(unique_relations)} unique relations")
        
        if not unique_relations:
            return True, [
                dbc.Alert([
                    html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
                    "No relations found. Add some relations first!"
                ], color='warning')
            ], None
        
        # Build the list of relation cards
        relation_cards = []
        for i, rel in enumerate(unique_relations):
            relation_type_label = RELATION_TYPES.get(rel['type'], 'Unknown')
            
            card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        # Left: Persons and type
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-users", style={'color': '#667eea', 'marginRight': '10px', 'fontSize': '20px'}),
                                html.Span(rel['person1'], style={'fontSize': '16px', 'fontWeight': 'bold'}),
                                html.Span(" ↔ ", style={'margin': '0 10px', 'color': '#999'}),
                                html.Span(rel['person2'], style={'fontSize': '16px', 'fontWeight': 'bold'}),
                            ], style={'marginBottom': '8px'}),
                            
                            html.Div([
                                html.I(className="fas fa-heart", style={'color': '#e74c3c', 'marginRight': '8px'}),
                                html.Span(f"Type: {relation_type_label}", style={'fontSize': '14px', 'color': '#666'})
                            ])
                        ], width=8),
                        
                        # Right: Action buttons
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className="fas fa-edit", style={'marginRight': '5px'}),
                                    "Edit"
                                ], id={'type': 'btn-edit-rel', 'index': i}, color='primary', size='sm', outline=True),
                                
                                dbc.Button([
                                    html.I(className="fas fa-trash", style={'marginRight': '5px'}),
                                    "Delete"
                                ], id={'type': 'btn-delete-rel', 'index': i}, color='danger', size='sm', outline=True)
                            ], style={'float': 'right'})
                        ], width=4, className='text-end')
                    ])
                ])
            ], style={
                'marginBottom': '10px',
                'borderLeft': '4px solid #667eea',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
            
            relation_cards.append(card)
        
        return True, relation_cards, None
    
    return no_update, no_update, no_update

# Handle Edit button click - open Edit modal
@app.callback(
    [Output('modal-edit-relation', 'is_open'),
     Output('edit-relation-info', 'children'),
     Output('dropdown-edit-relation-type', 'value'),
     Output('selected-relation-store', 'data')],
    [Input({'type': 'btn-edit-rel', 'index': ALL}, 'n_clicks'),
     Input('btn-cancel-edit-relation', 'n_clicks'),
     Input('btn-submit-edit-relation', 'n_clicks')],
    [State('dropdown-edit-relation-type', 'value'),
     State('selected-relation-store', 'data'),
     State('data-version', 'data')],
    prevent_initial_call=True
)
def handle_edit_relation(edit_clicks, cancel_clicks, submit_clicks, new_type, selected_rel_data, current_version):
    """Handle edit relation modal"""
    triggered_id = ctx.triggered_id
    
    # Check if triggered_id is None or empty - don't process
    if not triggered_id:
        raise PreventUpdate
    
    print(f"✏️ [EDIT RELATION] triggered_id={triggered_id}")
    
    # Cancel
    if triggered_id == 'btn-cancel-edit-relation':
        return False, None, None, None
    
    # Submit
    if triggered_id == 'btn-submit-edit-relation':
        if not selected_rel_data or new_type is None:
            print(f"   ❌ Missing data!")
            return False, None, None, None
        
        try:
            print(f"   → Updating: {selected_rel_data['person1']} - {selected_rel_data['person2']} to type {new_type}")
            
            # Delete old relation (both directions due to symmetry)
            relation_repository.delete(selected_rel_data['person1'], selected_rel_data['person2'])
            
            # Create new relation with new type
            relation_repository.create(
                person1=selected_rel_data['person1'],
                person2=selected_rel_data['person2'],
                relation_type=new_type
            )
            
            history_service.record_action(
                action_type='UPDATE',
                person1=selected_rel_data['person1'],
                person2=selected_rel_data['person2'],
                relation_type=new_type
            )
            
            graph_builder.clear_cache()
            print(f"   ✅ Relation updated!")
            
            return False, None, None, None
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            return False, None, None, None
    
    # Open edit modal (when clicking Edit button)
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'btn-edit-rel':
        idx = triggered_id['index']
        
        # Check if this button was actually clicked (not just triggered by ALL)
        # edit_clicks is a list, check if the clicked button has a value > 0
        if not edit_clicks or idx >= len(edit_clicks) or not edit_clicks[idx]:
            raise PreventUpdate
        
        print(f"   → Opening edit modal for relation {idx}")
        
        # Get all unique relations
        all_relations = relation_repository.read_all(deduplicate=False)
        seen = set()
        unique_relations = []
        for rel_tuple in all_relations:
            person1, person2, rel_type = rel_tuple  # Unpack tuple
            pair = tuple(sorted([person1, person2]))
            if pair not in seen:
                seen.add(pair)
                unique_relations.append({
                    'person1': person1,
                    'person2': person2,
                    'type': rel_type
                })
        
        if idx >= len(unique_relations):
            return False, None, None, None
        
        rel = unique_relations[idx]
        
        info = dbc.Alert([
            html.I(className="fas fa-users", style={'marginRight': '8px', 'fontSize': '18px'}),
            html.Strong(f"{rel['person1']} ↔ {rel['person2']}", style={'fontSize': '16px'}),
            html.Br(),
            html.Span(f"Current type: {RELATION_TYPES.get(rel['type'], 'Unknown')}", style={'fontSize': '14px', 'color': '#666'})
        ], color='light', style={'borderLeft': '4px solid #667eea'})
        
        # Store relation data for later use
        rel_data = {
            'person1': rel['person1'],
            'person2': rel['person2'],
            'current_type': rel['type']
        }
        
        return True, info, rel['type'], rel_data
    
    return no_update, no_update, no_update, no_update

# Handle Delete button click
@app.callback(
    [Output('manage-relation-status', 'children', allow_duplicate=True),
     Output('data-version', 'data', allow_duplicate=True)],
    Input({'type': 'btn-delete-rel', 'index': ALL}, 'n_clicks'),
    [State('data-version', 'data')],
    prevent_initial_call=True
)
def handle_delete_relation(delete_clicks, current_version):
    """Handle delete relation"""
    triggered_id = ctx.triggered_id
    
    if not isinstance(triggered_id, dict) or triggered_id.get('type') != 'btn-delete-rel':
        raise PreventUpdate
    
    idx = triggered_id['index']
    
    # Check if this button was actually clicked (not just triggered by ALL)
    if not delete_clicks or idx >= len(delete_clicks) or not delete_clicks[idx]:
        raise PreventUpdate
    
    print(f"🗑️ [DELETE RELATION] index={idx}")
    
    try:
        # Get all unique relations
        all_relations = relation_repository.read_all(deduplicate=False)
        seen = set()
        unique_relations = []
        for rel_tuple in all_relations:
            person1, person2, rel_type = rel_tuple  # Unpack tuple
            pair = tuple(sorted([person1, person2]))
            if pair not in seen:
                seen.add(pair)
                unique_relations.append({
                    'person1': person1,
                    'person2': person2,
                    'type': rel_type
                })
        
        if idx >= len(unique_relations):
            return dbc.Alert("Relation not found!", color='danger', duration=3000), no_update
        
        rel = unique_relations[idx]
        
        print(f"   → Deleting: {rel['person1']} - {rel['person2']}")
        
        # Delete relation (both directions)
        relation_repository.delete(rel['person1'], rel['person2'])
        
        history_service.record_action(
            action_type='DELETE',
            person1=rel['person1'],
            person2=rel['person2'],
            relation_type=rel['type']
        )
        
        graph_builder.clear_cache()
        
        # Bump version
        new_version = (current_version or 0) + 1
        print(f"   ✅ Relation deleted! New version: {new_version}")
        
        return dbc.Alert(f"Relation between {rel['person1']} and {rel['person2']} deleted!", color='success', duration=3000), new_version
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return dbc.Alert(f"Error: {str(e)}", color='danger', duration=3000), no_update


# ============================================================================
# ENREGISTREMENT DES CALLBACKS CRUD PERSONNES
# ============================================================================

# Note: person_callbacks.py utilise des pattern IDs différents
# Pour app_v2, on crée des callbacks compatibles directement ici

@app.callback(
    [Output('modal-edit-person', 'is_open'),
     Output('dropdown-edit-person-select', 'options')],
    [Input('btn-edit-person', 'n_clicks'),
     Input('btn-cancel-edit-person', 'n_clicks'),
     Input('btn-submit-edit-person', 'n_clicks')],
    State('modal-edit-person', 'is_open'),
    prevent_initial_call=True
)
def toggle_edit_person_modal_v2(open_clicks, cancel_clicks, submit_clicks, is_open):
    """Toggle edit person modal and populate dropdown"""
    if not ctx.triggered:
        return no_update, no_update
    
    triggered_id = ctx.triggered_id
    print(f"✅ [ADMIN] Edit Person Modal: {triggered_id}")
    
    # Vérification des n_clicks
    if triggered_id == 'btn-edit-person' and (not open_clicks or open_clicks < 1):
        print(f"⚠️ Spurious trigger on btn-edit-person")
        return no_update, no_update
    
    if triggered_id == 'btn-cancel-edit-person' and (not cancel_clicks or cancel_clicks < 1):
        print(f"⚠️ Spurious trigger on btn-cancel-edit-person")
        return no_update, no_update
    
    if triggered_id == 'btn-submit-edit-person' and (not submit_clicks or submit_clicks < 1):
        print(f"⚠️ Spurious trigger on btn-submit-edit-person")
        return no_update, no_update
    
    # Ouvrir le modal
    if triggered_id == 'btn-edit-person':
        print(f"   → Opening Edit Person modal")
        persons = person_repository.read_all()
        options = [{'label': p['name'], 'value': p['id']} for p in persons]
        return True, options
    
    # Fermer le modal
    if triggered_id in ['btn-cancel-edit-person', 'btn-submit-edit-person']:
        print(f"   → Closing Edit Person modal")
        return False, []
    
    return no_update, no_update

@app.callback(
    Output('input-edit-person-name', 'value'),
    Input('dropdown-edit-person-select', 'value'),
    prevent_initial_call=True
)
def load_person_data_for_edit(person_id):
    """Load person data when selected in edit modal"""
    if not person_id:
        raise PreventUpdate
    
    print(f"✅ [ADMIN] Loading person data for edit: ID={person_id}")
    
    person = person_repository.read(person_id)
    if person:
        print(f"   → Person found: {person.get('name')}")
        return person.get('name', '')
    
    print(f"   ❌ Person not found")
    return ''

@app.callback(
    [Output('modal-edit-person', 'is_open', allow_duplicate=True),
     Output('data-version', 'data', allow_duplicate=True)],
    Input('btn-submit-edit-person', 'n_clicks'),
    [State('dropdown-edit-person-select', 'value'),
     State('input-edit-person-name', 'value'),
     State('data-version', 'data')],
    prevent_initial_call=True
)
def submit_edit_person(n_clicks, person_id, new_name, current_version):
    """Submit person edit using PersonRepository"""
    if not ctx.triggered or not n_clicks or n_clicks < 1:
        return no_update, no_update
    
    print(f"✅ [ADMIN] SUBMIT EDIT PERSON: n_clicks={n_clicks}, person_id={person_id}, new_name={new_name}")
    
    if not person_id or not new_name:
        print(f"   ❌ Missing person_id or new_name")
        return False, no_update
    
    try:
        # Get old value before updating
        old_person = person_repository.read(person_id)
        old_name = old_person['name'] if old_person else None
        
        # Update using repository (only name, keep existing gender/orientation)
        print(f"   → Updating person ID {person_id} from '{old_name}' to '{new_name.strip()}'")
        success, message = person_repository.update(
            person_id=person_id,
            name=new_name.strip()
        )
        
        print(f"   → Update result: {success}, message: {message}")
        
        if success:
            # Record in history with old and new values
            history_service.record_action(
                action_type='UPDATE_PERSON',
                person1=new_name.strip(),
                entity_type='person',
                entity_id=person_id,
                entity_name=new_name.strip(),
                old_value=old_name,
                new_value=new_name.strip()
            )
            print(f"   ✅ History recorded (old: '{old_name}' -> new: '{new_name.strip()}')")
            
            # Invalidate graph cache
            graph_builder.clear_cache()
            print(f"   ✅ Graph cache cleared")
            
            # Bump version
            new_version = (current_version or 0) + 1
            print(f"   ✅ Person updated! New data version: {new_version}")
            return False, new_version  # Close modal
        else:
            print(f"   ❌ Update failed: {message}")
            return False, no_update  # Close modal anyway
        
    except Exception as e:
        print(f"   ❌ Exception during update: {e}")
        import traceback
        traceback.print_exc()
        return False, no_update  # Close modal
        print(f"Error updating person: {e}")
        return True, no_update  # Keep modal open

@app.callback(
    Output('search-results-relations', 'children'),
    Input('input-search-person-relations', 'value'),
    prevent_initial_call=True
)
def search_person_relations(search_query):
    """Search for persons and display their relations"""
    if not search_query or len(search_query.strip()) < 2:
        return html.Div([
            html.I(className="fas fa-info-circle", style={'marginRight': '8px', 'color': '#6c757d'}),
            "Type at least 2 characters to search..."
        ], style={'color': '#6c757d', 'fontSize': '14px', 'padding': '10px'})
    
    try:
        search_query = search_query.strip().lower()
        
        # Get all persons
        all_persons = person_repository.read_all()
        
        # Filter persons matching the search
        matching_persons = [
            p for p in all_persons 
            if search_query in p['name'].lower()
        ]
        
        if not matching_persons:
            return html.Div([
                html.I(className="fas fa-search", style={'marginRight': '8px', 'color': '#ffc107'}),
                f"No person found matching '{search_query}'"
            ], style={'color': '#856404', 'fontSize': '14px', 'padding': '10px', 'backgroundColor': '#fff3cd', 'borderRadius': '4px'})
        
        # Get all relations
        all_relations = relation_repository.read_all(deduplicate=False)
        
        # Build results
        results = []
        for person in matching_persons[:5]:  # Limit to 5 results
            person_name = person['name']
            person_id = person['id']
            
            # Find relations for this person
            person_relations = [
                (p1, p2, rel_type) for p1, p2, rel_type in all_relations
                if p1.lower() == person_name.lower() or p2.lower() == person_name.lower()
            ]
            
            # Create person card
            relation_items = []
            if person_relations:
                for p1, p2, rel_type in person_relations[:10]:  # Limit to 10 relations
                    # Determine the other person
                    other_person = p2 if p1.lower() == person_name.lower() else p1
                    
                    # Format relation with emoji
                    relation_emoji = {
                        'friends': '👥',
                        'family': '👨‍👩‍👧‍👦',
                        'colleagues': '💼',
                        'romantic': '💕',
                        'other': '🔗'
                    }.get(rel_type, '🔗')
                    
                    relation_items.append(
                        html.Div([
                            html.Span(relation_emoji, style={'marginRight': '6px'}),
                            html.Span(rel_type.capitalize(), style={
                                'fontWeight': 'bold',
                                'color': '#667eea',
                                'marginRight': '6px'
                            }),
                            html.Span('with', style={'marginRight': '6px', 'color': '#6c757d'}),
                            html.Span(other_person, style={'fontWeight': '500'})
                        ], style={'padding': '4px 0', 'fontSize': '13px'})
                    )
                
                if len(person_relations) > 10:
                    relation_items.append(
                        html.Div(
                            f"... and {len(person_relations) - 10} more relations",
                            style={'fontSize': '12px', 'color': '#6c757d', 'fontStyle': 'italic', 'padding': '4px 0'}
                        )
                    )
            else:
                relation_items.append(
                    html.Div([
                        html.I(className="fas fa-unlink", style={'marginRight': '6px'}),
                        "No relations found"
                    ], style={'color': '#6c757d', 'fontSize': '13px', 'padding': '4px 0'})
                )
            
            results.append(
                html.Div([
                    html.Div([
                        html.I(className="fas fa-user", style={'marginRight': '8px', 'color': '#667eea'}),
                        html.Strong(person_name, style={'fontSize': '15px', 'color': '#2c3e50'}),
                        html.Span(
                            f" ({len(person_relations)} relation{'s' if len(person_relations) != 1 else ''})",
                            style={'fontSize': '12px', 'color': '#6c757d', 'marginLeft': '6px'}
                        )
                    ], style={'marginBottom': '8px', 'paddingBottom': '8px', 'borderBottom': '1px solid #dee2e6'}),
                    html.Div(relation_items, style={'paddingLeft': '24px'})
                ], style={
                    'padding': '12px',
                    'marginBottom': '10px',
                    'backgroundColor': 'white',
                    'borderRadius': '6px',
                    'border': '1px solid #e0e0e0',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.05)'
                })
            )
        
        if len(matching_persons) > 5:
            results.append(
                html.Div(
                    f"+ {len(matching_persons) - 5} more persons found. Refine your search for better results.",
                    style={
                        'fontSize': '13px',
                        'color': '#6c757d',
                        'fontStyle': 'italic',
                        'padding': '8px',
                        'textAlign': 'center'
                    }
                )
            )
        
        return html.Div(results)
        
    except Exception as e:
        print(f"❌ Error searching relations: {e}")
        import traceback
        traceback.print_exc()
        return html.Div([
            html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px', 'color': '#dc3545'}),
            f"Error: {str(e)}"
        ], style={'color': '#721c24', 'fontSize': '14px', 'padding': '10px', 'backgroundColor': '#f8d7da', 'borderRadius': '4px'})

@app.callback(
    [Output('modal-merge-persons', 'is_open'),
     Output('dropdown-merge-source', 'options'),
     Output('dropdown-merge-target', 'options'),
     Output('dropdown-merge-source', 'value'),
     Output('dropdown-merge-target', 'value'),
     Output('data-version', 'data', allow_duplicate=True)],
    [Input('btn-merge-persons', 'n_clicks'),
     Input('btn-cancel-merge-persons', 'n_clicks'),
     Input('btn-submit-merge-persons', 'n_clicks')],
    [State('modal-merge-persons', 'is_open'),
     State('dropdown-merge-source', 'value'),
     State('dropdown-merge-target', 'value'),
     State('data-version', 'data')],
    prevent_initial_call=True
)
def toggle_and_submit_merge_persons(open_clicks, cancel_clicks, submit_clicks, is_open, source_id, target_id, current_version):
    """Toggle merge modal AND handle submit"""
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    triggered_id = ctx.triggered_id
    
    # Safety check: verify the button that triggered has actually been clicked (n_clicks > 0)
    if triggered_id == 'btn-merge-persons' and (not open_clicks or open_clicks == 0):
        print(f"⚠️ [MERGE] Spurious trigger on btn-merge-persons (n_clicks={open_clicks})")
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    if triggered_id == 'btn-cancel-merge-persons' and (not cancel_clicks or cancel_clicks == 0):
        print(f"⚠️ [MERGE] Spurious trigger on btn-cancel-merge-persons (n_clicks={cancel_clicks})")
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    if triggered_id == 'btn-submit-merge-persons' and (not submit_clicks or submit_clicks == 0):
        print(f"⚠️ [MERGE] Spurious trigger on btn-submit-merge-persons (n_clicks={submit_clicks})")
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    print(f"🔍 [MERGE PERSONS] triggered_id={triggered_id}")
    
    # Open modal
    if triggered_id == 'btn-merge-persons':
        print(f"   → Opening merge modal")
        persons = person_repository.read_all()
        options = [{'label': p['name'], 'value': p['id']} for p in persons]
        return True, options, options, None, None, no_update
    
    # Cancel
    if triggered_id == 'btn-cancel-merge-persons':
        print(f"   → Canceling merge")
        return False, [], [], None, None, no_update
    
    # Submit
    if triggered_id == 'btn-submit-merge-persons':
        print(f"   → Submitting merge: source={source_id}, target={target_id}")
        
        if not source_id or not target_id:
            print(f"   ❌ Missing source or target!")
            return True, [], [], source_id, target_id, no_update
        
        if source_id == target_id:
            print(f"   ❌ Cannot merge person with themselves!")
            return True, [], [], source_id, target_id, no_update
        
        try:
            # Get names BEFORE merge (source will be deleted)
            source = person_repository.read(source_id)
            target = person_repository.read(target_id)
            
            if not source or not target:
                print(f"   ❌ Person not found!")
                return True, [], [], source_id, target_id, no_update
            
            source_name = source['name']
            target_name = target['name']
            
            print(f"   → Merging {source_name} → {target_name}")
            
            # Merge using repository
            success, message = person_repository.merge(source_id, target_id)
            
            if success:
                print(f"   → Recording history...")
                # Record in history
                history_service.record_action(
                    action_type='MERGE_PERSON',
                    person1=source_name,
                    person2=target_name
                )
                
                print(f"   → Invalidating cache...")
                # Invalidate graph cache
                graph_builder.clear_cache()
                
                # Bump version
                new_version = (current_version or 0) + 1
                print(f"   ✅ Merge successful! New data version: {new_version}")
                return False, [], [], None, None, new_version  # Close modal
            else:
                print(f"   ❌ Merge failed: {message}")
                return True, [], [], source_id, target_id, no_update  # Keep modal open
                
        except Exception as e:
            print(f"   ❌ Exception during merge: {e}")
            import traceback
            traceback.print_exc()
            return True, [], [], source_id, target_id, no_update  # Keep modal open
    
    # Fallback
    return False, [], [], None, None, no_update

@app.callback(
    Output('merge-preview-info', 'children'),
    [Input('dropdown-merge-source', 'value'),
     Input('dropdown-merge-target', 'value')],
    prevent_initial_call=True
)
def preview_merge(source_id, target_id):
    """Show merge preview"""
    if not source_id or not target_id:
        return None
    
    if source_id == target_id:
        return dbc.Alert("⚠️ Cannot merge person with themselves!", color='warning')
    
    source = person_repository.read(source_id)
    target = person_repository.read(target_id)
    
    if not source or not target:
        return None
    
    return dbc.Alert([
        html.H6("Merge Preview:", className='mb-2'),
        html.P([
            html.Strong(f"{source['name']}"), 
            " → ",
            html.Strong(f"{target['name']}")
        ]),
        html.Small("All relations from source will be transferred to target, then source will be deleted.")
    ], color='info')

@app.callback(
    [Output('modal-delete-person', 'is_open'),
     Output('dropdown-delete-person-select', 'options')],
    [Input('btn-delete-person', 'n_clicks'),
     Input('btn-cancel-delete-person', 'n_clicks'),
     Input('btn-submit-delete-person', 'n_clicks')],
    State('modal-delete-person', 'is_open'),
    prevent_initial_call=True
)
def toggle_delete_person_modal_v2(open_clicks, cancel_clicks, submit_clicks, is_open):
    """Toggle delete person modal and populate dropdown"""
    if ctx.triggered_id == 'btn-delete-person':
        persons = person_repository.read_all()
        options = [{'label': p['name'], 'value': p['id']} for p in persons]
        return True, options
    return False, []

@app.callback(
    Output('delete-person-info', 'children'),
    Input('dropdown-delete-person-select', 'value'),
    prevent_initial_call=True
)
def show_delete_info(person_id):
    """Show info about person to delete"""
    if not person_id:
        return None
    
    person = person_repository.read(person_id)
    if not person:
        return None
    
    # Count relations
    all_relations = relation_repository.read_all()
    relations = [r for r in all_relations if r[0] == person['name'] or r[1] == person['name']]
    
    return dbc.Alert([
        html.H6(f"Delete: {person['name']}", className='mb-2'),
        html.P(f"This person has {len(relations)} relation(s)."),
        html.Small("⚠️ This action cannot be undone!")
    ], color='warning')

@app.callback(
    [Output('modal-delete-person', 'is_open', allow_duplicate=True),
     Output('data-version', 'data', allow_duplicate=True)],
    Input('btn-submit-delete-person', 'n_clicks'),
    [State('dropdown-delete-person-select', 'value'),
     State('checkbox-delete-cascade', 'value'),
     State('data-version', 'data')],
    prevent_initial_call=True
)
def submit_delete_person(n_clicks, person_id, cascade, current_version):
    """Submit person deletion using PersonRepository"""
    if not person_id:
        raise PreventUpdate
    
    try:
        person = person_repository.read(person_id)
        person_name = person['name'] if person else 'Unknown'
        
        # Delete using repository
        success, message = person_repository.delete(person_id, cascade=bool(cascade))
        
        if success:
            print(f"✅ [ADMIN] Person deleted: {person_name}")
            
            # Record in history
            history_service.record_action(
                action_type='DELETE_PERSON',
                person1=person_name,
                entity_type='person',
                entity_name=person_name
            )
            print(f"   ✅ History recorded")
            
            # Invalidate graph cache
            graph_builder.clear_cache()
            print(f"   ✅ Graph cache cleared")
            
            # Increment version to trigger graph refresh
            new_version = (current_version or 0) + 1
            print(f"   ✅ Data version incremented: {new_version}")
            
            return False, new_version  # Close modal and update version
        else:
            print(f"   ❌ Deletion failed: {message}")
            return False, no_update  # Close modal anyway
        
    except Exception as e:
        print(f"❌ Error deleting person: {e}")
        import traceback
        traceback.print_exc()
        return True, no_update  # Keep modal open on error

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Audit de démarrage
    print("\n" + "="*70)
    print("  🗺️  CENTRALE POTINS MAPS - V2")
    print("="*70)
    
    # Stats
    persons = person_repository.read_all()
    relations = relation_repository.read_all(deduplicate=True)
    unique_relations = len(relations)
    
    print(f"\n  📊 Data: {len(persons)} persons, {unique_relations} relations")
    
    # Vérification symétrie
    asymmetric = symmetry_manager.audit_symmetry()
    if asymmetric:
        print(f"  ⚠️  Warning: {len(asymmetric)} asymmetric relations found")
        print("  🔧 Auto-fixing...")
        fixed_count, messages = symmetry_manager.fix_asymmetric_relations()
        print(f"  ✅ Fixed {fixed_count} asymmetries - all relations now symmetric")
    else:
        print("  ✅ Symmetry: 100% guaranteed")
    
    print(f"\n  🚀 Dashboard: http://localhost:8052")
    print(f"  🏗️  Architecture: Services + Repositories")
    print(f"  💾 Cache: Enabled for performance")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=8052, debug=False)
