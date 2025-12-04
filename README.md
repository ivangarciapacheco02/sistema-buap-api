# Sistema BUAP API

API REST para el sistema de gestión de la BUAP (Benemérita Universidad Autónoma de Puebla).

## Requerimientos

### Software
* Python 3.5+
* Pip 3
* MySQL o MariaDB

### Dependencias del sistema (Linux/Debian)

Antes de instalar las dependencias de Python, es necesario instalar las librerías de desarrollo del sistema:

```bash
sudo apt-get update
sudo apt-get install -y pkg-config default-libmysqlclient-dev python3-dev build-essential
```

**Nota:** Si usas MariaDB en lugar de MySQL, instala `libmariadb-dev` en lugar de `default-libmysqlclient-dev`:

```bash
sudo apt-get install -y pkg-config libmariadb-dev python3-dev build-essential
```

## Instalación

1. Instalar Python 3.5+
2. Instalar Pip 3
3. Instalar virtualenv
4. Clonar el proyecto
5. Activar el ambiente virtual:
   ```bash
   $ source env/bin/activate
   ```
   Windows:
   ```bash
   C:/path_to_the_folder/> env/Project_name/Scripts/activate.bat
   ```
6. **Instalar las dependencias del sistema** (ver sección de Requerimientos arriba)
7. Instalar las librerías requeridas:
   ```bash
   $ pip3 install -r requirements.txt
   ```
7. Configurar conexión a base de datos (MySQL) en `/sistema_buap_api/my.cnf`
8. Crear la base de datos y aplicar las migraciones:
   ```bash
   $ python3 manage.py makemigrations sistema_buap_api
   $ python3 manage.py migrate
   ```
9. Crear un superusuario de Django:
   ```bash
   $ python3 manage.py createsuperuser --email admin@admin.com --username admin
   ```
10. Ejecutar el servidor:
    ```bash
    $ python3 manage.py runserver
    ```

---

## Autenticación

La API utiliza autenticación por token. Para obtener un token, debes hacer login usando el endpoint `/token/`. Una vez obtenido el token, inclúyelo en el header de las peticiones:

```
Authorization: Token <tu_token>
```

---

## Endpoints

### Bootstrap

#### Obtener versión de la API
- **URL:** `/bootstrap/version`
- **Método:** `GET`
- **Autenticación:** No requerida
- **Descripción:** Retorna la versión actual de la API
- **Respuesta exitosa (200):**
  ```json
  {
    "version": "1.0.0"
  }
  ```

---

### Autenticación

#### Login
- **URL:** `/token/`
- **Método:** `POST`
- **Autenticación:** No requerida
- **Descripción:** Autentica un usuario y retorna su token junto con la información del perfil según su rol
- **Parámetros del body:**
  ```json
  {
    "username": "email@ejemplo.com",
    "password": "contraseña"
  }
  ```
- **Respuesta exitosa (200):**
  - Para alumno:
    ```json
    {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan@ejemplo.com"
      },
      "id_alumno": "123456",
      "fecha_nacimiento": "2000-01-01",
      "curp": "PEPJ000101HDFRRNA1",
      "rfc": "PEPJ000101XXX",
      "edad": 24,
      "telefono": "2221234567",
      "ocupacion": "Estudiante",
      "token": "abc123def456...",
      "rol": "alumno"
    }
    ```
  - Para maestro:
    ```json
    {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "María",
        "last_name": "González",
        "email": "maria@ejemplo.com"
      },
      "id_trabajador": "T001",
      "fecha_nacimiento": "1980-05-15",
      "telefono": "2227654321",
      "rfc": "GOMR800515XXX",
      "cubiculo": "A-101",
      "area_investigacion": "Ciencias de la Computación",
      "materias_json": "[{\"id\": 1, \"nombre\": \"Algoritmos\"}]",
      "token": "abc123def456...",
      "rol": "maestro"
    }
    ```
  - Para administrador:
    ```json
    {
      "id": 1,
      "first_name": "Admin",
      "last_name": "Sistema",
      "email": "admin@ejemplo.com",
      "token": "abc123def456...",
      "rol": "administrador"
    }
    ```
- **Respuesta de error (403):**
  ```json
  {
    "details": "Forbidden"
  }
  ```

