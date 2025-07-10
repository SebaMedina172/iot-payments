# Proyecto IoT Payments - Plataforma de Pagos IoT con Azure

## Descripción
Plataforma completa de terminal de pago IoT que procesa transacciones reales a través de Azure IoT Hub, con backend en FastAPI desplegado en Azure App Service con HTTPS nativo, base de datos MySQL gestionada en Azure, y frontend React/Tailwind en Azure Static Web Apps.

### Características principales:
- **Backend** en FastAPI con endpoints seguros (HTTPS):
  - `GET /transactions`: lista transacciones paginadas.
  - `DELETE /transactions`: borra todas las transacciones (protegido).
  - `POST /simulate`: simula transacciones vía Azure IoT Hub.
  - `POST /simulate-direct`: simula transacciones directamente (para testing).
- **Frontend** en React + Vite + Tailwind:
  - Dashboard con tabla paginada de transacciones.
  - Gráficas de estadísticas (aprobadas vs rechazadas).
  - Botones para simulación y gestión de transacciones.
- **MQTT Real** con Azure IoT Hub:
  - Dispositivos IoT registrados y autenticados.
  - Procesamiento de eventos en tiempo real.
- **Base de datos** Azure Database for MySQL:
  - Almacenamiento persistente y escalable.
  - Respaldos automáticos y alta disponibilidad.
- **Despliegue completo en Azure**:
  - Backend en Azure App Service con HTTPS nativo.
  - Frontend en Azure Static Web Apps.
  - Base de datos MySQL gestionada.
  - Azure IoT Hub para comunicación MQTT.

---

## 🌐 Demo en Vivo

