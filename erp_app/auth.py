from flask import session, redirect, url_for, request, flash, jsonify, current_app
from functools import wraps
from .models import Usuario
import os

# Endpoints POST permitidos para usuarios solo lectura
POST_PERMITIDOS_LECTURA = frozenset({
    'login', 'static', 'cambiar_contraseña', 'cambiar_idioma',
})

# Rutas GET de edición que no siguen el prefijo nuevo_/editar_
RUTAS_EDICION_EXTRA = frozenset({
    'gestionar_productos_proveedor',
})


def get_usuario_actual():
    """Obtiene el usuario actual de la sesión"""
    if 'usuario_id' in session:
        return Usuario.query.get(session['usuario_id'])
    return None


def usuario_puede_editar(usuario=None):
    usuario = usuario or get_usuario_actual()
    return bool(usuario and usuario.puede_editar())


def _es_ruta_edicion(endpoint):
    if not endpoint:
        return False
    if endpoint.startswith('admin_'):
        return True
    if endpoint in RUTAS_EDICION_EXTRA:
        return True
    for prefix in ('nuevo_', 'nueva_', 'editar_', 'eliminar_'):
        if endpoint.startswith(prefix):
            return True
    if 'eliminar' in endpoint:
        return True
    return False


def _redirect_lectura(endpoint):
    """Redirige rutas de edición a vista cuando existe equivalente."""
    if endpoint and endpoint.startswith('editar_'):
        ver_name = 'ver_' + endpoint[len('editar_'):]
        if ver_name in current_app.view_functions:
            return redirect(url_for(ver_name, **dict(request.view_args or {})))
    flash('Su usuario tiene permisos de solo lectura.', 'warning')
    return redirect(request.referrer or url_for('portal_erps'))


def control_permisos_usuario():
    """Middleware: bloquea escritura y pantallas de edición a usuarios view."""
    endpoint = request.endpoint
    if not endpoint or endpoint in ('static', 'login', 'logout', 'registro'):
        return None

    usuario = get_usuario_actual()
    if not usuario or usuario.puede_editar():
        return None

    if request.method != 'GET' and endpoint not in POST_PERMITIDOS_LECTURA:
        if request.is_json or (request.path or '').startswith('/api/'):
            return jsonify({'error': 'Permisos de solo lectura'}), 403
        flash('No tiene permisos para modificar datos.', 'error')
        return redirect(request.referrer or url_for('portal_erps'))

    if _es_ruta_edicion(endpoint):
        return _redirect_lectura(endpoint)

    return None


def usuario_requerido(f):
    """Decorador para requerir que el usuario esté autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def edicion_requerida(f):
    """Decorador para rutas que modifican datos."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login', next=request.url))
        usuario = get_usuario_actual()
        if not usuario or not usuario.puede_editar():
            if request.is_json or request.method != 'GET':
                return jsonify({'error': 'Permisos de solo lectura'}), 403
            return _redirect_lectura(request.endpoint)
        return f(*args, **kwargs)
    return decorated_function


def admin_requerido(f):
    """Decorador para requerir que el usuario sea admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login', next=request.url))
        
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario or not usuario.is_admin():
            return redirect(url_for('portal_erps'))
        
        return f(*args, **kwargs)
    return decorated_function
