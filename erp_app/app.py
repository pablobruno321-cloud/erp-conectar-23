from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from .models import db, ERP, Cliente, Proveedor, Producto, Pedido, ItemPedido, Pago, Cobranza, ProveedorLogistico, Usuario, Cotizacion, ConfigMargen
from .auth import usuario_requerido, admin_requerido, get_usuario_actual
from .backup_excel import crear_backup_excel
from datetime import datetime, date
from sqlalchemy import func, extract
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{basedir}/erp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu_clave_secreta_desarrollo_aqui')

db.init_app(app)

def init_db():
    with app.app_context():
        print("  -> Verificando estructura de tablas en la DB...")
        db.create_all()
        
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
        print("✅ Base de datos lista.")

# ==================== CONTEXTO ====================

@app.context_processor
def inject_usuario():
    return {'usuario_actual': get_usuario_actual()}

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
            return redirect(url_for('portal_erps'))
        else:
            return render_template('login.html', error='Email o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
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
    total_pedidos = db.session.query(func.count(Pedido.id)).scalar()
    
    venta_total = db.session.query(func.sum(Pedido.precio_venta_total)).scalar() or 0
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
    ).filter(Cobranza.fecha_cobranza.isnot(None))
    
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
        Cobranza, Cobranza.cliente_id == Cliente.id
    ).group_by(Cliente.id).all()
    
    clientes_deuda = []
    for row in clientes_deuda_query:
        total_facturado = float(row.total_facturado or 0)
        if total_facturado > 0:
            total_cobrado = float(row.total_cobrado or 0)
            saldo = total_facturado - total_cobrado
            clientes_deuda.append({
                'nombre': row.nombre,
                'total_facturado': f"{total_facturado:,.2f}",
                'total_cobrado': f"{total_cobrado:,.2f}",
                'saldo': f"{saldo:,.2f}"
            })
    
    # ===== DEUDA POR PROVEEDOR (OPTIMIZADO) =====
    proveedores_deuda_query = db.session.query(
        Proveedor.nombre,
        func.sum(Pedido.costo_total).label('total_facturado'),
        func.sum(Pago.monto).label('total_pagado')
    ).outerjoin(Producto, Producto.proveedor_id == Proveedor.id).outerjoin(
        ItemPedido, ItemPedido.producto_id == Producto.id
    ).outerjoin(
        Pedido, Pedido.id == ItemPedido.pedido_id
    ).outerjoin(
        Pago, Pago.proveedor_id == Proveedor.id
    ).group_by(Proveedor.id).all()
    
    proveedores_deuda = []
    for row in proveedores_deuda_query:
        total_facturado = float(row.total_facturado or 0)
        if total_facturado > 0:
            total_pagado = float(row.total_pagado or 0)
            saldo = total_facturado - total_pagado
            proveedores_deuda.append({
                'nombre': row.nombre,
                'total_facturado': f"{total_facturado:,.2f}",
                'total_pagado': f"{total_pagado:,.2f}",
                'saldo': f"{saldo:,.2f}"
            })
    
    context = {
        'total_clientes': total_clientes,
        'total_proveedores': total_proveedores,
        'total_pedidos': total_pedidos,
        'venta_total': f"{venta_total:,.0f}",
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
        'proveedores_deuda': proveedores_deuda,
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
        Cobranza, Cobranza.cliente_id == Cliente.id
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
                cuit=request.form.get('cuit'),
                telefono=request.form.get('telefono'),
                direccion=request.form.get('direccion'),
                email=request.form.get('email')
            )
            db.session.add(cliente)
            db.session.commit()
            
            try:
                crear_backup_excel()
            except Exception as e:
                print(f"Error en backup: {str(e)}")
            
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
                cuit=request.form.get('cuit'),
                telefono=request.form.get('telefono'),
                direccion=request.form.get('direccion'),
                email=request.form.get('email')
            )
            db.session.add(proveedor)
            db.session.commit()
            return redirect(url_for('listar_proveedores'))
        except Exception as e:
            return render_template('proveedores/formulario.html', error=str(e))
    
    return render_template('proveedores/formulario.html')

@app.route('/api/proveedores/buscar')
@usuario_requerido
def buscar_proveedores():
    query = request.args.get('q', '')
    proveedores = Proveedor.query.filter(Proveedor.nombre.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{'id': p.id, 'nombre': p.nombre} for p in proveedores])

# ==================== PRODUCTOS ====================

