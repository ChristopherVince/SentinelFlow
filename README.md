# 🌊 SentinelFlow: Sistema de Alerta Temprana de Inundaciones con Edge AI

Un prototipo de hackathon diseñado para monitorear cuerpos de agua en tiempo real y emitir alertas tempranas de desbordamiento utilizando visión por computadora y procesamiento en el borde (Edge Computing). 

Este proyecto aprovecha la potencia de la arquitectura **AARCH64** y la Unidad de Procesamiento Neuronal (NPU) de **Qualcomm**.

---

## La Solución
SentinelFlow actúa como un vigía digital ininterrumpido. A través de una cámara conectada a un cerebro embebido, el sistema "observa" el nivel del río y clasifica el estado del entorno en dos categorías críticas: `RIO_NORMAL` y `RIO_PELIGRO`. 

Al detectar una anomalía visual (ej. agua turbia subiendo rápidamente o deslaves), el sistema detona una alerta local (indicadores visuales) y prepara el paquete de datos (JSON) para escalarlo a las autoridades correspondientes.

## Tecnologías y Hardware Utilizado
* **Cerebro Principal:** Arduino UNO Q (Chip Qualcomm QRB2210).
* **Visión:** Cámara web Logitech Brio (vía USB) controlada mediante entorno Linux.
* **Sensores de Respaldo:** Familia Modulino (I2C/Qwiic).
* **Inteligencia Artificial:** Edge Impulse (TinyML).
* **Lenguaje:** Python 3 (OpenCV Headless).

---

## Desarrollo del Modelo de Inteligencia Artificial
Nuestra prioridad fue crear un modelo ligero, rápido y preciso que pudiera correr sin internet directamente en los aceleradores de Qualcomm.

1. **Recolección de Datos:** Construimos un dataset balanceado con más de 160 imágenes de alta calidad, controlando el *background bias* para asegurar que la IA se enfocara en el comportamiento del agua y no en el entorno.
2. **Entrenamiento:** Utilizamos un modelo de clasificación de imágenes (Transfer Learning).
3. **Resultados de Validación:** Logramos una precisión sobresaliente del **85%** en el entorno de validación (`int8` Quantized), con un F1 Score de 0.85, haciéndolo altamente confiable para evitar falsas alarmas.


<img width="723" height="367" alt="edgeimpulse" src="https://github.com/user-attachments/assets/a2080504-7e40-41f7-994d-0b6c3a6d8a2f" />


---

## Arquitectura del Software (Pipeline)
El script principal (`main.py`) opera bajo la siguiente lógica:
1. **Inicialización:** Carga el binario optimizado para Linux AARCH64 (`modelo.eim`).
2. **Captura:** Extrae *frames* en vivo desde la cámara Brio usando OpenCV en su versión Headless (para compatibilidad en contenedores de la nube).
3. **Inferencia:** El `ImageImpulseRunner` procesa la imagen y devuelve el nivel de confianza.
4. **Alerta:** Si la clase `RIO_PELIGRO` supera el 80% de confianza, se detonan los protocolos de seguridad.

---

## Estado Actual y Limitaciones Técnicas (Hackathon)
La arquitectura teórica, la recolección de datos y el modelo predictivo en la nube fueron completados con éxito. 

Durante la fase final de *Deployment* (despliegue) en el hardware físico, encontramos una restricción de compatibilidad en el entorno virtualizado del **Arduino App Lab**. El sistema de seguridad del contenedor Linux bloqueó la asignación de permisos de ejecución (`chmod +x` / `Exec format error`) para el binario nativo compilado de Edge Impulse.

**Nota para la demostración:** Para efectos de la validación del MVP y la grabación del video pitch ante los jueces, la lógica de disparadores y el envío de datos han sido probados utilizando un entorno simulado (*hardcoded triggers*), mientras que el modelo de IA original permanece 100% funcional en su entorno de validación en la nube.

---
*Desarrollado con ☕ y pasión durante el Hackathon 2026.*