#### Logout
- **URL:** `/logout/`
- **Método:** `GET`
- **Autenticación:** Requerida (Token)
- **Descripción:** Elimina el token de autenticación del usuario
- **Respuesta exitosa (200):**
  ```json
  {
    "logout": true
  }
  ```

---

### Administradores

#### Crear administrador
- **URL:** `/admin/`
- **Método:** `POST`
- **Autenticación:** No requerida
- **Descripción:** Crea un nuevo administrador en el sistema
- **Parámetros del body:**
  ```json
  {
    "rol": "administrador",
    "first_name": "Admin",
    "last_name": "Sistema",
    "email": "admin@ejemplo.com",
    "password": "contraseña123",
    "clave_admin": "ADM001",
    "telefono": "2221234567",
    "rfc": "ADMS800101XXX",
    "edad": 40,
    "ocupacion": "Administrador"
  }
  ```
- **Respuesta exitosa (201):**
  ```json
  {
    "admin_created_id": 1
  }
  ```
- **Respuesta de error (400):**
  ```json
  {
    "message": "Username admin@ejemplo.com, is already taken"
  }
  ```

#### Obtener administrador por ID
- **URL:** `/admin/?id=<id>`
- **Método:** `GET`
- **Autenticación:** No requerida
- **Parámetros de query:**
  - `id` (requerido): ID del administrador
- **Respuesta exitosa (200):**
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "first_name": "Admin",
      "last_name": "Sistema",
      "email": "admin@ejemplo.com"
    },
    "clave_admin": "ADM001",
    "telefono": "2221234567",
    "rfc": "ADMS800101XXX",
    "edad": 40,
    "ocupacion": "Administrador"
  }
  ```

#### Listar todos los administradores
- **URL:** `/lista-admins/`
- **Método:** `GET`
- **Autenticación:** Requerida (Token)
- **Descripción:** Retorna una lista de todos los administradores activos
- **Respuesta exitosa (200):**
  ```json
  [
    {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "Admin",
        "last_name": "Sistema",
        "email": "admin@ejemplo.com"
      },
      "clave_admin": "ADM001",
      "telefono": "2221234567",
      "rfc": "ADMS800101XXX",
      "edad": 40,
      "ocupacion": "Administrador"
    }
  ]
  ```

#### Editar administrador
- **URL:** `/admins-edit/`
- **Método:** `PUT`
- **Autenticación:** Requerida (Token)
- **Descripción:** Actualiza la información de un administrador
- **Parámetros del body:**
  ```json
  {
    "id": 1,
    "first_name": "Admin",
    "last_name": "Actualizado",
    "clave_admin": "ADM001",
    "telefono": "2221234567",
    "rfc": "ADMS800101XXX",
    "edad": 41,
    "ocupacion": "Administrador Principal"
  }
  ```
- **Respuesta exitosa (200):**
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "first_name": "Admin",
      "last_name": "Actualizado",
      "email": "admin@ejemplo.com"
    },
    "clave_admin": "ADM001",
    "telefono": "2221234567",
    "rfc": "ADMS800101XXX",
    "edad": 41,
    "ocupacion": "Administrador Principal"
  }
  ```

#### Eliminar administrador
- **URL:** `/admins-edit/?id=<id>`
- **Método:** `DELETE`
- **Autenticación:** Requerida (Token)
- **Parámetros de query:**
  - `id` (requerido): ID del administrador a eliminar
- **Respuesta exitosa (200):**
  ```json
  {
    "details": "Administrador eliminado"
  }
  ```
- **Respuesta de error (400):**
  ```json
  {
    "details": "Algo pasó al eliminar"
  }
  ```

#### Obtener estadísticas de usuarios
- **URL:** `/admins-edit/`
- **Método:** `GET`
- **Autenticación:** Requerida (Token)
- **Descripción:** Retorna el conteo total de administradores, maestros y alumnos activos
- **Respuesta exitosa (200):**
  ```json
  {
    "admins": 5,
    "maestros": 25,
    "alumnos:": 150
  }
  ```

---

### Alumnos

#### Crear alumno
- **URL:** `/alumnos/`
- **Método:** `POST`
- **Autenticación:** No requerida
- **Descripción:** Registra un nuevo alumno en el sistema
- **Parámetros del body:**
  ```json
  {
    "rol": "alumno",
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@ejemplo.com",
    "password": "contraseña123",
    "id_alumno": "123456",
    "fecha_nacimiento": "2000-01-01",
    "curp": "PEPJ000101HDFRRNA1",
    "rfc": "PEPJ000101XXX",
    "edad": 24,
    "telefono": "2221234567",
    "ocupacion": "Estudiante"
  }
  ```
