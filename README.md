<p align="center">
  <img src="https://raw.githubusercontent.com/FrefLabs/NTI-client/master/src/img/NTI-LOGO-FINAL.svg" width="280" alt="N.T.I. Logo">
</p>
<h2 align="center">NTI-node</h2>
<p align="center">Nodo de cómputo distribuido - NeuroFref Trading Intelligence</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python">
  <img src="https://img.shields.io/badge/WebSocket-Client-7B1FA2?style=flat-square">
  <img src="https://img.shields.io/badge/Estado-Finalizado-2e7d32?style=flat-square">
</p>

---

## El sistema N.T.I. (NeuroFref Trading Intelligence) es una plataforma que entrena redes neuronales para predecir el precio de cierre de acciones del mercado bursátil. El sistema completo tiene cinco componentes:

- **NTI-client** - interfaz de escritorio para el usuario
- **NTI-server** - servidor REST central que coordina todo
- **NTI-gateway** - gateway Python que ejecuta los scripts de datos financieros
- **NTI-train** - proceso de entrenamiento distribuido que corre en dispositivos disponibles
- **NTI-node** (este repo) - nodos de cómputo que se conectan al gateway vía WebSocket para ejecutar scripts de datos

> [!IMPORTANT]
> Para una explicación completa de la arquitectura distribuida, el flujo de entrenamiento y la red neuronal, ver el [README de la organización](https://github.com/FrefLabs).

---

## NTI-node

Es un proceso ligero que se conecta al gateway vía WebSocket, se registra como Nodo de cómputo, y ejecuta scripts Python en demanda. Cada instancia genera un ID único basado en hostname + timestamp. Múltiples Nodos pueden conectarse al mismo gateway para distribuir la carga de trabajo.

Cuando el gateway recibe una petición de ejecución de script desde NTI-server, puede delegarla a un Nodo conectado. El Nodo ejecuta el script en un entorno virtual aislado, captura la salida y envía el resultado de vuelta al gateway.

---

## Flujo de ejecución

```
NTI-gateway ──WebSocket──▶ NTI-node
         │
         │ 1. Registro (node_id)
         │ 2. Heartbeat (ping/pong)
         │ 3. Ejecutar script
         │    ├── Recibir código + args
         │    ├── Ejecutar en venv aislado
         │    ├── Capturar stdout
         │    └── Enviar resultado
         │
         └──────────────────────────────
```

---

## Entorno virtual de scripts

Al primer arranque, el Nodo crea automáticamente un entorno virtual (`scripts_venv/`) e instala las dependencias necesarias (`yfinance`, `pandas`, `numpy`). Los scripts se ejecutan dentro de este venv para evitar conflictos con el Python del sistema.

---

## Protocolo WebSocket

### Registro
```json
{
  "type": "register",
  "node_id": "DESKTOP-ABC_1732564892345",
  "hostname": "DESKTOP-ABC",
  "capabilities": ["python3"]
}
```

### Ejecución de tarea (desde gateway)
```json
{
  "type": "execute",
  "task_id": "uuid",
  "script_name": "generate_stock_data_table.py",
  "script_code": "...",
  "args": ["AAPL"],
  "timeout": 120
}
```

### Resultado (hacia gateway)
```json
{
  "type": "result",
  "task_id": "uuid",
  "success": true,
  "output": "...",
  "exit_code": 0
}
```

### Heartbeat

El gateway envía pings periódicos. El Nodo responde con `pong` y su cantidad de tareas activas. Si no responde dentro del timeout, el gateway lo marca como inactivo.

---

## Configuración

`config.yaml`:
```yaml
gateway:
  url: "ws://localhost:8000/ws/node"
  reconnect_interval: 5
  max_reconnect_attempts: 0  # 0 = infinito

execution:
  timeout: 120

node:
  hostname: null  # Auto-detectar si es null
```

---

## Instalación y ejecución

**Requisitos:** Python 3.9+

### Linux/macOS
```bash
pip install -r requirements.txt
python main.py
```

### Windows
Doble clic en `start.bat` (verifica Python, instala dependencias y ejecuta automáticamente).

Para instrucciones detalladas en Windows, ver [INSTRUCCIONES_WINDOWS.md](INSTRUCCIONES_WINDOWS.md).

**Dependencias:**
```
websockets==12.0
pyyaml==6.0.1
```

---

## Estructura del proyecto

```
NTI-node/
├── main.py                 # Entrada principal, conexión al gateway
├── config.yaml             # Configuración del nodo
├── requirements.txt
├── start.bat               # Script de inicio para Windows
├── INSTRUCCIONES_WINDOWS.md   # Guía detallada para Windows
├── node/
│   ├── __init__.py
│   ├── connection.py       # Conexión WebSocket con reconexión automática
│   └── executor.py         # Ejecutor de scripts en venv aislado
└── temp/                   # Archivos temporales de ejecución
```

---

## Equipo - Fref Labs

Desarrollado por Federico Battistello, Luca Guarna, Nicolás Pereira, Franco Perfetti y Juan Sirota
