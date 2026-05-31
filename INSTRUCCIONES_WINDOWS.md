# Instrucciones para ejecutar NTI Node en Windows

## Opción 1: Usando el script start.bat (Recomendado)

1. **Instalar Python 3.9 o superior**
   - Descargar desde: https://www.python.org/downloads/
   - **IMPORTANTE**: Marcar "Add Python to PATH" durante la instalación

2. **Copiar la carpeta NTI-node** a la computadora donde quieres ejecutar el Node

3. **Editar config.yaml**
   - Abrir `config.yaml` con Notepad
   - Cambiar la URL del Gateway:
     ```yaml
     gateway:
       url: "ws://TU-SERVIDOR-GATEWAY:8000/ws/node"
     ```
   - Ejemplo: `url: "ws://192.168.1.100:8000/ws/node"`
   - Guardar y cerrar

4. **Ejecutar start.bat**
   - Doble clic en `start.bat`
   - El script automáticamente:
     - Verifica Python
     - Instala dependencias
     - Crea config.yaml si no existe
     - Inicia el Node

5. **Verificar conexión**
   - Deberías ver en la consola:
     ```
     [INFO]: Starting NTI Node...
     [INFO]: Python check passed: Python 3.x.x
     [INFO]: Node ID: NOMBRE-PC_1732564892345
     [INFO]: Connecting to Gateway...
     [INFO]: Connected to Gateway
     [INFO]: Registered as NOMBRE-PC_1732564892345
     ```

## Opción 2: Manual (Línea de comandos)

1. **Abrir PowerShell o CMD** en la carpeta NTI-node

2. **Instalar dependencias**
   ```cmd
   python -m pip install -r requirements.txt
   ```

3. **Editar config.yaml** (ver paso 3 de Opción 1)

4. **Ejecutar el Node**
   ```cmd
   python main.py
   ```

## Solución de Problemas

### "Python no está instalado o no está en PATH"

**Solución:**
1. Instalar Python desde https://www.python.org/downloads/
2. Durante instalación, marcar "Add Python to PATH"
3. Reiniciar la computadora
4. Intentar nuevamente

### "No se puede conectar al Gateway"

**Verificar:**
1. URL del Gateway en config.yaml es correcta
2. Gateway está ejecutándose
3. Firewall permite conexión al puerto 8000
4. Puedes hacer ping al servidor del Gateway

**Probar conexión:**
```cmd
curl http://TU-GATEWAY:8000/health
```

### "ModuleNotFoundError"

**Solución:**
```cmd
python -m pip install -r requirements.txt
```

### El Node se desconecta constantemente

**Verificar:**
1. Conexión de red estable
2. Gateway está ejecutándose
3. Revisar logs del Gateway para errores

## Ejecutar como Servicio (Opcional)

Para que el Node se ejecute automáticamente al iniciar Windows:

1. **Crear tarea programada**
   - Abrir "Programador de tareas" (Task Scheduler)
   - Crear tarea básica
   - Nombre: "NTI Node"
   - Disparador: Al iniciar el sistema
   - Acción: Iniciar programa
   - Programa: `C:\ruta\a\NTI-node\start.bat`
   - Marcar "Ejecutar con los privilegios más altos"

## Detener el Node

- Presionar `Ctrl+C` en la ventana de consola
- O cerrar la ventana de consola

## Logs

Los logs se muestran en la consola. Para guardarlos en archivo:

```cmd
python main.py > node.log 2>&1
```

## Actualizar el Node

1. Detener el Node (Ctrl+C)
2. Reemplazar archivos de NTI-node con nueva versión
3. Ejecutar `start.bat` nuevamente

## Múltiples Nodes en la misma computadora

Para ejecutar múltiples Nodes en la misma PC:

1. Copiar carpeta NTI-node a diferentes ubicaciones
2. Cada uno tendrá su propio Node ID automáticamente
3. Ejecutar start.bat en cada carpeta

Cada Node se registrará con ID único: `NOMBRE-PC_{timestamp}`