- **Respuesta exitosa (201):**
  ```json
  {
    "alumno_created_id": 1
  }
  ```
- **Respuesta de error (400):**
  ```json
  {
    "message": "Username juan@ejemplo.com, is already taken"
  }
  ```

#### Obtener alumno por ID
- **URL:** `/alumnos/?id=<id>`
- **Método:** `GET`
- **Autenticación:** No requerida
- **Parámetros de query:**
  - `id` (requerido): ID del alumno
- **Respuesta exitosa (200):**
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan@ejemplo.com"
    },
    "id_alumno": "123456",
    "fecha_nacimiento": "2000-01-01",
    "curp": "PEPJ000101HDFRRNA1",
    "rfc": "PEPJ000101XXX",
    "edad": 24,
    "telefono": "2221234567",
    "ocupacion": "Estudiante"
  }
  ```

#### Listar todos los alumnos
- **URL:** `/lista-alumnos/`
- **Método:** `GET`
- **Autenticación:** Requerida (Token)
- **Descripción:** Retorna una lista de todos los alumnos activos
- **Respuesta exitosa (200):**
  ```json
  [
    {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan@ejemplo.com"
      },
      "id_alumno": "123456",
      "fecha_nacimiento": "2000-01-01",
      "curp": "PEPJ000101HDFRRNA1",
      "rfc": "PEPJ000101XXX",
      "edad": 24,
      "telefono": "2221234567",
      "ocupacion": "Estudiante"
    }
  ]
  ```
- **Respuesta de error (400):** Si no hay alumnos
  ```json
  {}
  ```

#### Editar alumno
- **URL:** `/alumnos-edit/`
- **Método:** `PUT`
- **Autenticación:** Requerida (Token)
- **Descripción:** Actualiza la información de un alumno
- **Parámetros del body:**
  ```json
  {
    "id": 1,
    "first_name": "Juan",
    "last_name": "Pérez García",
    "id_alumno": "123456",
    "fecha_nacimiento": "2000-01-01",
    "curp": "PEPJ000101HDFRRNA1",
    "rfc": "PEPJ000101XXX",
    "edad": 25,
    "telefono": "2221234567",
    "ocupacion": "Estudiante"
  }
  ```
- **Respuesta exitosa (200):**
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "first_name": "Juan",
      "last_name": "Pérez García",
      "email": "juan@ejemplo.com"
    },
    "id_alumno": "123456",
    "fecha_nacimiento": "2000-01-01",
    "curp": "PEPJ000101HDFRRNA1",
    "rfc": "PEPJ000101XXX",
    "edad": 25,
    "telefono": "2221234567",
    "ocupacion": "Estudiante"
  }
  ```

#### Eliminar alumno
- **URL:** `/alumnos-edit/?id=<id>`
- **Método:** `DELETE`
- **Autenticación:** Requerida (Token)
- **Parámetros de query:**
  - `id` (requerido): ID del alumno a eliminar
- **Respuesta exitosa (200):**
  ```json
  {
    "details": "Alumno eliminado"
  }
  ```
- **Respuesta de error (400):**
  ```json
  {
    "details": "Algo pasó al eliminar"
  }
  ```

---

### Maestros

#### Crear maestro
- **URL:** `/maestros/`
- **Método:** `POST`
- **Autenticación:** No requerida
- **Descripción:** Registra un nuevo maestro en el sistema
- **Parámetros del body:**
  ```json
  {
    "rol": "maestro",
    "first_name": "María",
    "last_name": "González",
    "email": "maria@ejemplo.com",
    "password": "contraseña123",
    "id_trabajador": "T001",
    "fecha_nacimiento": "1980-05-15",
    "telefono": "2227654321",
    "rfc": "GOMR800515XXX",
    "cubiculo": "A-101",
    "area_investigacion": "Ciencias de la Computación",
    "materias_json": [
      {
        "id": 1,
        "nombre": "Algoritmos"
      }
    ]
  }
  ```
- **Respuesta exitosa (201):**
  ```json
  {
    "maestro_created_id": 1
  }
  ```
