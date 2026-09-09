# AutoClicker Enterprise

Sistema de automatización de eventos de puntero de alto rendimiento para entornos Windows, diseñado para operaciones continuas en flujos de trabajo multitarea sin degradación de productividad.

Desarrollado por **Yovan Enovore**.

---

## Resumen Ejecutivo

AutoClicker Enterprise resuelve la problemática inherente a los sistemas de automatización de clics estándar: la pérdida del foco de entrada y el bloqueo operativo del usuario. Mediante la integración con las interfaces de bajo nivel de la API de Windows (`user32.dll` a través de `ctypes`), el motor traslada el cursor, despacha el evento de interacción física y restablece instantáneamente el cursor y el foco a la posición original en una ventana de milisegundos.

Esta arquitectura permite que operadores técnicos, desarrolladores y analistas mantengan actividades simultáneas de alta concentración (como escritura en terminales, depuración en entornos de desarrollo o procesamiento de datos) mientras las secuencias automatizadas se ejecutan de manera continua.

---

## Características Principales

### Restauración de Foco y Cursor
El algoritmo de despacho realiza una operación bidireccional mediante llamadas a `SetCursorPos` y `mouse_event`. Tras activar el objetivo designado, el cursor retorna a las coordenadas de trabajo activas, emitiendo un evento de reactivación que preserva el estado del teclado y la ventana activa.

### Interfaz Gráfica Flotante Asíncrona
Panel de administración construido sobre Tkinter configurado con la propiedad de ventana persistente (`-topmost`), asegurando visibilidad sobre interfaces complejas o escritorios con múltiples monitores sin interferir con el área de trabajo activa.

### Mapeo Dinámico de Coordenadas
Sistema de captura de objetivos mediante escucha global de eventos de teclado. Permite calibrar las coordenadas exactas de pantalla posicionando el cursor sobre el elemento deseado y accionando la tecla designada sin necesidad de ingreso manual de parámetros.

### Subflujo de Confirmación Visual
Módulo de retroalimentación gráfica que proyecta una marca temporal transparente sobre el punto de impacto. Proporciona validación visual del evento sin alterar el orden de apilamiento de las ventanas ni interceptar clics secundarios.

### Protocolo de Parada de Emergencia Global
Mecanismo de corte a nivel de sistema operativo mediante interrupción global de hardware (tecla de escape), garantizando la detención inmediata del hilo de automatización con independencia del contexto o ventana activa.

---

## Arquitectura del Proyecto

El repositorio se estructura en módulos desacoplados orientados a distintos escenarios de operación:

| Archivo | Rol del Componente | Descripción Técnica |
| :--- | :--- | :--- |
| `interfaz.py` | Núcleo de Aplicación Gráfica | Implementa la clase principal `AutoClickerApp`, la gestión del hilo de trabajo en segundo plano, la captura de atajos globales y el despacho de eventos Win32. |
| `main.py` | Motor de Ejecución en Línea de Comandos | Módulo de terminal para ejecuciones directas con parámetros estáticos de posición e intervalo temporal. |
| `coordenadas.py` | Herramienta de Inspección de Coordenadas | Utilidad de terminal para lectura y reporte en tiempo real de las posiciones X/Y del cursor en pantalla. |

---

## Especificaciones Técnicas

| Componente | Especificación |
| :--- | :--- |
| Lenguaje | Python 3.8 o superior |
| Plataforma | Microsoft Windows 10 / Windows 11 / Windows Server |
| Subsistema Gráfico | Tkinter |
| Integración de Hardware | Win32 API (`ctypes.windll.user32`) |
| Controladores de Entrada | `pyautogui`, `keyboard` |
| Modelo de Concurrencia | Subprocesamiento mediante `threading.Thread` en modo demonio |

---

## Instalación y Configuración

### Prerrequisitos de Sistema

El software requiere privilegios adecuados en Windows para registrar interceptores globales de teclado y despachar eventos de puntero mediante `user32.dll`.

### Despliegue del Entorno

```bash
git clone https://github.com/ynvYauneEnovore/AutoClicker.git
cd AutoClicker
python -m venv venv
venv\Scripts\activate
pip install pyautogui keyboard
```

---

## Guía de Operación

### Modalidad Interfaz Gráfica

Para iniciar el entorno interactivo:

```bash
python interfaz.py
```

Flujo operativo estándar:

1. **Inicialización**: La ventana de control se posiciona en primer plano permanente.
2. **Calibración de Posición**: Presione el botón de captura o sitúe el puntero sobre el objetivo y accione la tecla `C`. Las coordenadas quedarán registradas en el panel.
3. **Inicio de Secuencia**: Presione el botón de ejecución para iniciar el hilo de automatización periódica.
4. **Interrupción de Operación**: Accione la tecla `ESC` en cualquier momento para abortar la secuencia de manera inmediata.

### Modalidad Inspección de Coordenadas

Para auditoría manual y visualización continua de vectores de pantalla:

```bash
python coordenadas.py
```

### Modalidad Línea de Comandos Directa

Para ejecuciones directas o integración en scripts batch:

```bash
python main.py
```

---

## Parámetros de Configuración

En `interfaz.py`, las siguientes variables determinan el comportamiento del ciclo operativo:

| Parámetro | Tipo | Valor Predeterminado | Función |
| :--- | :--- | :--- | :--- |
| `pausa` | Entero / Flotante | `10` | Intervalo de reposo en segundos entre cada ciclo de ejecución. |
| `geometry` | Cadena | `"350x200"` | Dimensiones iniciales de la ventana del panel de control. |
| `attributes("-topmost", True)` | Booleano | `True` | Bloqueo de posición en primer plano persistente. |
| `after(300, ...)` | Milisegundos | `300` | Latencia de persistencia de la marca visual sobre pantalla. |

---

## Consideraciones de Seguridad y Entorno

- **Escalado de Pantalla (DPI)**: En configuraciones con múltiples monitores o escalado DPI superior al 100%, se recomienda ejecutar con compatibilidad DPI consistente para asegurar la correspondencia exacta de píxeles.
- **Ventanas Elevadas**: Si la aplicación destino se ejecuta bajo privilegios de Administrador (UAC elevado), el script debe iniciarse con permisos administrativos equivalentes para que Windows permita la inyección de eventos.

---

## Licencia

Este proyecto se distribuye bajo los términos de la Licencia MIT.