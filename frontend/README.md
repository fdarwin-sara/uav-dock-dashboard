# INTINAUTA | UAV-DOCK OPERATIONS

Frontend del **Módulo 4 — Dashboard / HMI** de UAV-Dock V1, versión 0.3.0. Es una aplicación
local de escritorio, supervisora y de solo lectura. El modo permanente
`SIMULATION MODE` usa datos deterministas y no envía comandos a hardware.

## Tecnologías y arquitectura

- Python 3.11+, PySide6/Qt Widgets y QSS.
- pyqtgraph se utiliza para tendencias fluidas de altitud y voltaje.
- `models` contiene dataclasses con unidades explícitas y timestamps con zona.
- `contracts` define `IDataProvider`; `services` implementa el proveedor simulado.
- `viewmodels` conecta el proveedor con señales Qt y un `QTimer`.
- `views` y `components` contienen pantallas y controles reutilizables.

La versión 0.2.0 añadió navegación exclusiva con `QButtonGroup`, una pantalla de
misiones con línea temporal, una vista ampliada del Dock, tarjetas y gráficos
separados para telemetría y tablas redimensionables para alertas e histórico.
La versión 0.3.0 aplica una identidad visual space-tech, mayor contraste,
estados de misión diferenciados, chips de estado y una presentación más clara
para telemetría, eventos, alertas e histórico sin cambiar la arquitectura.

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
histórico demostrativo. Las lecturas y eventos siguen siendo simulados. No incluye MAVLink, ROS 2, control de vuelo, actuadores,
intercambio físico, base de datos ni persistencia real. Los registros de
History son deliberadamente de demostración y no deben interpretarse como
evidencia operacional.
