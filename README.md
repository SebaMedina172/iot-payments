# Proyecto IoT Payments - MVP con FastAPI, React/Tailwind y Azure Deployment

## Descripción
Prototipo de terminal de pago IoT que simula transacciones y las procesa en un backend FastAPI, guarda en SQLite y muestra en un dashboard React/Tailwind. Incluye:
- **Backend** en FastAPI con endpoints:
  - `GET /transactions`: lista transacciones.
  - `DELETE /transactions`: borra todas (reinicia BD).
  - `POST /simulate`: simula transacciones vía MQTT (solo en local/con broker).
  - `POST /simulate-direct`: simula transacciones procesándolas directamente (útil para demo en nube).
- **Frontend** en React + Vite + Tailwind:
  - Tabla paginada de transacciones.
  - Botones “Simular”, “Simular-direct” y “Borrar transacciones”.
- **Docker Compose** local:
  - Mosquitto (broker MQTT).
  - Backend contenedorizado.
  - Frontend contenedorizado.
- **Despliegue en Azure** (demo mínimo):
  - Backend en Azure Container Instances usando `simulate-direct`.
  - Frontend en Azure Static Web Apps.
  - Flujo público con URL accesible sin depender de MQTT en la nube.
- **Documentación de pasos, errores y soluciones**: incluye cómo desplegar, incidencias (por ejemplo hardcodeo de `API_URL`), y plan de mejoras.

---

## 🌐 Demo en Vivo