- **Respuesta de error (400):**
  ```json
  {
    "message": "Username maria@ejemplo.com, is already taken"
  }
  ```

#### Obtener maestro por ID
- **URL:** `/maestros/?id=<id>`
- **Método:** `GET`
- **Autenticación:** No requerida
- **Parámetros de query:**
  - `id` (requerido): ID del maestro
- **Respuesta exitosa (200):**
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "first_name": "María",
      "last_name": "González",
      "email": "maria@ejemplo.com"
    },
    "id_trabajador": "T001",
    "fecha_nacimiento": "1980-05-15",
    "telefono": "2227654321",
    "rfc": "GOMR800515XXX",
    "cubiculo": "A-101",
    "area_investigacion": "Ciencias de la Computación",
    "materias_json": [
      {
        "id": 1,
        "nombre": "Algoritmos"
      }
    ]
  }
  ```

#### Listar todos los maestros
- **URL:** `/lista-maestros/`
- **Método:** `GET`
- **Autenticación:** Requerida (Token)
- **Descripción:** Retorna una lista de todos los maestros activos con sus materias parseadas
- **Respuesta exitosa (200):**
  ```json
  [
    {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "María",
        "last_name": "González",
        "email": "maria@ejemplo.com"
      },
      "id_trabajador": "T001",
      "fecha_nacimiento": "1980-05-15",
      "telefono": "2227654321",
      "rfc": "GOMR800515XXX",
      "cubiculo": "A-101",
      "area_investigacion": "Ciencias de la Computación",
      "materias_json": [
        {
          "id": 1,
          "nombre": "Algoritmos"
        }
      ]
    }
  ]
  ```
- **Respuesta de error (400):** Si no hay maestros
  ```json
  {}
  ```

#### Obtener nombres de maestros
- **URL:** `/nombre-maestros/`
- **Método:** `GET`
- **Autenticación:** Requerida (Token)
- **Descripción:** Retorna una lista de todos los maestros activos (similar a lista-maestros pero sin parsear materias_json)
- **Respuesta exitosa (200):**
  ```json
  [
    {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "María",
        "last_name": "González",
        "email": "maria@ejemplo.com"
      },
      "id_trabajador": "T001",
      "fecha_nacimiento": "1980-05-15",
      "telefono": "2227654321",
      "rfc": "GOMR800515XXX",
      "cubiculo": "A-101",
      "area_investigacion": "Ciencias de la Computación",
      "materias_json": "[{\"id\": 1, \"nombre\": \"Algoritmos\"}]"
    }
  ]
  ```

#### Editar maestro
- **URL:** `/maestros-edit/`
- **Método:** `PUT`
- **Autenticación:** Requerida (Token)
- **Descripción:** Actualiza la información de un maestro
- **Parámetros del body:**
  ```json
  {
    "id": 1,
    "first_name": "María",
    "last_name": "González López",
    "id_trabajador": "T001",
    "fecha_nacimiento": "1980-05-15",
    "telefono": "2227654321",
    "rfc": "GOMR800515XXX",
    "cubiculo": "A-102",
    "area_investigacion": "Inteligencia Artificial",
    "materias_json": [
      {
        "id": 1,
        "nombre": "Algoritmos"
      },
      {
        "id": 2,
        "nombre": "Machine Learning"
      }
    ]
  }
  ```
- **Respuesta exitosa (200):**
  ```json
  {
    "id": 1,
    "user": {
      "id": 1,
      "first_name": "María",
      "last_name": "González López",
      "email": "maria@ejemplo.com"
    },
    "id_trabajador": "T001",
    "fecha_nacimiento": "1980-05-15",
    "telefono": "2227654321",
    "rfc": "GOMR800515XXX",
    "cubiculo": "A-102",
    "area_investigacion": "Inteligencia Artificial",
    "materias_json": "[{\"id\": 1, \"nombre\": \"Algoritmos\"}, {\"id\": 2, \"nombre\": \"Machine Learning\"}]"
  }
  ```

#### Eliminar maestro
- **URL:** `/maestros-edit/?id=<id>`
- **Método:** `DELETE`
- **Autenticación:** Requerida (Token)
- **Parámetros de query:**
  - `id` (requerido): ID del maestro a eliminar
- **Respuesta exitosa (200):**
  ```json
  {
    "details": "Maestro eliminado"
  }
  ```
- **Respuesta de error (400):**
  ```json
  {
    "details": "Algo pasó al eliminar"
  }
  ```

---

### Eventos

#### Crear evento
- **URL:** `/eventos/`
- **Método:** `POST`
- **Autenticación:** No requerida
- **Descripción:** Registra un nuevo evento en el sistema. Todos los campos son obligatorios.
- **Parámetros del body:**
  ```json
  {
    "nombre_evento": "Conferencia de Tecnología",
    "tipo_evento": "Conferencia",
    "fecha_realizacion": "2024-12-15",
    "hora_inicio": "09:00",
    "hora_fin": "11:00",
    "lugar": "Auditorio Principal",
    "publico_objetivo": "Estudiantes",
    "programa_educativo": "Ingeniería en Ciencias de la Computación",
    "responsable": 1,
    "descripcion_breve": "Conferencia sobre las últimas tendencias en tecnología",
    "cupo_maximo": 100
  }
  ```
- **Campos requeridos:**
  - `nombre_evento` (string): Nombre del evento
  - `tipo_evento` (string): Tipo de evento. Opciones: "Conferencia", "Taller", "Seminario", "Curso", "Congreso", "Simposio", "Foro", "Otro"
  - `fecha_realizacion` (date): Fecha de realización en formato YYYY-MM-DD
  - `hora_inicio` (string): Hora de inicio en formato HH:MM
  - `hora_fin` (string): Hora de fin en formato HH:MM (debe ser posterior a hora_inicio)
  - `lugar` (string): Lugar donde se realizará el evento
  - `publico_objetivo` (string): Público objetivo. Opciones: "Estudiantes", "Profesores", "Público general"
  - `programa_educativo` (string): **Requerido solo si publico_objetivo es "Estudiantes"**
  - `responsable` (integer): ID del usuario responsable (debe ser maestro o administrador)
  - `descripcion_breve` (string): Descripción breve del evento
  - `cupo_maximo` (integer): Cupo máximo de asistentes (debe ser mayor a 0)
- **Respuesta exitosa (201):**
  ```json
  {
    "evento_created_id": 1
  }
  ```
- **Respuestas de error (400):**
  - Campos faltantes:
    ```json
    {
      "details": "Campos requeridos faltantes",
      "campos_faltantes": ["nombre_evento", "tipo_evento"],
      "campos_requeridos": ["nombre_evento", "tipo_evento", ...]
    }
    ```
  - Programa educativo faltante:
    ```json
    {
      "details": "El programa educativo es requerido cuando el público objetivo es Estudiantes"
    }
    ```
  - Responsable inválido:
    ```json
    {
      "details": "El responsable debe ser un maestro o administrador",
      "usuario_id": 1
    }
    ```

#### Obtener evento por ID
- **URL:** `/eventos/?id=<id>`
- **Método:** `GET`
- **Autenticación:** No requerida
- **Parámetros de query:**
  - `id` (requerido): ID del evento
- **Respuesta exitosa (200):**
  ```json
  {
    "id": 1,
    "nombre_evento": "Conferencia de Tecnología",
    "tipo_evento": "Conferencia",
    "fecha_realizacion": "2024-12-15",
    "hora_inicio": "09:00",
    "hora_fin": "11:00",
    "lugar": "Auditorio Principal",
    "publico_objetivo": "Estudiantes",
    "programa_educativo": "Ingeniería en Ciencias de la Computación",
    "responsable": 1,
    "descripcion_breve": "Conferencia sobre las últimas tendencias en tecnología",
    "cupo_maximo": 100,
    "creation": "2024-12-01T10:00:00Z",
    "update": "2024-12-01T10:00:00Z"
  }
  ```
- **Respuesta de error (404):**
  ```json
  {
    "details": "Evento no encontrado"
  }
  ```

#### Listar todos los eventos
- **URL:** `/lista-eventos/`
- **Método:** `GET`
- **Autenticación:** Requerida (Token)
- **Descripción:** Retorna una lista de todos los eventos ordenados por fecha de realización y hora de inicio
- **Respuesta exitosa (200):**
  ```json
  [
    {
      "id": 1,
      "nombre_evento": "Conferencia de Tecnología",
      "tipo_evento": "Conferencia",
      "fecha_realizacion": "2024-12-15",
      "hora_inicio": "09:00",
      "hora_fin": "11:00",
      "lugar": "Auditorio Principal",
      "publico_objetivo": "Estudiantes",
      "programa_educativo": "Ingeniería en Ciencias de la Computación",
      "responsable": 1,
      "descripcion_breve": "Conferencia sobre las últimas tendencias en tecnología",
      "cupo_maximo": 100,
      "creation": "2024-12-01T10:00:00Z",
      "update": "2024-12-01T10:00:00Z"
    }
  ]
  ```
- **Respuesta exitosa (200):** Si no hay eventos, retorna lista vacía
  ```json
  []
  ```

#### Editar evento
- **URL:** `/eventos-edit/`
- **Método:** `PUT`
- **Autenticación:** Requerida (Token)
- **Descripción:** Actualiza la información de un evento. Todos los campos son obligatorios.
- **Parámetros del body:**
  ```json
  {
    "id": 1,
    "nombre_evento": "Conferencia de Tecnología Avanzada",
    "tipo_evento": "Conferencia",
    "fecha_realizacion": "2024-12-20",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "lugar": "Auditorio Secundario",
    "publico_objetivo": "Profesores",
    "programa_educativo": null,
    "responsable": 2,
    "descripcion_breve": "Conferencia actualizada sobre tecnología",
    "cupo_maximo": 150
  }
  ```
- **Nota:** Si `publico_objetivo` es "Estudiantes", el campo `programa_educativo` es requerido. Si es "Profesores" o "Público general", puede ser `null`.
- **Respuesta exitosa (200):** Retorna el evento actualizado con la misma estructura que GET

#### Eliminar evento
- **URL:** `/eventos-edit/?id=<id>`
- **Método:** `DELETE`
- **Autenticación:** Requerida (Token)
- **Parámetros de query:**
  - `id` (requerido): ID del evento a eliminar
- **Respuesta exitosa (200):**
  ```json
  {
    "details": "Evento eliminado"
  }
  ```
- **Respuesta de error (400):**
  ```json
  {
    "details": "Algo pasó al eliminar"
  }
  ```

---

## Notas importantes

### Campos JSON

Algunos campos en la base de datos se almacenan como JSON en formato de texto:

- **`materias_json`** (Maestros): Array de objetos con las materias que imparte el maestro
### Validaciones de Eventos

- **Todos los campos son obligatorios** al crear o editar un evento
- **Programa educativo condicional**: Solo es requerido cuando `publico_objetivo` es "Estudiantes"
- **Responsable**: Debe ser un usuario existente con rol "maestro" o "administrador"
- **Cupo máximo**: Debe ser un entero positivo mayor a 0
- **Fecha de realización**: No puede ser una fecha en el pasado
- **Horarios**: `hora_fin` debe ser posterior a `hora_inicio` (formato HH:MM)
- **Tipo de evento**: Debe ser uno de los valores válidos: "Conferencia", "Taller", "Seminario", "Curso", "Congreso", "Simposio", "Foro", "Otro"
- **Público objetivo**: Debe ser uno de los valores válidos: "Estudiantes", "Profesores", "Público general"

### Validaciones Generales

- El email debe ser único en el sistema
- Los campos RFC y CURP se convierten automáticamente a mayúsculas
- Los campos de salón y cubículo se convierten automáticamente a mayúsculas

### Códigos de estado HTTP

- **200**: Petición exitosa
- **201**: Recurso creado exitosamente
- **400**: Error en la petición (validación, datos faltantes, etc.)
- **403**: Acceso prohibido (usuario no autenticado o sin permisos)
- **404**: Recurso no encontrado

---

## Despliegue en producción - Google App Engine

1. Generar los archivos estáticos de Django (solo se requiere en el primer deploy):
   ```bash
   $ python3 manage.py collectstatic
   ```

2. Conectarse a la BD de producción mediante un proxy (previamente instalar SDK de Google Cloud):
   ```bash
   $ ./cloud_sql_proxy -instances="PROJECT_ID:REGION:INSTANCE_NAME"=tcp:3307
   ```

3. Configurar en el archivo `my.cnf` la conexión hacia esta BD

4. Aplicar las migraciones del proyecto

5. Configurar en el archivo `settings.py` la conexión a la BD de Google Cloud

6. Ejecutar el comando de publicación:
   ```bash
   $ gcloud app deploy -v {ULTIMA_VERSION_DESPLEGADA}
   ```
