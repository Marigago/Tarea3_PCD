# Tarea 3 — API de Usuarios con FastAPI + DB

API REST para crear, actualizar, obtener y eliminar usuarios. Todos los endpoints bajo `/api/v1` están protegidos con **API Key** por header `X-API-Key`.

---

## Requisitos
- Python y `uv` instalados.
- Git (opcional).
- SQLite (incluido con Python).

---

## Instalación (con uv)

1) Crear carpeta del proyecto y entrar:
   - `mkdir Tarea3_PCD && cd Tarea3_PCD`

2) Inicializar proyecto:
   - `uv init`

3) Instalar dependencias:
   - `uv add fastapi --extra standard`
   - `uv add sqlalchemy`
   - `uv add pydantic`
   - `uv add python-dotenv`

---

## Variables de entorno

1) Crea el archivo `.env` a partir de `.env.example`.  

Contenido recomendado de `.env.example`:
API_KEY=<VALOR_AQUI>

En tu máquina, crea `.env` y reemplaza `<VALOR_AQUI>` por tu clave real:
API_KEY=mi_api_key_super_secreta


---

## Ejecutar la app

- `uv run fastapi dev main.py`

La app se sirve en:
- API: `http://127.0.0.1:8000`
- Documentación Swagger: `http://127.0.0.1:8000/docs`

**Importante:** En cada endpoint bajo `/api/v1` agrega el header `X-API-Key` con el mismo valor definido en `.env`.

---


## Endpoints (prefijo `/api/v1`)

### Explicación 

`curl`
Programa de línea de comandos para hacer peticiones HTTP (y otros protocolos). Permite llamar a tus endpoints desde la terminal.

`-X` (method)
Indica el método HTTP a usar. Ejemplos: `-X GET`, `-X POST`, `-X PUT`, `-X DELETE`.

Nota: si usas `-d` sin especificar `-X`, curl asume `POST`. Para enviar cuerpo con `PUT`, debes poner `-X PUT`.

`-H` (header)
Añade un header a la petición, con el formato `Nombre: valor`.
Puedes repetir `-H` varias veces para múltiples headers.

Ejemplos:

- `-H 'X-API-Key: API_KEY_AQUI'` → envía el API Key.

- `-H 'Content-Type: application/json'` → indica que el cuerpo es JSON.

`-d` (data)
Envía datos en el cuerpo (body) de la petición.

- Para JSON, combina con `-H 'Content-Type: application/json'` y pasa el JSON como cadena

- Si omites `-X`, `curl` hará POST automáticamente; para otros métodos con body, usa `-X PUT`.


### Ejemplo

1) **POST** `/api/v1/users/` — Crear usuario  
   - Example Body (JSON): 
     ```
        {
        "user_id": 1003,
        "user_name": "Lucía Gómez",
        "user_email": "lucia.gomez@hotmail.com",
        "recommendations": [
            "series",
            "fotografía",
            "arte"
        ],
        "age": 22,
        "ZIP": "28013"
        }
     ```
   - Respuestas:
     - `201 Created`
     - `409 Conflict` si `user_email` ya existe

2) **PUT** `/api/v1/users/{user_id}` — Actualizar usuario por id  
   - Body (JSON): campos opcionales a modificar.
   - Respuestas:
     - `200 OK`
     - `404 Not Found` si no existe
     - `409 Conflict` si `user_email` choca con otro

3) **GET** `/api/v1/users/{user_id}` — Obtener usuario por id  
   - Respuestas:
     - `200 OK`
     - `404 Not Found` si no existe

4) **DELETE** `/api/v1/users/{user_id}` — Eliminar usuario por id  
   - Respuestas:
     - `204 No Content`
     - `404 Not Found` si no existe

**Seguridad:** Todos los endpoints anteriores requieren header `X-API-Key`.

---

## Ejemplos de requests (curl)

> Reemplaza `API_KEY` por el valor real de tu `.env`.

# Crear (POST)
curl -X POST http://127.0.0.1:8000/api/v1/users/ \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: API_KEY_AQUI' \
  -d '{
    "user_name": "María Fernanda Ruiz",
    "user_id": 1001,
    "user_email": "mfernanda.ruiz@gmail.com",
    "age": 27,
    "recommendations": ["libros","viajes","café"],
    "ZIP": "44100"
  }'

# Obtener (GET)
curl -H 'X-API-Key: API_KEY_AQUI' \
  http://127.0.0.1:8000/api/v1/users/1001

# Actualizar (PUT)
curl -X PUT http://127.0.0.1:8000/api/v1/users/1001 \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: API_KEY_AQUI' \
  -d '{
    "user_name": "M. Fernanda Ruiz",
    "recommendations": ["viajes","café"]
  }'

# Eliminar (DELETE)
curl -X DELETE \
  -H 'X-API-Key: API_KEY_AQUI' \
  http://127.0.0.1:8000/api/v1/users/1001


---

## Notas
- DB por defecto: `sqlite:///./app.db`.  
- Códigos comunes:
  - `401 Unauthorized`: API Key inválida o ausente en header `X-API-Key`.
  - `404 Not Found`: Usuario no encontrado.
  - `409 Conflict`:   El email ya existe en la tabla, o conflicto al crear: verifica que user_id y email no estén repetidos.
  - `422 Unprocessable Entity`: body inválido (p. ej., email mal formado).