from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory, abort, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from .models import (
    db, ERP, Cliente, Proveedor, ProveedorContacto, Producto, Cotizacion, ConfigMargen,
    Pedido, ItemPedido, Cobranza, CobranzaLinea, CobranzaImputacion,
    ProveedorLogistico, Usuario, Fruta, Variedad, Clasificacion, Envase, Marca, Kilogramo, FormaCobro
)
from .auth import usuario_requerido, admin_requerido, get_usuario_actual, control_permisos_usuario, usuario_puede_editar
from .backup import ejecutar_backups_produccion, listar_backups_recientes, backup_excel_opcional
from .paths import ERP_DB_PATH, UPLOAD_REMITOS_DIR as _UPLOAD_REMITOS_PATH
from datetime import datetime, date
from sqlalchemy import func, extract, and_, or_
import os
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_REMITOS_DIR = str(_UPLOAD_REMITOS_PATH)
REMITO_ADJUNTO_MAX_MB = 15
REMITO_ADJUNTO_EXT = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'heic', 'heif'}


def _database_uri():
    url = os.getenv('DATABASE_URL', '').strip()
    if url:
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    return f'sqlite:///{ERP_DB_PATH}'


app.config['SQLALCHEMY_DATABASE_URI'] = _database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu_clave_secreta_desarrollo_aqui')

IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = IS_PRODUCTION and os.getenv('SESSION_COOKIE_SECURE', 'true').lower() != 'false'

if IS_PRODUCTION:
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

db.init_app(app)


@app.before_request
def _verificar_permisos():
    return control_permisos_usuario()

# ==================== API MAESTROS ====================

@app.route('/api/frutas', methods=['GET'])
@usuario_requerido
def api_listar_frutas():
    frutas = Fruta.query.order_by(Fruta.nombre).all()
    return jsonify([{'id': f.id, 'nombre': f.nombre, 'activo': f.activo} for f in frutas])

@app.route('/api/frutas/nueva', methods=['POST'])
@usuario_requerido
def api_nueva_fruta():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Fruta.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'Ya existe una fruta con ese nombre'}), 400
    fruta = Fruta(nombre=nombre)
    db.session.add(fruta)
    db.session.commit()
    return jsonify({'success': True, 'fruta': {'id': fruta.id, 'nombre': fruta.nombre}})

@app.route('/api/frutas/<int:id>/editar', methods=['POST'])
@usuario_requerido
def api_editar_fruta(id):
    fruta = Fruta.query.get_or_404(id)
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Fruta.query.filter(Fruta.nombre == nombre, Fruta.id != id).first():
        return jsonify({'error': 'Ya existe una fruta con ese nombre'}), 400
    fruta.nombre = nombre
    db.session.commit()
    return jsonify({'success': True, 'fruta': {'id': fruta.id, 'nombre': fruta.nombre}})

@app.route('/api/frutas/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def api_eliminar_fruta(id):
    fruta = Fruta.query.get_or_404(id)
    if Producto.query.filter_by(fruta=fruta.nombre).count() > 0:
        return jsonify({'error': 'No se puede eliminar porque hay productos usando este valor'}), 400
    db.session.delete(fruta)
    db.session.commit()
    return jsonify({'success': True})

# --- Variedad ---
@app.route('/api/variedades', methods=['GET'])
@usuario_requerido
def api_listar_variedades():
    variedades = Variedad.query.order_by(Variedad.nombre).all()
    return jsonify([{'id': v.id, 'nombre': v.nombre, 'activo': v.activo} for v in variedades])

@app.route('/api/variedades/nueva', methods=['POST'])
@usuario_requerido
def api_nueva_variedad():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Variedad.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'Ya existe una variedad con ese nombre'}), 400
    variedad = Variedad(nombre=nombre)
    db.session.add(variedad)
    db.session.commit()
    return jsonify({'success': True, 'variedad': {'id': variedad.id, 'nombre': variedad.nombre}})

@app.route('/api/variedades/<int:id>/editar', methods=['POST'])
@usuario_requerido
def api_editar_variedad(id):
    variedad = Variedad.query.get_or_404(id)
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Variedad.query.filter(Variedad.nombre == nombre, Variedad.id != id).first():
        return jsonify({'error': 'Ya existe una variedad con ese nombre'}), 400
    variedad.nombre = nombre
    db.session.commit()
    return jsonify({'success': True, 'variedad': {'id': variedad.id, 'nombre': variedad.nombre}})

@app.route('/api/variedades/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def api_eliminar_variedad(id):
    variedad = Variedad.query.get_or_404(id)
    if Producto.query.filter_by(variedad=variedad.nombre).count() > 0:
        return jsonify({'error': 'No se puede eliminar porque hay productos usando este valor'}), 400
    db.session.delete(variedad)
    db.session.commit()
    return jsonify({'success': True})

# --- Clasificacion ---
@app.route('/api/clasificaciones', methods=['GET'])
@usuario_requerido
def api_listar_clasificaciones():
    clasificaciones = Clasificacion.query.order_by(Clasificacion.nombre).all()
    return jsonify([{'id': c.id, 'nombre': c.nombre, 'activo': c.activo} for c in clasificaciones])

@app.route('/api/clasificaciones/nueva', methods=['POST'])
@usuario_requerido
def api_nueva_clasificacion():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Clasificacion.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'Ya existe una clasificación con ese nombre'}), 400
    clasificacion = Clasificacion(nombre=nombre)
    db.session.add(clasificacion)
    db.session.commit()
    return jsonify({'success': True, 'clasificacion': {'id': clasificacion.id, 'nombre': clasificacion.nombre}})

@app.route('/api/clasificaciones/<int:id>/editar', methods=['POST'])
@usuario_requerido
def api_editar_clasificacion(id):
    clasificacion = Clasificacion.query.get_or_404(id)
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Clasificacion.query.filter(Clasificacion.nombre == nombre, Clasificacion.id != id).first():
        return jsonify({'error': 'Ya existe una clasificación con ese nombre'}), 400
    clasificacion.nombre = nombre
    db.session.commit()
    return jsonify({'success': True, 'clasificacion': {'id': clasificacion.id, 'nombre': clasificacion.nombre}})

@app.route('/api/clasificaciones/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def api_eliminar_clasificacion(id):
    clasificacion = Clasificacion.query.get_or_404(id)
    if Producto.query.filter_by(clasificacion=clasificacion.nombre).count() > 0:
        return jsonify({'error': 'No se puede eliminar porque hay productos usando este valor'}), 400
    db.session.delete(clasificacion)
    db.session.commit()
    return jsonify({'success': True})

# --- Envase ---
@app.route('/api/envases', methods=['GET'])
@usuario_requerido
def api_listar_envases():
    envases = Envase.query.order_by(Envase.nombre).all()
    return jsonify([{'id': e.id, 'nombre': e.nombre, 'activo': e.activo} for e in envases])

@app.route('/api/envases/nuevo', methods=['POST'])
@usuario_requerido
def api_nuevo_envase():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Envase.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'Ya existe un envase con ese nombre'}), 400
    envase = Envase(nombre=nombre)
    db.session.add(envase)
    db.session.commit()
    return jsonify({'success': True, 'envase': {'id': envase.id, 'nombre': envase.nombre}})

@app.route('/api/envases/<int:id>/editar', methods=['POST'])
@usuario_requerido
def api_editar_envase(id):
    envase = Envase.query.get_or_404(id)
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Envase.query.filter(Envase.nombre == nombre, Envase.id != id).first():
        return jsonify({'error': 'Ya existe un envase con ese nombre'}), 400
    envase.nombre = nombre
    db.session.commit()
    return jsonify({'success': True, 'envase': {'id': envase.id, 'nombre': envase.nombre}})

@app.route('/api/envases/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def api_eliminar_envase(id):
    envase = Envase.query.get_or_404(id)
    if Producto.query.filter_by(envase=envase.nombre).count() > 0:
        return jsonify({'error': 'No se puede eliminar porque hay productos usando este valor'}), 400
    db.session.delete(envase)
    db.session.commit()
    return jsonify({'success': True})

# --- Marca ---
@app.route('/api/marcas', methods=['GET'])
@usuario_requerido
def api_listar_marcas():
    marcas = Marca.query.order_by(Marca.nombre).all()
    return jsonify([{'id': m.id, 'nombre': m.nombre, 'activo': m.activo} for m in marcas])

@app.route('/api/marcas/nueva', methods=['POST'])
@usuario_requerido
def api_nueva_marca():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Marca.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'Ya existe una marca con ese nombre'}), 400
    marca = Marca(nombre=nombre)
    db.session.add(marca)
    db.session.commit()
    return jsonify({'success': True, 'marca': {'id': marca.id, 'nombre': marca.nombre}})

@app.route('/api/marcas/<int:id>/editar', methods=['POST'])
@usuario_requerido
def api_editar_marca(id):
    marca = Marca.query.get_or_404(id)
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Marca.query.filter(Marca.nombre == nombre, Marca.id != id).first():
        return jsonify({'error': 'Ya existe una marca con ese nombre'}), 400
    marca.nombre = nombre
    db.session.commit()
    return jsonify({'success': True, 'marca': {'id': marca.id, 'nombre': marca.nombre}})

@app.route('/api/marcas/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def api_eliminar_marca(id):
    marca = Marca.query.get_or_404(id)
    if Producto.query.filter_by(marca=marca.nombre).count() > 0:
        return jsonify({'error': 'No se puede eliminar porque hay productos usando este valor'}), 400
    db.session.delete(marca)
    db.session.commit()
    return jsonify({'success': True})


# --- Kilogramo ---
@app.route('/api/kilogramos', methods=['GET'])
@usuario_requerido
def api_listar_kilogramos():
    items = Kilogramo.query.order_by(Kilogramo.nombre).all()
    return jsonify([{'id': k.id, 'nombre': k.nombre, 'activo': k.activo} for k in items])

@app.route('/api/kilogramos/nuevo', methods=['POST'])
@usuario_requerido
def api_nuevo_kilogramo():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Kilogramo.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'Ya existe ese kilogramo'}), 400
    kg = Kilogramo(nombre=nombre)
    db.session.add(kg)
    db.session.commit()
    return jsonify({'success': True, 'kilogramo': {'id': kg.id, 'nombre': kg.nombre}})

@app.route('/api/kilogramos/<int:id>/editar', methods=['POST'])
@usuario_requerido
def api_editar_kilogramo(id):
    kg = Kilogramo.query.get_or_404(id)
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if Kilogramo.query.filter(Kilogramo.nombre == nombre, Kilogramo.id != id).first():
        return jsonify({'error': 'Ya existe ese kilogramo'}), 400
    kg.nombre = nombre
    db.session.commit()
    return jsonify({'success': True, 'kilogramo': {'id': kg.id, 'nombre': kg.nombre}})

