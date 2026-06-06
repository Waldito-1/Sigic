"""
PROYECTO SIGIC - SISTEMA INTEGRAL DE GESTIÓN DE INSPECCIONES DE CALIDAD
Arquitectura base: Flask, SQLAlchemy, Bootstrap 5.
Nota: Este script es auto-extraíble. Al ejecutarse, creará la estructura
de carpetas (templates, uploads, static) y los archivos necesarios.
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ==============================================================================
# 1. GENERACIÓN AUTOMÁTICA DE LA ESTRUCTURA DEL PROYECTO (AUTO-SETUP)
# ==============================================================================
def setup_project_structure():
    """Crea los directorios y plantillas HTML necesarios para el proyecto."""
    directories = ['templates', 'static', 'uploads']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    templates = {
        'base.html': """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIGIC - Calidad</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .sidebar { min-height: 100vh; background-color: #2c3e50; color: white; }
        .sidebar a { color: #ecf0f1; text-decoration: none; padding: 15px; display: block; border-bottom: 1px solid #34495e; }
        .sidebar a:hover { background-color: #34495e; }
        .sidebar i { width: 25px; }
        .navbar-top { background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,.08); }
        .fiori-card { 
            border: none; border-radius: 12px; transition: transform 0.2s, box-shadow 0.2s; 
            cursor: pointer; height: 100%; text-align: center; padding: 30px 15px;
            background: linear-gradient(145deg, #ffffff, #f0f0f0);
            box-shadow: 5px 5px 15px #e1e1e1, -5px -5px 15px #ffffff;
        }
        .fiori-card:hover { transform: translateY(-5px); box-shadow: 8px 8px 20px #d1d1d1; }
        .fiori-icon { font-size: 3rem; margin-bottom: 15px; color: #3498db; }
        .timeline { border-left: 3px solid #3498db; padding-left: 20px; margin-left: 20px; }
        .timeline-item { position: relative; margin-bottom: 25px; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .timeline-item::before { content: ''; position: absolute; left: -29px; top: 15px; width: 15px; height: 15px; background: #fff; border: 3px solid #3498db; border-radius: 50%; }
        .status-conforme { border-left: 5px solid #2ecc71; }
        .status-noconforme { border-left: 5px solid #e74c3c; }
    </style>
</head>
<body>
    <div class="d-flex">
        <div class="sidebar p-0 flex-shrink-0" style="width: 250px;">
            <div class="p-4 bg-dark text-center">
                <h4 class="mb-0 text-white fw-bold"><i class="fa-solid fa-shield-check"></i> SIGIC</h4>
                <small class="text-muted">Inspecciones de Calidad</small>
            </div>
            <a href="{{ url_for('dashboard.index') }}"><i class="fa-solid fa-chart-pie"></i> Dashboard</a>
            <a href="{{ url_for('areas.index') }}"><i class="fa-solid fa-industry"></i> Planta (Fiori)</a>
            <a href="{{ url_for('trazabilidad.index') }}"><i class="fa-solid fa-route"></i> Trazabilidad</a>
            {% if current_user.username == 'admin' %}
            <a href="{{ url_for('pedidos.index') }}" style="color: #f39c12;"><i class="fa-solid fa-box-open"></i> Gestión de Pedidos</a>
            <a href="{{ url_for('operarios.index') }}" style="color: #2ecc71;"><i class="fa-solid fa-users-gear"></i> Gestión de Operarios</a>
            {% endif %}
            <a href="{{ url_for('auth.logout') }}" style="margin-top: auto; color: #e74c3c;"><i class="fa-solid fa-right-from-bracket"></i> Cerrar Sesión</a>
        </div>
        <div class="flex-grow-1">
            <nav class="navbar navbar-top navbar-expand-lg px-4 py-3">
                <div class="container-fluid">
                    <span class="navbar-brand mb-0 h1">Sistema Integral de Gestión de Inspecciones</span>
                    <div class="d-flex align-items-center">
                        <!-- Campana de notificaciones (solo áreas con reprocesos) -->
                        <div class="me-3 position-relative" id="notif-wrapper" style="display:none!important;">
                            <button class="btn btn-outline-warning btn-sm position-relative" id="notif-btn" onclick="toggleNotifs()">
                                <i class="fa-solid fa-bell"></i>
                                <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" id="notif-badge">0</span>
                            </button>
                            <div class="dropdown-menu show p-0 shadow" id="notif-dropdown" style="display:none!important; position:absolute; right:0; min-width:300px; z-index:9999;">
                                <div class="p-2 bg-warning text-dark fw-bold small rounded-top">Hijas en reproceso asignadas a tu área</div>
                                <div id="notif-list"></div>
                            </div>
                        </div>
                        <span class="me-3"><i class="fa-solid fa-user-circle"></i> {{ current_user.nombre_completo }}</span>
                        <a href="{{ url_for('auth.logout') }}" class="btn btn-outline-secondary btn-sm">
                            <i class="fa-solid fa-right-from-bracket"></i> Salir
                        </a>
                    </div>
                </div>
            </nav>
            <div class="container-fluid p-4">
                {% with messages = get_flashed_messages(with_categories=true) %}
                  {% if messages %}
                    {% for category, message in messages %}
                      <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                      </div>
                    {% endfor %}
                  {% endif %}
                {% endwith %}
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    // Sistema de notificaciones de reproceso
    // El area_id se inyecta desde la URL actual si estamos en una página de inspección
    // De lo contrario se consulta todas las áreas con reprocesos pendientes
    function toggleNotifs() {
        const dd = document.getElementById('notif-dropdown');
        dd.style.display = dd.style.display === 'none' || dd.style.display === '' ? 'block' : 'none';
    }
    document.addEventListener('click', function(e) {
        if(!document.getElementById('notif-btn').contains(e.target)) {
            const dd = document.getElementById('notif-dropdown');
            if(dd) dd.style.display = 'none';
        }
    });
    function cargarNotificaciones() {
        // Buscar area_id en la URL (ej: /inspeccion/3)
        const match = window.location.pathname.match(/[/]inspeccion[/]([0-9]+)/);
        if(!match) return;
        const areaId = match[1];
        fetch('/api/notificaciones/' + areaId)
            .then(r => r.json())
            .then(data => {
                const wrapper = document.getElementById('notif-wrapper');
                const badge = document.getElementById('notif-badge');
                const list = document.getElementById('notif-list');
                if(data.length > 0) {
                    wrapper.style.display = 'block';
                    badge.textContent = data.length;
                    list.innerHTML = data.map(n =>
                        `<div class="p-2 border-bottom small">
                            <i class="fa-solid fa-arrow-rotate-left text-warning me-1"></i>
                            <strong>${n.hija}</strong> — Pedido ${n.pedido}
                            <span class="badge bg-danger ms-1">${n.veces_reproceso}x reproceso</span>
                        </div>`
                    ).join('');
                }
            }).catch(() => {});
    }
    cargarNotificaciones();
    setInterval(cargarNotificaciones, 30000); // refresca cada 30s
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>""",

        'dashboard.html': """{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Dashboard de Calidad</h2>

<!-- Tarjetas KPI -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-white bg-primary mb-3 shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div><h5 class="card-title mb-0">Inspecciones Hoy</h5><h2 class="mb-0 mt-1">{{ stats.insp_hoy }}</h2></div>
                    <i class="fa-solid fa-clipboard-check fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-danger mb-3 shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div><h5 class="card-title mb-0">NC Abiertas</h5><h2 class="mb-0 mt-1">{{ stats.nc_abiertas }}</h2></div>
                    <i class="fa-solid fa-triangle-exclamation fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success mb-3 shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div><h5 class="card-title mb-0">% Conformidad</h5><h2 class="mb-0 mt-1">{{ stats.pct_conforme }}%</h2></div>
                    <i class="fa-solid fa-circle-check fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning mb-3 shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="card-title mb-0">Reprocesos</h5>
                        <h2 class="mb-0 mt-1">{{ stats.total_reprocesos }}</h2>
                        <small>Pedidos cerrados hoy: {{ stats.pedidos_terminados_hoy }}</small>
                    </div>
                    <i class="fa-solid fa-arrows-rotate fa-2x opacity-50"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Alerta si hay hijas bloqueadas -->
{% if hijas_bloqueadas %}
<div class="alert alert-warning d-flex align-items-start gap-2 mb-4" role="alert">
    <i class="fa-solid fa-circle-exclamation fa-lg mt-1"></i>
    <div>
        <strong>Atención:</strong> Hay {{ hijas_bloqueadas|length }} hija(s) bloqueadas actualmente.
        {% for h in hijas_bloqueadas %}
        <span class="badge {% if h.estado == 'EN_ESPERA' %}bg-warning text-dark{% else %}bg-info text-dark{% endif %} ms-1">
            {{ h.pedido.numero_pedido }} / {{ h.codigo_hija }} — {{ h.estado.replace('_',' ') }}{% if h.area_reproceso %} → {{ h.area_reproceso.nombre }}{% endif %}
        </span>
        {% endfor %}
    </div>
</div>
{% endif %}

<!-- Gráficos principales -->
<div class="row mb-4">
    <div class="col-md-6 mb-4">
        <div class="card shadow-sm h-100">
            <div class="card-body">
                <h5 class="card-title">Defectos por Área</h5>
                <canvas id="chartAreas"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card shadow-sm h-100">
            <div class="card-body">
                <h5 class="card-title">Defectos por Causa</h5>
                <canvas id="chartCausas"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- Indicadores avanzados -->
<div class="row">
    <!-- Ranking operarios -->
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-white fw-bold"><i class="fa-solid fa-ranking-star text-danger me-1"></i> Top Operarios con NC</div>
            <div class="card-body p-0">
                {% if ranking_operarios %}
                <table class="table table-hover mb-0">
                    <thead class="table-light"><tr><th>#</th><th>Operario</th><th class="text-center">NC</th></tr></thead>
                    <tbody>
                        {% for op in ranking_operarios %}
                        <tr>
                            <td class="text-muted fw-bold">{{ loop.index }}</td>
                            <td>{{ op[0] }}</td>
                            <td class="text-center"><span class="badge bg-danger">{{ op[1] }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="text-center text-muted py-4">Sin datos aún</div>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Top defectos -->
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-white fw-bold"><i class="fa-solid fa-bug text-warning me-1"></i> Defectos más Frecuentes</div>
            <div class="card-body p-0">
                {% if top_defectos %}
                <table class="table table-hover mb-0">
                    <thead class="table-light"><tr><th>#</th><th>Defecto</th><th class="text-center">Total</th></tr></thead>
                    <tbody>
                        {% for d in top_defectos %}
                        <tr>
                            <td class="text-muted fw-bold">{{ loop.index }}</td>
                            <td>{{ d[0] }}</td>
                            <td class="text-center"><span class="badge bg-warning text-dark">{{ d[1] }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="text-center text-muted py-4">Sin datos aún</div>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Estado de hijas en tiempo real -->
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-white fw-bold"><i class="fa-solid fa-diagram-project text-info me-1"></i> Hijas Bloqueadas</div>
            <div class="card-body p-0">
                {% if hijas_bloqueadas %}
                <table class="table table-hover mb-0">
                    <thead class="table-light"><tr><th>Pedido/Hija</th><th>Estado</th><th class="text-center">Rep.</th></tr></thead>
                    <tbody>
                        {% for h in hijas_bloqueadas %}
                        <tr>
                            <td class="small"><strong>{{ h.pedido.numero_pedido }}</strong><br><span class="text-muted">{{ h.codigo_hija }}</span></td>
                            <td>
                                {% if h.estado == 'EN_ESPERA' %}
                                    <span class="badge bg-warning text-dark">EN ESPERA</span>
                                {% else %}
                                    <span class="badge bg-info text-dark">REPROCESO</span>
                                    {% if h.area_reproceso %}<br><small class="text-muted">→ {{ h.area_reproceso.nombre }}</small>{% endif %}
                                {% endif %}
                            </td>
                            <td class="text-center">
                                {% if h.veces_reproceso > 0 %}<span class="badge bg-danger">{{ h.veces_reproceso }}</span>{% else %}<span class="text-muted">—</span>{% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="text-center text-muted py-4">
                    <i class="fa-solid fa-circle-check fa-2x text-success mb-2"></i>
                    <p>Sin hijas bloqueadas</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
    const ctxAreas = document.getElementById('chartAreas').getContext('2d');
    new Chart(ctxAreas, {
        type: 'bar',
        data: {
            labels: {{ areas_labels | safe }},
            datasets: [{
                label: 'No Conformidades',
                data: {{ areas_data | safe }},
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
    const ctxCausas = document.getElementById('chartCausas').getContext('2d');
    new Chart(ctxCausas, {
        type: 'pie',
        data: {
            labels: {{ causas_labels | safe }},
            datasets: [{
                data: {{ causas_data | safe }},
                backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0', '#9966ff']
            }]
        },
        options: { responsive: true }
    });
</script>
{% endblock %}""",

        'areas.html': """{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h2 class="mb-0">Planta de Producción</h2>
        <p class="text-muted mb-0">Seleccione el área para registrar una inspección</p>
    </div>
    {% if current_user.username == 'admin' %}
    <button type="button" class="btn btn-primary shadow-sm" data-bs-toggle="modal" data-bs-target="#modalNuevaArea">
        <i class="fa-solid fa-plus"></i> Nueva Área
    </button>
    {% endif %}
</div>

{% if current_user.username == 'admin' %}
<div class="modal fade" id="modalNuevaArea" tabindex="-1" aria-labelledby="modalNuevaAreaLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-light">
                <h5 class="modal-title" id="modalNuevaAreaLabel"><i class="fa-solid fa-industry text-primary me-2"></i>Agregar Nueva Área</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form method="POST" action="{{ url_for('areas.nueva_area') }}">
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="nombreArea" class="form-label fw-bold">Nombre del Área <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="nombreArea" name="nombre" placeholder="Ej: Soldadura, Ensamblaje..." required>
                        <small class="text-muted">Esta área aparecerá automáticamente en el panel de operarios.</small>
                    </div>
                </div>
                <div class="modal-footer border-top-0">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-primary"><i class="fa-solid fa-floppy-disk me-1"></i> Guardar Área</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endif %}

<div class="row g-4">
    {% for area in areas %}
    <div class="col-xl-3 col-lg-4 col-md-6">
        <a href="{{ url_for('inspeccion.nueva', area_id=area.id) }}" class="text-decoration-none text-dark">
            <div class="fiori-card">
                <div class="fiori-icon">
                    <i class="fa-solid fa-clipboard-check"></i>
                </div>
                <h5 class="fw-bold">{{ area.nombre }}</h5>
                <span class="badge bg-secondary">Activa</span>
            </div>
        </a>
    </div>
    {% endfor %}
</div>
{% endblock %}""",

        'inspeccion.html': """{% extends "base.html" %}
{% block content %}
<div class="card shadow-sm max-w-lg mx-auto">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h4 class="mb-0">Registrar Inspección - <strong>{{ area.nombre }}</strong></h4>
        <a href="{{ url_for('criterios.gestionar', area_id=area.id) }}" class="btn btn-outline-primary btn-sm">
            <i class="fa-solid fa-list-check"></i> Gestionar Criterios
        </a>
    </div>
    <div class="card-body">
        <form action="{{ url_for('inspeccion.nueva', area_id=area.id) }}" method="POST" enctype="multipart/form-data">
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <label class="form-label fw-bold">Pedido</label>
                    <select class="form-select" id="pedido_id" name="pedido_id" required>
                        <option value="">Seleccione Pedido...</option>
                        {% for pedido in pedidos %}
                        <option value="{{ pedido.id }}">{{ pedido.numero_pedido }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Hija (Puerta)</label>
                    <select class="form-select" id="hija_id" name="hija_id" required disabled>
                        <option value="">Primero seleccione pedido</option>
                    </select>
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-md-6">
                    <label class="form-label fw-bold">Inspector</label>
                    <input type="text" class="form-control" name="inspector" value="{{ current_user.nombre_completo }}" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Cantidad Inspeccionada</label>
                    <input type="number" class="form-control" name="cantidad" placeholder="Ej: 10" min="1" required>
                    <small class="text-muted">Número de unidades inspeccionadas en el área.</small>
                </div>
            </div>

            <div class="mb-4">
                <label class="form-label fw-bold">Estado de Inspección</label>
                <select class="form-select form-select-lg" id="estado" name="estado" required>
                    <option value="CONFORME">CONFORME - Pasa a siguiente proceso</option>
                    <option value="NO_CONFORME">NO CONFORME - Se detectó defecto</option>
                </select>
            </div>

            <!-- SECCIÓN CRITERIOS DE CALIDAD -->
            <div class="p-4 bg-light border rounded mb-4">
                <h5 class="mb-3"><i class="fa-solid fa-list-check text-primary"></i> Criterios de Calidad</h5>
                {% if criterios %}
                <p class="text-muted small mb-3">Marque los criterios que la pieza <strong>cumple</strong> satisfactoriamente.</p>
                <div class="row">
                    {% for criterio in criterios %}
                    <div class="col-md-6 mb-2">
                        <div class="form-check p-3 bg-white border rounded h-100">
                            <input class="form-check-input" type="checkbox" name="criterio_{{ criterio.id }}" id="crit_{{ criterio.id }}">
                            <label class="form-check-label" for="crit_{{ criterio.id }}">
                                <span class="fw-bold">{{ criterio.nombre }}</span>
                                {% if criterio.descripcion %}
                                <br><small class="text-muted">{{ criterio.descripcion }}</small>
                                {% endif %}
                            </label>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="alert alert-warning mb-0">
                    <i class="fa-solid fa-circle-info me-2"></i>
                    No hay criterios configurados para esta área. 
                    <a href="{{ url_for('criterios.gestionar', area_id=area.id) }}" class="alert-link">Agregar criterios</a>
                </div>
                {% endif %}
            </div>

            <!-- SECCIÓN NO CONFORMIDAD (Oculta por defecto) -->
            <div id="nc-section" class="p-4 bg-light border rounded mb-4" style="display: none;">
                <h5 class="text-danger mb-3"><i class="fa-solid fa-triangle-exclamation"></i> Detalle de No Conformidad</h5>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Tipo de Defecto</label>
                        <select class="form-select" name="tipo_defecto_id">
                            {% for d in defectos %}
                            <option value="{{ d.id }}">{{ d.nombre }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Causa Raíz</label>
                        <select class="form-select" name="causa">
                            {% for c in causas %}
                            <option value="{{ c }}">{{ c }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>

                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Operario Responsable</label>
                        <select class="form-select" name="operario_id" id="operario_id">
                            <option value="">-- Sin asignar --</option>
                            {% for op in operarios %}
                            <option value="{{ op.id }}">{{ op.nombre }}</option>
                            {% endfor %}
                        </select>
                        <small class="text-muted">Operario del área <strong>{{ area.nombre }}</strong> responsable del error.</small>
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label">Observación Detallada</label>
                    <textarea class="form-control" name="observacion_nc" rows="2"></textarea>
                </div>

                <div class="mb-3">
                    <label class="form-label">Evidencia Fotográfica</label>
                    <input class="form-control" type="file" name="fotos" accept="image/*" multiple>
                    <small class="text-muted">Puede seleccionar múltiples imágenes.</small>
                </div>

                {% if area.nombre == 'Empaque' %}
                <div class="p-3 border border-danger rounded bg-white mt-3">
                    <h6 class="text-danger fw-bold mb-3"><i class="fa-solid fa-code-branch"></i> Acción para esta No Conformidad</h6>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label fw-bold">¿Qué se hace con la hija?</label>
                            <select class="form-select" name="accion_empaque" id="accion_empaque" required>
                                <option value="espera">⏸ No Conforme Temporal (EN ESPERA)</option>
                                <option value="reproceso">🔄 Enviar a Reproceso</option>
                            </select>
                            <small class="text-muted">EN ESPERA: se corrige en sitio. Reproceso: se devuelve a otra área.</small>
                        </div>
                        <div class="col-md-6 mb-3" id="bloque-area-reproceso" style="display:none;">
                            <label class="form-label fw-bold">Área de Reproceso</label>
                            <select class="form-select" name="area_reproceso_id" id="area_reproceso_id">
                                <option value="">-- Seleccione área --</option>
                                {% for ar in areas_reproceso %}
                                <option value="{{ ar.id }}">{{ ar.nombre }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>

            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <a href="{{ url_for('areas.index') }}" class="btn btn-secondary">Cancelar</a>
                <button type="submit" class="btn btn-primary px-5">Guardar Inspección</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
    document.getElementById('estado').addEventListener('change', function() {
        const ncSection = document.getElementById('nc-section');
        if(this.value === 'NO_CONFORME') {
            ncSection.style.display = 'block';
            document.querySelector('[name="tipo_defecto_id"]').required = true;
            document.querySelector('[name="causa"]').required = true;
        } else {
            ncSection.style.display = 'none';
            document.querySelector('[name="tipo_defecto_id"]').required = false;
            document.querySelector('[name="causa"]').required = false;
        }
    });

    // Toggle área de reproceso en Empaque
    const accionEmpaque = document.getElementById('accion_empaque');
    if(accionEmpaque) {
        accionEmpaque.addEventListener('change', function() {
            const bloqueReproceso = document.getElementById('bloque-area-reproceso');
            const selectArea = document.getElementById('area_reproceso_id');
            if(this.value === 'reproceso') {
                bloqueReproceso.style.display = 'block';
                selectArea.required = true;
            } else {
                bloqueReproceso.style.display = 'none';
                selectArea.required = false;
            }
        });
    }

    document.getElementById('pedido_id').addEventListener('change', function() {
        const pedidoId = this.value;
        const hijaSelect = document.getElementById('hija_id');
        if(!pedidoId) {
            hijaSelect.innerHTML = '<option value="">Primero seleccione pedido</option>';
            hijaSelect.disabled = true;
            return;
        }
        fetch('/api/hijas/' + pedidoId + '/area/{{ area.id }}')
            .then(response => response.json())
            .then(data => {
                hijaSelect.innerHTML = '<option value="">Seleccione Hija...</option>';
                data.forEach(hija => {
                    let badge = hija.estado === 'EN_ESPERA' ? ' ⏸ EN ESPERA' : (hija.estado === 'EN_REPROCESO' ? ' 🔄 REPROCESO' : '');
                    hijaSelect.innerHTML += `<option value="${hija.id}">${hija.codigo_hija}${badge}</option>`;
                });
                hijaSelect.disabled = false;
                if(data.length === 0) {
                    hijaSelect.innerHTML = '<option value="">Sin hijas disponibles para esta área</option>';
                }
            });
    });
</script>
{% endblock %}""",

        'trazabilidad.html': """{% extends "base.html" %}
{% block content %}
<h2 class="mb-4">Trazabilidad de Producción</h2>

<!-- PEDIDOS ACTIVOS -->
<div class="card shadow-sm mb-4">
    <div class="card-header bg-white"><h5 class="mb-0"><i class="fa-solid fa-magnifying-glass text-primary"></i> Consultar Pedido Activo</h5></div>
    <div class="card-body">
        <form method="GET" action="{{ url_for('trazabilidad.index') }}" class="row g-3 align-items-end">
            <div class="col-md-4">
                <label class="form-label">Número de Pedido</label>
                <select class="form-select" name="pedido_id" id="pedido_id">
                    <option value="">Seleccione...</option>
                    {% for p in pedidos %}
                    <option value="{{ p.id }}" {% if request.args.get('pedido_id')|int == p.id %}selected{% endif %}>{{ p.numero_pedido }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4">
                <label class="form-label">Hija (Puerta)</label>
                <select class="form-select" name="hija_id" id="hija_id">
                    {% if hijas_seleccionadas %}
                        {% for h in hijas_seleccionadas %}
                        <option value="{{ h.id }}" {% if request.args.get('hija_id')|int == h.id %}selected{% endif %}>{{ h.codigo_hija }}</option>
                        {% endfor %}
                    {% else %}
                        <option value="">Seleccione Pedido primero</option>
                    {% endif %}
                </select>
            </div>
            <div class="col-md-4">
                <button type="submit" class="btn btn-primary w-100"><i class="fa-solid fa-magnifying-glass"></i> Consultar Historial</button>
            </div>
        </form>
    </div>
</div>

{% if inspecciones %}
<div class="card shadow-sm mb-4">
    <div class="card-header bg-white">
        <h5 class="mb-0">Historial: <strong>Pedido {{ pedido_actual.numero_pedido }} - {{ hija_actual.codigo_hija }}</strong>
            {% if hija_actual.veces_reproceso > 0 %}
            <span class="badge bg-danger ms-2">{{ hija_actual.veces_reproceso }} reproceso(s)</span>
            {% endif %}
        </h5>
    </div>
    <div class="card-body">
        <div class="timeline mt-3">
            {% for insp in inspecciones %}
            <div class="timeline-item {% if insp.estado == 'CONFORME' %}status-conforme{% else %}status-noconforme{% endif %}">
                <div class="d-flex justify-content-between">
                    <h5 class="fw-bold">{{ insp.area.nombre }}</h5>
                    <span class="text-muted"><i class="fa-regular fa-clock"></i> {{ insp.fecha_hora.strftime('%d/%m/%Y %H:%M') }}</span>
                </div>
                <p class="mb-1"><strong>Inspector:</strong> {{ insp.inspector }} | <strong>Estado:</strong>
                    {% if insp.estado == 'CONFORME' %}
                        <span class="badge bg-success">CONFORME</span>
                    {% else %}
                        <span class="badge bg-danger">NO CONFORME</span>
                    {% endif %}
                </p>
                {% if insp.resultados_criterios %}
                <div class="mt-2">
                    <small class="text-muted fw-bold">Criterios evaluados:</small>
                    <div class="d-flex flex-wrap gap-1 mt-1">
                        {% for resultado in insp.resultados_criterios %}
                        <span class="badge {% if resultado.cumple %}bg-success{% else %}bg-secondary{% endif %} fs-6 fw-normal px-2 py-1">
                            <i class="fa-solid {% if resultado.cumple %}fa-check{% else %}fa-xmark{% endif %} me-1"></i>{{ resultado.criterio.nombre }}
                        </span>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
                {% if insp.estado == 'NO_CONFORME' and insp.no_conformidades %}
                <div class="alert alert-danger mt-2 p-2 mb-0">
                    {% for nc in insp.no_conformidades %}
                        <strong>Defecto:</strong> {{ nc.tipo_defecto.nombre }} <br>
                        <strong>Causa:</strong> {{ nc.causa }} <br>
                        {% if nc.operario %}<strong>Operario:</strong> {{ nc.operario.nombre }} <br>{% endif %}
                        <strong>Observación:</strong> {{ nc.observacion }}
                        {% if nc.evidencias %}
                        <div class="mt-2">
                            <strong>Evidencias:</strong><br>
                            <div class="d-flex gap-2 mt-1">
                            {% for ev in nc.evidencias %}
                                <img src="{{ url_for('static', filename='../uploads/' + ev.ruta_imagen) }}" alt="Evidencia" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;">
                            {% endfor %}
                            </div>
                        </div>
                        {% endif %}
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% elif request.args.get('pedido_id') %}
<div class="alert alert-info">No se encontraron registros de inspección para esta puerta.</div>
{% endif %}

<!-- ARCHIVO DE PEDIDOS TERMINADOS -->
<div class="card shadow-sm mt-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fa-solid fa-box-archive text-success"></i> Archivo — Pedidos Terminados</h5>
        <button class="btn btn-outline-secondary btn-sm" type="button" data-bs-toggle="collapse" data-bs-target="#archivo-trazabilidad">
            <i class="fa-solid fa-chevron-down"></i> Ver / Ocultar
        </button>
    </div>
    <div class="collapse" id="archivo-trazabilidad">
        <div class="card-body border-bottom">
            <form method="GET" action="{{ url_for('trazabilidad.index') }}" class="row g-2 align-items-end">
                <div class="col-md-5">
                    <label class="form-label">Buscar pedido terminado</label>
                    <input type="text" class="form-control" name="buscar_archivo" value="{{ buscar_archivo }}" placeholder="Número de pedido...">
                </div>
                <div class="col-md-3">
                    <button type="submit" class="btn btn-outline-success w-100"><i class="fa-solid fa-magnifying-glass"></i> Buscar</button>
                </div>
            </form>
        </div>
        {% if buscar_archivo %}
            {% if resultados_archivo %}
            <div class="card-body p-0">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr><th>Pedido</th><th class="text-center">Hijas</th><th class="text-center">Reprocesos</th><th></th></tr>
                    </thead>
                    <tbody>
                        {% for p in resultados_archivo %}
                        <tr>
                            <td class="fw-bold align-middle">{{ p.numero_pedido }}</td>
                            <td class="text-center align-middle"><span class="badge bg-secondary">{{ p.hijas|length }}</span></td>
                            <td class="text-center align-middle">
                                {% set tr = p.hijas|sum(attribute='veces_reproceso') %}
                                {% if tr > 0 %}<span class="badge bg-danger">{{ tr }}</span>{% else %}<span class="text-muted">—</span>{% endif %}
                            </td>
                            <td class="text-center align-middle">
                                <a href="{{ url_for('trazabilidad.index') }}?pedido_id={{ p.id }}&hija_id={{ p.hijas[0].id if p.hijas else '' }}" class="btn btn-sm btn-outline-success">
                                    <i class="fa-solid fa-eye"></i> Ver historial
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="card-body"><div class="alert alert-warning mb-0">No se encontraron pedidos terminados con ese número.</div></div>
            {% endif %}
        {% else %}
        <div class="card-body text-muted text-center py-3">Ingresa un número de pedido para buscar en el archivo.</div>
        {% endif %}
    </div>
</div>

{% endblock %}
{% block scripts %}
<script>
    document.getElementById('pedido_id').addEventListener('change', function() {
        const pedidoId = this.value;
        const hijaSelect = document.getElementById('hija_id');
        if(!pedidoId) return;
        fetch('/api/hijas/' + pedidoId)
            .then(response => response.json())
            .then(data => {
                hijaSelect.innerHTML = '';
                data.forEach(hija => {
                    hijaSelect.innerHTML += `<option value="${hija.id}">${hija.codigo_hija}</option>`;
                });
            });
    });
</script>
{% endblock %}""",
    

        'criterios.html': """{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h2 class="mb-0">Criterios de Calidad</h2>
        <span class="text-muted">Área: <strong>{{ area.nombre }}</strong></span>
    </div>
    <a href="{{ url_for('areas.index') }}" class="btn btn-secondary">
        <i class="fa-solid fa-arrow-left"></i> Volver a Planta
    </a>
</div>

<div class="row">
    <!-- Formulario para agregar criterio -->
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fa-solid fa-plus-circle text-primary"></i> Nuevo Criterio</h5>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('criterios.gestionar', area_id=area.id) }}">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Código / Nombre <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" name="nombre" placeholder="Ej: ROV01" required>
                        <small class="text-muted">Código corto o nombre del criterio.</small>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Descripción <span class="text-muted fw-normal">(opcional)</span></label>
                        <textarea class="form-control" name="descripcion" rows="3" placeholder="Ej: La puerta cumple con la estructura deseada sin deformaciones"></textarea>
                        <small class="text-muted">Explica qué significa este criterio para nuevos inspectores.</small>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fa-solid fa-floppy-disk"></i> Agregar Criterio
                    </button>
                </form>
            </div>
        </div>
    </div>

    <!-- Lista de criterios existentes -->
    <div class="col-md-8">
        <div class="card shadow-sm">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fa-solid fa-list-check text-primary"></i> Criterios Configurados ({{ criterios|length }})</h5>
            </div>
            <div class="card-body p-0">
                {% if criterios %}
                <ul class="list-group list-group-flush">
                    {% for c in criterios %}
                    <li class="list-group-item py-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="d-flex align-items-start gap-3 flex-grow-1">
                                {% if c.activo %}
                                    <i class="fa-solid fa-circle-check text-success fs-5 mt-1"></i>
                                {% else %}
                                    <i class="fa-solid fa-circle-xmark text-secondary fs-5 mt-1"></i>
                                {% endif %}
                                <div>
                                    <span class="fw-bold {% if not c.activo %}text-muted text-decoration-line-through{% endif %}">{{ c.nombre }}</span>
                                    {% if c.descripcion %}
                                    <p class="mb-0 text-muted small mt-1">{{ c.descripcion }}</p>
                                    {% endif %}
                                </div>
                            </div>
                            <div class="d-flex gap-2 ms-3 flex-shrink-0">
                                <!-- Toggle activar/desactivar (todos pueden) -->
                                <form method="POST" action="{{ url_for('criterios.toggle', criterio_id=c.id) }}">
                                    <button type="submit" class="btn btn-sm {% if c.activo %}btn-outline-warning{% else %}btn-outline-success{% endif %}">
                                        <i class="fa-solid {% if c.activo %}fa-toggle-on{% else %}fa-toggle-off{% endif %}"></i>
                                        {% if c.activo %}Activo{% else %}Inactivo{% endif %}
                                    </button>
                                </form>
                                <!-- Eliminar solo admin -->
                                {% if current_user.username == 'admin' %}
                                <form method="POST" action="{{ url_for('criterios.borrar', criterio_id=c.id) }}" onsubmit="return confirm('¿Eliminar permanentemente el criterio {{ c.nombre }}? Esta acción no se puede deshacer.')">
                                    <button type="submit" class="btn btn-sm btn-outline-danger">
                                        <i class="fa-solid fa-trash"></i>
                                    </button>
                                </form>
                                {% endif %}
                            </div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <div class="p-4 text-center text-muted">
                    <i class="fa-solid fa-clipboard fa-2x mb-2"></i>
                    <p class="mb-0">No hay criterios configurados para esta área.</p>
                    <small>Use el formulario de la izquierda para agregar el primero.</small>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

        'pedidos.html': """{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h2 class="mb-0">Gestión de Pedidos</h2>
        <span class="text-muted">Solo visible para administradores</span>
    </div>
    <a href="{{ url_for('pedidos.nuevo') }}" class="btn btn-primary">
        <i class="fa-solid fa-plus"></i> Nuevo Pedido
    </a>
</div>

<!-- PEDIDOS ACTIVOS -->
<h5 class="mb-3 text-primary"><i class="fa-solid fa-spinner"></i> Pedidos Activos ({{ pedidos|length }})</h5>
{% if pedidos %}
<div class="card shadow-sm mb-5">
    <div class="card-body p-0">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                    <th>Número de Pedido</th>
                    <th>Fecha Creación</th>
                    <th class="text-center">Hijas</th>
                    <th class="text-center">Reprocesos</th>
                    <th class="text-center">Estado</th>
                    <th class="text-center">Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pedidos %}
                <tr>
                    <td class="fw-bold align-middle">{{ p.numero_pedido }}</td>
                    <td class="align-middle text-muted">{{ p.fecha_creacion.strftime('%d/%m/%Y') }}</td>
                    <td class="text-center align-middle">
                        <span class="badge bg-secondary">{{ p.hijas|length }}</span>
                        {% set en_espera = p.hijas|selectattr('estado','equalto','EN_ESPERA')|list|length %}
                        {% set en_reproceso = p.hijas|selectattr('estado','equalto','EN_REPROCESO')|list|length %}
                        {% if en_espera %}<span class="badge bg-warning text-dark ms-1">{{ en_espera }} espera</span>{% endif %}
                        {% if en_reproceso %}<span class="badge bg-info text-dark ms-1">{{ en_reproceso }} reproceso</span>{% endif %}
                    </td>
                    <td class="text-center align-middle">
                        {% set total_rep = p.hijas|sum(attribute='veces_reproceso') %}
                        {% if total_rep > 0 %}
                            <span class="badge bg-danger">{{ total_rep }}</span>
                        {% else %}
                            <span class="text-muted">—</span>
                        {% endif %}
                    </td>
                    <td class="text-center align-middle">
                        {% if p.estado == 'EN_PROCESO' %}
                            <span class="badge bg-primary">EN PROCESO</span>
                        {% elif p.estado == 'TERMINADO' %}
                            <span class="badge bg-success">TERMINADO</span>
                        {% else %}
                            <span class="badge bg-warning text-dark">PAUSADO</span>
                        {% endif %}
                    </td>
                    <td class="text-center align-middle">
                        <a href="{{ url_for('pedidos.detalle', pedido_id=p.id) }}" class="btn btn-sm btn-outline-primary">
                            <i class="fa-solid fa-eye"></i> Ver detalle
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% else %}
<div class="card shadow-sm mb-5">
    <div class="card-body text-center py-5 text-muted">
        <i class="fa-solid fa-box-open fa-3x mb-3"></i>
        <p class="mb-1 fs-5">No hay pedidos activos.</p>
        <a href="{{ url_for('pedidos.nuevo') }}" class="btn btn-primary mt-2">Crear el primer pedido</a>
    </div>
</div>
{% endif %}

<!-- PEDIDOS TERMINADOS (ARCHIVO) -->
<div class="d-flex justify-content-between align-items-center mb-3">
    <h5 class="mb-0 text-success"><i class="fa-solid fa-box-archive"></i> Pedidos Terminados / Archivo ({{ pedidos_terminados|length }})</h5>
    <button class="btn btn-outline-secondary btn-sm" type="button" data-bs-toggle="collapse" data-bs-target="#archivo-pedidos">
        <i class="fa-solid fa-chevron-down"></i> Ver / Ocultar
    </button>
</div>
<div class="collapse" id="archivo-pedidos">
{% if pedidos_terminados %}
<div class="card shadow-sm">
    <div class="card-body p-0">
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                    <th>Número de Pedido</th>
                    <th>Fecha Creación</th>
                    <th class="text-center">Hijas</th>
                    <th class="text-center">Reprocesos</th>
                    <th class="text-center">Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pedidos_terminados %}
                <tr class="table-success">
                    <td class="fw-bold align-middle">{{ p.numero_pedido }}</td>
                    <td class="align-middle text-muted">{{ p.fecha_creacion.strftime('%d/%m/%Y') }}</td>
                    <td class="text-center align-middle"><span class="badge bg-secondary">{{ p.hijas|length }}</span></td>
                    <td class="text-center align-middle">
                        {% set total_rep = p.hijas|sum(attribute='veces_reproceso') %}
                        {% if total_rep > 0 %}<span class="badge bg-danger">{{ total_rep }}</span>{% else %}<span class="text-muted">—</span>{% endif %}
                    </td>
                    <td class="text-center align-middle">
                        <a href="{{ url_for('pedidos.detalle', pedido_id=p.id) }}" class="btn btn-sm btn-outline-success">
                            <i class="fa-solid fa-eye"></i> Ver detalle
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% else %}
<div class="alert alert-light">Aún no hay pedidos terminados.</div>
{% endif %}
</div>
{% endblock %}""",

        'pedido_form.html': """{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2>Nuevo Pedido de Producción</h2>
    <a href="{{ url_for('pedidos.index') }}" class="btn btn-secondary">
        <i class="fa-solid fa-arrow-left"></i> Volver
    </a>
</div>

<div class="card shadow-sm">
    <div class="card-body">
        <form method="POST" action="{{ url_for('pedidos.nuevo') }}">
            <div class="mb-4">
                <label class="form-label fw-bold fs-5">Número de Pedido <span class="text-danger">*</span></label>
                <input type="text" class="form-control form-control-lg" name="numero_pedido" placeholder="Ej: 8552" required style="max-width: 300px;">
            </div>

            <hr>
            <h5 class="mb-3"><i class="fa-solid fa-list text-primary"></i> Hijas (Puertas del pedido)</h5>
            <p class="text-muted small">Agrega todas las puertas/hijas que componen este pedido con su cantidad.</p>

            <div id="hijas-container">
                <div class="row hija-row g-2 mb-2 align-items-center">
                    <div class="col-md-3">
                        <label class="form-label small text-muted mb-1">Letra</label>
                        <select class="form-select hija-letra" name="letra_hija[]">
                            <option value="">-- Letra --</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small text-muted mb-1">Sufijo (opcional)</label>
                        <input type="text" class="form-control hija-sufijo" placeholder="Ej: Principal" maxlength="30">
                    </div>
                    <input type="hidden" class="hija-codigo-final" name="codigo_hija[]">
                    <div class="col-md-2">
                        <label class="form-label small text-muted mb-1">Cantidad</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="fa-solid fa-hashtag"></i></span>
                            <input type="number" class="form-control" name="cantidad_hija[]" placeholder="Cant." min="1" value="1">
                        </div>
                    </div>
                    <div class="col-md-2 pt-3">
                        <button type="button" class="btn btn-outline-danger btn-eliminar-hija" title="Eliminar fila"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </div>
            </div>

            <button type="button" id="btn-agregar-hija" class="btn btn-outline-primary mt-2 mb-4">
                <i class="fa-solid fa-plus"></i> Agregar otra hija
            </button>

            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary px-5" id="btn-guardar"><i class="fa-solid fa-floppy-disk"></i> Guardar Pedido</button>
                <a href="{{ url_for('pedidos.index') }}" class="btn btn-secondary">Cancelar</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
    const LETRAS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    
    function buildLetraOptions(selected) {
        let opts = '<option value="">-- Letra --</option>';
        LETRAS.forEach(l => {
            opts += `<option value="${l}" ${selected === l ? 'selected' : ''}>Hija ${l}</option>`;
        });
        return opts;
    }

    function syncCodigo(row) {
        const letra = row.querySelector('.hija-letra').value;
        const sufijo = row.querySelector('.hija-sufijo').value.trim();
        const hidden = row.querySelector('.hija-codigo-final');
        if (letra) {
            hidden.value = sufijo ? `Hija ${letra} - ${sufijo}` : `Hija ${letra}`;
        } else {
            hidden.value = '';
        }
    }

    function initRow(row) {
        row.querySelector('.hija-letra').innerHTML = buildLetraOptions('');
        row.querySelector('.hija-letra').addEventListener('change', () => syncCodigo(row));
        row.querySelector('.hija-sufijo').addEventListener('input', () => syncCodigo(row));
    }

    // Inicializar primera fila
    document.querySelectorAll('.hija-row').forEach(initRow);

    document.getElementById('btn-agregar-hija').addEventListener('click', function() {
        const container = document.getElementById('hijas-container');
        const row = document.createElement('div');
        row.className = 'row hija-row g-2 mb-2 align-items-center';
        row.innerHTML = `
            <div class="col-md-3">
                <label class="form-label small text-muted mb-1">Letra</label>
                <select class="form-select hija-letra" name="letra_hija[]"></select>
            </div>
            <div class="col-md-3">
                <label class="form-label small text-muted mb-1">Sufijo (opcional)</label>
                <input type="text" class="form-control hija-sufijo" placeholder="Ej: Principal" maxlength="30">
            </div>
            <input type="hidden" class="hija-codigo-final" name="codigo_hija[]">
            <div class="col-md-2">
                <label class="form-label small text-muted mb-1">Cantidad</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="fa-solid fa-hashtag"></i></span>
                    <input type="number" class="form-control" name="cantidad_hija[]" placeholder="Cant." min="1" value="1">
                </div>
            </div>
            <div class="col-md-2 pt-3">
                <button type="button" class="btn btn-outline-danger btn-eliminar-hija"><i class="fa-solid fa-trash"></i></button>
            </div>`;
        container.appendChild(row);
        initRow(row);
    });

    document.getElementById('hijas-container').addEventListener('click', function(e) {
        if (e.target.closest('.btn-eliminar-hija')) {
            const filas = document.querySelectorAll('.hija-row');
            if (filas.length > 1) {
                e.target.closest('.hija-row').remove();
            }
        }
    });

    // Antes de enviar, sincronizar todos los códigos finales
    document.querySelector('form').addEventListener('submit', function(e) {
        document.querySelectorAll('.hija-row').forEach(row => syncCodigo(row));
        // Validar que todas las filas con letra tengan código
        let ok = true;
        document.querySelectorAll('.hija-row').forEach(row => {
            const letra = row.querySelector('.hija-letra').value;
            if (letra && !row.querySelector('.hija-codigo-final').value) ok = false;
        });
        if (!ok) { e.preventDefault(); alert('Por favor completa todas las letras de hija.'); }
    });
</script>
{% endblock %}""",

        'pedido_detalle.html': """{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h2 class="mb-0">Pedido: <strong>{{ pedido.numero_pedido }}</strong></h2>
        <span class="text-muted">Creado el {{ pedido.fecha_creacion.strftime('%d/%m/%Y') }}</span>
    </div>
    <a href="{{ url_for('pedidos.index') }}" class="btn btn-secondary">
        <i class="fa-solid fa-arrow-left"></i> Volver a Pedidos
    </a>
</div>

<div class="row mb-4">
    <!-- Estado del pedido -->
    <div class="col-md-4">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-white"><h5 class="mb-0">Estado del Pedido</h5></div>
            <div class="card-body">
                <div class="mb-3 text-center">
                    {% if pedido.estado == 'EN_PROCESO' %}
                        <span class="badge bg-primary fs-5 px-4 py-2">EN PROCESO</span>
                    {% elif pedido.estado == 'TERMINADO' %}
                        <span class="badge bg-success fs-5 px-4 py-2">TERMINADO</span>
                    {% else %}
                        <span class="badge bg-warning text-dark fs-5 px-4 py-2">PAUSADO</span>
                    {% endif %}
                </div>
                <form method="POST" action="{{ url_for('pedidos.cambiar_estado', pedido_id=pedido.id) }}">
                    <select class="form-select mb-2" name="estado">
                        <option value="EN_PROCESO" {% if pedido.estado == 'EN_PROCESO' %}selected{% endif %}>EN PROCESO</option>
                        <option value="PAUSADO" {% if pedido.estado == 'PAUSADO' %}selected{% endif %}>PAUSADO</option>
                        <option value="TERMINADO" {% if pedido.estado == 'TERMINADO' %}selected{% endif %}>TERMINADO</option>
                    </select>
                    <button type="submit" class="btn btn-outline-primary w-100">
                        <i class="fa-solid fa-arrows-rotate"></i> Cambiar Estado
                    </button>
                </form>
            </div>
        </div>
    </div>

    <!-- Resumen -->
    <div class="col-md-8">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-white"><h5 class="mb-0">Resumen</h5></div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-4">
                        <div class="fs-1 fw-bold text-primary">{{ pedido.hijas|length }}</div>
                        <div class="text-muted small">Hijas registradas</div>
                    </div>
                    <div class="col-4">
                        <div class="fs-1 fw-bold text-success">{{ pedido.hijas|sum(attribute='cantidad') }}</div>
                        <div class="text-muted small">Puertas totales</div>
                    </div>
                    <div class="col-4">
                        <div class="fs-1 fw-bold text-danger">
                            {{ pedido.hijas|selectattr('estado', 'equalto', 'EN_PROCESO')|list|length }}
                        </div>
                        <div class="text-muted small">En proceso</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Tabla de hijas -->
<div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fa-solid fa-list text-primary"></i> Hijas del Pedido</h5>
    </div>
    <div class="card-body p-0">
        {% if pedido.hijas %}
        <table class="table table-hover mb-0">
            <thead class="table-light">
                <tr>
                    <th>Código / Nombre</th>
                    <th class="text-center">Cantidad</th>
                    <th class="text-center">Estado</th>
                    <th class="text-center">Acción</th>
                </tr>
            </thead>
            <tbody>
                {% for h in pedido.hijas %}
                <tr>
                    <td class="fw-semibold align-middle">{{ h.codigo_hija }}</td>
                    <td class="text-center align-middle">{{ h.cantidad }}</td>
                    <td class="text-center align-middle">
                        {% if h.estado == 'EN_PROCESO' %}
                            <span class="badge bg-primary">EN PROCESO</span>
                        {% elif h.estado == 'EN_ESPERA' %}
                            <span class="badge bg-warning text-dark">EN ESPERA</span>
                        {% elif h.estado == 'EN_REPROCESO' %}
                            <span class="badge bg-info text-dark">REPROCESO{% if h.area_reproceso %} → {{ h.area_reproceso.nombre }}{% endif %}</span>
                        {% elif h.estado == 'TERMINADO' %}
                            <span class="badge bg-success">TERMINADO</span>
                        {% endif %}
                        {% if h.veces_reproceso > 0 %}
                            <span class="badge bg-danger ms-1" title="Reprocesos acumulados">{{ h.veces_reproceso }}x reproceso</span>
                        {% endif %}
                    </td>
                    <td class="text-center align-middle">
                        <form method="POST" action="{{ url_for('pedidos.eliminar_hija', hija_id=h.id) }}" onsubmit="return confirm('¿Eliminar la hija {{ h.codigo_hija }}?')">
                            <button type="submit" class="btn btn-sm btn-outline-danger">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="p-4 text-center text-muted">No hay hijas registradas aún.</div>
        {% endif %}
    </div>
</div>

<!-- Agregar hija -->
<div class="card shadow-sm">
    <div class="card-header bg-white"><h5 class="mb-0"><i class="fa-solid fa-plus text-primary"></i> Agregar Hija</h5></div>
    <div class="card-body">
        <form method="POST" action="{{ url_for('pedidos.agregar_hija', pedido_id=pedido.id) }}" class="row g-2 align-items-end" id="form-agregar-hija">
            <div class="col-md-3">
                <label class="form-label fw-bold">Letra</label>
                <select class="form-select" id="det-letra" name="_letra">
                    <option value="">-- Letra --</option>
                    {% for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' %}
                    <option value="{{ letra }}">Hija {{ letra }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label fw-bold">Sufijo (opcional)</label>
                <input type="text" class="form-control" id="det-sufijo" placeholder="Ej: Principal" maxlength="30">
            </div>
            <input type="hidden" name="codigo_hija" id="det-codigo-final">
            <div class="col-md-2">
                <label class="form-label fw-bold">Cantidad</label>
                <input type="number" class="form-control" name="cantidad" min="1" value="1" required>
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-primary w-100">
                    <i class="fa-solid fa-plus"></i> Agregar
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
    function syncDetCodigo() {
        const letra = document.getElementById('det-letra').value;
        const sufijo = document.getElementById('det-sufijo').value.trim();
        const hidden = document.getElementById('det-codigo-final');
        if (letra) {
            hidden.value = sufijo ? `Hija ${letra} - ${sufijo}` : `Hija ${letra}`;
        } else {
            hidden.value = '';
        }
    }
    document.getElementById('det-letra').addEventListener('change', syncDetCodigo);
    document.getElementById('det-sufijo').addEventListener('input', syncDetCodigo);
    document.getElementById('form-agregar-hija').addEventListener('submit', function(e) {
        syncDetCodigo();
        if (!document.getElementById('det-codigo-final').value) {
            e.preventDefault();
            alert('Por favor selecciona una letra para la hija.');
        }
    });
</script>
{% endblock %}""",

        'login.html': """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIGIC - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            /* Fondo con degradado teal profundo idéntico a tu referencia */
            background: linear-gradient(135deg, #07474a 0%, #106e74 100%) !important;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        
        /* Título superior "USER LOGIN" perfectamente centrado */
        .user-login-title {
            color: #a9b8b8;
            letter-spacing: 2px;
            font-weight: 600;
            font-size: 2.2rem;
            margin-bottom: 25px;
            text-transform: uppercase;
            text-align: center;
        }
        
        /* Tarjeta contenedora ultra oscura y perfectamente simétrica */
        .user-login-card {
            background-color: #1e1e1e;
            border: none;
            border-radius: 10px;
            padding: 45px 40px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            width: 100%;
            max-width: 420px;
        }
        
        /* Estilos simétricos para los inputs de Usuario y Contraseña */
        .form-control.fiori-input {
            background-color: #d0d8d8;
            color: #2b2b2b;
            border: none;
            padding: 12px 15px;
            font-size: 1rem;
        }
        
        .form-control.fiori-input::placeholder {
            color: #6c7a7a;
        }
        
        .form-control.fiori-input:focus {
            background-color: #e2e8e8;
            box-shadow: none;
        }
        
        /* Iconos de los inputs */
        .input-group-text.fiori-icon {
            background-color: #d0d8d8;
            color: #3e3e3e;
            border: none;
            padding: 12px 15px;
        }
        
        /* Texto inferior (Remember me / Forgot Password) */
        .remember-forgot {
            color: #a9b8b8;
            font-size: 0.9rem;
        }
        
        .remember-forgot a {
            color: #a9b8b8;
            text-decoration: none;
        }
        
        .remember-forgot a:hover {
            color: #5c9e9f;
        }
        
        /* Casilla de verificación */
        .form-check-input.fiori-check {
            background-color: #1e1e1e;
            border: 2px solid #a9b8b8;
        }
        
        .form-check-input.fiori-check:checked {
            background-color: #5c9e9f;
            border-color: #5c9e9f;
        }
        
        /* Botón de LOGIN estilo Teal */
        .btn-fiori-login {
            background-color: #5c9e9f;
            color: #ffffff;
            font-weight: 600;
            letter-spacing: 1.5px;
            padding: 12px;
            font-size: 1.1rem;
            border: none;
            margin-top: 25px;
            text-transform: uppercase;
            transition: background-color 0.2s ease-in-out;
        }
        
        .btn-fiori-login:hover {
            background-color: #4c8e8f;
            color: #ffffff;
        }

        /* Contenedor de alertas de error de Flask */
        .alert-container {
            width: 100%;
            max-width: 420px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="alert-container">
          {% for category, message in messages %}
            <div class="alert alert-danger text-center border-0 shadow-sm" role="alert">
              <i class="fa-solid fa-circle-exclamation me-2"></i> {{ message }}
            </div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <div class="user-login-title">
        USER LOGIN
    </div>

    <div class="card user-login-card">
        <div class="card-body p-0">
            <form method="POST" action="{{ url_for('auth.login') }}">
                
                <div class="input-group mb-4">
                    <span class="input-group-text fiori-icon"><i class="fa-solid fa-user"></i></span>
                    <input type="text" class="form-control fiori-input" name="username" placeholder="Username" required>
                </div>
                
                <div class="input-group mb-4">
                    <span class="input-group-text fiori-icon"><i class="fa-solid fa-lock"></i></span>
                    <input type="password" class="form-control fiori-input" name="password" placeholder="Password" required>
                </div>
                
                <div class="d-flex justify-content-between align-items-center remember-forgot">
                    <div class="form-check">
                        <input class="form-check-input fiori-check" type="checkbox" name="remember" id="remember_me">
                        <label class="form-check-label" for="remember_me">
                            Remember me
                        </label>
                    </div>
                    <a href="#">Forgot Password?</a>
                </div>
                
                <button type="submit" class="btn btn-primary w-100 btn-fiori-login">
                    LOGIN
                </button>
            </form>
        </div>
    </div>

</body>
</html>""",

        'operarios.html': """{% extends "base.html" %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h2 class="mb-0"><i class="fa-solid fa-users-gear text-primary"></i> Gestión de Operarios</h2>
        <span class="text-muted">Administra el personal por área de producción</span>
    </div>
</div>

<div class="row">
    <!-- Selector de área -->
    <div class="col-md-3">
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-white fw-bold">Áreas de Producción</div>
            <div class="list-group list-group-flush">
                {% for area in areas %}
                <a href="{{ url_for('operarios.index', area_id=area.id) }}"
                   class="list-group-item list-group-item-action d-flex justify-content-between align-items-center {% if area_sel and area_sel.id == area.id %}active{% endif %}">
                    {{ area.nombre }}
                    <span class="badge bg-secondary rounded-pill">
                        {{ area.operarios|selectattr('activo')|list|length }}
                    </span>
                </a>
                {% endfor %}
            </div>
        </div>
    </div>

    <!-- Panel derecho -->
    <div class="col-md-9">
        {% if area_sel %}
        <!-- Formulario agregar operario -->
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-white fw-bold"><i class="fa-solid fa-plus text-success"></i> Agregar operario en {{ area_sel.nombre }}</div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('operarios.nuevo') }}" class="row g-2 align-items-end">
                    <input type="hidden" name="area_id" value="{{ area_sel.id }}">
                    <div class="col-md-7">
                        <label class="form-label">Nombre completo</label>
                        <input type="text" class="form-control" name="nombre" placeholder="Ej: Carlos Martínez" required maxlength="150">
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-success w-100"><i class="fa-solid fa-plus"></i> Agregar</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Tabla de operarios -->
        <div class="card shadow-sm">
            <div class="card-header bg-white fw-bold">Operarios de {{ area_sel.nombre }} ({{ operarios|length }})</div>
            {% if operarios %}
            <div class="card-body p-0">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Nombre</th>
                            <th class="text-center">Estado</th>
                            <th class="text-center">NC Registradas</th>
                            <th class="text-center">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for op in operarios %}
                        <tr class="{% if not op.activo %}table-secondary text-muted{% endif %}">
                            <td class="align-middle fw-semibold">{{ op.nombre }}</td>
                            <td class="text-center align-middle">
                                {% if op.activo %}
                                    <span class="badge bg-success">Activo</span>
                                {% else %}
                                    <span class="badge bg-secondary">Inactivo</span>
                                {% endif %}
                            </td>
                            <td class="text-center align-middle">
                                {% set nc_count = op.no_conformidades|length %}
                                {% if nc_count > 0 %}
                                    <span class="badge bg-danger">{{ nc_count }}</span>
                                {% else %}
                                    <span class="text-muted">—</span>
                                {% endif %}
                            </td>
                            <td class="text-center align-middle">
                                <div class="d-flex gap-1 justify-content-center">
                                    <!-- Editar nombre -->
                                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#editModal{{ op.id }}">
                                        <i class="fa-solid fa-pen"></i>
                                    </button>
                                    <!-- Activar/Desactivar -->
                                    <form method="POST" action="{{ url_for('operarios.toggle', op_id=op.id) }}">
                                        <button type="submit" class="btn btn-sm {% if op.activo %}btn-outline-warning{% else %}btn-outline-success{% endif %}"
                                                title="{{ 'Desactivar' if op.activo else 'Activar' }}">
                                            <i class="fa-solid {% if op.activo %}fa-user-slash{% else %}fa-user-check{% endif %}"></i>
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                        <!-- Modal editar -->
                        <div class="modal fade" id="editModal{{ op.id }}" tabindex="-1">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">Editar Operario</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <form method="POST" action="{{ url_for('operarios.editar', op_id=op.id) }}">
                                        <div class="modal-body">
                                            <label class="form-label">Nombre completo</label>
                                            <input type="text" class="form-control" name="nombre" value="{{ op.nombre }}" required maxlength="150">
                                        </div>
                                        <div class="modal-footer">
                                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                            <button type="submit" class="btn btn-primary">Guardar cambios</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="card-body text-center text-muted py-4">
                <i class="fa-solid fa-user-plus fa-2x mb-2"></i>
                <p>No hay operarios registrados en esta área.</p>
            </div>
            {% endif %}
        </div>
        {% else %}
        <div class="card shadow-sm">
            <div class="card-body text-center text-muted py-5">
                <i class="fa-solid fa-hand-pointer fa-3x mb-3 text-primary"></i>
                <p class="fs-5">Selecciona un área en el panel izquierdo para gestionar sus operarios.</p>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}""",
    }

    for name, content in templates.items():
        filepath = os.path.join('templates', name)
        with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

# Ejecutar el setup antes de configurar Flask
setup_project_structure()

# ==============================================================================
# 2. CONFIGURACIÓN DE FLASK Y SQLALCHEMY
# ==============================================================================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_local_dev_cambiar_en_produccion')

# Base de datos: PostgreSQL en producción (Render), SQLite en local
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///sigic.db')
# Render provee URLs con "postgres://" — convertir al dialecto pg8000
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+pg8000://', 1)
elif DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder al sistema.'
login_manager.login_message_category = 'danger'

# ==============================================================================
# 3. DEFINICIÓN DE MODELOS DE DATOS (models.py equivalente)
# ==============================================================================
class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_pedido = db.Column(db.String(50), unique=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='EN_PROCESO')
    hijas = db.relationship('Hija', backref='pedido', lazy=True)

class Hija(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    codigo_hija = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    # Estados: EN_PROCESO, EN_ESPERA, EN_REPROCESO, TERMINADO
    estado = db.Column(db.String(20), default='EN_PROCESO')
    area_reproceso_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=True)
    veces_reproceso = db.Column(db.Integer, default=0)
    area_reproceso = db.relationship('Area', foreign_keys=[area_reproceso_id])

class TipoDefecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)

class Inspeccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    hija_id = db.Column(db.Integer, db.ForeignKey('hija.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    inspector = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), nullable=False) # CONFORME, NO_CONFORME
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones para facilitar consultas
    area = db.relationship('Area', backref='inspecciones')
    hija = db.relationship('Hija', backref='inspecciones')
    no_conformidades = db.relationship('NoConformidad', backref='inspeccion', lazy=True)
    resultados_criterios = db.relationship('ResultadoCriterio', backref='inspeccion', lazy=True)

class NoConformidad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspeccion_id = db.Column(db.Integer, db.ForeignKey('inspeccion.id'), nullable=False)
    tipo_defecto_id = db.Column(db.Integer, db.ForeignKey('tipo_defecto.id'), nullable=False)
    operario_id = db.Column(db.Integer, db.ForeignKey('operario.id'), nullable=True)
    causa = db.Column(db.String(100), nullable=False)
    observacion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='ABIERTA') # ABIERTA, EN_PROCESO, CERRADA
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    tipo_defecto = db.relationship('TipoDefecto')
    operario = db.relationship('Operario', overlaps='no_conformidades,operario_ref')
    evidencias = db.relationship('Evidencia', backref='no_conformidad', lazy=True)
    acciones = db.relationship('AccionCorrectiva', backref='no_conformidad', lazy=True)

class Evidencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_conformidad_id = db.Column(db.Integer, db.ForeignKey('no_conformidad.id'), nullable=False)
    ruta_imagen = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class AccionCorrectiva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_conformidad_id = db.Column(db.Integer, db.ForeignKey('no_conformidad.id'), nullable=False)
    responsable = db.Column(db.String(100))
    accion = db.Column(db.Text, nullable=False)
    resultado = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class CantidadInspeccionada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    hija_id = db.Column(db.Integer, db.ForeignKey('hija.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class Criterio(db.Model):
    """Criterios de calidad configurables por área."""
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    area = db.relationship('Area', backref='criterios')

class ResultadoCriterio(db.Model):
    """Resultado de cada criterio evaluado en una inspección."""
    id = db.Column(db.Integer, primary_key=True)
    inspeccion_id = db.Column(db.Integer, db.ForeignKey('inspeccion.id'), nullable=False)
    criterio_id = db.Column(db.Integer, db.ForeignKey('criterio.id'), nullable=False)
    cumple = db.Column(db.Boolean, default=False)
    criterio = db.relationship('Criterio')

class Operario(db.Model):
    """Operarios asignados a cada área de producción."""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    area = db.relationship('Area', backref='operarios')
    no_conformidades = db.relationship('NoConformidad', backref='operario_ref', lazy=True, foreign_keys='NoConformidad.operario_id', overlaps='operario')

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ==============================================================================
# 4. BLUEPRINTS / RUTAS (routes/ equivalente)
# ==============================================================================
bp_dashboard = Blueprint('dashboard', __name__)
bp_areas = Blueprint('areas', __name__)
bp_inspeccion = Blueprint('inspeccion', __name__)
bp_trazabilidad = Blueprint('trazabilidad', __name__)
bp_auth = Blueprint('auth', __name__)

from functools import wraps
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            flash('Solo el administrador puede acceder a esta sección.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = Usuario.query.filter_by(username=username, activo=True).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@bp_auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('auth.login'))

@bp_dashboard.route('/')
@login_required
def index():
    # Calcular KPIs para el Dashboard
    hoy = datetime.utcnow().date()
    insp_hoy = Inspeccion.query.filter(db.func.date(Inspeccion.fecha_hora) == hoy).count()
    nc_abiertas = NoConformidad.query.filter_by(estado='ABIERTA').count()
    
    total_insp = Inspeccion.query.count()
    conforme_count = Inspeccion.query.filter_by(estado='CONFORME').count()
    pct_conforme = round((conforme_count / total_insp * 100) if total_insp > 0 else 0, 1)
    total_reprocesos = db.session.query(db.func.sum(Hija.veces_reproceso)).scalar() or 0
    pedidos_terminados_hoy = Pedido.query.filter(
        Pedido.estado == 'TERMINADO',
        db.func.date(Pedido.fecha_creacion) == hoy
    ).count()

    # Ranking operarios con más NC
    ranking_operarios = db.session.query(
        Operario.nombre,
        db.func.count(NoConformidad.id).label('total')
    ).join(NoConformidad, NoConformidad.operario_id == Operario.id)\
     .group_by(Operario.id, Operario.nombre)\
     .order_by(db.desc('total')).limit(5).all()

    # Defectos más frecuentes
    top_defectos = db.session.query(
        TipoDefecto.nombre,
        db.func.count(NoConformidad.id).label('total')
    ).join(NoConformidad, NoConformidad.tipo_defecto_id == TipoDefecto.id)\
     .group_by(TipoDefecto.id, TipoDefecto.nombre)\
     .order_by(db.desc('total')).limit(5).all()

    # Hijas actualmente en reproceso o en espera
    hijas_bloqueadas = Hija.query.filter(
        Hija.estado.in_(['EN_REPROCESO', 'EN_ESPERA'])
    ).all()

    # Datos para gráfico de Áreas (Top defectos)
    areas_data = db.session.query(
        Area.nombre,
        db.func.count(NoConformidad.id)
    ).join(Inspeccion, Inspeccion.area_id == Area.id)\
     .join(NoConformidad, NoConformidad.inspeccion_id == Inspeccion.id)\
     .group_by(Area.id, Area.nombre).all()

    # Datos para gráfico de Causas
    causas_data = db.session.query(
        NoConformidad.causa,
        db.func.count(NoConformidad.id)
    ).group_by(NoConformidad.causa).all()

    stats = {
        'insp_hoy': insp_hoy,
        'nc_abiertas': nc_abiertas,
        'pct_conforme': pct_conforme,
        'total_reprocesos': total_reprocesos,
        'pedidos_terminados_hoy': pedidos_terminados_hoy
    }

    return render_template('dashboard.html', 
                           stats=stats,
                           areas_labels=[d[0] for d in areas_data],
                           areas_data=[d[1] for d in areas_data],
                           causas_labels=[d[0] for d in causas_data],
                           causas_data=[d[1] for d in causas_data],
                           ranking_operarios=ranking_operarios,
                           top_defectos=top_defectos,
                           hijas_bloqueadas=hijas_bloqueadas)

@bp_areas.route('/areas')
@login_required
def index():
    areas = Area.query.filter_by(activo=True).order_by(Area.nombre).all()
    todas = Area.query.order_by(Area.nombre).all()
    return render_template('areas.html', areas=areas, todas=todas)

@bp_areas.route('/areas/nueva', methods=['POST'])
@login_required
@admin_required
def nueva_area():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre del área es obligatorio.', 'danger')
        return redirect(url_for('areas.index'))
    if Area.query.filter_by(nombre=nombre).first():
        flash(f'Ya existe un área llamada "{nombre}".', 'danger')
        return redirect(url_for('areas.index'))
    db.session.add(Area(nombre=nombre))
    db.session.commit()
    flash(f'Área "{nombre}" creada exitosamente.', 'success')
    return redirect(url_for('areas.index'))

@bp_areas.route('/areas/<int:area_id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_area(area_id):
    area = Area.query.get_or_404(area_id)
    nuevo_nombre = request.form.get('nombre', '').strip()
    if nuevo_nombre and nuevo_nombre != area.nombre:
        if Area.query.filter_by(nombre=nuevo_nombre).first():
            flash('Ya existe un área con ese nombre.', 'danger')
        else:
            area.nombre = nuevo_nombre
            db.session.commit()
            flash(f'Área renombrada a "{nuevo_nombre}".', 'success')
    return redirect(url_for('areas.index'))

@bp_areas.route('/areas/<int:area_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_area(area_id):
    area = Area.query.get_or_404(area_id)
    area.activo = not area.activo
    db.session.commit()
    estado = 'activada' if area.activo else 'desactivada'
    flash(f'Área "{area.nombre}" {estado}.', 'success' if area.activo else 'warning')
    return redirect(url_for('areas.index'))

@bp_inspeccion.route('/inspeccion/nueva/<int:area_id>', methods=['GET', 'POST'])
@login_required
def nueva(area_id):
    area = Area.query.get_or_404(area_id)
    
    if request.method == 'POST':
        pedido_id = request.form.get('pedido_id')
        hija_id = request.form.get('hija_id')
        inspector = request.form.get('inspector')
        estado = request.form.get('estado')
        cantidad = request.form.get('cantidad', 0)

        # 1. Crear Inspección
        nueva_insp = Inspeccion(
            pedido_id=pedido_id, hija_id=hija_id, area_id=area_id,
            inspector=inspector, estado=estado
        )
        db.session.add(nueva_insp)
        db.session.flush() # Para obtener el ID de la inspección

        # 2. Registrar Cantidad Inspeccionada
        if cantidad and int(cantidad) > 0:
            cant = CantidadInspeccionada(
                pedido_id=pedido_id, hija_id=hija_id, area_id=area_id,
                cantidad=int(cantidad)
            )
            db.session.add(cant)

        # 3. Guardar Resultados de Criterios
        criterios_area = Criterio.query.filter_by(area_id=area_id, activo=True).all()
        for criterio in criterios_area:
            cumple = request.form.get(f'criterio_{criterio.id}') == 'on'
            resultado = ResultadoCriterio(
                inspeccion_id=nueva_insp.id,
                criterio_id=criterio.id,
                cumple=cumple
            )
            db.session.add(resultado)

        # 4. Procesar No Conformidad si aplica
        if estado == 'NO_CONFORME':
            tipo_defecto_id = request.form.get('tipo_defecto_id')
            causa = request.form.get('causa')
            observacion = request.form.get('observacion_nc')
            operario_id = request.form.get('operario_id') or None
            
            nc = NoConformidad(
                inspeccion_id=nueva_insp.id,
                tipo_defecto_id=tipo_defecto_id,
                causa=causa,
                observacion=observacion,
                operario_id=operario_id
            )
            db.session.add(nc)
            db.session.flush()

            # Guardar Fotos (Evidencias)
            fotos = request.files.getlist('fotos')
            for foto in fotos:
                if foto and foto.filename:
                    filename = secure_filename(f"{nueva_insp.id}_{foto.filename}")
                    foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    evidencia = Evidencia(no_conformidad_id=nc.id, ruta_imagen=filename)
                    db.session.add(evidencia)

            # 5. Lógica especial para NO CONFORME en Empaque
            if area.nombre == 'Empaque':
                accion_empaque = request.form.get('accion_empaque')  # 'espera' o 'reproceso'
                hija_obj = Hija.query.get(int(hija_id))
                if accion_empaque == 'reproceso':
                    area_reproceso_id = request.form.get('area_reproceso_id')
                    if area_reproceso_id:
                        hija_obj.estado = 'EN_REPROCESO'
                        hija_obj.area_reproceso_id = int(area_reproceso_id)
                        hija_obj.veces_reproceso = (hija_obj.veces_reproceso or 0) + 1
                        flash(f'Hija {hija_obj.codigo_hija} enviada a reproceso. Reprocesos acumulados: {hija_obj.veces_reproceso}.', 'warning')
                else:
                    hija_obj.estado = 'EN_ESPERA'
                    flash(f'Hija {hija_obj.codigo_hija} marcada EN ESPERA hasta resolver el defecto.', 'warning')

        # 6. Lógica de cierre automático si es CONFORME en Empaque
        elif estado == 'CONFORME' and area.nombre == 'Empaque':
            hija_obj = Hija.query.get(int(hija_id))
            hija_obj.estado = 'TERMINADO'
            hija_obj.area_reproceso_id = None
            # Verificar si todas las hijas del pedido están terminadas
            pedido_obj = Pedido.query.get(int(pedido_id))
            todas_terminadas = all(h.estado == 'TERMINADO' for h in pedido_obj.hijas)
            if todas_terminadas:
                pedido_obj.estado = 'TERMINADO'
                flash(f'✅ Pedido {pedido_obj.numero_pedido} completado. Todas las hijas pasaron Empaque.', 'success')
            else:
                pendientes = sum(1 for h in pedido_obj.hijas if h.estado != 'TERMINADO')
                flash(f'Hija {hija_obj.codigo_hija} terminada. Quedan {pendientes} hija(s) pendientes en el pedido.', 'success')

        db.session.commit()
        if estado == 'CONFORME' and area.nombre != 'Empaque':
            flash(f'Inspección registrada con éxito en el área {area.nombre}.', 'success')
        elif estado == 'NO_CONFORME' and area.nombre != 'Empaque':
            flash(f'No conformidad registrada en el área {area.nombre}.', 'danger')
        return redirect(url_for('areas.index'))

    # Para el GET, cargar datos iniciales del formulario
    pedidos = Pedido.query.filter(Pedido.estado.in_(['EN_PROCESO', 'PAUSADO'])).all()
    defectos = TipoDefecto.query.filter_by(activo=True).all()
    causas = ['Mano de obra', 'Máquina', 'Método', 'Material', 'Ambiente', 'Medición']
    criterios = Criterio.query.filter_by(area_id=area_id, activo=True).all()
    operarios = Operario.query.filter_by(area_id=area_id, activo=True).order_by(Operario.nombre).all()
    areas_reproceso = Area.query.filter(Area.activo == True, Area.id != area_id).order_by(Area.nombre).all()
    
    return render_template('inspeccion.html', area=area, pedidos=pedidos, defectos=defectos,
                           causas=causas, criterios=criterios, operarios=operarios,
                           areas_reproceso=areas_reproceso)

@bp_trazabilidad.route('/trazabilidad')
@login_required
def index():
    # Pedidos activos (no terminados) para el selector principal
    pedidos_activos = Pedido.query.filter(Pedido.estado != 'TERMINADO').order_by(Pedido.numero_pedido).all()
    # Pedidos archivados (terminados) para búsqueda separada
    pedidos_archivados = Pedido.query.filter_by(estado='TERMINADO').order_by(Pedido.fecha_creacion.desc()).all()
    
    pedido_id = request.args.get('pedido_id')
    hija_id = request.args.get('hija_id')
    buscar_archivo = request.args.get('buscar_archivo', '').strip()
    
    inspecciones = []
    hijas_seleccionadas = []
    pedido_actual = None
    hija_actual = None
    resultados_archivo = []

    if pedido_id:
        hijas_seleccionadas = Hija.query.filter_by(pedido_id=pedido_id).all()
        pedido_actual = Pedido.query.get(pedido_id)
        if hija_id:
            hija_actual = Hija.query.get(hija_id)
            inspecciones = Inspeccion.query.filter_by(hija_id=hija_id)\
                .order_by(Inspeccion.fecha_hora.asc()).all()

    if buscar_archivo:
        resultados_archivo = Pedido.query.filter(
            Pedido.estado == 'TERMINADO',
            Pedido.numero_pedido.ilike(f'%{buscar_archivo}%')
        ).all()

    return render_template('trazabilidad.html',
                           pedidos=pedidos_activos,
                           pedidos_archivados=pedidos_archivados,
                           inspecciones=inspecciones,
                           hijas_seleccionadas=hijas_seleccionadas,
                           pedido_actual=pedido_actual,
                           hija_actual=hija_actual,
                           buscar_archivo=buscar_archivo,
                           resultados_archivo=resultados_archivo)

# Endpoint API para cargar Hijas dinámicamente en los formularios
@app.route('/api/hijas/<int:pedido_id>')
def api_hijas(pedido_id):
    hijas = Hija.query.filter_by(pedido_id=pedido_id).all()
    return jsonify([{'id': h.id, 'codigo_hija': h.codigo_hija} for h in hijas])

# Endpoint API para hijas filtradas por área (inspección activa)
@app.route('/api/hijas/<int:pedido_id>/area/<int:area_id>')
def api_hijas_area(pedido_id, area_id):
    area = Area.query.get_or_404(area_id)
    if area.nombre == 'Empaque':
        # Empaque ve hijas en proceso o en espera (no terminadas ni en reproceso en otra área)
        hijas = Hija.query.filter(
            Hija.pedido_id == pedido_id,
            Hija.estado.in_(['EN_PROCESO', 'EN_ESPERA'])
        ).all()
    else:
        # Otras áreas ven hijas EN_PROCESO o EN_REPROCESO asignadas a esta área
        hijas = Hija.query.filter(
            Hija.pedido_id == pedido_id,
            db.or_(
                Hija.estado == 'EN_PROCESO',
                db.and_(Hija.estado == 'EN_REPROCESO', Hija.area_reproceso_id == area_id)
            )
        ).all()
    return jsonify([{'id': h.id, 'codigo_hija': h.codigo_hija, 'estado': h.estado} for h in hijas])

# Endpoint API para cargar Operarios por área
@app.route('/api/operarios/<int:area_id>')
def api_operarios(area_id):
    operarios = Operario.query.filter_by(area_id=area_id, activo=True).order_by(Operario.nombre).all()
    return jsonify([{'id': o.id, 'nombre': o.nombre} for o in operarios])

# Blueprint para gestión de pedidos (solo admin)
bp_pedidos = Blueprint('pedidos', __name__)

@bp_pedidos.route('/pedidos')
@login_required
@admin_required
def index():
    pedidos_activos = Pedido.query.filter(Pedido.estado != 'TERMINADO').order_by(Pedido.fecha_creacion.desc()).all()
    pedidos_terminados = Pedido.query.filter_by(estado='TERMINADO').order_by(Pedido.fecha_creacion.desc()).all()
    return render_template('pedidos.html', pedidos=pedidos_activos, pedidos_terminados=pedidos_terminados)

@bp_pedidos.route('/pedidos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo():
    if request.method == 'POST':
        numero = request.form.get('numero_pedido', '').strip()
        if not numero:
            flash('El número de pedido es obligatorio.', 'danger')
            return redirect(url_for('pedidos.nuevo'))
        if Pedido.query.filter_by(numero_pedido=numero).first():
            flash(f'Ya existe un pedido con el número {numero}.', 'danger')
            return redirect(url_for('pedidos.nuevo'))
        pedido = Pedido(numero_pedido=numero)
        db.session.add(pedido)
        db.session.flush()
        # Procesar hijas enviadas dinámicamente
        codigos = request.form.getlist('codigo_hija[]')
        cantidades = request.form.getlist('cantidad_hija[]')
        for codigo, cantidad in zip(codigos, cantidades):
            codigo = codigo.strip()
            if codigo:
                try:
                    cant = int(cantidad)
                except (ValueError, TypeError):
                    cant = 1
                db.session.add(Hija(pedido_id=pedido.id, codigo_hija=codigo, cantidad=cant))
        db.session.commit()
        flash(f'Pedido {numero} creado con éxito.', 'success')
        return redirect(url_for('pedidos.detalle', pedido_id=pedido.id))
    return render_template('pedido_form.html')

@bp_pedidos.route('/pedidos/<int:pedido_id>')
@login_required
@admin_required
def detalle(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('pedido_detalle.html', pedido=pedido)

@bp_pedidos.route('/pedidos/<int:pedido_id>/estado', methods=['POST'])
@login_required
@admin_required
def cambiar_estado(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    nuevo_estado = request.form.get('estado')
    if nuevo_estado in ['EN_PROCESO', 'TERMINADO', 'PAUSADO']:
        pedido.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado del pedido {pedido.numero_pedido} actualizado a {nuevo_estado}.', 'success')
    return redirect(url_for('pedidos.detalle', pedido_id=pedido_id))

@bp_pedidos.route('/pedidos/<int:pedido_id>/hija/agregar', methods=['POST'])
@login_required
@admin_required
def agregar_hija(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    codigo = request.form.get('codigo_hija', '').strip()
    cantidad = request.form.get('cantidad', 1)
    if codigo:
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            cantidad = 1
        db.session.add(Hija(pedido_id=pedido_id, codigo_hija=codigo, cantidad=cantidad))
        db.session.commit()
        flash(f'Hija "{codigo}" agregada al pedido {pedido.numero_pedido}.', 'success')
    return redirect(url_for('pedidos.detalle', pedido_id=pedido_id))

@bp_pedidos.route('/pedidos/hija/<int:hija_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_hija(hija_id):
    hija = Hija.query.get_or_404(hija_id)
    pedido_id = hija.pedido_id
    nombre = hija.codigo_hija
    db.session.delete(hija)
    db.session.commit()
    flash(f'Hija "{nombre}" eliminada.', 'success')
    return redirect(url_for('pedidos.detalle', pedido_id=pedido_id))

# Blueprint para gestión de criterios por área
bp_criterios = Blueprint('criterios', __name__)

@bp_criterios.route('/criterios/<int:area_id>', methods=['GET', 'POST'])
@login_required
def gestionar(area_id):
    area = Area.query.get_or_404(area_id)
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        if nombre:
            db.session.add(Criterio(area_id=area_id, nombre=nombre, descripcion=descripcion or None))
            db.session.commit()
            flash(f'Criterio "{nombre}" agregado correctamente.', 'success')
        return redirect(url_for('criterios.gestionar', area_id=area_id))
    criterios = Criterio.query.filter_by(area_id=area_id).all()
    return render_template('criterios.html', area=area, criterios=criterios)

@bp_criterios.route('/criterios/toggle/<int:criterio_id>', methods=['POST'])
@login_required
def toggle(criterio_id):
    criterio = Criterio.query.get_or_404(criterio_id)
    area_id = criterio.area_id
    criterio.activo = not criterio.activo
    db.session.commit()
    estado = 'activado' if criterio.activo else 'desactivado'
    flash(f'Criterio "{criterio.nombre}" {estado}.', 'success')
    return redirect(url_for('criterios.gestionar', area_id=area_id))

@bp_criterios.route('/criterios/borrar/<int:criterio_id>', methods=['POST'])
@login_required
def borrar(criterio_id):
    if current_user.username != 'admin':
        flash('Solo el administrador puede eliminar criterios.', 'danger')
        criterio = Criterio.query.get_or_404(criterio_id)
        return redirect(url_for('criterios.gestionar', area_id=criterio.area_id))
    criterio = Criterio.query.get_or_404(criterio_id)
    area_id = criterio.area_id
    nombre = criterio.nombre
    # Eliminar resultados relacionados primero
    ResultadoCriterio.query.filter_by(criterio_id=criterio_id).delete()
    db.session.delete(criterio)
    db.session.commit()
    flash(f'Criterio "{nombre}" eliminado permanentemente.', 'success')
    return redirect(url_for('criterios.gestionar', area_id=area_id))

bp_operarios = Blueprint('operarios', __name__)

@bp_operarios.route('/operarios')
@login_required
@admin_required
def index():
    areas = Area.query.filter_by(activo=True).order_by(Area.nombre).all()
    area_id = request.args.get('area_id', type=int)
    area_sel = Area.query.get(area_id) if area_id else None
    operarios = Operario.query.filter_by(area_id=area_id).order_by(Operario.nombre).all() if area_id else []
    return render_template('operarios.html', areas=areas, operarios=operarios, area_sel=area_sel)

@bp_operarios.route('/operarios/nuevo', methods=['POST'])
@login_required
@admin_required
def nuevo():
    nombre = request.form.get('nombre', '').strip()
    area_id = request.form.get('area_id', type=int)
    if nombre and area_id:
        db.session.add(Operario(nombre=nombre, area_id=area_id))
        db.session.commit()
        flash(f'Operario "{nombre}" agregado exitosamente.', 'success')
    return redirect(url_for('operarios.index', area_id=area_id))

@bp_operarios.route('/operarios/<int:op_id>/editar', methods=['POST'])
@login_required
@admin_required
def editar(op_id):
    op = Operario.query.get_or_404(op_id)
    nuevo_nombre = request.form.get('nombre', '').strip()
    if nuevo_nombre:
        op.nombre = nuevo_nombre
        db.session.commit()
        flash('Nombre actualizado.', 'success')
    return redirect(url_for('operarios.index', area_id=op.area_id))

@bp_operarios.route('/operarios/<int:op_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle(op_id):
    op = Operario.query.get_or_404(op_id)
    op.activo = not op.activo
    db.session.commit()
    estado = 'activado' if op.activo else 'desactivado'
    flash(f'Operario "{op.nombre}" {estado}.', 'success' if op.activo else 'warning')
    return redirect(url_for('operarios.index', area_id=op.area_id))

# API: Notificaciones de reproceso para un área
@app.route('/api/notificaciones/<int:area_id>')
@login_required
def api_notificaciones(area_id):
    hijas_reproceso = Hija.query.filter_by(estado='EN_REPROCESO', area_reproceso_id=area_id).all()
    notifs = []
    for h in hijas_reproceso:
        notifs.append({
            'hija': h.codigo_hija,
            'pedido': h.pedido.numero_pedido,
            'veces_reproceso': h.veces_reproceso
        })
    return jsonify(notifs)

# API: Stats avanzadas para dashboard
@app.route('/api/stats/operarios')
@login_required
def api_stats_operarios():
    data = db.session.query(
        Operario.nombre,
        db.func.count(NoConformidad.id).label('total_nc')
    ).join(NoConformidad, NoConformidad.operario_id == Operario.id)\
     .group_by(Operario.id, Operario.nombre)\
     .order_by(db.desc('total_nc'))\
     .limit(10).all()
    return jsonify([{'nombre': d[0], 'total': d[1]} for d in data])

# Registrar Blueprints
app.register_blueprint(bp_auth)
app.register_blueprint(bp_dashboard)
app.register_blueprint(bp_areas)
app.register_blueprint(bp_inspeccion)
app.register_blueprint(bp_trazabilidad)
app.register_blueprint(bp_criterios)
app.register_blueprint(bp_pedidos)
app.register_blueprint(bp_operarios)

# ==============================================================================
# 5. INICIALIZACIÓN DE LA BASE DE DATOS Y POBLADO DE CATÁLOGOS (SEEDER)
# ==============================================================================
def seed_database():
    """Pobla la base de datos con los catálogos requeridos si está vacía."""
    # Crear usuario admin si no existe
    if not Usuario.query.filter_by(username='admin').first():
        admin = Usuario(username='admin', nombre_completo='Administrador SIGIC')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(">> Usuario admin creado (usuario: admin / contraseña: admin123)")

    if not Area.query.first():
        # Áreas
        nombres_areas = ['Esqueleto', 'Prensa', 'Escuadradora', 'Rover', 'Enchapadora', 
                         'Maquinado', 'Carpintería', 'Preparación', 'Armado', 'Pintura', 
                         'Empaque', 'Revisión Visual']
        for nombre in nombres_areas:
            db.session.add(Area(nombre=nombre))
        
        # Defectos
        nombres_defectos = ['Rayón', 'Golpe', 'Desportillado', 'Medida incorrecta', 
                            'Mala perforación', 'Defecto de pintura', 'Otro']
        for defecto in nombres_defectos:
            db.session.add(TipoDefecto(nombre=defecto))
            
        # Datos de Prueba (Pedidos e Hijas)
        pedido1 = Pedido(numero_pedido='8550')
        db.session.add(pedido1)
        db.session.flush()
        db.session.add(Hija(pedido_id=pedido1.id, codigo_hija='Hija A'))
        db.session.add(Hija(pedido_id=pedido1.id, codigo_hija='Hija B'))
        db.session.add(Hija(pedido_id=pedido1.id, codigo_hija='Hija C'))
        
        pedido2 = Pedido(numero_pedido='8551')
        db.session.add(pedido2)
        db.session.flush()
        db.session.add(Hija(pedido_id=pedido2.id, codigo_hija='Puerta Ppal'))
        
        db.session.commit()
        print(">> Base de datos poblada exitosamente con datos semilla.")

        # Operarios de ejemplo por área (agregar después del commit anterior)
        with app.app_context():
            areas_obj = {a.nombre: a for a in Area.query.all()}
            operarios_por_area = {
                'Rover':        ['Carlos Martínez', 'Luis Pérez', 'Andrés Gómez'],
                'Esqueleto':    ['Juan Torres', 'Pedro Ramírez'],
                'Prensa':       ['Miguel Herrera', 'Sergio López'],
                'Escuadradora': ['David Morales', 'Felipe Castro'],
                'Enchapadora':  ['Ricardo Vargas', 'Jorge Díaz'],
                'Maquinado':    ['Alejandro Ruiz', 'Camilo Soto'],
                'Carpintería':  ['Hernán Medina', 'Gustavo Ríos'],
                'Preparación':  ['Mauricio Silva', 'Iván Blanco'],
                'Armado':       ['Nelson Pardo', 'Óscar Fuentes'],
                'Pintura':      ['Fernando Jiménez', 'Raúl Mendoza'],
                'Empaque':      ['Cristian Rojas', 'Wilson Peña'],
                'Revisión Visual': ['Sofía Ortega', 'Valentina Cruz'],
            }
            for area_nombre, nombres in operarios_por_area.items():
                area_obj = areas_obj.get(area_nombre)
                if area_obj:
                    for nombre in nombres:
                        db.session.add(Operario(nombre=nombre, area_id=area_obj.id))
            db.session.commit()
            print(">> Operarios de ejemplo creados por área.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    
    print("=========================================================")
    print(">> SIGIC - SISTEMA INTEGRAL DE GESTION DE CALIDAD INICIADO")
    print("=========================================================")
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)