from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ==================== ERP ====================

class ERP(db.Model):
    __tablename__ = 'erps'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    descripcion = db.Column(db.String(500))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    color_primario = db.Column(db.String(7), default='#667eea')  # Color del sidebar
    icono = db.Column(db.String(50), default='📊')  # Emoji representativo
    
    def __repr__(self):
        return f'<ERP {self.nombre}>'

# ==================== USUARIO ====================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    nombre = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255))
    rol = db.Column(db.String(50), default='usuario')  # admin, usuario
    permisos = db.Column(db.String(50), default='view')  # view, edit
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    idioma = db.Column(db.String(10), default='es')  # es, en
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.rol == 'admin'

    def puede_editar(self):
        return self.is_admin() or self.permisos == 'edit'
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

# ==================== MAESTROS ====================

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    mercado = db.Column(db.String(255))
    puesto = db.Column(db.String(255))
    contacto = db.Column(db.String(255))
    cuit = db.Column(db.String(20))
    telefono = db.Column(db.String(50))
    direccion = db.Column(db.String(255))
    email = db.Column(db.String(255))
    saldo = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True, cascade="all, delete-orphan")
    cobranzas = db.relationship('Cobranza', backref='cliente', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'


class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    razon_social = db.Column(db.String(255))
    cuit = db.Column(db.String(20), unique=True)
    direccion = db.Column(db.String(255))
    provincia = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(255))
    saldo = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    contactos = db.relationship('ProveedorContacto', backref='proveedor', lazy=True, cascade="all, delete-orphan")
    productos = db.relationship('Producto', backref='proveedor', lazy=True, cascade="all, delete-orphan")
    
    def tiene_contacto_logistico(self):
        return any(contacto.contacto_logistico for contacto in self.contactos)
    
    def validar_contacto_logistico(self):
        if not self.tiene_contacto_logistico():
            raise ValueError('El campo contacto logístico debe tener un si en el proveedor cargado')
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'


class ProveedorContacto(db.Model):
    __tablename__ = 'proveedores_contactos'
    
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(100))
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(255))
    contacto_logistico = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ProveedorContacto {self.nombre} ({"Logístico" if self.contacto_logistico else "No logístico"})>'


class ProveedorLogistico(db.Model):
    __tablename__ = 'proveedores_logisticos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    cuit = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(255))
    tarifa = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    pedidos = db.relationship('Pedido', backref='prov_logistico', lazy=True)
    
    def __repr__(self):
        return f'<ProveedorLogistico {self.nombre}>'



# Tablas maestras independientes
class Fruta(db.Model):
    __tablename__ = 'frutas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f'<Fruta {self.nombre}>'

class Variedad(db.Model):
    __tablename__ = 'variedades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f'<Variedad {self.nombre}>'

class Clasificacion(db.Model):
    __tablename__ = 'clasificaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f'<Clasificacion {self.nombre}>'

class Envase(db.Model):
    __tablename__ = 'envases'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f'<Envase {self.nombre}>'

class Marca(db.Model):
    __tablename__ = 'marcas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    def __repr__(self):
        return f'<Marca {self.nombre}>'


class Kilogramo(db.Model):
    __tablename__ = 'kilogramos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Kilogramo {self.nombre}>'


class FormaCobro(db.Model):
    """Formas de pago en cobranzas (Efectivo, Transferencia, etc.)"""
    __tablename__ = 'formas_cobro'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<FormaCobro {self.nombre}>'