@app.route('/productos')
@usuario_requerido
def listar_productos():
    """CORREGIDO: Paginar"""
    page = request.args.get('page', 1, type=int)
    productos = Producto.query.paginate(page=page, per_page=20)
    return render_template('productos/lista.html', productos=productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_producto():
    proveedores = Proveedor.query.all()
    
    if request.method == 'POST':
        try:
            producto = Producto(
                nombre=request.form['nombre'],
                proveedor_id=request.form['proveedor_id'],
                clasificacion=request.form.get('clasificacion'),
                variedad=request.form.get('variedad'),
                marca=request.form.get('marca'),
                envase=request.form.get('envase'),
                costo_unitario=float(request.form.get('costo_unitario', 0))
            )
            db.session.add(producto)
            db.session.commit()
            return redirect(url_for('listar_productos'))
        except Exception as e:
            return render_template('productos/formulario.html', proveedores=proveedores, error=str(e))
    
    return render_template('productos/formulario.html', proveedores=proveedores)

# ==================== COTIZACIONES ====================

@app.route('/cotizaciones')
@usuario_requerido
def listar_cotizaciones():
    """CORREGIDO: Paginar"""
    page = request.args.get('page', 1, type=int)
    cotizaciones = Cotizacion.query.order_by(Cotizacion.fecha_desde.desc()).paginate(page=page, per_page=20)
    config = ConfigMargen.query.first()
    margen_default = config.margen_default if config else 30
    return render_template('cotizaciones/lista.html', cotizaciones=cotizaciones, margen_default=margen_default)

@app.route('/cotizaciones/nueva', methods=['GET', 'POST'])
@usuario_requerido
def nueva_cotizacion():
    productos = Producto.query.filter_by(activo=True).all()
    config = ConfigMargen.query.first()
    margen_default = config.margen_default if config else 30
    
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        fecha_desde = datetime.strptime(request.form.get('fecha_desde'), '%Y-%m-%d').date()
        fecha_hasta = datetime.strptime(request.form.get('fecha_hasta'), '%Y-%m-%d').date()
        costo = float(request.form.get('costo_unitario', 0))
        margen = float(request.form.get('margen_ganancia', margen_default))
        
        cotizacion = Cotizacion(
            producto_id=producto_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            costo_unitario=costo,
            margen_ganancia=margen,
            activo=True
        )
        cotizacion.calcular_precio_venta()
        
        db.session.add(cotizacion)
        db.session.commit()
        return redirect(url_for('listar_cotizaciones'))
    
    return render_template('cotizaciones/formulario.html', productos=productos, margen_default=margen_default)

@app.route('/cotizaciones/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_cotizacion(id):
    cotizacion = Cotizacion.query.get_or_404(id)
    productos = Producto.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        cotizacion.producto_id = request.form.get('producto_id')
        cotizacion.fecha_desde = datetime.strptime(request.form.get('fecha_desde'), '%Y-%m-%d').date()
        cotizacion.fecha_hasta = datetime.strptime(request.form.get('fecha_hasta'), '%Y-%m-%d').date()
        cotizacion.costo_unitario = float(request.form.get('costo_unitario', 0))
        cotizacion.margen_ganancia = float(request.form.get('margen_ganancia', 30))
        cotizacion.calcular_precio_venta()
        
        db.session.commit()
        return redirect(url_for('listar_cotizaciones'))
    
    return render_template('cotizaciones/formulario.html', cotizacion=cotizacion, productos=productos)

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

# ==================== PEDIDOS ====================

@app.route('/pedidos')
@usuario_requerido
def listar_pedidos():
    """CORREGIDO: Paginar"""
    page = request.args.get('page', 1, type=int)
    pedidos = Pedido.query.order_by(Pedido.fecha_venta.desc()).paginate(page=page, per_page=20)
    return render_template('pedidos/lista.html', pedidos=pedidos)

@app.route('/pedidos/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_pedido():
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    prov_logisticos = ProveedorLogistico.query.all()
    
    if request.method == 'POST':
        try:
            cliente_id = request.form['cliente_id']
            
            numero = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            pedido = Pedido(
                numero=numero,
                cliente_id=cliente_id,
                prov_logistico_id=request.form.get('prov_logistico_id'),
                mercado=request.form.get('mercado'),
                puesto=request.form.get('puesto')
            )
            
            db.session.add(pedido)
            db.session.flush()
            
            item_count = int(request.form.get('item_count', 0))
            costo_total = 0
            precio_venta_total = 0
            
            for i in range(item_count):
                producto_id = request.form.get(f'producto_{i}')
                cantidad = float(request.form.get(f'cantidad_{i}', 0))
                precio_unitario = float(request.form.get(f'precio_unitario_{i}', 0))
                
                if producto_id and cantidad > 0:
                    producto = Producto.query.get(producto_id)
                    subtotal = cantidad * precio_unitario
                    
                    item = ItemPedido(
                        pedido_id=pedido.id,
                        producto_id=producto_id,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal
                    )
                    
                    db.session.add(item)
                    
                    costo_total += cantidad * producto.costo_unitario
                    precio_venta_total += subtotal
            
            resultado = precio_venta_total - costo_total
            
            pedido.costo_total = costo_total
            pedido.precio_venta_total = precio_venta_total
            pedido.resultado = resultado
            
            cliente = Cliente.query.get(cliente_id)
            cliente.saldo += precio_venta_total
            
            db.session.commit()
            
            try:
                crear_backup_excel()
            except Exception as e:
                print(f"Error en backup: {str(e)}")
            
            return redirect(url_for('listar_pedidos'))
        except Exception as e:
            db.session.rollback()
            return render_template('pedidos/formulario.html', 
                                 clientes=clientes, 
                                 productos=productos,
                                 prov_logisticos=prov_logisticos,
                                 error=str(e))
    
    return render_template('pedidos/formulario.html', 
                         clientes=clientes, 
                         productos=productos,
                         prov_logisticos=prov_logisticos)

@app.route('/pedidos/<int:id>')
@usuario_requerido
def ver_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    return render_template('pedidos/detalle.html', pedido=pedido)

# ==================== COBRANZAS ====================

@app.route('/cobranzas')
@usuario_requerido
def listar_cobranzas():
    """CORREGIDO: Paginar"""
    page = request.args.get('page', 1, type=int)
    cobranzas = Cobranza.query.order_by(Cobranza.fecha_cobranza.desc()).paginate(page=page, per_page=20)
    return render_template('cobranzas/lista.html', cobranzas=cobranzas)

@app.route('/cobranzas/nueva', methods=['GET', 'POST'])
@usuario_requerido
def nueva_cobranza():
    clientes = Cliente.query.all()
    pedidos = Pedido.query.all()
    
    if request.method == 'POST':
        try:
            cobranza = Cobranza(
                cliente_id=request.form['cliente_id'],
                monto=float(request.form['monto']),
                metodo=request.form.get('metodo'),
                referencia=request.form.get('referencia'),
                notas=request.form.get('notas'),
                pedido_id=request.form.get('pedido_id') or None,
                numero_comprobante=request.form.get('numero_comprobante'),
                tipo_comprobante=request.form.get('tipo_comprobante')
            )
            
            cliente = Cliente.query.get(cobranza.cliente_id)
            cliente.saldo -= cobranza.monto
            
            db.session.add(cobranza)
            db.session.commit()
            return redirect(url_for('listar_cobranzas'))
        except Exception as e:
            return render_template('cobranzas/formulario.html', clientes=clientes, pedidos=pedidos, error=str(e))
    
    return render_template('cobranzas/formulario.html', clientes=clientes, pedidos=pedidos)

@app.route('/cobranzas/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_cobranza(id):
    cobranza = Cobranza.query.get_or_404(id)
    clientes = Cliente.query.all()
    pedidos = Pedido.query.all()
    
    if request.method == 'POST':
        try:
            cliente_anterior = Cliente.query.get(cobranza.cliente_id)
            cliente_anterior.saldo += cobranza.monto
            
            cobranza.cliente_id = request.form['cliente_id']
            cobranza.monto = float(request.form['monto'])
            cobranza.metodo = request.form.get('metodo')
            cobranza.referencia = request.form.get('referencia')
            cobranza.notas = request.form.get('notas')
            cobranza.pedido_id = request.form.get('pedido_id') or None
            cobranza.numero_comprobante = request.form.get('numero_comprobante')
            cobranza.tipo_comprobante = request.form.get('tipo_comprobante')
            
            cliente_nuevo = Cliente.query.get(cobranza.cliente_id)
            cliente_nuevo.saldo -= cobranza.monto
            
            db.session.commit()
            return redirect(url_for('listar_cobranzas'))
        except Exception as e:
            db.session.rollback()
            return render_template('cobranzas/formulario.html', cobranza=cobranza, clientes=clientes, pedidos=pedidos, error=str(e))
    
    return render_template('cobranzas/formulario.html', cobranza=cobranza, clientes=clientes, pedidos=pedidos)

# ==================== PAGOS ====================

@app.route('/pagos')
@usuario_requerido
def listar_pagos():
    """CORREGIDO: Paginar"""
    page = request.args.get('page', 1, type=int)
    pagos = Pago.query.order_by(Pago.fecha_pago.desc()).paginate(page=page, per_page=20)
    return render_template('pagos/lista.html', pagos=pagos)

@app.route('/pagos/nuevo', methods=['GET', 'POST'])
@usuario_requerido
def nuevo_pago():
    proveedores = Proveedor.query.all()
    pedidos = Pedido.query.all()
    clientes = Cliente.query.all()
    
    if request.method == 'POST':
        try:
            pago = Pago(
                proveedor_id=request.form['proveedor_id'],
                monto=float(request.form['monto']),
                metodo=request.form.get('metodo'),
                referencia=request.form.get('referencia'),
                notas=request.form.get('notas'),
                pedido_id=request.form.get('pedido_id') or None,
                numero_comprobante=request.form.get('numero_comprobante'),
                tipo_comprobante=request.form.get('tipo_comprobante')
            )
            
            proveedor = Proveedor.query.get(pago.proveedor_id)
            proveedor.saldo -= pago.monto
            
            db.session.add(pago)
            db.session.commit()
            return redirect(url_for('listar_pagos'))
        except Exception as e:
            return render_template('pagos/formulario.html', proveedores=proveedores, pedidos=pedidos, clientes=clientes, error=str(e))
    
    return render_template('pagos/formulario.html', proveedores=proveedores, pedidos=pedidos, clientes=clientes)

@app.route('/pagos/<int:id>/editar', methods=['GET', 'POST'])
@usuario_requerido
def editar_pago(id):
    pago = Pago.query.get_or_404(id)
    proveedores = Proveedor.query.all()
    pedidos = Pedido.query.all()
    clientes = Cliente.query.all()
    
    if request.method == 'POST':
        try:
            proveedor_anterior = Proveedor.query.get(pago.proveedor_id)
            proveedor_anterior.saldo += pago.monto
            
            pago.proveedor_id = request.form['proveedor_id']
            pago.monto = float(request.form['monto'])
            pago.metodo = request.form.get('metodo')
            pago.referencia = request.form.get('referencia')
            pago.notas = request.form.get('notas')
            pago.pedido_id = request.form.get('pedido_id') or None
            pago.numero_comprobante = request.form.get('numero_comprobante')
            pago.tipo_comprobante = request.form.get('tipo_comprobante')
            
            proveedor_nuevo = Proveedor.query.get(pago.proveedor_id)
            proveedor_nuevo.saldo -= pago.monto
            
            db.session.commit()
            return redirect(url_for('listar_pagos'))
        except Exception as e:
            db.session.rollback()
            return render_template('pagos/formulario.html', pago=pago, proveedores=proveedores, pedidos=pedidos, clientes=clientes, error=str(e))
    
    return render_template('pagos/formulario.html', pago=pago, proveedores=proveedores, pedidos=pedidos, clientes=clientes)

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
        proveedor.nombre = request.form['nombre']
        proveedor.cuit = request.form.get('cuit')
        proveedor.telefono = request.form.get('telefono')
        proveedor.direccion = request.form.get('direccion')
        proveedor.email = request.form.get('email')
        db.session.commit()
        return redirect(url_for('listar_proveedores'))
    
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
    
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.codigo = request.form.get('codigo')
        producto.precio_costo = request.form.get('precio_costo')
        producto.precio_venta = request.form.get('precio_venta')
        producto.stock = request.form.get('stock')
        db.session.commit()
        return redirect(url_for('listar_productos'))
    
    return render_template('productos/formulario.html', producto=producto)

@app.route('/pedidos/<int:id>/eliminar', methods=['POST'])
@usuario_requerido
def eliminar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    try:
        ItemPedido.query.filter_by(pedido_id=id).delete()
        db.session.delete(pedido)
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
    
    if request.method == 'POST':
        try:
            pedido.cliente_id = request.form['cliente_id']
            pedido.fecha_venta = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
            pedido.descripcion = request.form.get('descripcion')
            
            ItemPedido.query.filter_by(pedido_id=id).delete()
            
            productos_ids = request.form.getlist('producto_id[]')
            cantidades = request.form.getlist('cantidad[]')
            
            for prod_id, cantidad in zip(productos_ids, cantidades):
                if prod_id and cantidad:
                    producto = Producto.query.get(prod_id)
                    if producto:
                        item = ItemPedido(
                            pedido_id=id,
                            producto_id=int(prod_id),
                            cantidad=int(cantidad),
                            precio_unitario=producto.precio_venta
                        )
                        db.session.add(item)
            
            items = ItemPedido.query.filter_by(pedido_id=id).all()
            pedido.costo_total = sum(item.producto.precio_costo * item.cantidad for item in items)
            pedido.precio_venta_total = sum(item.precio_unitario * item.cantidad for item in items)
            pedido.resultado = pedido.precio_venta_total - pedido.costo_total
            
            db.session.commit()
            return redirect(url_for('listar_pedidos'))
        except Exception as e:
            db.session.rollback()
            return render_template('pedidos/formulario.html', pedido=pedido, clientes=clientes, productos=productos, error=str(e))
    
    return render_template('pedidos/formulario.html', pedido=pedido, clientes=clientes, productos=productos)

# ==================== REPORTES ====================

@app.route('/reportes/ventas')
@usuario_requerido
def reporte_ventas():
    """CORREGIDO: Paginar resultados"""
    page = request.args.get('page', 1, type=int)
    pedidos = Pedido.query.paginate(page=page, per_page=50)
    
    total_venta = db.session.query(func.sum(Pedido.precio_venta_total)).scalar() or 0
    total_costo = db.session.query(func.sum(Pedido.costo_total)).scalar() or 0
    total_resultado = db.session.query(func.sum(Pedido.resultado)).scalar() or 0
    
    return render_template('reportes/ventas.html',
                         pedidos=pedidos,
                         total_venta=total_venta,
                         total_costo=total_costo,
                         total_resultado=total_resultado)

@app.route('/reportes/saldos')
@usuario_requerido
def reporte_saldos():
    """CORREGIDO: Paginar"""
    page = request.args.get('page', 1, type=int)
    clientes = Cliente.query.paginate(page=page, per_page=20)
    proveedores = Proveedor.query.all()
    
    return render_template('reportes/saldos.html',
                         clientes=clientes,
                         proveedores=proveedores)

# ==================== CONCILIACIÓN ====================

@app.route('/conciliacion')
@usuario_requerido
def conciliacion():
    total_facturado = db.session.query(func.sum(Pedido.precio_venta_total)).scalar() or 0
    total_cobrado = db.session.query(func.sum(Cobranza.monto)).scalar() or 0
    saldo_pendiente = total_facturado - total_cobrado
    
    total_facturado_proveedores = db.session.query(func.sum(Pedido.costo_total)).scalar() or 0
    total_pagado = db.session.query(func.sum(Pago.monto)).scalar() or 0
    saldo_pendiente_proveedores = total_facturado_proveedores - total_pagado
    
    # CORREGIDO: Paginar en lugar de cargar todo
    page = request.args.get('page', 1, type=int)
    cobranzas_sin_conciliar = Cobranza.query.filter(Cobranza.pedido_id.is_(None)).paginate(page=page, per_page=20)
    pagos_sin_conciliar = Pago.query.filter(Pago.pedido_id.is_(None)).paginate(page=page, per_page=20)
    
    return render_template('conciliacion.html',
                         total_facturado=total_facturado,
                         total_cobrado=total_cobrado,
                         saldo_pendiente=saldo_pendiente,
                         total_facturado_proveedores=total_facturado_proveedores,
                         total_pagado=total_pagado,
                         saldo_pendiente_proveedores=saldo_pendiente_proveedores,
                         cobranzas_sin_conciliar=cobranzas_sin_conciliar,
                         pagos_sin_conciliar=pagos_sin_conciliar)

@app.route('/conciliar/cobranza/<int:cobranza_id>', methods=['GET', 'POST'])
@usuario_requerido
def conciliar_cobranza(cobranza_id):
    cobranza = Cobranza.query.get_or_404(cobranza_id)
    
    if request.method == 'POST':
        pedido_id = request.form.get('pedido_id')
        if pedido_id:
            cobranza.pedido_id = pedido_id
            db.session.commit()
            return redirect(url_for('conciliacion'))
    
    pedidos = Pedido.query.filter_by(cliente_id=cobranza.cliente_id).all()
    
    return render_template('conciliacion_cobranza.html', cobranza=cobranza, pedidos=pedidos)

@app.route('/conciliar/pago/<int:pago_id>', methods=['GET', 'POST'])
@usuario_requerido
def conciliar_pago(pago_id):
    pago = Pago.query.get_or_404(pago_id)
    
    if request.method == 'POST':
        pedido_id = request.form.get('pedido_id')
        if pedido_id:
            pago.pedido_id = pedido_id
            db.session.commit()
            return redirect(url_for('conciliacion'))
    
    pedidos = Pedido.query.join(Producto).filter(Producto.proveedor_id == pago.proveedor_id).all()
    
    return render_template('conciliacion_pago.html', pago=pago, pedidos=pedidos)

@app.template_filter('eur')
def formato_eur(valor):
    try:
        num = float(valor)
        return f"{num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return valor

@app.template_filter('formato_numero')
def formato_numero(valor):
    try:
        num = float(valor)
        return f"{num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return valor

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)