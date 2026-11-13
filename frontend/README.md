# INTINAUTA | UAV-DOCK OPERATIONS

Frontend del **Módulo 4 — Dashboard / HMI** de UAV-Dock V1. Es una aplicación
local de escritorio, supervisora y de solo lectura. El modo permanente
`SIMULATION MODE` usa datos deterministas y no envía comandos a hardware.

## Tecnologías y arquitectura

- Python 3.11+, PySide6/Qt Widgets y QSS.
- pyqtgraph está preparado como dependencia para la gráfica real del siguiente
  incremento; la V1 usa un histórico compacto de puntos para mantener la
  instalación ligera.
- `models` contiene dataclasses con unidades explícitas y timestamps con zona.
- `contracts` define `IDataProvider`; `services` implementa el proveedor simulado.
- `viewmodels` conecta el proveedor con señales Qt y un `QTimer`.
- `views` y `components` contienen pantallas y controles reutilizables.

Flujo: `MockDataProvider -> DashboardViewModel -> MainWindow/pages/components`.
Un proveedor real puede reemplazar al mock sin que las vistas conozcan su origen.

## Instalación y ejecución en Windows

```powershell
cd frontend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Pruebas:

```powershell
python -m pytest
```

Para empaquetar cuando la ejecución esté validada:

```powershell
python -m pip install pyinstaller
pyinstaller --noconsole --name UAVDockDashboard main.py
```

## Alcance y limitaciones

Incluye overview, telemetría, misiones, estado Dock, alertas filtrables e
histórico demostrativo. No incluye MAVLink, ROS 2, control de vuelo, actuadores,
intercambio físico, base de datos ni persistencia real. Los registros de
History son deliberadamente de demostración y no deben interpretarse como
evidencia operacional.
