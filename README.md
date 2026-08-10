# E-Commerce Argentina API (FastAPI)

¡Bienvenido al repositorio inicial de **E-Commerce Argentina API**! Este proyecto es una API REST backend desarrollada en Python con FastAPI, diseñada bajo una arquitectura limpia y modular sin almacenamiento persistente inicial (sin base de datos).

El objetivo principal es servir como base sólida, escalable y conforme al marco normativo vigente para tiendas de comercio electrónico en la República Argentina.

---

## 📐 Estructura del Proyecto

El código está organizado siguiendo la separación de responsabilidades y buenas prácticas de desarrollo backend:

```text
mi-ecomerce/
├── .gitignore
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py
    ├── main.py
    ├── core/          # Configuraciones globales y constantes del sistema
    ├── models/        # Representación de entidades internas
    ├── schemas/       # Esquemas de validación Pydantic (DTOs)
    ├── services/      # Lógica de negocio de la tienda
    └── routers/       # Endpoints y controladores API REST
```

---

## ⚖️ Marco Legal y Normativa (República Argentina)

Este backend incorpora desde su diseño base la preparación para dar cumplimiento estricto a las regulaciones nacionales exigidas para el comercio electrónico:

1. **Ley N° 24.240 — Defensa del Consumidor**
   - Garantiza el acceso transparente a la información de los productos, términos de contratación y derecho a la información clara, precisa y gratuita.

2. **Resolución 424/2020 (Secretaría de Comercio Interior) — Botón de Arrepentimiento**
   - Facilita la revocación de la compra (derecho de desestimación) dentro de los 10 días corridos a partir de la entrega del producto o la firma del contrato, mediante un enlace accesible y visible.

3. **Ley N° 25.326 — Protección de Datos Personales (Habeas Data)**
   - Establece los principios de seguridad, confidencialidad y tratamiento responsable de los datos recolectados de los usuarios y clientes en la plataforma.

---

## 🛠️ Requisitos Previos

- **Python 3.10+**
- **pip** (administrador de paquetes de Python)

---

## 🚀 Instalación y Ejecución Local

### 1. Clonar el repositorio y acceder a la carpeta
```bash
git clone <URL_DEL_REPOSITORIO>
cd mi-ecomerce
```

### 2. Crear y activar un entorno virtual (Recomendado)

- **En Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

- **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar el servidor de desarrollo
Para iniciar la API en modo de desarrollo con recarga automática (*live reload*), ejecutá:

```bash
uvicorn app.main:app --reload
```

---

## 🌐 Endpoints y Documentación Interactive

Una vez encendido el servidor, podés acceder a las siguientes direcciones en tu navegador:

- **Mensaje de bienvenida y verificación:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentación Swagger UI (Interactive API Docs):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentación ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