👉 Puedes probar la aplicación funcionando en el siguiente enlace:  
[🔗 Ver Demo](https://calm-glacier-0b826dd0f.6.azurestaticapps.net/)  

---

## Índice
1. [Estructura de carpetas](#estructura-de-carpetas)  
2. [Requisitos previos](#requisitos-previos)  
3. [Ejecución local (MVP Día 1 y Día 2)](#ejecución-local-mvp-día-1-y-día-2)  
   - [Backend local](#backend-local)  
   - [Simulador IoT local](#simulador-iot-local)  
   - [Frontend local](#frontend-local)  
   - [Docker Compose local](#docker-compose-local)  
4. [Endpoints detallados](#endpoints-detallados)  
5. [Configuración de entorno y variables](#configuración-de-entorno-y-variables)  
6. [Despliegue en Azure (demo mínimo)](#despliegue-en-azure-demo-mínimo)  
   - [Preparativos](#preparativos)  
   - [Construir y publicar imagen del backend](#construir-y-publicar-imagen-del-backend)  
   - [Desplegar backend en Azure Container Instances](#desplegar-backend-en-azure-container-instances)  
   - [Desplegar frontend en Azure Static Web Apps](#desplegar-frontend-en-azure-static-web-apps)  
   - [Ajustes de CORS y pruebas](#ajustes-de-cors-y-pruebas)  
   - [Resumen de comandos](#resumen-de-comandos)  
7. [Errores comunes y soluciones / Workarounds](#errores-comunes-y-soluciones--workarounds)  
8. [Próximos pasos y mejoras en producción](#próximos-pasos-y-mejoras-en-producción)  

---

## Estructura de carpetas
``` text
proyecto-iot-payments/
├── backend/
│ ├── main.py
│ ├── mqtt_client.py
│ ├── models.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── venv/ # entorno virtual local (no versionar)
├── front/
│ ├── package.json
│ ├── vite.config.js
│ ├── src/
│ │ ├── App.jsx
│ │ ├── index.css
│ │ └── ...
│ ├── Dockerfile
│ └── .env # para desarrollo local: VITE_API_URL=http://localhost:8000
├── simulator/ # opcional, para pruebas MQTT local
│ ├── simulate.py
│ └── venv/
├── docker-compose.yml # orquesta mosquitto + backend + front (local)
└── README.md # este archivo
```

---

## Requisitos previos
- **Docker** instalado y funcionando.
- **Node.js** (18+) y npm instalados.
- **Python 3.9+** instalado.
- **Git** para versionar.
- **Azure CLI** instalado (`az`) y autenticado (`az login`) si vas a desplegar.
- Cuenta Azure con permisos para crear recursos (Resource Group, Static Web Apps, Container Instances o App Service).
- (Opcional) Cuenta DockerHub si vas a publicar imagen.

---

## **Ejecución local (MVP)**

### **Backend local**
1. Crear y activar entorno virtual:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Verificar que `main.py` incluye lógica de `simulate-direct` y manejo de `USE_SIMULATE_DIRECT` en startup si corresponde.

4. Ejecutar:
  ``` bash
    python main.py
  ```
- Arranca FastAPI en `http://0.0.0.0:8000`.

- Imprime logs de “Base de datos inicializada.” y, si `USE_SIMULATE_DIRECT` no es true, también inicia MQTT subscriber.

4. Probar endpoints:

```bash
  curl http://localhost:8000/transactions
  curl -X DELETE http://localhost:8000/transactions
  curl -X POST "http://localhost:8000/simulate-direct?count=5"
  curl http://localhost:8000/transactions
```

- Si todo funciona, la lista de transacciones se llena y borra correctamente.

---
### **Simulador IoT local**
- En `simulator/simulate.py`, envía mensajes por MQTT:
  ```bash
    cd simulator
    python3 -m venv venv
    source venv/bin/activate
    pip install paho-mqtt
    python simulate.py
    ```
- Útil solo en local con broker Mosquitto. Para demo local completa con MQTT, pero no necesario para demo en nube.

---
### **Frontend Local**

1) Ir a front/:

  ```bash
    cd front
    npm install
  ```

2) Crear .env con:

  ```ini
    VITE_API_URL=http://localhost:8000
  ```

3) Ejecutar:

  ```bash
    npm run dev
    Abre http://localhost:5173.
  ```

4) Verifica UI: botones “Simular”, “Simular-direct”, “Borrar transacciones” funcionan contra backend local.

5) CORS: en backend FastAPI, allowed_origins debe incluir http://localhost:5173.

---

### **Docker Compose local**
En la raíz docker-compose.yml:

```yaml
  version: '3.9'
  services:
    mosquitto:
      image: eclipse-mosquitto:2.0
      container_name: mosquitto
      ports:
        - "1883:1883"

    backend:
      build:
        context: ./backend
      container_name: backend
      environment:
        - MQTT_BROKER=mosquitto
        - MQTT_PORT=1883
        - USE_SIMULATE_DIRECT=false     # en local puedes false para usar MQTT
      depends_on:
        - mosquitto
      ports:
        - "8000:8000"

    front:
      build:
        context: ./front
        args:
          - VITE_API_URL=http://backend:8000
      container_name: front
      ports:
        - "3000:80"
      depends_on:
        - backend
  ```
  
1) Iniciar:
  ```bash
    docker-compose up --build -d  
  ```
2) Backend se conecta a broker Mosquitto; frontend en http://localhost:3000.

3) Ejecutar simulador local o usar botón “Simular” que publica vía MQTT.

4) Probar “Borrar” y “Simular-direct” también en local.

---

### **Endpoints detallados**
- `GET /transactions`

  Lista todas las transacciones en formato JSON:

``` json
  [
    {"id": "...", "amount": 42.5, "status": "approved", "timestamp": "2025-06-15 12:34:56"},
    ...
  ]
```

- `DELETE /transactions`

  Borra todas las transacciones (elimina archivo SQLite y recrea tabla). Retorna { "detail": "Transacciones borradas" }.

- `POST /simulate?count=N&interval_ms=M`

  Publica N transacciones al broker MQTT en background, con intervalo M ms entre cada mensaje. Retorna 202 con { "detail": "Simulación iniciada: N transacciones" }. Requiere broker accesible (en nube no se usa).

- `POST /simulate-direct?count=N`
  Simula N transacciones procesándolas directamente en la lógica process_logic_and_update, sin MQTT. Retorna { "detail": "...", "transactions": [...] }. Útil para demo en nube.

---

### **Configuración de entorno y variables**

- **Backend:**

  - `HOST` (por defecto `0.0.0.0`), `PORT` (por defecto `8000`).

  - `USE_SIMULATE_DIRECT`: `"true"` o `"false"`. En nube usar `"true"` para no iniciar MQTT.

  - `MQTT_BROKER`, `MQTT_PORT`, `MQTT_TOPIC_REQ`: para local si se usa MQTT.

  - `FRONT_URL`: si despliegue frontend en nube, agregar la URL pública para CORS.

- **Frontend:**

`VITE_API_URL`: URL base del backend, e.g. `http://localhost:8000` en desarrollo o `https://<backend-publico>` en Azure Static Web Apps.

- En Dockerfile de front:

  ```dockerfile
    ARG VITE_API_URL
    ENV VITE_API_URL=$VITE_API_URL
  ```

- En `docker-compose.yml` local se pasa `VITE_API_URL=http://backend:8000`.

### **Despliegue en Azure (demo mínimo)**
#### **Preparativos**
1) **Instalar Azure CLI y `az login`.**

2) **Crear Resource Group:**

```bash
az group create --name rg-iot-demo --location eastus
```
3) (Opcional) **Elegir registro de contenedores:**

  - Para rapidez, usar DockerHub público.

  - Si prefieres ACR, crear con:

    ```bash
      az acr create --resource-group rg-iot-demo --name <tuACRunico> --sku Basic
      az acr login --name <tuACRunico>
    ```

#### **Construir y publicar imagen del backend**
- DockerHub:

  ```bash
  cd backend
  docker build -t tuusuario/backend-iot:latest .
  docker push tuusuario/backend-iot:latest
  ```
- ACR:

  ```bash
  cd backend
  docker build -t <tuACRunico>.azurecr.io/backend-iot:latest .
  docker push <tuACRunico>.azurecr.io/backend-iot:latest
  ```
#### **Desplegar backend en Azure Container Instances**
- Usar simulate-direct:

  ```bash
  # Con DockerHub público:
  az container create \
    --resource-group rg-iot-demo \
    --name backend-iot-demo \
    --image tuusuario/backend-iot:latest \
    --cpu 1 --memory 1 \
    --ports 8000 \
    --environment-variables USE_SIMULATE_DIRECT=true,FRONT_URL=https://<tu-front>.azurestaticapps.net \
    --dns-name-label backend-iot-demo-$(date +%s)
  ```
- Si ACR, añadir `--registry-login-server`, `--registry-username`, `--registry-password`.

- Obtener FQDN:

  ```bash
  az container show -g rg-iot-demo -n backend-iot-demo --query "ipAddress.fqdn" -o tsv
  ```
- Probar:

  ```bash
  curl http://<FQDN>:8000/transactions
  curl -X POST "http://<FQDN>:8000/simulate-direct?count=5"
  curl http://<FQDN>:8000/transactions
  ```

#### **Desplegar frontend en Azure Static Web Apps**
1) **Repositorio GitHub**: asegúrate de tener front en repo.

2) **Crear Static Web App:**

    ``` bash
    az staticwebapp create \
      --name front-iot-demo-$(date +%s) \
      --resource-group rg-iot-demo \
      --location eastus \
      --source https://github.com/tuusuario/tu-repo \
      --branch main \
      --login-with-github \
      --app-location "front" \
      --output-location "dist"
    ```

3) **Configurar variable VITE_API_URL:**

    - En Azure Portal > Static Web App > Configuration > Application Settings:

      ``` ini
      VITE_API_URL = "http://<FQDN-backend>:8000"
      ```

    - O en el workflow de GitHub Actions generado, bajo env:.

4) **Ajustar CORS en backend:**

    - En `allowed_origins` de FastAPI añade `"https://<tu-front>.azurestaticapps.net"`.

    - Si cambias CORS, reinicia o redeploy backend en ACI.

5) **Probar UI pública**:

    - Abre `https://<tu-front>.azurestaticapps.net.`

    - Pulsar “Borrar transacciones” y “Simular-direct N”: la tabla debe actualizarse desde el backend en ACI.

---

### Ajustes de CORS y pruebas
- Backend FastAPI:

  ```python
  allowed_origins = [
      "http://localhost:5173",
      "http://localhost:3000",
      "http://front:80",
      "https://<tu-front>.azurestaticapps.net"
  ]
  ```

- Asegura reinicio del contenedor backend para aplicar cambios.

- Verifica en consola del navegador si hay errores de CORS y ajusta orígenes.

---
### Resumen de comandos

``` bash
  # Azure CLI login y group
  az login
  az group create --name rg-iot-demo --location eastus

  # Build y push backend (DockerHub)
  cd backend
  docker build -t tuusuario/backend-iot:latest .
  docker push tuusuario/backend-iot:latest

  # Desplegar backend en ACI
  az container create \
    --resource-group rg-iot-demo \
    --name backend-iot-demo \
    --image tuusuario/backend-iot:latest \
    --cpu 1 --memory 1 \
    --ports 8000 \
    --environment-variables USE_SIMULATE_DIRECT=true,FRONT_URL=https://<tu-front>.azurestaticapps.net \
    --dns-name-label backend-iot-demo-$(date +%s)

  # Obtener FQDN
  FQDN=$(az container show -g rg-iot-demo -n backend-iot-demo --query "ipAddress.fqdn" -o tsv)
  echo "Backend en: http://$FQDN:8000"

  # Probar endpoints
  curl http://$FQDN:8000/transactions
  curl -X POST "http://$FQDN:8000/simulate-direct?count=5"

  # Desplegar frontend en Static Web Apps
  az staticwebapp create \
    --name front-iot-demo-$(date +%s) \
    --resource-group rg-iot-demo \
    --location eastus \
    --source https://github.com/tuusuario/tu-repo \
    --branch main \
    --login-with-github \
    --app-location "front" \
    --output-location "dist"

  # En Static Web Apps config: VITE_API_URL="http://$FQDN:8000"
```

---

### Errores comunes y soluciones / Workarounds
- **Hardcodeo de API_URL**: si no logró leer env var en build de front, a veces Vite no recoge `VITE_API_URL` en GitHub Actions; revisar workflow y settings en Static Web Apps. Documentar el incidente y cómo refactorizar:

  - Verificar que en workflow YAML exista:

  ```yaml
    env:
      VITE_API_URL: "http://<FQDN-backend>:8000"
  ```
  - O ajustar `staticwebapp.config.json` si aplicable.

- **CORS rechazado**: agregar el dominio exacto del front público a `allowed_origins`.

- **ACI no arranca**: revisar logs con `az container logs`; problemas de imagen o variables. Si ACR, verificar credenciales correctas.

- **Nombre DNS en uso**: `--dns-name-label` debe ser único; usar sufijo con timestamp.

- **Timeout en simulate-direct**: si count muy alto, backend puede tardar. Mantener count razonable (<=50).

- **HTTPS en backend**: ACI expone HTTP; para producción usar App Service o proxy con HTTPS. Para demo, documentar la limitación.

- **Variables de entorno en contenedores**: confirmar que backend lee `USE_SIMULATE_DIRECT` correctamente con `.lower()`.

- **Build Vite falla en Actions**: verificar Node version y sintaxis. Probar localmente con `npm run build` antes de commit.

- **Permisos GitHub Actions**: autorizar Static Web Apps en repo.

---

### Próximos pasos y mejoras en producción
- **MQTT real con Azure IoT Hub:** reemplazar simulate-direct por flujo real IoT:

  - Registrar dispositivos en IoT Hub, usar SDK para publicar/subscribir.

  - Procesar eventos con Azure Functions o listener basado en paho-mqtt apuntando a IoT Hub.

- **Base de datos gestionada:** migrar SQLite a Azure Database for MySQL/PostgreSQL.

- **HTTPS y seguridad:** desplegar backend en App Service para HTTPS nativo; usar Managed Identity o Key Vault para secretos.

- **Autenticación/Autorización:** proteger endpoints sensibles (simulate, delete) con JWT o API Key.

- **CI/CD automático:** GitHub Actions que al push a main:

  - Construya y push la imagen a ACR o DockerHub.

  - Despliegue o actualice ACI o App Service.

  - Deploy del frontend en Static Web Apps.

- **Monitorización y logging:** integrar Application Insights para métricas, logs estructurados.

- **Escalabilidad:** si aumenta carga, usar AKS o App Service escalado; para IoT Hub escalar según devices.

- **Testing end-to-end:** tests automatizados que validen flujo completo (mock de MQTT o simulate-direct).

- **Infraestructura como código:** definir Bicep o Terraform para automatizar creación de recursos Azure.

- Mejora UX: gráficas de estadísticas (aprobadas vs rechazadas) en frontend; WebSocket/SSE para actualizaciones en tiempo real.

- Gestión de secretos: usar Azure Key Vault para credenciales en backend.