@app.route('/api/kilogramos/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def api_eliminar_kilogramo(id):
    kg = Kilogramo.query.get_or_404(id)
    if Producto.query.filter_by(kilogramo=kg.nombre).count() > 0:
        return jsonify({'error': 'No se puede eliminar porque hay productos usando este valor'}), 400
    db.session.delete(kg)
    db.session.commit()
    return jsonify({'success': True})


def _migrar_columnas_db():
    """Agrega columnas nuevas en SQLite sin perder datos."""
    import sqlite3
    db_path = str(ERP_DB_PATH)
    if not os.path.exists(db_path):
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    migraciones = [
        ("proveedores_logisticos", "cuit", "TEXT"),
        ("cobranzas_imputaciones", "pago_proveedor", "REAL DEFAULT 0"),
        ("cobranzas_imputaciones", "comision", "REAL DEFAULT 0"),
        ("cobranzas", "eliminado", "INTEGER DEFAULT 0"),
        ("cobranzas", "fecha_eliminacion", "TEXT"),
        ("pedidos", "fecha_remito", "TEXT"),
        ("pedidos", "fecha_entrega", "TEXT"),
        ("pedidos", "entregado_opcion", "TEXT DEFAULT ''"),
        ("pedidos", "eliminado", "INTEGER DEFAULT 0"),
        ("pedidos", "fecha_eliminacion", "TEXT"),
        ("pedidos", "remito_adjunto_path", "TEXT"),
        ("pedidos", "remito_adjunto_nombre", "TEXT"),
        ("pedidos", "descuento_monto", "REAL DEFAULT 0"),
        ("pedidos", "descuento_costo", "REAL DEFAULT 0"),
        ("pedidos", "descuento_comision", "REAL DEFAULT 0"),
        ("pedidos", "descuento_sobre_costo", "INTEGER DEFAULT 0"),
        ("pedidos", "descuento_sobre_comision", "INTEGER DEFAULT 0"),
    ]
    for tabla, col, tipo in migraciones:
        cur.execute(f"PRAGMA table_info({tabla})")
        cols = [r[1] for r in cur.fetchall()]
        if col not in cols:
            cur.execute(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo}")
    conn.commit()
    conn.close()


def init_db():
    with app.app_context():
        print("  -> Verificando estructura de tablas en la DB...")
        db.create_all()
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            _migrar_columnas_db()
        
        erp_existente = ERP.query.filter_by(nombre="Conectar 23").first()
        if not erp_existente:
            erp = ERP(
                nombre="Conectar 23",
                descripcion="Sistema de gestión integral para el negocio",
                activo=True,
                color_primario="#667eea",
                icono="📊"
            )
            db.session.add(erp)
            db.session.commit()
            print("  -> ERP 'Conectar 23' creado.")
        
        admin_emails = [
            ('pablobruno321@hotmail.com', 'Pablo Bruno', 'admin123'),
            ('pablo.geba.river@gmail.com', 'Pablo Geba River', 'admin123')
        ]
        for email, nombre, password in admin_emails:
            if not Usuario.query.filter_by(email=email).first():
                admin_user = Usuario(email=email, nombre=nombre, rol='admin', activo=True)
                admin_user.set_password(password)
                db.session.add(admin_user)
                print(f"  -> Usuario admin '{email}' creado.")
        
        db.session.commit()
        
        if not ConfigMargen.query.first():
            config = ConfigMargen(margen_default=30)
            db.session.add(config)
            db.session.commit()
            print("  -> Configuración de margen creada.")

        # Inicializar tablas maestras independientes si están vacías
        from .models import Fruta, Variedad, Clasificacion, Envase, Marca, Kilogramo, FormaCobro
        if not Fruta.query.first():
            frutas = set(p.fruta for p in Producto.query.all() if p.fruta)
            for nombre in sorted(frutas):
                db.session.add(Fruta(nombre=nombre))
        if not Variedad.query.first():
            variedades = set(p.variedad for p in Producto.query.all() if p.variedad)
            for nombre in sorted(variedades):
                db.session.add(Variedad(nombre=nombre))
        if not Clasificacion.query.first():
            clasificaciones = set(p.clasificacion for p in Producto.query.all() if p.clasificacion)
            for nombre in sorted(clasificaciones):
                db.session.add(Clasificacion(nombre=nombre))
        if not Envase.query.first():
            envases = set(p.envase for p in Producto.query.all() if p.envase)
            for nombre in sorted(envases):
                db.session.add(Envase(nombre=nombre))
        if not Marca.query.first():
            marcas = set(p.marca for p in Producto.query.all() if p.marca)
            for nombre in sorted(marcas):
                db.session.add(Marca(nombre=nombre))
        if not Kilogramo.query.first():
            kgs = set(p.kilogramo for p in Producto.query.all() if p.kilogramo)
            for nombre in sorted(kgs):
                db.session.add(Kilogramo(nombre=nombre))
        for nombre in ['Efectivo', 'Transferencia', 'Cheque']:
            if not FormaCobro.query.filter_by(nombre=nombre).first():
                db.session.add(FormaCobro(nombre=nombre))
        db.session.commit()
        print("  -> Maestros de productos independientes inicializados.")
        print("Base de datos lista.")

# ==================== CONTEXTO ====================

@app.context_processor
def inject_usuario():
    u = get_usuario_actual()
    allow_registro = os.getenv('ALLOW_REGISTRATION', 'false' if IS_PRODUCTION else 'true').lower() == 'true'
    return {
        'usuario_actual': u,
        'puede_editar': usuario_puede_editar(u),
        'allow_registro': allow_registro,
    }

# ==================== AUTENTICACIÓN ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password) and usuario.activo:
            session['usuario_id'] = usuario.id
            session['usuario_email'] = usuario.email
            destino = request.args.get('next') or request.form.get('next')
            if destino and destino.startswith('/'):
                return redirect(destino)
            return redirect(url_for('portal_erps'))
        else:
            return render_template('login.html', error='Email o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    allow = os.getenv('ALLOW_REGISTRATION', 'false' if IS_PRODUCTION else 'true').lower() == 'true'
    if not allow:
        flash('El registro público está deshabilitado. Solicite acceso al administrador.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not email or not nombre or not password:
            return render_template('registro.html', error='Todos los campos son requeridos')
        
        if password != password_confirm:
            return render_template('registro.html', error='Las contraseñas no coinciden')
        
        if len(password) < 6:
            return render_template('registro.html', error='La contraseña debe tener al menos 6 caracteres')
        
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return render_template('registro.html', error='El email ya está registrado')
        
        usuario = Usuario(
            email=email,
            nombre=nombre,
            rol='usuario',
            activo=True
        )
        usuario.set_password(password)
        
        try:
            db.session.add(usuario)
            db.session.commit()
            
            session['usuario_id'] = usuario.id
            session['usuario_email'] = usuario.email
            
            return redirect(url_for('portal_erps'))
        except Exception as e:
            db.session.rollback()
            return render_template('registro.html', error=f'Error al registrar: {str(e)}')
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==================== ADMINISTRACIÓN Y CONFIGURACIÓN ====================

@app.route('/admin/usuarios')
@usuario_requerido
def admin_usuarios():
    usuario = get_usuario_actual()
    if not usuario.is_admin():
        return redirect(url_for('portal_erps'))
    
    # CORREGIDO: Paginar en lugar de cargar todo
    page = request.args.get('page', 1, type=int)
    usuarios = Usuario.query.paginate(page=page, per_page=20)
    
    idioma = usuario.idioma or 'es'
    etiquetas = {
        'es': {'titulo': 'Administración de Usuarios', 'email': 'Email', 'nombre': 'Nombre', 'rol': 'Rol', 'permisos': 'Permisos', 'estado': 'Estado', 'fecha_creacion': 'Fecha Creación', 'opciones': 'Opciones', 'agregar_usuario': 'Agregar Usuario'},
        'en': {'titulo': 'User Administration', 'email': 'Email', 'nombre': 'Name', 'rol': 'Role', 'permisos': 'Permissions', 'estado': 'Status', 'fecha_creacion': 'Creation Date', 'opciones': 'Options', 'agregar_usuario': 'Add User'}
    }
    etiq = etiquetas.get(idioma, etiquetas['es'])
    
    return render_template('admin/usuarios.html', usuarios=usuarios, usuario=usuario, idioma=idioma, etiq=etiq)

@app.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_usuario():
    usuario = get_usuario_actual()
    if not usuario.is_admin():
        return redirect(url_for('portal_erps'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        nombre = request.form.get('nombre', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', 'usuario')
        permisos = request.form.get('permisos', 'view')
        
        if not email or not nombre or not password:
            return render_template('admin/nuevo_usuario.html', error='Todos los campos son requeridos', usuario=usuario)
        
        if Usuario.query.filter_by(email=email).first():
            return render_template('admin/nuevo_usuario.html', error='El email ya existe', usuario=usuario)
        
        nuevo = Usuario(
            email=email,
            nombre=nombre,
            rol=rol,
            permisos=permisos,
            idioma='es'
        )
        nuevo.set_password(password)
        db.session.add(nuevo)
        db.session.commit()
        
        return redirect(url_for('admin_usuarios'))
    
    idioma = usuario.idioma or 'es'
    return render_template('admin/nuevo_usuario.html', usuario=usuario, idioma=idioma)

@app.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_usuario(usuario_id):
    usuario = get_usuario_actual()
    if not usuario or not usuario.is_admin():
        return redirect(url_for('portal_erps'))

    objetivo = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        objetivo.nombre = request.form.get('nombre', objetivo.nombre).strip()
        objetivo.rol = request.form.get('rol', objetivo.rol)
        objetivo.permisos = request.form.get('permisos', objetivo.permisos)
        objetivo.activo = True if request.form.get('activo') == 'on' else False

        if objetivo.rol not in ['admin', 'usuario']:
            objetivo.rol = 'usuario'
        if objetivo.permisos not in ['view', 'edit']:
            objetivo.permisos = 'view'

        db.session.commit()
        return redirect(url_for('admin_usuarios'))

    return render_template('admin/usuario_form.html', usuario=objetivo, idioma=usuario.idioma or 'es')

@app.route('/admin/usuarios/<int:usuario_id>/resetear-password', methods=['POST'])
@usuario_requerido
def resetear_password_usuario(usuario_id):
    usuario = get_usuario_actual()
    if not usuario or not usuario.is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    objetivo = Usuario.query.get_or_404(usuario_id)
    nueva_pass = 'P@ss' + str(os.urandom(4).hex())
    objetivo.set_password(nueva_pass)
    db.session.commit()

    return jsonify({'success': True, 'password': nueva_pass})

@app.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_usuario(usuario_id):
    usuario = get_usuario_actual()
    if not usuario or not usuario.is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    if usuario.id == usuario_id:
        return jsonify({'error': 'No puede eliminarse a sí mismo'}), 400

    objetivo = Usuario.query.get_or_404(usuario_id)
    db.session.delete(objetivo)
    db.session.commit()

    return jsonify({'success': True})


@app.route('/admin/backups', methods=['GET', 'POST'])
@usuario_requerido
def admin_backups():
    usuario = get_usuario_actual()
    if not usuario or not usuario.is_admin():
        return redirect(url_for('portal_erps'))

    mensaje = None
    error = None
    resultado = None

    if request.method == 'POST':
        try:
            resultado = ejecutar_backups_produccion()
            mensaje = 'Backups creados correctamente (SQLite + Excel).'
        except Exception as e:
            error = str(e)

    backups = listar_backups_recientes(limite=15)
    return render_template(
        'admin/backups.html',
        usuario=usuario,
        mensaje=mensaje,
        error=error,
        resultado=resultado,
        backups=backups,
    )


@app.route('/configuracion')
@usuario_requerido
def configuracion():
    usuario = get_usuario_actual()
    if not usuario:
        return redirect(url_for('login'))

    idioma = usuario.idioma or 'es'
    
    etiquetas = {
        'es': {'titulo': 'Configuración', 'cambiar_contraseña': 'Cambiar Contraseña', 'idioma': 'Idioma', 'email': 'Email', 'nombre': 'Nombre', 'contraseña_actual': 'Contraseña Actual', 'nueva_contraseña': 'Nueva Contraseña', 'confirmar': 'Confirmar Nueva Contraseña', 'actualizar': 'Actualizar'},
        'en': {'titulo': 'Settings', 'cambiar_contraseña': 'Change Password', 'idioma': 'Language', 'email': 'Email', 'nombre': 'Name', 'contraseña_actual': 'Current Password', 'nueva_contraseña': 'New Password', 'confirmar': 'Confirm New Password', 'actualizar': 'Update'}
    }
    etiq = etiquetas.get(idioma, etiquetas['es'])
    
    return render_template('usuario/configuracion.html', usuario=usuario, idioma=idioma, etiq=etiq)

@app.route('/configuracion/cambiar-contraseña', methods=['POST'])
@usuario_requerido
def cambiar_contraseña():
    usuario = get_usuario_actual()
    
    contraseña_actual = request.form.get('contraseña_actual', '')
    nueva_contraseña = request.form.get('nueva_contraseña', '')
    confirmar = request.form.get('confirmar', '')
    
    if not usuario.check_password(contraseña_actual):
        return jsonify({'error': 'Contraseña actual incorrecta'}), 400
    
    if nueva_contraseña != confirmar:
        return jsonify({'error': 'Las contraseñas no coinciden'}), 400
    
    if len(nueva_contraseña) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
    
    usuario.set_password(nueva_contraseña)
    db.session.commit()
    
    return jsonify({'success': True, 'mensaje': 'Contraseña actualizada correctamente'})

@app.route('/configuracion/cambiar-idioma', methods=['POST'])
@usuario_requerido
def cambiar_idioma():
    usuario = get_usuario_actual()
    
    idioma = request.form.get('idioma', 'es')
    if idioma not in ['es', 'en']:
        idioma = 'es'
    
    usuario.idioma = idioma
    db.session.commit()
    
    return jsonify({'success': True, 'idioma': idioma})

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
@usuario_requerido
def index():
    return redirect(url_for('portal_erps'))

@app.route('/portal')
@usuario_requerido
def portal_erps():
    usuario = get_usuario_actual()
    erps = ERP.query.filter_by(activo=True).all()
    
    return render_template('portal.html', erps=erps, usuario=usuario)

@app.route('/erp/<int:erp_id>')
@usuario_requerido
def inicio(erp_id):
    """CORREGIDO: Optimizado sin loops innecesarios"""
    
    erp = ERP.query.get_or_404(erp_id)
    session['erp_id'] = erp_id
    session['erp_nombre'] = erp.nombre
    
    clientes_filtro = request.args.getlist('clientes')
    
    # CORREGIDO: Usar COUNT en SQL en lugar de cargar todo
    total_clientes = db.session.query(func.count(Cliente.id)).scalar()
    total_proveedores = db.session.query(func.count(Proveedor.id)).scalar()
    total_pedidos = db.session.query(func.count(Pedido.id)).filter(Pedido.eliminado == False).scalar()
    
    kpis = _kpis_dashboard()
    gestion = _kpis_gestion()
    deuda_clientes = db.session.query(func.sum(Cliente.saldo)).scalar() or 0
    
    meses_nombres = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    # ===== VENTAS POR MES (OPTIMIZADO) =====
    ventas_por_mes_query = db.session.query(
        extract('month', Pedido.fecha_venta).label('mes'),
        extract('year', Pedido.fecha_venta).label('anio'),
        func.sum(Pedido.precio_venta_total).label('total')
    ).filter(Pedido.fecha_venta.isnot(None))
    
    if clientes_filtro:
        ventas_por_mes_query = ventas_por_mes_query.filter(Pedido.cliente_id.in_(clientes_filtro))
    
    ventas_por_mes_query = ventas_por_mes_query.group_by(
        extract('year', Pedido.fecha_venta),
        extract('month', Pedido.fecha_venta)
    ).order_by(
        extract('year', Pedido.fecha_venta),
        extract('month', Pedido.fecha_venta)
    ).all()
    
    ventas_meses = []
    ventas_valores = []
    for row in ventas_por_mes_query[-12:]:
        mes_nombre = f"{meses_nombres[int(row.mes)]}-{int(row.anio)}"
        ventas_meses.append(mes_nombre)
        ventas_valores.append(float(row.total or 0))
    
    # ===== GANANCIA POR MES (OPTIMIZADO) =====
    ganancia_total_query = db.session.query(
        extract('month', Pedido.fecha_venta).label('mes'),
        extract('year', Pedido.fecha_venta).label('anio'),
        func.sum(Pedido.resultado).label('total')
    ).filter(Pedido.fecha_venta.isnot(None))
    
    if clientes_filtro:
        ganancia_total_query = ganancia_total_query.filter(Pedido.cliente_id.in_(clientes_filtro))
    
    ganancia_total_query = ganancia_total_query.group_by(
        extract('year', Pedido.fecha_venta),
        extract('month', Pedido.fecha_venta)
    ).order_by(
        extract('year', Pedido.fecha_venta),
        extract('month', Pedido.fecha_venta)
    ).all()
    
    ganancia_cobrada_query = db.session.query(
        extract('month', Cobranza.fecha_cobranza).label('mes'),
        extract('year', Cobranza.fecha_cobranza).label('anio'),
        func.sum(Cobranza.monto).label('total')
    ).filter(Cobranza.fecha_cobranza.isnot(None), Cobranza.eliminado == False)
    
    if clientes_filtro:
        ganancia_cobrada_query = ganancia_cobrada_query.filter(Cobranza.cliente_id.in_(clientes_filtro))
    
    ganancia_cobrada_query = ganancia_cobrada_query.group_by(
        extract('year', Cobranza.fecha_cobranza),
        extract('month', Cobranza.fecha_cobranza)
    ).order_by(
        extract('year', Cobranza.fecha_cobranza),
        extract('month', Cobranza.fecha_cobranza)
    ).all()
    
    cobradas_dict = {(int(row.anio), int(row.mes)): float(row.total or 0) for row in ganancia_cobrada_query}
    totales_dict = {(int(row.anio), int(row.mes)): float(row.total or 0) for row in ganancia_total_query}
    
    ganancia_meses = []
    ganancia_cobrada = []
    ganancia_no_cobrada = []
    
    for row in ganancia_total_query[-12:]:
        mes_nombre = f"{meses_nombres[int(row.mes)]}-{int(row.anio)}"
        ganancia_meses.append(mes_nombre)
        
        key = (int(row.anio), int(row.mes))
        total = totales_dict.get(key, 0)
        cobrada = cobradas_dict.get(key, 0)
        no_cobrada = total - cobrada
        
        ganancia_cobrada.append(max(0, cobrada))
        ganancia_no_cobrada.append(max(0, no_cobrada))
    
    # ===== TOP CLIENTES (OPTIMIZADO - SIN LOOP) =====
    top_clientes_query = db.session.query(
        Cliente.nombre,
        func.sum(Pedido.precio_venta_total).label('total_venta')
    ).join(Pedido, Pedido.cliente_id == Cliente.id).group_by(
        Cliente.id
    ).order_by(func.sum(Pedido.precio_venta_total).desc()).limit(5).all()
    
    top_clientes_nombres = [row.nombre for row in top_clientes_query]
    top_clientes_montos = [float(row.total_venta or 0) for row in top_clientes_query]
    
    # ===== TOP PRODUCTOS (OPTIMIZADO) =====
    top_productos_query = db.session.query(
        Producto.nombre,
        func.sum(ItemPedido.cantidad).label('total_cantidad')
    ).join(ItemPedido, ItemPedido.producto_id == Producto.id).group_by(
        Producto.id
    ).order_by(func.sum(ItemPedido.cantidad).desc()).limit(5).all()
    
    top_productos_nombres = [row.nombre for row in top_productos_query]
    top_productos_cantidades = [int(row.total_cantidad or 0) for row in top_productos_query]
    
    todos_clientes = Cliente.query.order_by(Cliente.nombre).all()
    
    # ===== DEUDA POR CLIENTE (OPTIMIZADO CON JOIN - NO LOOP) =====
    clientes_deuda_query = db.session.query(
        Cliente.nombre,
        func.sum(Pedido.precio_venta_total).label('total_facturado'),
        func.sum(Cobranza.monto).label('total_cobrado')
    ).outerjoin(Pedido, Pedido.cliente_id == Cliente.id).outerjoin(
        Cobranza, (Cobranza.cliente_id == Cliente.id) & (Cobranza.eliminado == False)
    ).group_by(Cliente.id).all()
    
    clientes_deuda = []
    for row in clientes_deuda_query:
        total_facturado = float(row.total_facturado or 0)
        if total_facturado > 0:
            total_cobrado = float(row.total_cobrado or 0)
            saldo = total_facturado - total_cobrado
            clientes_deuda.append({
                'nombre': row.nombre,
                'total_facturado': formatear_numero_ar(total_facturado),
                'total_cobrado': formatear_numero_ar(total_cobrado),
                'saldo': formatear_numero_ar(saldo),
            })
    
    context = {
        'total_clientes': total_clientes,
        'total_proveedores': total_proveedores,
        'total_pedidos': total_pedidos,
        'kpis': kpis,
        'gestion': gestion,
        'deuda_clientes': f"{deuda_clientes:,.0f}",
        'ventas_por_mes': {
            'meses': ventas_meses,
            'valores': ventas_valores
        },
        'ganancia_por_mes': {
            'meses': ganancia_meses,
            'cobrada': ganancia_cobrada,
            'no_cobrada': ganancia_no_cobrada
        },
        'top_clientes': {
            'nombres': top_clientes_nombres,
            'montos': top_clientes_montos
        },
        'top_productos': {
            'nombres': top_productos_nombres,
            'cantidades': top_productos_cantidades
        },
        'todos_clientes': todos_clientes,
        'clientes_filtrados': clientes_filtro,
        'clientes_deuda': clientes_deuda,
        'erp': erp,
        'erp_id': erp_id
    }
    
    return render_template('index.html', **context)

# ==================== CUENTAS POR COBRAR ====================

@app.route('/cuentas-por-cobrar')
@usuario_requerido
def cuentas_por_cobrar():
    """CORREGIDO: Sin loops"""
    erp_id = session.get('erp_id')
    if not erp_id:
        return redirect(url_for('portal_erps'))
    
    erp = ERP.query.get_or_404(erp_id)
    
    # CORREGIDO: Usar JOIN + GROUP_BY en SQL (no loop en Python)
    cxc_query = db.session.query(
        Cliente.id,
        Cliente.nombre,
        func.sum(Pedido.precio_venta_total).label('total_venta'),
        func.sum(Cobranza.monto).label('total_cobrado')
    ).outerjoin(Pedido, Pedido.cliente_id == Cliente.id).outerjoin(
        Cobranza, (Cobranza.cliente_id == Cliente.id) & (Cobranza.eliminado == False)
    ).group_by(Cliente.id, Cliente.nombre).all()
    
    cxc_list = []
    total_venta_general = 0
    total_cobrado_general = 0
    
    for row in cxc_query:
        total_venta = float(row.total_venta or 0)
        total_cobrado = float(row.total_cobrado or 0)
        
        if total_venta > 0:
            saldo = total_venta - total_cobrado
            cxc_list.append({
                'cliente_id': row.id,
                'nombre': row.nombre,
                'total_venta': total_venta,
                'total_cobrado': total_cobrado,
                'saldo': saldo,
                'porcentaje_cobrado': (total_cobrado / total_venta * 100) if total_venta > 0 else 0
            })
            total_venta_general += total_venta
            total_cobrado_general += total_cobrado
    
    cxc_list.sort(key=lambda x: x['saldo'], reverse=True)
    
    context = {
        'cxc_list': cxc_list,
        'total_venta': total_venta_general,
        'total_cobrado': total_cobrado_general,
        'total_saldo': total_venta_general - total_cobrado_general,
        'erp': erp,
        'erp_id': erp_id
    }
    
    return render_template('cuentas_por_cobrar.html', **context)

# ==================== CLIENTES ====================

@app.route('/clientes')
@usuario_requerido
def listar_clientes():
    """CORREGIDO: Paginar en lugar de cargar todo"""
    page = request.args.get('page', 1, type=int)
    clientes = Cliente.query.paginate(page=page, per_page=20)
    return render_template('clientes/lista.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_cliente():
    if request.method == 'POST':
        try:
            cliente = Cliente(
                nombre=request.form['nombre'],
                mercado=request.form.get('mercado'),
                puesto=request.form.get('puesto'),
                contacto=request.form.get('contacto'),
                cuit=request.form.get('cuit'),
                telefono=request.form.get('telefono'),
                direccion=request.form.get('direccion'),
                email=request.form.get('email')
            )
            db.session.add(cliente)
            db.session.commit()
            
            backup_excel_opcional()
            
            return redirect(url_for('listar_clientes'))
        except Exception as e:
            return render_template('clientes/formulario.html', error=str(e))
    
    return render_template('clientes/formulario.html')

@app.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.mercado = request.form.get('mercado')
        cliente.puesto = request.form.get('puesto')
        cliente.contacto = request.form.get('contacto')
        cliente.cuit = request.form.get('cuit')
        cliente.telefono = request.form.get('telefono')
        cliente.direccion = request.form.get('direccion')
        cliente.email = request.form.get('email')
        db.session.commit()
        return redirect(url_for('listar_clientes'))
    
    return render_template('clientes/formulario.html', cliente=cliente)

@app.route('/clientes/<int:id>')
@usuario_requerido
def ver_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template('clientes/detalle.html', cliente=cliente)

@app.route('/api/clientes/buscar')
@usuario_requerido
def buscar_clientes():
    query = request.args.get('q', '')
    clientes = Cliente.query.filter(Cliente.nombre.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{'id': c.id, 'nombre': c.nombre} for c in clientes])


@app.route('/api/cliente/<int:cliente_id>/datos')
@usuario_requerido
def api_datos_cliente(cliente_id):
    c = Cliente.query.get_or_404(cliente_id)
    return jsonify({
        'id': c.id, 'nombre': c.nombre, 'mercado': c.mercado, 'puesto': c.puesto,
        'cuit': c.cuit, 'contacto': c.contacto, 'direccion': c.direccion, 'telefono': c.telefono,
    })


def _imputaciones_activas_query(pedido_id=None, excluir_cobranza_id=None):
    """Solo imputaciones de cobranzas no eliminadas."""
    q = CobranzaImputacion.query.join(Cobranza).filter(Cobranza.eliminado == False)
    if pedido_id is not None:
        q = q.filter(CobranzaImputacion.pedido_id == pedido_id)
    if excluir_cobranza_id:
        q = q.filter(CobranzaImputacion.cobranza_id != excluir_cobranza_id)
    return q


def _sum_imputado_pedido(pedido_id):
    return _imputaciones_activas_query(pedido_id=pedido_id).with_entities(
        func.coalesce(func.sum(CobranzaImputacion.monto_imputado), 0)
    ).scalar() or 0


def _saldos_imputacion_pedido(pedido, excluir_cobranza_id=None):
    """Saldos pendientes de pago a proveedor y de comisión por pedido."""
    imps = _imputaciones_activas_query(pedido_id=pedido.id, excluir_cobranza_id=excluir_cobranza_id).all()
    pagado_prov = sum((i.pago_proveedor or 0) for i in imps)
    pagado_com = sum((i.comision or 0) for i in imps)
    saldo_prov = round(pedido.costo_total - pagado_prov, 2)
    saldo_com = round(pedido.resultado - pagado_com, 2)
    return saldo_prov, saldo_com, pagado_prov, pagado_com


def _saldo_pagar_pedido(pedido):
    """Total pendiente de pago (proveedor + comisión) del pedido."""
    saldo_prov, saldo_com, _, _ = _saldos_imputacion_pedido(pedido)
    return round(max(0, saldo_prov) + max(0, saldo_com), 2)


def _sync_cliente_saldo_ventas(cliente_id):
    """Actualiza Cliente.saldo legacy = suma de ventas en pedidos no eliminados."""
    cliente = Cliente.query.get(cliente_id)
    if cliente:
        cliente.saldo = sum(p.precio_venta_total or 0 for p in cliente.pedidos if not p.eliminado)


def _kpis_dashboard():
    """Ventas/costo/resultado y saldos pendientes (solo pedidos activos)."""
    filt = Pedido.eliminado == False
    total_ventas = db.session.query(func.coalesce(func.sum(Pedido.precio_venta_total), 0)).filter(filt).scalar() or 0
    total_costo = db.session.query(func.coalesce(func.sum(Pedido.costo_total), 0)).filter(filt).scalar() or 0
    total_resultado = round(float(total_ventas) - float(total_costo), 2)

    saldo_cobrar = saldo_proveedor = saldo_comision = 0.0
    for p in Pedido.query.filter(filt).all():
        sp, sc, _, _ = _saldos_imputacion_pedido(p)
        saldo_proveedor += max(0.0, sp)
        saldo_comision += max(0.0, sc)
        saldo_cobrar += max(0.0, sp) + max(0.0, sc)

    cob_filt = Cobranza.eliminado == False
    cobrado_total = db.session.query(func.coalesce(func.sum(Cobranza.monto), 0)).filter(cob_filt).scalar() or 0
    cobrado_costo = db.session.query(
        func.coalesce(func.sum(CobranzaImputacion.pago_proveedor), 0)
    ).join(Cobranza).filter(cob_filt).scalar() or 0
    cobrado_comision = db.session.query(
        func.coalesce(func.sum(CobranzaImputacion.comision), 0)
    ).join(Cobranza).filter(cob_filt).scalar() or 0

    return {
        'total_ventas': float(total_ventas),
        'total_costo': float(total_costo),
        'total_resultado': total_resultado,
        'saldo_cobrar': round(saldo_cobrar, 2),
        'saldo_proveedor': round(saldo_proveedor, 2),
        'saldo_comision': round(saldo_comision, 2),
        'cobrado_total': round(float(cobrado_total), 2),
        'cobrado_costo': round(float(cobrado_costo), 2),
        'cobrado_comision': round(float(cobrado_comision), 2),
    }


def _kpis_gestion():
    """Conteos de pedidos por remito, entrega y estado de cobranza."""
    pedidos = Pedido.query.filter_by(eliminado=False).all()
    con_remito = sin_remito = entregados = sin_entregar = 0
    pedidos_cobrados = sin_cobrar = parcial_cobrado = 0

    for p in pedidos:
        if (p.remito or '').strip():
            con_remito += 1
        else:
            sin_remito += 1
        if p.entregado:
            entregados += 1
        else:
            sin_entregar += 1

        sp, sc, pagado_prov, pagado_com = _saldos_imputacion_pedido(p)
        pagado = (pagado_prov or 0) + (pagado_com or 0)
        pendiente = max(0.0, sp) + max(0.0, sc)
        if pendiente <= 0.01 and pagado > 0.01:
            pedidos_cobrados += 1
        elif pagado <= 0.01 and pendiente > 0.01:
            sin_cobrar += 1
        elif pagado > 0.01 and pendiente > 0.01:
            parcial_cobrado += 1

    return {
        'pedidos_totales': len(pedidos),
        'con_remito': con_remito,
        'sin_remito': sin_remito,
        'entregados': entregados,
        'sin_entregar': sin_entregar,
        'pedidos_cobrados': pedidos_cobrados,
        'sin_cobrar': sin_cobrar,
        'parcial_cobrado': parcial_cobrado,
    }


def _aplicar_remito_entregado_pedido(pedido, form):
    pedido.remito = (form.get('remito') or '').strip() or None
    fr = form.get('fecha_remito', '').strip()
    pedido.fecha_remito = datetime.strptime(fr, '%Y-%m-%d').date() if fr else None
    pedido.entregado_opcion = form.get('entregado_opcion') or ''
    fe = form.get('fecha_entrega', '').strip()
    pedido.fecha_entrega = datetime.strptime(fe, '%Y-%m-%d').date() if fe else None
    pedido.entregado = pedido.entregado_opcion == 'SI' and pedido.fecha_entrega is not None


def _ruta_absoluta_adjunto_remito(rel_path):
    if not rel_path:
        return None
    return os.path.join(basedir, 'uploads', rel_path.replace('/', os.sep))


def _eliminar_archivo_adjunto_remito(pedido):
    if not pedido or not pedido.remito_adjunto_path:
        return
    abs_path = _ruta_absoluta_adjunto_remito(pedido.remito_adjunto_path)
    if abs_path and os.path.isfile(abs_path):
        try:
            os.remove(abs_path)
        except OSError:
            pass
    pedido.remito_adjunto_path = None
    pedido.remito_adjunto_nombre = None


def _extension_adjunto_permitida(filename):
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in REMITO_ADJUNTO_EXT


def _procesar_adjunto_remito(pedido, form, files):
    """Guarda PDF/foto del remito en uploads/remitos/ y registra ruta en el pedido."""
    if form.get('eliminar_remito_adjunto') == '1':
        _eliminar_archivo_adjunto_remito(pedido)
        return
    archivo = files.get('remito_adjunto') if files else None
    if not archivo or not getattr(archivo, 'filename', None):
        return
    nombre_orig = secure_filename(archivo.filename) or 'adjunto'
    if not _extension_adjunto_permitida(nombre_orig):
        raise ValueError('Formato no permitido. Use PDF o imagen (JPG, PNG, etc.).')
    archivo.seek(0, os.SEEK_END)
    tam = archivo.tell()
    archivo.seek(0)
    if tam > REMITO_ADJUNTO_MAX_MB * 1024 * 1024:
        raise ValueError(f'El archivo supera {REMITO_ADJUNTO_MAX_MB} MB.')
    os.makedirs(UPLOAD_REMITOS_DIR, exist_ok=True)
    _eliminar_archivo_adjunto_remito(pedido)
    ext = nombre_orig.rsplit('.', 1)[-1].lower()
    nombre_disk = f"pedido_{pedido.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    abs_path = os.path.join(UPLOAD_REMITOS_DIR, nombre_disk)
    archivo.save(abs_path)
    pedido.remito_adjunto_path = f"remitos/{nombre_disk}"
    pedido.remito_adjunto_nombre = nombre_orig


def _estado_pedido_lista(pedido):
    saldo_pagar = _saldo_pagar_pedido(pedido)
    tiene_remito = bool((pedido.remito or '').strip())
    entregado_si = pedido.entregado_opcion == 'SI' and pedido.fecha_entrega is not None
    completado = saldo_pagar <= 0.01 and tiene_remito and entregado_si
    return {
        'saldo_pagar': saldo_pagar,
        'remito_col': 'SI' if tiene_remito else 'NO',
        'entregado_col': 'SI' if entregado_si else '',
        'estado_col': 'Completado' if completado else 'Incompleto',
        'completado': completado,
    }


def _pedido_a_dict_imputacion(p, excluir_cobranza_id=None):
    saldo_prov, saldo_com, _, _ = _saldos_imputacion_pedido(p, excluir_cobranza_id)
    if saldo_prov <= 0.01 and saldo_com <= 0.01:
        return None
    proveedores = set()
    lineas = []
    for it in p.items:
        prod = it.producto
        prov_nombre = prod.proveedor.nombre if prod and prod.proveedor else ''
        if prov_nombre:
            proveedores.add(prov_nombre)
        lineas.append({
            'proveedor': prov_nombre,
            'fruta': prod.fruta if prod else '',
            'variedad': prod.variedad or '',
            'clasificacion': prod.clasificacion or '',
            'marca': prod.marca or '',
        })
    return {
        'id': p.id,
        'numero': p.numero,
        'fecha': p.fecha_venta.isoformat() if p.fecha_venta else '',
        'fecha_venta_ts': p.fecha_venta.toordinal() if p.fecha_venta else 0,
        'costo_total': round(p.costo_total, 2),
        'rtdo_comision': round(p.resultado, 2),
        'precio_total': round(p.precio_venta_total, 2),
        'saldo_proveedor': max(0, saldo_prov),
        'saldo_comision': max(0, saldo_com),
        'saldo_pendiente': round(max(0, saldo_prov) + max(0, saldo_com), 2),
        'proveedores': ', '.join(sorted(proveedores)),
        'lineas': lineas,
        'resumen_frutas': ', '.join({ln['fruta'] for ln in lineas if ln.get('fruta')}),
    }


@app.route('/api/cliente/<int:cliente_id>/pedidos-pendientes')
@usuario_requerido
def api_pedidos_pendientes(cliente_id):
    excluir = request.args.get('excluir_cobranza_id', type=int)
    excluir_pedidos = request.args.get('excluir_pedidos', '')
    ids_excluir = {int(x) for x in excluir_pedidos.split(',') if x.strip().isdigit()}

    pedidos = Pedido.query.filter_by(cliente_id=cliente_id, eliminado=False).order_by(Pedido.fecha_venta.asc()).all()
    resultado = []
    for p in pedidos:
        if p.id in ids_excluir:
            continue
        data = _pedido_a_dict_imputacion(p, excluir)
        if data:
            resultado.append(data)
    return jsonify(resultado)


def _imputaciones_desde_cobranza(cobranza):
    """Imputaciones existentes para editar, ordenadas de más viejo a más nuevo."""
    resultado = []
    imps = sorted(cobranza.imputaciones, key=lambda i: (i.pedido.fecha_venta or date.min, i.id))
    for imp in imps:
        p = imp.pedido
        saldo_prov, saldo_com, _, _ = _saldos_imputacion_pedido(p, cobranza.id)
        max_prov = round(saldo_prov + (imp.pago_proveedor or 0), 2)
        max_com = round(saldo_com + (imp.comision or 0), 2)
        base = _pedido_a_dict_imputacion(p, cobranza.id) or {
            'id': p.id, 'pedido_id': p.id, 'numero': p.numero,
            'fecha': p.fecha_venta.isoformat() if p.fecha_venta else '',
            'fecha_venta_ts': p.fecha_venta.toordinal() if p.fecha_venta else 0,
            'costo_total': round(p.costo_total, 2),
            'rtdo_comision': round(p.resultado, 2),
            'precio_total': round(p.precio_venta_total, 2),
            'saldo_proveedor': max_prov, 'saldo_comision': max_com,
            'proveedores': '', 'resumen_frutas': '', 'lineas': [],
        }
        base['pedido_id'] = p.id
        base['pago_proveedor'] = round(imp.pago_proveedor or 0, 2)
        base['comision'] = round(imp.comision or 0, 2)
        base['max_proveedor'] = max_prov
        base['max_comision'] = max_com
        resultado.append(base)
    return resultado


def _buscar_producto_pedido(proveedor_id, fruta, variedad=None, clasificacion=None, envase=None, kilogramo=None, marca=None):
    """Busca producto coincidiendo con campos vacíos como NULL o cadena vacía."""
    if not proveedor_id or not _txt(fruta):
        return None
    q = Producto.query.filter_by(proveedor_id=int(proveedor_id), fruta=_txt(fruta), activo=True)
    for col, val in (
        ('variedad', variedad), ('clasificacion', clasificacion),
        ('envase', envase), ('kilogramo', kilogramo), ('marca', marca),
    ):
        v = _txt(val)
        if v:
            q = q.filter(getattr(Producto, col) == v)
        else:
            q = q.filter(or_(getattr(Producto, col).is_(None), getattr(Producto, col) == ''))
    return q.first()


def _indices_lineas_pedido(form):
    """Índices de líneas enviadas (por campos bultos_N o proveedor_id_N)."""
    indices = set()
    for key in form.keys():
        if key.startswith('bultos_'):
            try:
                indices.add(int(key.split('_', 1)[1]))
            except ValueError:
                pass
        elif key.startswith('proveedor_id_'):
            try:
                indices.add(int(key.split('_', 2)[2]))
            except (ValueError, IndexError):
                pass
    if not indices:
        try:
            n = int(form.get('item_count', 0) or 0)
            indices = set(range(n))
        except ValueError:
            pass
    return sorted(indices)


def _resolver_producto_fila(form, i):
    pid = form.get(f'producto_id_{i}')
    if pid:
        return int(pid)
    proveedor_id = form.get(f'proveedor_id_{i}')
    fruta = form.get(f'fruta_{i}')
    if not proveedor_id or not fruta:
        return None
    producto = _buscar_producto_pedido(
        proveedor_id, fruta,
        form.get(f'variedad_{i}'),
        form.get(f'clasificacion_{i}'),
        form.get(f'envase_{i}'),
        form.get(f'kilogramo_{i}'),
        form.get(f'marca_{i}'),
    )
    return producto.id if producto else None


def _procesar_lineas_pedido(form, pedido_id):
    """Procesa líneas del pedido: bultos obligatorios, precios desde cotización."""
    indices = _indices_lineas_pedido(form)
    costo_total = 0
    precio_venta_total = 0
    lineas_ok = 0
    for i in indices:
        producto_id = _resolver_producto_fila(form, i)
        bultos_raw = form.get(f'bultos_{i}', '')
        bultos = int(bultos_raw or 0)
        if bultos <= 0:
            if not producto_id and not form.get(f'proveedor_id_{i}') and not form.get(f'fruta_{i}'):
                continue
            raise ValueError(f'La línea {lineas_ok + 1} requiere bultos (entero positivo)')
        if not producto_id:
            raise ValueError(
                f'La línea {lineas_ok + 1} no tiene un producto válido. '
                'Verificá proveedor, fruta, variedad, clasificación, envase, kg y marca.'
            )
        lineas_ok += 1
        pallets = form.get(f'pallets_{i}')
        pallets = int(pallets) if pallets and str(pallets).strip() else None
        costo_unitario = parse_numero_ar(form.get(f'costo_unitario_{i}', 0))
        precio_unitario = parse_numero_ar(form.get(f'precio_unitario_{i}', 0))
        costo_total_linea = costo_unitario * bultos
        precio_total_linea = precio_unitario * bultos
        rtdo = precio_total_linea - costo_total_linea
        producto = Producto.query.get(producto_id)
        item = ItemPedido(
            pedido_id=pedido_id,
            producto_id=producto_id,
            pallets=pallets or 0,
            bultos=bultos,
            kg=_txt(form.get(f'kilogramo_{i}')) or (producto.kilogramo if producto else None),
            cantidad=bultos,
            unidad='Bultos',
            costo_unitario=costo_unitario,
            precio_unitario=precio_unitario,
            costo_total=costo_total_linea,
            precio_total=precio_total_linea,
            comision=rtdo,
            resultado=rtdo,
        )
        db.session.add(item)
        costo_total += costo_total_linea
        precio_venta_total += precio_total_linea
    return costo_total, precio_venta_total


def _validar_mismo_proveedor_pedido(form):
    """Todos los renglones del pedido deben compartir el mismo proveedor de producto."""
    proveedores = set()
    for i in _indices_lineas_pedido(form):
        pid = form.get(f'proveedor_id_{i}')
        if pid and str(pid) != '__nuevo__':
            proveedores.add(int(pid))
    if len(proveedores) > 1:
        raise ValueError('Cada pedido tiene que tener el mismo proveedor')


def _leer_descuento_pedido_form(form):
    activo = form.get('descuento_activo') in ('on', '1', 'true')
    if not activo:
        return 0.0, 0.0
    desc_costo = max(0.0, parse_numero_ar(form.get('descuento_costo', 0)))
    desc_comision = max(0.0, parse_numero_ar(form.get('descuento_comision', 0)))
    return desc_costo, desc_comision


def _calcular_totales_con_descuento(costo_bruto, venta_bruta, desc_costo=0, desc_comision=0):
    """Descuentos separados en costo proveedor y comisión; venta final = costo + comisión."""
    comision_bruta = float(venta_bruta) - float(costo_bruto)
    costo = max(0.0, float(costo_bruto) - max(0.0, float(desc_costo or 0)))
    comision = max(0.0, comision_bruta - max(0.0, float(desc_comision or 0)))
    venta = costo + comision
    return round(costo, 2), round(venta, 2), round(comision, 2)


def _guardar_totales_pedido(pedido, form, costo_bruto, venta_bruta):
    desc_costo, desc_comision = _leer_descuento_pedido_form(form)
    pedido.descuento_costo = desc_costo
    pedido.descuento_comision = desc_comision
    pedido.descuento_monto = round(desc_costo + desc_comision, 2)
    pedido.descuento_sobre_costo = desc_costo > 0
    pedido.descuento_sobre_comision = desc_comision > 0
    costo, venta, comision = _calcular_totales_con_descuento(
        costo_bruto, venta_bruta, desc_costo, desc_comision
    )
    pedido.costo_total = costo
    pedido.precio_venta_total = venta
    pedido.resultado = comision
    pedido.comision = comision
    return venta


def _siguiente_numero_pedido():
    ultimo = Pedido.query.order_by(Pedido.id.desc()).first()
    n = 1
    if ultimo and ultimo.numero:
        import re
        m = re.search(r'(\d+)\s*$', ultimo.numero)
        if m:
            n = int(m.group(1)) + 1
    return str(n)


def _guardar_cobranza_desde_form(form, cobranza=None):
    cliente_id = int(form['cliente_id'])
    fecha = datetime.strptime(form.get('fecha_cobranza'), '%Y-%m-%d').date() if form.get('fecha_cobranza') else date.today()

    lineas_data = []
    i = 0
    while form.get(f'forma_{i}') is not None or form.get(f'monto_{i}') is not None:
        forma = form.get(f'forma_{i}', '').strip()
        monto_str = form.get(f'monto_{i}', '')
        if forma and monto_str:
            lineas_data.append((forma, parse_numero_ar(monto_str)))
        i += 1
    if not lineas_data:
        raise ValueError('Debe cargar al menos una línea de cobro (forma y monto)')

    total_cobrado = sum(m for _, m in lineas_data)

    if cobranza is None:
        cobranza = Cobranza(cliente_id=cliente_id, fecha_cobranza=fecha, monto=total_cobrado)
        db.session.add(cobranza)
        db.session.flush()
    else:
        CobranzaLinea.query.filter_by(cobranza_id=cobranza.id).delete()
        CobranzaImputacion.query.filter_by(cobranza_id=cobranza.id).delete()
        cobranza.cliente_id = cliente_id
        cobranza.fecha_cobranza = fecha
        cobranza.monto = total_cobrado

    for forma, monto in lineas_data:
        db.session.add(CobranzaLinea(cobranza_id=cobranza.id, forma=forma, monto=monto))
    cobranza.metodo = lineas_data[0][0]

    total_imputado = 0
    j = 0
    while form.get(f'imp_pedido_id_{j}') is not None:
        pedido_id = form.get(f'imp_pedido_id_{j}')
        if pedido_id:
            pago_prov = parse_numero_ar(form.get(f'imp_pago_proveedor_{j}', 0))
            comision = parse_numero_ar(form.get(f'imp_comision_{j}', 0))
            monto_imp = pago_prov + comision
            if monto_imp > 0:
                pedido = Pedido.query.get(int(pedido_id))
                saldo_prov, saldo_com, _, _ = _saldos_imputacion_pedido(pedido, cobranza.id)
                if pago_prov > saldo_prov + 0.01:
                    raise ValueError(f'Pedido {pedido.numero}: pago proveedor supera saldo (${saldo_prov:.2f})')
                if comision > saldo_com + 0.01:
                    raise ValueError(f'Pedido {pedido.numero}: comisión supera saldo (${saldo_com:.2f})')
                db.session.add(CobranzaImputacion(
                    cobranza_id=cobranza.id, pedido_id=pedido.id,
                    monto_imputado=monto_imp, pago_proveedor=pago_prov, comision=comision
                ))
                total_imputado += monto_imp
        j += 1

    if total_imputado > total_cobrado + 0.01:
        raise ValueError('El total imputado no puede superar el total cobrado')

    return cobranza

# ==================== PROVEEDORES ====================

@app.route('/proveedores')
@usuario_requerido
def listar_proveedores():
    """CORREGIDO: Paginar"""
    page = request.args.get('page', 1, type=int)
    proveedores = Proveedor.query.paginate(page=page, per_page=20)
    return render_template('proveedores/lista.html', proveedores=proveedores)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_proveedor():
    if request.method == 'POST':
        try:
            proveedor = Proveedor(
                nombre=request.form['nombre'],
                razon_social=request.form.get('razon_social'),
                cuit=request.form.get('cuit'),
                direccion=request.form.get('direccion'),
                provincia=request.form.get('provincia')
            )
            db.session.add(proveedor)
            db.session.flush()

            contacto_nombres = request.form.getlist('contacto_nombre[]')
            contacto_roles = request.form.getlist('contacto_rol[]')
            contacto_telefonos = request.form.getlist('contacto_telefono[]')
            contacto_emails = request.form.getlist('contacto_email[]')

            contactos_creados = []
            for idx, nombre in enumerate(contacto_nombres):
                if not nombre.strip():
                    continue
                contacto = ProveedorContacto(
                    proveedor_id=proveedor.id,
                    nombre=nombre.strip(),
                    rol=contacto_roles[idx].strip() if idx < len(contacto_roles) else None,
                    telefono=contacto_telefonos[idx].strip() if idx < len(contacto_telefonos) else None,
                    email=contacto_emails[idx].strip() if idx < len(contacto_emails) else None,
                    contacto_logistico=f'contacto_logistico_{idx}' in request.form
                )
                db.session.add(contacto)
                contactos_creados.append(contacto)

            if contactos_creados and not any(c.contacto_logistico for c in contactos_creados):
                raise ValueError('Al menos uno de los contactos debe tener marcado "Contacto Logístico"')

            db.session.commit()
            return redirect(url_for('listar_proveedores'))
        except Exception as e:
            db.session.rollback()
            # Reconstruir contactos temporales para mantenerlos en el formulario
            contacto_nombres = request.form.getlist('contacto_nombre[]')
            contacto_roles = request.form.getlist('contacto_rol[]')
            contacto_telefonos = request.form.getlist('contacto_telefono[]')
            contacto_emails = request.form.getlist('contacto_email[]')
            
            # Crear objetos temporales con los datos del formulario
            class ContactoTemp:
                def __init__(self, nombre, rol, telefono, email, logistico):
                    self.nombre = nombre
                    self.rol = rol
                    self.telefono = telefono
                    self.email = email
                    self.contacto_logistico = logistico
            
            contactos_temp = []
            for idx, nombre in enumerate(contacto_nombres):
                if nombre.strip():
                    contactos_temp.append(ContactoTemp(
                        nombre=nombre.strip(),
                        rol=contacto_roles[idx].strip() if idx < len(contacto_roles) else '',
                        telefono=contacto_telefonos[idx].strip() if idx < len(contacto_telefonos) else '',
                        email=contacto_emails[idx].strip() if idx < len(contacto_emails) else '',
                        logistico=f'contacto_logistico_{idx}' in request.form
                    ))
            
            # Crear proveedor temporal para mostrar datos
            temp_prov = Proveedor(
                nombre=request.form.get('nombre', ''),
                razon_social=request.form.get('razon_social', ''),
                cuit=request.form.get('cuit', ''),
                direccion=request.form.get('direccion', ''),
                provincia=request.form.get('provincia', '')
            )
            temp_prov.contactos = contactos_temp
            return render_template('proveedores/formulario.html', proveedor=temp_prov, error=str(e))
    
    return render_template('proveedores/formulario.html')

@app.route('/api/proveedores/buscar')
@usuario_requerido
def buscar_proveedores():
    query = request.args.get('q', '')
    proveedores = Proveedor.query.filter(Proveedor.nombre.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{'id': p.id, 'nombre': p.nombre} for p in proveedores])


# ==================== PROVEEDORES LOGÍSTICOS ====================

@app.route('/proveedores-logisticos')
@usuario_requerido
def listar_proveedores_logisticos():
    proveedores = ProveedorLogistico.query.order_by(ProveedorLogistico.nombre).all()
    return render_template('proveedores_logisticos/lista.html', proveedores=proveedores)


@app.route('/proveedores-logisticos/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_proveedor_logistico():
    if request.method == 'POST':
        try:
            prov = ProveedorLogistico(
                nombre=request.form['nombre'].strip(),
                cuit=request.form.get('cuit'),
                telefono=request.form.get('telefono'),
                email=request.form.get('email'),
            )
            db.session.add(prov)
            db.session.commit()
            return redirect(url_for('listar_proveedores_logisticos'))
        except Exception as e:
            db.session.rollback()
            return render_template('proveedores_logisticos/formulario.html', error=str(e))
    return render_template('proveedores_logisticos/formulario.html')


@app.route('/proveedores-logisticos/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_proveedor_logistico(id):
    prov = ProveedorLogistico.query.get_or_404(id)
    if request.method == 'POST':
        try:
            prov.nombre = request.form['nombre'].strip()
            prov.cuit = request.form.get('cuit')
            prov.telefono = request.form.get('telefono')
            prov.email = request.form.get('email')
            db.session.commit()
            return redirect(url_for('listar_proveedores_logisticos'))
        except Exception as e:
            db.session.rollback()
            return render_template('proveedores_logisticos/formulario.html', proveedor=prov, error=str(e))
    return render_template('proveedores_logisticos/formulario.html', proveedor=prov)


@app.route('/proveedores-logisticos/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_proveedor_logistico(id):
    prov = ProveedorLogistico.query.get_or_404(id)
    try:
        db.session.delete(prov)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': True})


# ==================== PRODUCTOS ====================

def _datos_maestros_producto():
    return {
        'frutas': Fruta.query.filter_by(activo=True).order_by(Fruta.nombre).all(),
        'variedades': Variedad.query.filter_by(activo=True).order_by(Variedad.nombre).all(),
        'clasificaciones': Clasificacion.query.filter_by(activo=True).order_by(Clasificacion.nombre).all(),
        'envases': Envase.query.filter_by(activo=True).order_by(Envase.nombre).all(),
        'marcas': Marca.query.filter_by(activo=True).order_by(Marca.nombre).all(),
        'kilogramos': Kilogramo.query.filter_by(activo=True).order_by(Kilogramo.nombre).all(),
    }


def _txt(val):
    v = (val or '').strip()
    return v if v else None


def _crear_o_actualizar_producto(proveedor_id, fruta, variedad, clasificacion, envase, kilogramo, marca, producto_id=None):
    fruta = _txt(fruta)
    if not fruta:
        raise ValueError('La fruta es obligatoria')
    variedad, clasificacion, envase, kilogramo, marca = map(_txt, (variedad, clasificacion, envase, kilogramo, marca))
    nombre = fruta
    filtros = dict(
        proveedor_id=proveedor_id, fruta=fruta,
        variedad=variedad, clasificacion=clasificacion,
        envase=envase, kilogramo=kilogramo, marca=marca
    )
    existente = Producto.query.filter_by(**filtros).first()
    if existente and (not producto_id or existente.id != producto_id):
        raise ValueError('Ya existe esa combinación de producto para el proveedor')
    if producto_id:
        producto = Producto.query.get_or_404(producto_id)
        producto.proveedor_id = proveedor_id
        producto.fruta = fruta
        producto.variedad = variedad or None
        producto.clasificacion = clasificacion or None
        producto.envase = envase or None
        producto.kilogramo = kilogramo or None
        producto.marca = marca or None
        producto.nombre = nombre
        return producto
    producto = Producto(nombre=nombre, **filtros)
    db.session.add(producto)
    return producto


@app.route('/productos')
@usuario_requerido
def listar_productos():
    proveedores = Proveedor.query.filter_by(activo=True).order_by(Proveedor.nombre).all()
    productos_por_proveedor = {}
    for p in Producto.query.filter_by(activo=True).order_by(Producto.fruta).all():
        productos_por_proveedor.setdefault(p.proveedor_id, []).append(p)
    return render_template('productos/lista.html', proveedores=proveedores, productos_por_proveedor=productos_por_proveedor)


@app.route('/productos/proveedor/<int:proveedor_id>', methods=['GET', 'POST'])
@usuario_requerido
def gestionar_productos_proveedor(proveedor_id):
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    maestros = _datos_maestros_producto()
    productos = Producto.query.filter_by(proveedor_id=proveedor_id, activo=True).order_by(Producto.fruta).all()

    if request.method == 'POST':
        try:
            indices = set()
            for key in request.form:
                if key.startswith('fruta_'):
                    indices.add(key.split('_', 1)[1])
            for idx in sorted(indices, key=lambda x: int(x) if x.isdigit() else x):
                fruta = request.form.get(f'fruta_{idx}')
                if not fruta:
                    continue
                pid = request.form.get(f'producto_id_{idx}')
                _crear_o_actualizar_producto(
                    proveedor_id,
                    fruta,
                    request.form.get(f'variedad_{idx}'),
                    request.form.get(f'clasificacion_{idx}'),
                    request.form.get(f'envase_{idx}'),
                    request.form.get(f'kilogramo_{idx}'),
                    request.form.get(f'marca_{idx}'),
                    int(pid) if pid else None
                )
            db.session.commit()
            return redirect(url_for('listar_productos'))
        except Exception as e:
            db.session.rollback()
            return render_template('productos/gestionar.html', proveedor=proveedor, productos=productos, error=str(e), **maestros)

    return render_template('productos/gestionar.html', proveedor=proveedor, productos=productos, **maestros)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_producto():
    proveedor_id = request.args.get('proveedor_id', type=int)
    if proveedor_id:
        return redirect(url_for('gestionar_productos_proveedor', proveedor_id=proveedor_id))
    proveedores = Proveedor.query.filter_by(activo=True).order_by(Proveedor.nombre).all()
    return render_template('productos/elegir_proveedor.html', proveedores=proveedores)


def _resolver_producto_id_desde_form(form):
    proveedor_id = form.get('proveedor_id')
    fruta = form.get('fruta')
    if not proveedor_id or not fruta:
        raise ValueError('Seleccione proveedor y fruta')
    producto = Producto.query.filter_by(
        proveedor_id=proveedor_id,
        fruta=fruta,
        variedad=form.get('variedad') or None,
        clasificacion=form.get('clasificacion') or None,
        envase=form.get('envase') or None,
        kilogramo=form.get('kilogramo') or None,
        marca=form.get('marca') or None,
    ).first()
    if not producto:
        raise ValueError('No existe esa combinación en Productos. Carguela primero en la tabla Productos.')
    return producto.id


def _validar_cotizacion_unica(producto_id, fecha_desde, fecha_hasta, excluir_id=None):
    q = Cotizacion.query.filter(
        Cotizacion.producto_id == producto_id,
        Cotizacion.fecha_desde == fecha_desde,
        Cotizacion.fecha_hasta == fecha_hasta,
    )
    if excluir_id:
        q = q.filter(Cotizacion.id != excluir_id)
    if q.first():
        raise ValueError('Ya existe una cotización con la misma combinación y vigencia')


@app.route('/api/productos/opciones')
@usuario_requerido
def api_opciones_productos():
    """Opciones filtradas en cascada para pedidos y cotizaciones."""
    proveedor_id = request.args.get('proveedor_id', type=int)
    fruta = request.args.get('fruta')
    variedad = request.args.get('variedad')
    clasificacion = request.args.get('clasificacion')
    envase = request.args.get('envase')
    kilogramo = request.args.get('kilogramo')
    campo = request.args.get('campo', 'fruta')

    q = Producto.query.filter_by(activo=True)
    if proveedor_id:
        q = q.filter_by(proveedor_id=proveedor_id)
    if fruta:
        q = q.filter_by(fruta=fruta)
    if variedad:
        q = q.filter_by(variedad=variedad)
    if clasificacion:
        q = q.filter_by(clasificacion=clasificacion)
    if envase:
        q = q.filter_by(envase=envase)
    if kilogramo:
        q = q.filter_by(kilogramo=kilogramo)

    productos = q.all()
    mapa = {
        'fruta': 'fruta', 'variedad': 'variedad', 'clasificacion': 'clasificacion',
        'envase': 'envase', 'kilogramo': 'kilogramo', 'marca': 'marca'
    }
    attr = mapa.get(campo, 'fruta')
    valores = sorted({getattr(p, attr) for p in productos if getattr(p, attr)})
    return jsonify(valores)


@app.route('/api/cotizaciones/vigente')
@usuario_requerido
def api_cotizacion_vigente():
    fecha_str = (request.args.get('fecha') or '').strip()
    if fecha_str:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    else:
        fecha = date.today()
    producto = _buscar_producto_pedido(
        request.args.get('proveedor_id', type=int),
        request.args.get('fruta'),
        request.args.get('variedad'),
        request.args.get('clasificacion'),
        request.args.get('envase'),
        request.args.get('kilogramo'),
        request.args.get('marca'),
    )
    if not producto:
        return jsonify({'encontrada': False})
    cot = Cotizacion.query.filter(
        Cotizacion.producto_id == producto.id,
        Cotizacion.fecha_desde <= fecha,
        Cotizacion.fecha_hasta >= fecha,
        Cotizacion.activo == True
    ).order_by(Cotizacion.fecha_desde.desc()).first()
    if not cot:
        return jsonify({'encontrada': False, 'producto_id': producto.id})
    return jsonify({
        'encontrada': True,
        'producto_id': producto.id,
        'costo_unitario': cot.costo_unitario,
        'precio_unitario': cot.precio_unitario,
        'margen': cot.margen_ganancia,
    })


# ==================== COTIZACIONES ====================

@app.route('/cotizaciones')
@usuario_requerido
def listar_cotizaciones():
    page = request.args.get('page', 1, type=int)
    estado = (request.args.get('estado') or 'activos').strip().lower()  # todos|activos|inactivos
    fecha = request.args.get('fecha', '').strip()  # YYYY-MM-DD o vacío
    fruta = (request.args.get('fruta') or '').strip()
    variedad = (request.args.get('variedad') or '').strip()
    clasificacion = (request.args.get('clasificacion') or '').strip()
    envase = (request.args.get('envase') or '').strip()
    try:
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date() if fecha else None
    except Exception:
        fecha_dt = None

    hoy = date.today()
    ref = fecha_dt or hoy

    q = Cotizacion.query.join(Producto)
    # filtros por campos del producto
    if fruta:
        q = q.filter(func.lower(Producto.fruta) == fruta.lower())
    if variedad:
        q = q.filter(func.lower(func.coalesce(Producto.variedad, "")) == variedad.lower())
    if clasificacion:
        q = q.filter(func.lower(func.coalesce(Producto.clasificacion, "")) == clasificacion.lower())
    if envase:
        q = q.filter(func.lower(func.coalesce(Producto.envase, "")) == envase.lower())

    vigente_ref = (Cotizacion.activo == True) & (Cotizacion.fecha_desde <= ref) & (Cotizacion.fecha_hasta >= ref)
    if estado == 'activos':
        q = q.filter(vigente_ref)
    elif estado == 'inactivos':
        q = q.filter(~vigente_ref)

    cotizaciones = q.order_by(Cotizacion.fecha_hasta.desc(), Cotizacion.fecha_desde.desc()).paginate(page=page, per_page=50)
    config = ConfigMargen.query.first()
    margen_default = config.margen_default if config else 30
    filas = []
    for c in cotizaciones.items:
        vigente = bool(c.activo and c.fecha_desde and c.fecha_hasta and c.fecha_desde <= ref <= c.fecha_hasta)
        filas.append({'cot': c, 'vigente': vigente})

    # opciones dropdown
    frutas = [r[0] for r in db.session.query(Producto.fruta).distinct().order_by(Producto.fruta).all() if r and r[0]]
    variedades = [r[0] for r in db.session.query(Producto.variedad).distinct().order_by(Producto.variedad).all() if r and r[0]]
    clasifs = [r[0] for r in db.session.query(Producto.clasificacion).distinct().order_by(Producto.clasificacion).all() if r and r[0]]
    envases = [r[0] for r in db.session.query(Producto.envase).distinct().order_by(Producto.envase).all() if r and r[0]]

    return render_template(
        'cotizaciones/lista.html',
        cotizaciones=cotizaciones,
        filas=filas,
        margen_default=margen_default,
        filtros={'estado': estado, 'fecha': fecha, 'fruta': fruta, 'variedad': variedad, 'clasificacion': clasificacion, 'envase': envase},
        frutas=frutas,
        variedades=variedades,
        clasificaciones=clasifs,
        envases=envases,
        hoy=hoy,
        ref=ref,
    )

@app.route('/cotizaciones/nueva', methods=['GET', 'POST'])
@usuario_requerido
def nueva_cotizacion():
    productos = Producto.query.filter_by(activo=True).all()
    config = ConfigMargen.query.first()
    margen_default = config.margen_default if config else 30
    
    if request.method == 'POST':
        try:
            producto_id = request.form.get('producto_id')
            if not producto_id:
                producto_id = _resolver_producto_id_desde_form(request.form)
            fecha_desde = datetime.strptime(request.form.get('fecha_desde'), '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(request.form.get('fecha_hasta'), '%Y-%m-%d').date()
            costo = parse_numero_ar(request.form.get('costo_unitario', 0))
            precio = parse_numero_ar(request.form.get('precio_unitario', 0))
            _validar_cotizacion_unica(producto_id, fecha_desde, fecha_hasta)
            cotizacion = Cotizacion(
                producto_id=producto_id,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                costo_unitario=costo,
                precio_unitario=precio,
                activo=True
            )
            cotizacion.calcular_margen_desde_precio()
            db.session.add(cotizacion)
            db.session.commit()
            return redirect(url_for('listar_cotizaciones'))
        except Exception as e:
            db.session.rollback()
            return render_template('cotizaciones/formulario.html', productos=productos, margen_default=margen_default,
                                   proveedores=Proveedor.query.filter_by(activo=True).all(), error=str(e))
    
    return render_template('cotizaciones/formulario.html', productos=productos, margen_default=margen_default,
                           proveedores=Proveedor.query.filter_by(activo=True).all())

@app.route('/cotizaciones/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_cotizacion(id):
    cotizacion = Cotizacion.query.get_or_404(id)
    productos = Producto.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        try:
            producto_id = request.form.get('producto_id') or _resolver_producto_id_desde_form(request.form)
            fecha_desde = datetime.strptime(request.form.get('fecha_desde'), '%Y-%m-%d').date()
            fecha_hasta = datetime.strptime(request.form.get('fecha_hasta'), '%Y-%m-%d').date()
            _validar_cotizacion_unica(producto_id, fecha_desde, fecha_hasta, excluir_id=cotizacion.id)
            cotizacion.producto_id = producto_id
            cotizacion.fecha_desde = fecha_desde
            cotizacion.fecha_hasta = fecha_hasta
            cotizacion.costo_unitario = parse_numero_ar(request.form.get('costo_unitario', 0))
            cotizacion.precio_unitario = parse_numero_ar(request.form.get('precio_unitario', 0))
            cotizacion.calcular_margen_desde_precio()
            db.session.commit()
            return redirect(url_for('listar_cotizaciones'))
        except Exception as e:
            db.session.rollback()
            return render_template('cotizaciones/formulario.html', cotizacion=cotizacion, productos=productos,
                                   proveedores=Proveedor.query.filter_by(activo=True).all(), error=str(e))
    
    return render_template('cotizaciones/formulario.html', cotizacion=cotizacion, productos=productos,
                           proveedores=Proveedor.query.filter_by(activo=True).all())

@app.route('/cotizaciones/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_cotizacion(id):
    cotizacion = Cotizacion.query.get_or_404(id)
    db.session.delete(cotizacion)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/config/margen', methods=['POST'])
@admin_requerido
def actualizar_margen_default():
    config = ConfigMargen.query.first() or ConfigMargen()
    config.margen_default = float(request.json.get('margen_default', 30))
    db.session.add(config)
    db.session.commit()
    return jsonify({'success': True, 'margen_default': config.margen_default})

# ==================== PEDIDOS LOGÍSTICOS ====================

def _opciones_pedidos_logisticos():
    """Fechas de carga y proveedores logísticos presentes en pedidos activos."""
    pedidos = Pedido.query.filter(
        Pedido.eliminado == False,
        Pedido.fecha_carga.isnot(None),
        Pedido.prov_logistico_id.isnot(None),
    ).order_by(Pedido.fecha_carga.desc()).all()
    fechas = []
    fechas_set = set()
    prov_por_fecha = {}
    for p in pedidos:
        iso = p.fecha_carga.isoformat()
        if iso not in fechas_set:
            fechas_set.add(iso)
            fechas.append({
                'iso': iso,
                'label': p.fecha_carga.strftime('%d/%m/%Y'),
            })
        prov_por_fecha.setdefault(iso, [])
        pl = p.prov_logistico
        if pl and not any(x['id'] == pl.id for x in prov_por_fecha[iso]):
            prov_por_fecha[iso].append({'id': pl.id, 'nombre': pl.nombre})
    for iso in prov_por_fecha:
        prov_por_fecha[iso].sort(key=lambda x: x['nombre'].lower())
    return {'fechas': fechas, 'prov_por_fecha': prov_por_fecha}


def _build_filas_pedidos_logisticos(fecha_carga, prov_logistico_id):
    """Una fila por línea de pedido que coincide en fecha de carga y transporte."""
    from sqlalchemy.orm import joinedload
    pedidos = (
        Pedido.query.options(
            joinedload(Pedido.items).joinedload(ItemPedido.producto).joinedload(Producto.proveedor),
            joinedload(Pedido.cliente),
            joinedload(Pedido.prov_logistico),
        )
        .filter(
            Pedido.eliminado == False,
            Pedido.fecha_carga == fecha_carga,
            Pedido.prov_logistico_id == prov_logistico_id,
        )
        .order_by(Pedido.numero.asc())
        .all()
    )
    filas = []
    for ped in pedidos:
        tpte = ped.prov_logistico.nombre if ped.prov_logistico else '—'
        fc_fmt = ped.fecha_carga.strftime('%d/%m/%Y') if ped.fecha_carga else '—'
        cli = ped.cliente
        for item in ped.items:
            prod = item.producto
            if not prod:
                continue
            filas.append({
                'pedido_id': ped.id,
                'pedido_numero': ped.numero,
                'fecha_carga_fmt': fc_fmt,
                'tpte': tpte,
                'fruta': prod.fruta or '—',
                'clasificacion': prod.clasificacion or '—',
                'envase': prod.envase or '—',
                'pallets': item.pallets or 0,
                'bultos': item.bultos or 0,
                'proveedor': prod.proveedor.nombre if prod.proveedor else '—',
                'cliente': cli.nombre if cli else '—',
                'mercado': (cli.mercado if cli and cli.mercado else None) or ped.mercado or '—',
                'puesto': (cli.puesto if cli and cli.puesto else None) or ped.puesto or '—',
                'cuit': cli.cuit if cli and cli.cuit else '—',
                'direccion': cli.direccion if cli and cli.direccion else '—',
                'telefono': cli.telefono if cli and cli.telefono else '—',
            })
    return filas


@app.route('/pedidos-logisticos')
@usuario_requerido
def pedidos_logisticos():
    import json
    opciones = _opciones_pedidos_logisticos()
    fecha_str = (request.args.get('fecha_carga') or '').strip()
    prov_id = request.args.get('prov_logistico_id', type=int)
    filas = []
    fecha_sel = fecha_str
    prov_sel = prov_id
    if fecha_str and prov_id:
        try:
            fc = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            filas = _build_filas_pedidos_logisticos(fc, prov_id)
        except ValueError:
            fecha_sel = ''
            prov_sel = None
    elif opciones['fechas'] and not fecha_str:
        fecha_sel = opciones['fechas'][0]['iso']
        provs = opciones['prov_por_fecha'].get(fecha_sel, [])
        if provs and not prov_id:
            prov_sel = provs[0]['id']
            fc = datetime.strptime(fecha_sel, '%Y-%m-%d').date()
            filas = _build_filas_pedidos_logisticos(fc, prov_sel)
    return render_template(
        'pedidos_logisticos/lista.html',
        filas=filas,
        fechas=opciones['fechas'],
        prov_por_fecha_json=json.dumps(opciones['prov_por_fecha']),
        fecha_sel=fecha_sel,
        prov_sel=prov_sel,
    )


@app.route('/api/pedidos-logisticos')
@usuario_requerido
def api_pedidos_logisticos():
    fecha_str = (request.args.get('fecha_carga') or '').strip()
    prov_id = request.args.get('prov_logistico_id', type=int)
    if not fecha_str or not prov_id:
        return jsonify({'filas': [], 'error': 'Seleccioná fecha de carga y proveedor logístico'})
    try:
        fc = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'filas': [], 'error': 'Fecha inválida'}), 400
    return jsonify({'filas': _build_filas_pedidos_logisticos(fc, prov_id)})


# ==================== PEDIDOS PROVEEDOR ====================

def _opciones_pedidos_proveedor():
    """Fechas de carga y proveedores (de producto) presentes en líneas de pedidos activos."""
    from sqlalchemy.orm import joinedload
    pedidos = (
        Pedido.query.options(
            joinedload(Pedido.items).joinedload(ItemPedido.producto).joinedload(Producto.proveedor),
        )
        .filter(Pedido.eliminado == False, Pedido.fecha_carga.isnot(None))
        .order_by(Pedido.fecha_carga.desc())
        .all()
    )
    fechas = []
    fechas_set = set()
    prov_por_fecha = {}
    for p in pedidos:
        iso = p.fecha_carga.isoformat()
        if iso not in fechas_set:
            fechas_set.add(iso)
            fechas.append({'iso': iso, 'label': p.fecha_carga.strftime('%d/%m/%Y')})
        for item in p.items:
            prod = item.producto
            if not prod or not prod.proveedor_id:
                continue
            prov = prod.proveedor
            if not prov:
                continue
            prov_por_fecha.setdefault(iso, [])
            if not any(x['id'] == prov.id for x in prov_por_fecha[iso]):
                prov_por_fecha[iso].append({'id': prov.id, 'nombre': prov.nombre})
    for iso in prov_por_fecha:
        prov_por_fecha[iso].sort(key=lambda x: x['nombre'].lower())
    return {'fechas': fechas, 'prov_por_fecha': prov_por_fecha}


def _build_filas_pedidos_proveedor(fecha_carga, proveedor_id):
    """Una fila por línea cuya fecha de carga y proveedor del producto coinciden."""
    from sqlalchemy.orm import joinedload
    pedidos = (
        Pedido.query.options(
            joinedload(Pedido.items).joinedload(ItemPedido.producto).joinedload(Producto.proveedor),
            joinedload(Pedido.cliente),
            joinedload(Pedido.prov_logistico),
        )
        .filter(Pedido.eliminado == False, Pedido.fecha_carga == fecha_carga)
        .order_by(Pedido.numero.asc())
        .all()
    )
    filas = []
    for ped in pedidos:
        tpte = ped.prov_logistico.nombre if ped.prov_logistico else '—'
        fc_fmt = ped.fecha_carga.strftime('%d/%m/%Y') if ped.fecha_carga else '—'
        cli = ped.cliente
        for item in ped.items:
            prod = item.producto
            if not prod or prod.proveedor_id != proveedor_id:
                continue
            filas.append({
                'pedido_id': ped.id,
                'pedido_numero': ped.numero,
                'fecha_carga_fmt': fc_fmt,
                'tpte': tpte,
                'fruta': prod.fruta or '—',
                'clasificacion': prod.clasificacion or '—',
                'envase': prod.envase or '—',
                'pallets': item.pallets or 0,
                'bultos': item.bultos or 0,
                'cliente': cli.nombre if cli else '—',
                'mercado': (cli.mercado if cli and cli.mercado else None) or ped.mercado or '—',
                'puesto': (cli.puesto if cli and cli.puesto else None) or ped.puesto or '—',
                'cuit': cli.cuit if cli and cli.cuit else '—',
                'direccion': cli.direccion if cli and cli.direccion else '—',
                'telefono': cli.telefono if cli and cli.telefono else '—',
            })
    return filas


@app.route('/pedidos-proveedor')
@usuario_requerido
def pedidos_proveedor():
    import json
    opciones = _opciones_pedidos_proveedor()
    fecha_str = (request.args.get('fecha_carga') or '').strip()
    prov_id = request.args.get('proveedor_id', type=int)
    filas = []
    fecha_sel = fecha_str
    prov_sel = prov_id
    if fecha_str and prov_id:
        try:
            fc = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            filas = _build_filas_pedidos_proveedor(fc, prov_id)
        except ValueError:
            fecha_sel = ''
            prov_sel = None
    elif opciones['fechas'] and not fecha_str:
        fecha_sel = opciones['fechas'][0]['iso']
        provs = opciones['prov_por_fecha'].get(fecha_sel, [])
        if provs and not prov_id:
            prov_sel = provs[0]['id']
            fc = datetime.strptime(fecha_sel, '%Y-%m-%d').date()
            filas = _build_filas_pedidos_proveedor(fc, prov_sel)
    return render_template(
        'pedidos_proveedor/lista.html',
        filas=filas,
        fechas=opciones['fechas'],
        prov_por_fecha_json=json.dumps(opciones['prov_por_fecha']),
        fecha_sel=fecha_sel,
        prov_sel=prov_sel,
    )


@app.route('/api/pedidos-proveedor')
@usuario_requerido
def api_pedidos_proveedor():
    fecha_str = (request.args.get('fecha_carga') or '').strip()
    prov_id = request.args.get('proveedor_id', type=int)
    if not fecha_str or not prov_id:
        return jsonify({'filas': [], 'error': 'Seleccioná fecha de carga y proveedor'})
    try:
        fc = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'filas': [], 'error': 'Fecha inválida'}), 400
    return jsonify({'filas': _build_filas_pedidos_proveedor(fc, prov_id)})


# ==================== PEDIDOS ====================

@app.route('/pedidos')
@usuario_requerido
def listar_pedidos():
    page = request.args.get('page', 1, type=int)
    pedidos = Pedido.query.filter_by(eliminado=False).order_by(Pedido.fecha_venta.desc()).paginate(page=page, per_page=100)
    filas = []
    for p in pedidos.items:
        extra = _estado_pedido_lista(p)
        filas.append({
            'pedido': p,
            'saldo_pagar': extra['saldo_pagar'],
            'remito_col': extra['remito_col'],
            'entregado_col': extra['entregado_col'],
            'estado_col': extra['estado_col'],
            'completado': extra['completado'],
        })
    return render_template('pedidos/lista.html', pedidos=pedidos, filas=filas)

@app.route('/pedidos/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_pedido():
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    prov_logisticos = ProveedorLogistico.query.all()
    
    if request.method == 'POST':
        try:
            cliente_id = request.form['cliente_id']
            fecha_venta = request.form.get('fecha_venta')
            fecha_carga = request.form.get('fecha_carga')
            mercado = request.form.get('mercado')
            puesto = request.form.get('puesto')
            prov_logistico_id = request.form.get('prov_logistico_id') or None

            numero = _siguiente_numero_pedido()
            
            pedido = Pedido(
                numero=numero,
                cliente_id=cliente_id,
                prov_logistico_id=prov_logistico_id,
                fecha_venta=datetime.strptime(fecha_venta, '%Y-%m-%d').date() if fecha_venta else datetime.now().date(),
                fecha_carga=datetime.strptime(fecha_carga, '%Y-%m-%d').date() if fecha_carga else None,
                mercado=mercado,
                puesto=puesto
            )
            _aplicar_remito_entregado_pedido(pedido, request.form)
            
            db.session.add(pedido)
            db.session.flush()

            _validar_mismo_proveedor_pedido(request.form)
            costo_bruto, venta_bruta = _procesar_lineas_pedido(request.form, pedido.id)
            if venta_bruta <= 0:
                raise ValueError(
                    'El pedido debe tener al menos una línea con producto completo y bultos mayor a cero.'
                )

            precio_venta_total = _guardar_totales_pedido(pedido, request.form, costo_bruto, venta_bruta)
            
            cliente = Cliente.query.get(cliente_id)
            cliente.saldo += precio_venta_total
            
            _procesar_adjunto_remito(pedido, request.form, request.files)
            db.session.commit()
            
            backup_excel_opcional()
            
            return redirect(url_for('listar_pedidos'))
        except Exception as e:
            db.session.rollback()
            return render_template('pedidos/formulario.html',
                                 clientes=clientes,
                                 productos=productos,
                                 prov_logisticos=prov_logisticos,
                                 proveedores=Proveedor.query.filter_by(activo=True).all(),
                                 numero_sugerido=_siguiente_numero_pedido(),
                                 error=str(e))
    
    return render_template('pedidos/formulario.html',
                         clientes=clientes,
                         productos=productos,
                         prov_logisticos=prov_logisticos,
                         proveedores=Proveedor.query.filter_by(activo=True).all(),
                         numero_sugerido=_siguiente_numero_pedido())

def _render_pedido_formulario(pedido, solo_lectura=False, error=None):
    return render_template(
        'pedidos/formulario.html',
        pedido=pedido,
        clientes=Cliente.query.all(),
        prov_logisticos=ProveedorLogistico.query.all(),
        proveedores=Proveedor.query.filter_by(activo=True).all(),
        numero_sugerido=pedido.numero if pedido else _siguiente_numero_pedido(),
        solo_lectura=solo_lectura,
        error=error,
    )


@app.route('/pedidos/<int:id>')
@app.route('/pedidos/<int:id>/ver')
@usuario_requerido
def ver_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    return _render_pedido_formulario(pedido, solo_lectura=True)

# ==================== COBRANZAS ====================

@app.route('/cobranzas')
@usuario_requerido
def listar_cobranzas():
    cobranzas = Cobranza.query.filter_by(eliminado=False).order_by(Cobranza.fecha_cobranza.desc()).all()
    return render_template('cobranzas/lista.html', cobranzas=cobranzas)


@app.route('/cobranzas/eliminadas')
@usuario_requerido
def cobranzas_eliminadas():
    cobranzas = Cobranza.query.filter_by(eliminado=True).order_by(Cobranza.fecha_eliminacion.desc()).all()
    return render_template('cobranzas/eliminadas.html', cobranzas=cobranzas)


@app.route('/cobranzas/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_cobranza(id):
    cobranza = Cobranza.query.filter_by(id=id, eliminado=False).first_or_404()
    cobranza.eliminado = True
    cobranza.fecha_eliminacion = datetime.now()
    db.session.commit()
    return jsonify({'success': True})


@app.route('/cobranzas/<int:id>/restaurar', methods=['POST'])
@usuario_requerido
def restaurar_cobranza(id):
    cobranza = Cobranza.query.filter_by(id=id, eliminado=True).first_or_404()
    cobranza.eliminado = False
    cobranza.fecha_eliminacion = None
    db.session.commit()
    return jsonify({'success': True})

@app.route('/cobranzas/nueva', methods=['GET', 'POST'])
@usuario_requerido
def nueva_cobranza():
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    formas = FormaCobro.query.filter_by(activo=True).order_by(FormaCobro.nombre).all()

    if request.method == 'POST':
        try:
            _guardar_cobranza_desde_form(request.form)
            db.session.commit()
            return redirect(url_for('listar_cobranzas'))
        except Exception as e:
            db.session.rollback()
            return render_template('cobranzas/formulario.html', clientes=clientes, formas=formas,
                                   cobranza_id=None, imputaciones_iniciales=[], error=str(e))

    cobranza_id = request.args.get('cobranza_id', type=int)
    return render_template('cobranzas/formulario.html', clientes=clientes, formas=formas,
                           cobranza_id=cobranza_id, imputaciones_iniciales=[])


@app.route('/cobranzas/formas/nueva', methods=['POST'])
@usuario_requerido
def nueva_forma_cobro():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'error': 'Nombre requerido'}), 400
    if FormaCobro.query.filter_by(nombre=nombre).first():
        return jsonify({'error': 'Ya existe'}), 400
    f = FormaCobro(nombre=nombre)
    db.session.add(f)
    db.session.commit()
    return jsonify({'success': True, 'id': f.id, 'nombre': f.nombre})


def _render_cobranza_formulario(cobranza=None, solo_lectura=False, error=None, clientes=None, formas=None):
    if clientes is None:
        clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    if formas is None:
        formas = FormaCobro.query.filter_by(activo=True).order_by(FormaCobro.nombre).all()
    imputaciones_iniciales = _imputaciones_desde_cobranza(cobranza) if cobranza else []
    return render_template(
        'cobranzas/formulario.html',
        cobranza=cobranza,
        clientes=clientes,
        formas=formas,
        cobranza_id=cobranza.id if cobranza else None,
        imputaciones_iniciales=imputaciones_iniciales,
        solo_lectura=solo_lectura,
        error=error,
    )


@app.route('/cobranzas/<int:id>')
@app.route('/cobranzas/<int:id>/ver')
@usuario_requerido
def ver_cobranza(id):
    cobranza = Cobranza.query.filter_by(id=id, eliminado=False).first_or_404()
    return _render_cobranza_formulario(cobranza, solo_lectura=True)


@app.route('/cobranzas/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_cobranza(id):
    cobranza = Cobranza.query.filter_by(id=id, eliminado=False).first_or_404()
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    formas = FormaCobro.query.filter_by(activo=True).order_by(FormaCobro.nombre).all()

    if request.method == 'POST':
        try:
            _guardar_cobranza_desde_form(request.form, cobranza=cobranza)
            db.session.commit()
            return redirect(url_for('listar_cobranzas'))
        except Exception as e:
            db.session.rollback()
            return _render_cobranza_formulario(
                cobranza, clientes=clientes, formas=formas, error=str(e),
            )

    return _render_cobranza_formulario(cobranza, clientes=clientes, formas=formas)

# ==================== ELIMINAR ====================

@app.route('/clientes/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': True})

@app.route('/proveedores/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    try:
        db.session.delete(proveedor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': True})

@app.route('/proveedores/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            proveedor.nombre = request.form['nombre']
            proveedor.razon_social = request.form.get('razon_social')
            proveedor.cuit = request.form.get('cuit')
            proveedor.direccion = request.form.get('direccion')
            proveedor.provincia = request.form.get('provincia')

            ProveedorContacto.query.filter_by(proveedor_id=proveedor.id).delete()
            contacto_nombres = request.form.getlist('contacto_nombre[]')
            contacto_roles = request.form.getlist('contacto_rol[]')
            contacto_telefonos = request.form.getlist('contacto_telefono[]')
            contacto_emails = request.form.getlist('contacto_email[]')

            contactos_creados = []
            for idx, nombre in enumerate(contacto_nombres):
                if not nombre.strip():
                    continue
                contacto = ProveedorContacto(
                    proveedor_id=proveedor.id,
                    nombre=nombre.strip(),
                    rol=contacto_roles[idx].strip() if idx < len(contacto_roles) else None,
                    telefono=contacto_telefonos[idx].strip() if idx < len(contacto_telefonos) else None,
                    email=contacto_emails[idx].strip() if idx < len(contacto_emails) else None,
                    contacto_logistico=f'contacto_logistico_{idx}' in request.form
                )
                db.session.add(contacto)
                contactos_creados.append(contacto)

            if contactos_creados and not any(c.contacto_logistico for c in contactos_creados):
                raise ValueError('Al menos uno de los contactos debe tener marcado "Contacto Logístico"')

            db.session.commit()
            return redirect(url_for('listar_proveedores'))
        except Exception as e:
            db.session.rollback()
            # Reconstruir contactos temporales para mantenerlos en el formulario
            contacto_nombres = request.form.getlist('contacto_nombre[]')
            contacto_roles = request.form.getlist('contacto_rol[]')
            contacto_telefonos = request.form.getlist('contacto_telefono[]')
            contacto_emails = request.form.getlist('contacto_email[]')
            
            # Crear objetos temporales con los datos del formulario
            class ContactoTemp:
                def __init__(self, nombre, rol, telefono, email, logistico):
                    self.nombre = nombre
                    self.rol = rol
                    self.telefono = telefono
                    self.email = email
                    self.contacto_logistico = logistico
            
            contactos_temp = []
            for idx, nombre in enumerate(contacto_nombres):
                if nombre.strip():
                    contactos_temp.append(ContactoTemp(
                        nombre=nombre.strip(),
                        rol=contacto_roles[idx].strip() if idx < len(contacto_roles) else '',
                        telefono=contacto_telefonos[idx].strip() if idx < len(contacto_telefonos) else '',
                        email=contacto_emails[idx].strip() if idx < len(contacto_emails) else '',
                        logistico=f'contacto_logistico_{idx}' in request.form
                    ))
            
            # Reemplazar contactos del proveedor con los temporales
            proveedor.contactos = contactos_temp
            return render_template('proveedores/formulario.html', proveedor=proveedor, error=str(e))
    
    return render_template('proveedores/formulario.html', proveedor=proveedor)

@app.route('/productos/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': True})

@app.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    return redirect(url_for('gestionar_productos_proveedor', proveedor_id=producto.proveedor_id))


@app.route('/productos/<int:id>/eliminar-linea', methods=['POST'])
@usuario_requerido
def eliminar_linea_producto(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': True})

@app.route('/pedidos/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    try:
        pedido.eliminado = True
        pedido.fecha_eliminacion = datetime.now()
        _sync_cliente_saldo_ventas(pedido.cliente_id)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': True})

@app.route('/pedidos/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    prov_logisticos = ProveedorLogistico.query.all()
    
    if request.method == 'POST':
        try:
            pedido.cliente_id = request.form['cliente_id']
            pedido.fecha_venta = datetime.strptime(request.form['fecha_venta'], '%Y-%m-%d').date()
            pedido.fecha_carga = datetime.strptime(request.form['fecha_carga'], '%Y-%m-%d').date() if request.form.get('fecha_carga') else None
            pedido.prov_logistico_id = request.form.get('prov_logistico_id') or None
            pedido.mercado = request.form.get('mercado')
            pedido.puesto = request.form.get('puesto')
            _aplicar_remito_entregado_pedido(pedido, request.form)
            
            ItemPedido.query.filter_by(pedido_id=id).delete()
            _validar_mismo_proveedor_pedido(request.form)
            costo_bruto, venta_bruta = _procesar_lineas_pedido(request.form, id)
            if venta_bruta <= 0:
                raise ValueError(
                    'El pedido debe tener al menos una línea con producto completo y bultos mayor a cero.'
                )
            _guardar_totales_pedido(pedido, request.form, costo_bruto, venta_bruta)
            _sync_cliente_saldo_ventas(pedido.cliente_id)
            
            _procesar_adjunto_remito(pedido, request.form, request.files)
            db.session.commit()
            return redirect(url_for('listar_pedidos'))
        except Exception as e:
            db.session.rollback()
            return render_template('pedidos/formulario.html', pedido=pedido, clientes=clientes,
                                   prov_logisticos=prov_logisticos,
                                   proveedores=Proveedor.query.filter_by(activo=True).all(),
                                   numero_sugerido=pedido.numero,
                                   error=str(e))
    
    return render_template('pedidos/formulario.html', pedido=pedido, clientes=clientes,
                           prov_logisticos=prov_logisticos,
                           proveedores=Proveedor.query.filter_by(activo=True).all(),
                           numero_sugerido=pedido.numero)


@app.route('/pedidos/<int:id>/remito-adjunto')
@usuario_requerido
def descargar_remito_adjunto(id):
    pedido = Pedido.query.get_or_404(id)
    if not pedido.remito_adjunto_path:
        abort(404)
    abs_path = _ruta_absoluta_adjunto_remito(pedido.remito_adjunto_path)
    if not abs_path or not os.path.isfile(abs_path):
        abort(404)
    directorio = os.path.dirname(abs_path)
    nombre = os.path.basename(abs_path)
    return send_from_directory(
        directorio,
        nombre,
        as_attachment=True,
        download_name=pedido.remito_adjunto_nombre or nombre,
    )


@app.route('/pedidos/eliminados')
@usuario_requerido
def pedidos_eliminados():
    pedidos = Pedido.query.filter_by(eliminado=True).order_by(Pedido.fecha_eliminacion.desc()).all()
    return render_template('pedidos/eliminados.html', pedidos=pedidos)


@app.route('/pedidos/<int:id>/restaurar', methods=['POST'])
@usuario_requerido
def restaurar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    pedido.eliminado = False
    pedido.fecha_eliminacion = None
    _sync_cliente_saldo_ventas(pedido.cliente_id)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/pedidos/<int:id>/borrar-definitivo', methods=['POST'])
@usuario_requerido
def borrar_definitivo_pedido(id):
    """Borra definitivamente un pedido (solo si está eliminado)."""
    pedido = Pedido.query.get_or_404(id)
    if not pedido.eliminado:
        return jsonify({'error': 'Solo se puede borrar definitivo un pedido eliminado'}), 400
    try:
        # Evitar referencias huérfanas en cobranzas/imputaciones
        CobranzaImputacion.query.filter_by(pedido_id=pedido.id).delete()
        # Items se borran por cascade, pero por seguridad:
        ItemPedido.query.filter_by(pedido_id=pedido.id).delete()
        cliente_id = pedido.cliente_id
        _eliminar_archivo_adjunto_remito(pedido)
        db.session.delete(pedido)
        _sync_cliente_saldo_ventas(cliente_id)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ==================== REPORTES ====================

MESES_REPORTE_ES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]


def _fecha_referencia_venta(pedido):
    """Fecha para agrupar ventas: venta del pedido, o fecha de carga si falta."""
    return pedido.fecha_venta or pedido.fecha_carga


def _meses_con_ventas_disponibles():
    meses = set()
    for p in Pedido.query.filter_by(eliminado=False).all():
        f = _fecha_referencia_venta(p)
        if f:
            meses.add((f.year, f.month))
    return sorted(meses, reverse=True)


def _clave_mes(anio, mes):
    return f'{anio:04d}-{mes:02d}'


def _etiqueta_mes(anio, mes):
    anio = int(anio)
    if 1 <= mes <= 12:
        return f'{MESES_REPORTE_ES[mes]} {anio}'
    return f'{mes:02d}/{anio}'


@app.route('/reportes/ventas')
@usuario_requerido
def reporte_ventas():
    """EERR mensual por fecha de venta + detalle de pedidos filtrados."""
    todos = _meses_con_ventas_disponibles()
    opciones_meses = [
        {'clave': _clave_mes(y, m), 'etiqueta': _etiqueta_mes(y, m), 'anio': y, 'mes': m}
        for y, m in todos
    ]

    seleccionados = request.args.getlist('mes')
    if not seleccionados and opciones_meses:
        seleccionados = [o['clave'] for o in opciones_meses]
    set_sel = set(seleccionados)

    pedidos_filtrados = []
    for p in Pedido.query.filter_by(eliminado=False).order_by(Pedido.id.desc()).all():
        f = _fecha_referencia_venta(p)
        if not f:
            continue
        if _clave_mes(f.year, f.month) in set_sel:
            pedidos_filtrados.append(p)
    pedidos_filtrados.sort(key=lambda p: (_fecha_referencia_venta(p) or date.min, p.id), reverse=True)

    eerr_meses = []
    for clave in sorted(set_sel):
        try:
            anio_s, mes_s = clave.split('-')
            anio, mes = int(anio_s), int(mes_s)
        except (ValueError, AttributeError):
            continue
        subset = []
        for p in pedidos_filtrados:
            f = _fecha_referencia_venta(p)
            if f and f.year == anio and f.month == mes:
                subset.append(p)
        ventas = sum(p.precio_venta_total or 0 for p in subset)
        costo = sum(p.costo_total or 0 for p in subset)
        eerr_meses.append({
            'clave': clave,
            'etiqueta': _etiqueta_mes(anio, mes),
            'ventas': ventas,
            'costo': costo,
            'resultado': round(ventas - costo, 2),
            'cantidad': len(subset),
        })

    totales_periodo = {
        'ventas': sum(m['ventas'] for m in eerr_meses),
        'costo': sum(m['costo'] for m in eerr_meses),
        'resultado': sum(m['resultado'] for m in eerr_meses),
        'cantidad': len(pedidos_filtrados),
    }

    detalle_ventas = []
    for p in pedidos_filtrados:
        venta_total = float(p.precio_venta_total or 0)
        comision = float(p.resultado or 0)
        cobrado = float(_sum_imputado_pedido(p.id))
        deuda = max(0.0, round(venta_total - cobrado, 2))
        margen = (comision / venta_total * 100) if venta_total > 0 else 0.0
        detalle_ventas.append({
            'numero': p.numero,
            'fecha': _fecha_referencia_venta(p),
            'cliente': p.cliente.nombre if p.cliente else '—',
            'venta_total': venta_total,
            'comision': comision,
            'margen_pct': margen,
            'cobrado': cobrado,
            'deuda': deuda,
        })

    return render_template(
        'reportes/ventas.html',
        opciones_meses=opciones_meses,
        meses_sel=seleccionados,
        eerr_meses=eerr_meses,
        totales_periodo=totales_periodo,
        detalle_ventas=detalle_ventas,
    )

def formatear_numero_ar(valor, decimales=2):
    """Formato AR: miles con punto, decimales con coma (ej. 1.234,56)."""
    try:
        if valor is None or valor == '':
            return '0' if decimales == 0 else ('0,' + '0' * decimales)
        num = float(valor)
        if decimales == 0:
            s = f"{num:,.0f}"
        else:
            s = f"{num:,.{decimales}f}"
        return s.replace(',', '\u0000').replace('.', ',').replace('\u0000', '.')
    except (TypeError, ValueError):
        return str(valor) if valor is not None else ''


def parse_numero_ar(valor, default=0.0):
    """Convierte texto con formato AR (1.234,56), miles con punto, o estándar a float."""
    if valor is None or valor == '':
        return default
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip().replace('$', '').replace(' ', '').replace('\u00a0', '')
    if not s:
        return default
    if re.fullmatch(r'-?\d+', s):
        return float(s)
    last_dot = s.rfind('.')
    last_comma = s.rfind(',')
    if last_comma >= 0 and (last_dot < 0 or last_comma > last_dot):
        # AR: 1.234.567,89
        s = s.replace('.', '').replace(',', '.')
    elif last_dot >= 0 and (last_comma < 0 or last_dot > last_comma):
        # Punto como decimal (1,234.56) o miles AR sin decimales (2.000.000)
        if s.count('.') > 1:
            s = s.replace('.', '')
        else:
            s = s.replace(',', '')
    else:
        s = s.replace('.', '').replace(',', '')
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


@app.template_filter('eur')
def formato_eur(valor):
    return formatear_numero_ar(valor, 2)

@app.template_filter('formato_numero')
def formato_numero(valor):
    return formatear_numero_ar(valor, 2)

@app.template_filter('formato_entero')
def formato_entero(valor):
    return formatear_numero_ar(valor, 0)

@app.template_filter('formato_porcentaje')
def formato_porcentaje(valor):
    return formatear_numero_ar(valor, 1)

@app.template_filter('currency')
def formato_moneda(valor):
    n = formatear_numero_ar(valor, 2)
    return f'${n}' if n else '$0,00'


@app.template_filter('moneda')
def formato_moneda_filter(valor):
    return formato_moneda(valor)


@app.context_processor
def inject_formato_global():
    return dict(formatear_numero_ar=formatear_numero_ar)

@app.route('/_debug/filters')
def debug_filters():
    return jsonify(sorted(app.jinja_env.filters.keys()))

@app.context_processor
def inject_report_urls():
    return {}

# ==================== RUTAS DE SALDOS ====================

@app.route('/api/cliente/<int:cliente_id>/pedidos')
@usuario_requerido
def api_cliente_pedidos(cliente_id):
    """API pedidos de un cliente (formato completo para Aging y compatibilidad)."""
    cliente = Cliente.query.get_or_404(cliente_id)
    pedidos_activos = sorted(
        [p for p in cliente.pedidos if not p.eliminado],
        key=lambda p: (p.fecha_venta or date.min, p.id),
    )
    filas = [_fila_aging_pedido(p) for p in pedidos_activos]
    return jsonify({'cliente': cliente.nombre, 'pedidos': filas})

@app.route('/api/pedido/<int:pedido_id>/detalle')
def api_pedido_detalle(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    items_data = []
    for item in pedido.items:
        items_data.append({
            'producto': item.producto.nombre if item.producto else 'N/A',
            'cantidad': item.cantidad,
            'precio_unitario': item.precio_unitario,
            'subtotal': item.precio_total
        })

    return jsonify({
        'pedido': pedido.numero,
        'items': items_data
    })

def _proveedores_pedido_nombres(pedido):
    nombres = set()
    for it in pedido.items:
        prod = it.producto
        if prod and prod.proveedor:
            nombres.add(prod.proveedor.nombre)
    return ', '.join(sorted(nombres)) if nombres else '—'


def _fila_aging_pedido(pedido):
    venta = float(pedido.precio_venta_total or 0)
    costo = float(pedido.costo_total or 0)
    comision = float(pedido.resultado or 0)
    cobrado = float(_sum_imputado_pedido(pedido.id))
    saldo_prov, saldo_com, _, _ = _saldos_imputacion_pedido(pedido)
    deuda_costo = round(max(0.0, saldo_prov), 2)
    deuda_comision = round(max(0.0, saldo_com), 2)
    total_deuda = round(max(0.0, venta - cobrado), 2)
    pct = (cobrado / venta * 100) if venta > 0 else 0.0
    completado = total_deuda <= 0.01
    return {
        'tipo': 'pedido',
        'pedido_id': pedido.id,
        'numero': pedido.numero,
        'cliente': pedido.cliente.nombre if pedido.cliente else '',
        'proveedor': _proveedores_pedido_nombres(pedido),
        'venta': venta,
        'costo': costo,
        'comision': comision,
        'cobrado': cobrado,
        'total_deuda': total_deuda,
        'deuda_costo': deuda_costo,
        'deuda_comision': deuda_comision,
        'pct_pagado': pct,
        'estado': 'Completo' if completado else 'Pendiente',
        'fecha': pedido.fecha_venta.isoformat() if pedido.fecha_venta else None,
    }


def _fila_aging_cliente(cliente, pedidos_filas):
    venta = sum(f['venta'] for f in pedidos_filas)
    costo = sum(f['costo'] for f in pedidos_filas)
    comision = sum(f['comision'] for f in pedidos_filas)
    cobrado = sum(f['cobrado'] for f in pedidos_filas)
    total_deuda = sum(f['total_deuda'] for f in pedidos_filas)
    deuda_costo = sum(f['deuda_costo'] for f in pedidos_filas)
    deuda_comision = sum(f['deuda_comision'] for f in pedidos_filas)
    pct = (cobrado / venta * 100) if venta > 0 else 0.0
    todos_completos = all(f['total_deuda'] <= 0.01 for f in pedidos_filas)
    return {
        'tipo': 'cliente',
        'cliente_id': cliente.id,
        'cliente': cliente.nombre,
        'proveedor': '',
        'venta': venta,
        'costo': costo,
        'comision': comision,
        'cobrado': cobrado,
        'total_deuda': total_deuda,
        'deuda_costo': deuda_costo,
        'deuda_comision': deuda_comision,
        'pct_pagado': pct,
        'estado': 'Completo' if todos_completos and venta > 0 else 'Pendiente',
        'pedidos': pedidos_filas,
        'num_pedidos': len(pedidos_filas),
    }


def _build_aging_clientes_data():
    """Arma filas agrupadas por cliente para Aging (HTML y API)."""
    filas = []
    total_vtas = total_cobrado = total_deuda = 0.0

    for cliente in Cliente.query.order_by(Cliente.nombre).all():
        pedidos_activos = sorted(
            [p for p in cliente.pedidos if not p.eliminado],
            key=lambda p: (p.fecha_venta or date.min, p.id),
        )
        if not pedidos_activos:
            continue
        pedidos_filas = [_fila_aging_pedido(p) for p in pedidos_activos]
        fila_cli = _fila_aging_cliente(cliente, pedidos_filas)
        filas.append(fila_cli)
        total_vtas += fila_cli['venta']
        total_cobrado += fila_cli['cobrado']
        total_deuda += fila_cli['total_deuda']

    filas.sort(key=lambda x: x['total_deuda'], reverse=True)
    return filas, total_vtas, total_cobrado, total_deuda


@app.route('/api/aging/clientes')
@usuario_requerido
def api_aging_clientes():
    filas, total_vtas, total_cobrado, total_deuda = _build_aging_clientes_data()
    return jsonify({
        'filas': filas,
        'total_vtas': total_vtas,
        'total_cobrado': total_cobrado,
        'total_deuda': total_deuda,
    })


@app.route('/api/aging/cliente/<int:cliente_id>/pedidos')
@usuario_requerido
def api_aging_cliente_pedidos(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    pedidos_activos = sorted(
        [p for p in cliente.pedidos if not p.eliminado],
        key=lambda p: (p.fecha_venta or date.min, p.id),
    )
    return jsonify([_fila_aging_pedido(p) for p in pedidos_activos])


@app.route('/aging/clientes')
@usuario_requerido
def aging_clientes():
    """Aging clientes: agrupado por cliente con detalle de pedidos expandible."""
    import json
    filas_aging, total_vtas, total_cobrado, total_deuda = _build_aging_clientes_data()
    aging_json = json.dumps({
        'filas': filas_aging,
        'total_vtas': total_vtas,
        'total_cobrado': total_cobrado,
        'total_deuda': total_deuda,
    })

    return render_template(
        'reportes/aging_clientes.html',
        filas_aging=filas_aging,
        aging_json=aging_json,
        total_vtas=total_vtas,
        total_cobrado=total_cobrado,
        total_deuda=total_deuda,
        total_saldo=total_deuda,
    )


def _items_proveedor_en_pedido(pedido, proveedor_id):
    return [
        it for it in pedido.items
        if it.producto and it.producto.proveedor_id == proveedor_id
    ]


def _ratio_costo_proveedor_pedido(pedido, costo_prov):
    if not pedido.costo_total or float(pedido.costo_total) <= 0:
        return 0.0
    return float(costo_prov) / float(pedido.costo_total)


def _pedidos_activos_proveedor(proveedor_id):
    ids = db.session.query(ItemPedido.pedido_id).join(Producto).filter(
        Producto.proveedor_id == proveedor_id,
    ).join(Pedido).filter(Pedido.eliminado == False).distinct().all()
    pedidos = []
    for (pid,) in ids:
        p = Pedido.query.get(pid)
        if p and not p.eliminado:
            pedidos.append(p)
    return sorted(pedidos, key=lambda x: (x.fecha_venta or date.min, x.id))


def _fila_aging_proveedor_pedido(pedido, proveedor_id):
    items = _items_proveedor_en_pedido(pedido, proveedor_id)
    if not items:
        return None
    costo = sum(float(it.costo_total or 0) for it in items)
    ratio = _ratio_costo_proveedor_pedido(pedido, costo)
    venta = float(pedido.precio_venta_total or 0) * ratio
    imps = _imputaciones_activas_query(pedido_id=pedido.id).all()
    pagado = sum((i.pago_proveedor or 0) for i in imps) * ratio
    total_deuda = round(max(0.0, costo - pagado), 2)
    deuda_costo = total_deuda
    pct = (pagado / costo * 100) if costo > 0 else 0.0
    completado = total_deuda <= 0.01
    return {
        'tipo': 'pedido',
        'pedido_id': pedido.id,
        'numero': pedido.numero,
        'cliente': pedido.cliente.nombre if pedido.cliente else '—',
        'venta': round(venta, 2),
        'costo': round(costo, 2),
        'pagado': round(pagado, 2),
        'total_deuda': total_deuda,
        'deuda_costo': deuda_costo,
        'pct_pagado': pct,
        'estado': 'Completo' if completado else 'Pendiente',
    }


def _fila_aging_proveedor(proveedor, pedidos_filas):
    venta = sum(f['venta'] for f in pedidos_filas)
    costo = sum(f['costo'] for f in pedidos_filas)
    pagado = sum(f['pagado'] for f in pedidos_filas)
    total_deuda = sum(f['total_deuda'] for f in pedidos_filas)
    deuda_costo = sum(f['deuda_costo'] for f in pedidos_filas)
    pct = (pagado / costo * 100) if costo > 0 else 0.0
    todos = all(f['total_deuda'] <= 0.01 for f in pedidos_filas)
    return {
        'tipo': 'proveedor',
        'proveedor_id': proveedor.id,
        'proveedor': proveedor.nombre,
        'cliente': '',
        'venta': venta,
        'costo': costo,
        'pagado': pagado,
        'total_deuda': total_deuda,
        'deuda_costo': deuda_costo,
        'pct_pagado': pct,
        'estado': 'Completo' if todos and costo > 0 else 'Pendiente',
        'pedidos': pedidos_filas,
        'num_pedidos': len(pedidos_filas),
    }


def _build_aging_proveedores_data():
    filas = []
    total_vtas = total_pagado = total_deuda = 0.0
    for prov in Proveedor.query.filter_by(activo=True).order_by(Proveedor.nombre).all():
        pedidos_filas = []
        for pedido in _pedidos_activos_proveedor(prov.id):
            fila = _fila_aging_proveedor_pedido(pedido, prov.id)
            if fila:
                pedidos_filas.append(fila)
        if not pedidos_filas:
            continue
        fila_prov = _fila_aging_proveedor(prov, pedidos_filas)
        filas.append(fila_prov)
        total_vtas += fila_prov['venta']
        total_pagado += fila_prov['pagado']
        total_deuda += fila_prov['total_deuda']
    filas.sort(key=lambda x: x['total_deuda'], reverse=True)
    return filas, total_vtas, total_pagado, total_deuda


@app.route('/api/aging/proveedores')
@usuario_requerido
def api_aging_proveedores():
    filas, total_vtas, total_pagado, total_deuda = _build_aging_proveedores_data()
    return jsonify({
        'filas': filas,
        'total_vtas': total_vtas,
        'total_pagado': total_pagado,
        'total_deuda': total_deuda,
    })


@app.route('/api/aging/proveedor/<int:proveedor_id>/pedidos')
@usuario_requerido
def api_aging_proveedor_pedidos(proveedor_id):
    Proveedor.query.get_or_404(proveedor_id)
    pedidos_filas = []
    for pedido in _pedidos_activos_proveedor(proveedor_id):
        fila = _fila_aging_proveedor_pedido(pedido, proveedor_id)
        if fila:
            pedidos_filas.append(fila)
    return jsonify(pedidos_filas)


@app.route('/aging/proveedores')
@app.route('/reportes/aging-proveedores')
@usuario_requerido
def aging_proveedores():
    """Aging proveedores: agrupado por proveedor con detalle de pedidos expandible."""
    import json
    filas_aging, total_vtas, total_pagado, total_deuda = _build_aging_proveedores_data()
    aging_json = json.dumps({
        'filas': filas_aging,
        'total_vtas': total_vtas,
        'total_pagado': total_pagado,
        'total_deuda': total_deuda,
    })
    return render_template(
        'reportes/aging_proveedores.html',
        filas_aging=filas_aging,
        aging_json=aging_json,
        total_vtas=total_vtas,
        total_pagado=total_pagado,
        total_deuda=total_deuda,
        total_compras=total_vtas,
        total_saldo=total_deuda,
    )


@app.route('/api/proveedor/<int:proveedor_id>/pedidos')
@usuario_requerido
def api_proveedor_pedidos(proveedor_id):
    """API pedidos del proveedor (formato aging)."""
    Proveedor.query.get_or_404(proveedor_id)
    pedidos_filas = []
    for pedido in _pedidos_activos_proveedor(proveedor_id):
        fila = _fila_aging_proveedor_pedido(pedido, proveedor_id)
        if fila:
            pedidos_filas.append(fila)
    return jsonify({
        'proveedor': Proveedor.query.get(proveedor_id).nombre,
        'pedidos': pedidos_filas,
    })


@app.route('/saldos/clientes')
@usuario_requerido
def saldos_clientes():
    """Reporte de saldos de clientes"""
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    datos = []
    total_vtas = 0
    total_cobrado = 0
    
    for cliente in clientes:
        vtas = sum(p.precio_venta_total for p in cliente.pedidos if not p.eliminado)
        cobrado = db.session.query(
            func.coalesce(func.sum(CobranzaImputacion.monto_imputado), 0)
        ).join(Cobranza, CobranzaImputacion.cobranza_id == Cobranza.id).join(
            Pedido, CobranzaImputacion.pedido_id == Pedido.id
        ).filter(Pedido.cliente_id == cliente.id, Pedido.eliminado == False, Cobranza.eliminado == False).scalar()
        
        saldo = vtas - cobrado
        pct = (cobrado / vtas * 100) if vtas > 0 else 0
        
        if vtas > 0:
            datos.append({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'vtas': vtas,
                'cobrado': cobrado,
                'saldo': saldo,
                'pct': pct
            })
            total_vtas += vtas
            total_cobrado += cobrado
    
    return render_template('reportes/saldos_clientes.html', 
                           datos=datos, 
                           total_vtas=total_vtas,
                           total_cobrado=total_cobrado,
                           total_saldo=total_vtas-total_cobrado)

@app.route('/saldos/cliente/<int:cliente_id>')
@usuario_requerido
def saldos_cliente_detalle(cliente_id):
    """Reporte detallado de un cliente"""
    cliente = Cliente.query.get_or_404(cliente_id)
    pedidos = []
    total_vta = 0
    total_cobrado = 0
    
    for pedido in cliente.pedidos:
        if pedido.eliminado:
            continue
        cobrado = _sum_imputado_pedido(pedido.id)
        
        saldo = pedido.precio_venta_total - cobrado
        estado = "Pagado" if abs(saldo) < 0.01 else ("Parcial" if cobrado > 0 else "Pendiente")
        
        pedidos.append({
            'numero': pedido.numero,
            'fecha': pedido.fecha_venta,
            'vta_total': pedido.precio_venta_total,
            'cobrado': cobrado,
            'saldo': saldo,
            'estado': estado
        })
        
        total_vta += pedido.precio_venta_total
        total_cobrado += cobrado
    
    return render_template('reportes/saldos_cliente_detalle.html',
                           cliente=cliente,
                           pedidos=pedidos,
                           total_vta=total_vta,
                           total_cobrado=total_cobrado,
                           total_saldo=total_vta-total_cobrado)

@app.route('/api/saldos/cliente/<int:cliente_id>')
def api_saldo_cliente(cliente_id):
    """API para obtener saldo de cliente"""
    cliente = Cliente.query.get_or_404(cliente_id)
    vtas = sum(p.precio_venta_total for p in cliente.pedidos if not p.eliminado)
    cobrado = db.session.query(
        func.coalesce(func.sum(CobranzaImputacion.monto_imputado), 0)
    ).join(Cobranza, CobranzaImputacion.cobranza_id == Cobranza.id).join(
        Pedido, CobranzaImputacion.pedido_id == Pedido.id
    ).filter(Pedido.cliente_id == cliente.id, Pedido.eliminado == False, Cobranza.eliminado == False).scalar()
    
    return jsonify({
        'cliente': cliente.nombre,
        'ventas': vtas,
        'cobrado': cobrado,
        'saldo': vtas - cobrado,
        'porcentaje': (cobrado / vtas * 100) if vtas > 0 else 0
    })

app.add_url_rule('/aging/clientes', 'aging_clientes', aging_clientes)
app.add_url_rule('/reportes/aging-clientes', 'aging_clientes', aging_clientes)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)