👉 Puedes probar la aplicación funcionando en el siguiente enlace:  
[🔗 Ver Demo](https://calm-glacier-0b826dd0f.6.azurestaticapps.net/)  

**Credenciales de demo**: (si aplica autenticación)

---

## Índice
1. [Arquitectura del sistema](#arquitectura-del-sistema)
2. [Estructura de carpetas](#estructura-de-carpetas)  
3. [Requisitos previos](#requisitos-previos)  
4. [Configuración de Azure Services](#configuración-de-azure-services)
5. [Ejecución local](#ejecución-local)  
6. [Endpoints detallados](#endpoints-detallados)  
7. [Despliegue en Azure](#despliegue-en-azure)  
8. [Configuración de variables de entorno](#configuración-de-variables-de-entorno)
9. [Monitorización y logging](#monitorización-y-logging)
10. [Errores comunes y soluciones](#errores-comunes-y-soluciones)  
11. [Próximos pasos](#próximos-pasos)  

---

## Arquitectura del sistema

```
┌─────────────────┐    HTTPS    ┌──────────────────┐
│                 │◄────────────►│                  │
│  React Frontend │             │  FastAPI Backend │
│  (Static Web    │             │  (App Service)   │
│   Apps)         │             │                  │
└─────────────────┘             └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │                  │
                                │ Azure Database   │
                                │ for MySQL        │
                                │                  │
                                └──────────────────┘
                                          ▲
                                          │
┌─────────────────┐    MQTT     ┌──────────────────┐
│                 │◄────────────►│                  │
│ Dispositivos    │             │  Azure IoT Hub   │
│ IoT             │             │                  │
│                 │             │                  │
└─────────────────┘             └──────────────────┘
```

---

## Estructura de carpetas
```text
proyecto-iot-payments/
├── backend/
│   ├── main.py
│   ├── iot_hub_client.py          # Cliente Azure IoT Hub
│   ├── database.py                # Conexión MySQL
│   ├── models.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TransactionTable.jsx
│   │   │   └── StatsChart.jsx
│   │   ├── index.css
│   │   └── ...
│   ├── Dockerfile
│   └── .env
├── iot-devices/                   # Simuladores de dispositivos IoT
│   ├── device_simulator.py
│   └── requirements.txt
├── infrastructure/                # IaC con Bicep/Terraform
│   ├── main.bicep
│   └── parameters.json
├── .github/workflows/             # CI/CD
│   ├── deploy-backend.yml
│   └── deploy-frontend.yml
└── README.md
```

---

## Requisitos previos
- **Azure CLI** instalado y autenticado (`az login`)
- **Node.js** (18+) y npm instalados
- **Python 3.9+** instalado  
- **Git** para control de versiones
- **Docker** (opcional, para desarrollo local)
- Cuenta Azure con permisos para crear recursos
- Suscripción Azure activa

---

## Configuración de Azure Services

### 1. Crear Resource Group
```bash
az group create --name rg-iot-payments --location eastus
```

### 2. Azure IoT Hub
```bash
# Crear IoT Hub
az iot hub create \
  --name iot-payments-hub \
  --resource-group rg-iot-payments \
  --sku S1 \
  --location eastus

# Obtener connection string
az iot hub connection-string show \
  --name iot-payments-hub \
  --resource-group rg-iot-payments
```

### 3. Azure Database for MySQL
```bash
# Crear servidor MySQL
az mysql flexible-server create \
  --name mysql-iot-payments \
  --resource-group rg-iot-payments \
  --location eastus \
  --admin-user adminuser \
  --admin-password 'TuPassword123!' \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 20 \
  --version 8.0.21

# Crear base de datos
az mysql flexible-server db create \
  --resource-group rg-iot-payments \
  --server-name mysql-iot-payments \
  --database-name iot_payments
```

### 4. Azure App Service
```bash
# Crear App Service Plan
az appservice plan create \
  --name asp-iot-payments \
  --resource-group rg-iot-payments \
  --sku B1 \
  --is-linux

# Crear Web App
az webapp create \
  --name app-iot-payments-backend \
  --resource-group rg-iot-payments \
  --plan asp-iot-payments \
  --runtime "PYTHON:3.9"
```

---

## Ejecución local

### Backend local
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar variables de entorno
export AZURE_IOT_HUB_CONNECTION_STRING="tu_connection_string"
export MYSQL_HOST="tu_mysql_host"
export MYSQL_USER="adminuser"
export MYSQL_PASSWORD="TuPassword123!"
export MYSQL_DATABASE="iot_payments"

# Ejecutar
python main.py
```

### Frontend local
```bash
cd frontend
npm install

# Crear .env
echo "VITE_API_URL=http://localhost:8000" > .env

# Ejecutar
npm run dev
```

### Simulador de dispositivos IoT
```bash
cd iot-devices
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar connection string del dispositivo
export DEVICE_CONNECTION_STRING="tu_device_connection_string"

# Ejecutar simulador
python device_simulator.py
```

---

## Endpoints detallados

### Públicos
- `GET /transactions` - Lista transacciones paginadas
- `GET /transactions/{id}` - Obtiene transacción específica
- `GET /health` - Health check del servicio

### Protegidos (requieren autenticación)
- `POST /simulate` - Simula transacciones vía IoT Hub
- `POST /simulate-direct` - Simula transacciones directamente
- `DELETE /transactions` - Borra todas las transacciones
- `GET /stats` - Estadísticas de transacciones

### Respuestas de ejemplo
```json
// GET /transactions
{
  "transactions": [
    {
      "id": "uuid-here",
      "device_id": "device-001", 
      "amount": 42.50,
      "status": "approved",
      "timestamp": "2025-07-10T12:34:56Z",
      "location": "Terminal 1"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20
}

// GET /stats
{
  "total_transactions": 150,
  "approved": 120,
  "rejected": 30,
  "total_amount": 5420.50,
  "avg_amount": 36.14
}
```

---

## Despliegue en Azure

### 1. Backend en App Service

#### Configurar variables de entorno
```bash
az webapp config appsettings set \
  --name app-iot-payments-backend \
  --resource-group rg-iot-payments \
  --settings \
    AZURE_IOT_HUB_CONNECTION_STRING="tu_connection_string" \
    MYSQL_HOST="mysql-iot-payments.mysql.database.azure.com" \
    MYSQL_USER="adminuser" \
    MYSQL_PASSWORD="TuPassword123!" \
    MYSQL_DATABASE="iot_payments" \
    FRONTEND_URL="https://tu-frontend.azurestaticapps.net"
```

#### Desplegar código
```bash
# Opción 1: Desde repositorio Git
az webapp deployment source config \
  --name app-iot-payments-backend \
  --resource-group rg-iot-payments \
  --repo-url https://github.com/tu-usuario/tu-repo \
  --branch main \
  --manual-integration

# Opción 2: ZIP deploy
cd backend
zip -r backend.zip .
az webapp deployment source config-zip \
  --name app-iot-payments-backend \
  --resource-group rg-iot-payments \
  --src backend.zip
```

### 2. Frontend en Static Web Apps

```bash
az staticwebapp create \
  --name frontend-iot-payments \
  --resource-group rg-iot-payments \
  --source https://github.com/tu-usuario/tu-repo \
  --branch main \
  --app-location "frontend" \
  --output-location "dist" \
  --login-with-github
```

#### Configurar variables de entorno del frontend
En Azure Portal → Static Web Apps → Configuration:
```
VITE_API_URL = "https://app-iot-payments-backend.azurewebsites.net"
```

---

## Configuración de variables de entorno

### Backend (App Service)
```bash
# Requeridas
AZURE_IOT_HUB_CONNECTION_STRING="HostName=..."
MYSQL_HOST="mysql-iot-payments.mysql.database.azure.com"
MYSQL_USER="adminuser"
MYSQL_PASSWORD="TuPassword123!"
MYSQL_DATABASE="iot_payments"

# Opcionales
FRONTEND_URL="https://tu-frontend.azurestaticapps.net"
LOG_LEVEL="INFO"
MAX_CONNECTIONS=10
```

### Frontend (Static Web Apps)
```bash
VITE_API_URL="https://app-iot-payments-backend.azurewebsites.net"
```

### Dispositivos IoT
```bash
DEVICE_CONNECTION_STRING="HostName=...;DeviceId=...;SharedAccessKey=..."
IOT_HUB_NAME="iot-payments-hub"
```

---

## Monitorización y logging

### Application Insights
```bash
# Habilitar en App Service
az webapp config appsettings set \
  --name app-iot-payments-backend \
  --resource-group rg-iot-payments \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="tu_instrumentation_key"
```

### Logs estructurados
El backend utiliza logging estructurado con:
- Nivel INFO para operaciones normales
- Nivel ERROR para errores de sistema
- Nivel DEBUG para troubleshooting

### Métricas disponibles
- Número de transacciones por minuto
- Tasa de aprobación/rechazo
- Latencia de procesamiento
- Conexiones activas a IoT Hub
- Queries de base de datos

---

## Errores comunes y soluciones

### 1. Error de conexión a MySQL
**Síntoma**: `Can't connect to MySQL server`
**Solución**: 
- Verificar firewall rules en Azure Database
- Confirmar connection string
- Revisar credenciales

```bash
# Agregar IP al firewall
az mysql flexible-server firewall-rule create \
  --resource-group rg-iot-payments \
  --name mysql-iot-payments \
  --rule-name AllowMyIP \
  --start-ip-address TU_IP \
  --end-ip-address TU_IP
```

### 2. Error CORS en frontend
**Síntoma**: `Access to fetch blocked by CORS policy`
**Solución**: Verificar `FRONTEND_URL` en configuración del backend

### 3. Dispositivos IoT no conectan
**Síntoma**: `Authentication failed`
**Solución**: 
- Verificar device connection string
- Confirmar que el dispositivo está registrado en IoT Hub
- Revisar policies de acceso

### 4. App Service no inicia
**Síntoma**: `Application Error`
**Solución**: 
- Revisar logs en Portal Azure
- Verificar variables de entorno
- Comprobar requirements.txt

---

## Próximos pasos

### Mejoras de seguridad
- [ ] Implementar autenticación JWT
- [ ] Usar Azure Key Vault para secretos
- [ ] Habilitar Managed Identity
- [ ] Configurar Azure AD B2C para usuarios

### Escalabilidad
- [ ] Migrar a Azure Kubernetes Service (AKS)
- [ ] Implementar Azure Redis Cache
- [ ] Configurar auto-scaling
- [ ] Optimizar queries de base de datos

### Funcionalidades
- [ ] Notificaciones push con Azure Notification Hubs
- [ ] Reportes avanzados con Power BI
- [ ] Machine Learning para detección de fraude
- [ ] APIs GraphQL

### DevOps
- [ ] Tests automatizados end-to-end
- [ ] Deployment slots para zero-downtime
- [ ] Infrastructure as Code con Bicep
- [ ] Monitoring con Azure Monitor

### Compliance
- [ ] Cumplimiento PCI DSS
- [ ] Auditoría de transacciones
- [ ] Backup y recovery automatizado
- [ ] Cifrado end-to-end

---

## Contribución

1. Fork del proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a branch (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

---

## Contacto

- **Desarrollador**: Tu Nombre
- **Email**: tu-email@example.com
- **LinkedIn**: [Tu perfil](https://linkedin.com/in/tu-perfil)
- **GitHub**: [Tu repositorio](https://github.com/tu-usuario/proyecto-iot-payments)

---

## Changelog

### v2.0.0 (2025-06-20)
- ✅ Migración a Azure IoT Hub para MQTT real
- ✅ Base de datos MySQL en Azure
- ✅ Backend en App Service con HTTPS
- ✅ Monitorización con Application Insights
- ✅ CI/CD con GitHub Actions

### v1.0.0 (2025-06-15)
- ✅ MVP con SQLite local
- ✅ MQTT simulado con Mosquitto
- ✅ Despliegue básico en Azure Container Instances