class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    fruta = db.Column(db.String(255), nullable=False)
    variedad = db.Column(db.String(255))
    clasificacion = db.Column(db.String(255))
    envase = db.Column(db.String(255))
    kilogramo = db.Column(db.String(50))
    marca = db.Column(db.String(255))
    costo_unitario = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('proveedor_id', 'fruta', 'variedad', 'clasificacion', 'envase', 'kilogramo', 'marca', name='uq_producto_combinacion'),
    )
    
    items_pedido = db.relationship('ItemPedido', backref='producto', lazy=True, cascade="all, delete-orphan")
    cotizaciones = db.relationship('Cotizacion', backref='producto', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'


# ==================== COTIZACIONES ====================

class Cotizacion(db.Model):
    __tablename__ = 'cotizaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date, nullable=False)
    costo_unitario = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    margen_ganancia = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    def calcular_margen_desde_precio(self):
        """Margen % = (Precio - Costo) / Costo"""
        if not self.costo_unitario:
            self.margen_ganancia = 0
            return 0
        self.margen_ganancia = ((self.precio_unitario - self.costo_unitario) / self.costo_unitario) * 100
        return self.margen_ganancia

    def calcular_precio_desde_margen(self):
        """Precio = Costo * (1 + margen/100) — uso legacy"""
        if self.margen_ganancia is None:
            self.margen_ganancia = 0
        self.precio_unitario = self.costo_unitario * (1 + self.margen_ganancia / 100)
        return self.precio_unitario
    
    def __repr__(self):
        return f'<Cotizacion {self.producto.nombre if self.producto else "?"} {self.fecha_desde}>'


class ConfigMargen(db.Model):
    __tablename__ = 'config_margen'
    
    id = db.Column(db.Integer, primary_key=True)
    margen_default = db.Column(db.Float, default=30)
    
    def __repr__(self):
        return f'<ConfigMargen {self.margen_default}%>'


# ==================== TRANSACCIONALES ====================

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    prov_logistico_id = db.Column(db.Integer, db.ForeignKey('proveedores_logisticos.id'))
    fecha_venta = db.Column(db.Date, nullable=False, default=datetime.now)
    fecha_carga = db.Column(db.Date)
    mercado = db.Column(db.String(100))
    puesto = db.Column(db.String(50))
    remito = db.Column(db.String(50))
    fecha_remito = db.Column(db.Date)
    remito_adjunto_path = db.Column(db.String(500))
    remito_adjunto_nombre = db.Column(db.String(255))
    entregado_opcion = db.Column(db.String(10), default='')  # 'SI' o vacío
    fecha_entrega = db.Column(db.Date)
    cargado = db.Column(db.Boolean, default=False)
    entregado = db.Column(db.Boolean, default=False)
    eliminado = db.Column(db.Boolean, default=False)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    
    costo_total = db.Column(db.Float, default=0)
    precio_venta_total = db.Column(db.Float, default=0)
    comision = db.Column(db.Float, default=0)
    resultado = db.Column(db.Float, default=0)
    descuento_monto = db.Column(db.Float, default=0)
    descuento_costo = db.Column(db.Float, default=0)
    descuento_comision = db.Column(db.Float, default=0)
    descuento_sobre_costo = db.Column(db.Boolean, default=False)
    descuento_sobre_comision = db.Column(db.Boolean, default=False)
    
    items = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Pedido {self.numero}>'


class ItemPedido(db.Model):
    __tablename__ = 'items_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    pallets = db.Column(db.Integer, default=0)
    bultos = db.Column(db.Integer, default=0)
    kg = db.Column(db.String(50))
    cantidad = db.Column(db.Float, default=0)
    unidad = db.Column(db.String(50), default='Bultos')
    costo_unitario = db.Column(db.Float, default=0)
    precio_unitario = db.Column(db.Float, default=0)
    costo_total = db.Column(db.Float, default=0)
    precio_total = db.Column(db.Float, default=0)
    comision = db.Column(db.Float, default=0)
    resultado = db.Column(db.Float, default=0)
    
    def __repr__(self):
        return f'<ItemPedido {self.id}>'


class Cobranza(db.Model):
    __tablename__ = 'cobranzas'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha_cobranza = db.Column(db.Date, default=datetime.now)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(100))
    referencia = db.Column(db.String(100))
    notas = db.Column(db.Text)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=True)
    numero_comprobante = db.Column(db.String(100))
    tipo_comprobante = db.Column(db.String(50))
    eliminado = db.Column(db.Boolean, default=False)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    
    lineas = db.relationship('CobranzaLinea', backref='cobranza', lazy=True, cascade="all, delete-orphan")
    imputaciones = db.relationship('CobranzaImputacion', back_populates='cobranza', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Cobranza {self.id}>'


class CobranzaLinea(db.Model):
    __tablename__ = 'cobranzas_lineas'
    
    id = db.Column(db.Integer, primary_key=True)
    cobranza_id = db.Column(db.Integer, db.ForeignKey('cobranzas.id'), nullable=False)
    forma = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    concepto = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<CobranzaLinea {self.id} {self.forma} {self.monto}>'


# ==================== CONCILIACIÓN ====================

class CobranzaImputacion(db.Model):
    __tablename__ = 'cobranzas_imputaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    cobranza_id = db.Column(db.Integer, db.ForeignKey('cobranzas.id'), nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    monto_imputado = db.Column(db.Float, nullable=False)
    pago_proveedor = db.Column(db.Float, default=0)
    comision = db.Column(db.Float, default=0)
    fecha_conciliacion = db.Column(db.DateTime, default=datetime.now)
    
    pedido = db.relationship('Pedido')
    cobranza = db.relationship('Cobranza', back_populates='imputaciones')
    
    def __repr__(self):
        return f'<CobranzaImputacion {self.id} {self.monto_imputado}>'
