import cv2
import math
import os
import sys

# Verificar OpenCV
try:
    print(f"OpenCV version: {cv2.__version__}")
    # Test básico de funciones
    test_cap = cv2.VideoCapture
    test_tracker = cv2.legacy.TrackerCSRT_create
    print("OpenCV funciona correctamente")
except AttributeError as e:
    print(f"Error con OpenCV: {e}")
    print("Reinstala con: pip uninstall opencv-python opencv-contrib-python -y && pip install opencv-contrib-python")
    sys.exit(1)

# Variables globales
puntos_referencia = []
puntos_zona_A = []
frame_original = None
fps = 30

# Bandera global para controlar la cancelación
cancelar_analisis = False

def seleccionar_puntos_referencia(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(puntos_referencia) < 2:
        puntos_referencia.append((x, y))
        cv2.circle(frame_original, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Selecciona referencia", frame_original)

def seleccionar_zona_A(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(puntos_zona_A) < 2:
        puntos_zona_A.append((x, y))
        cv2.circle(frame_original, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Selecciona zona A", frame_original)

def crear_tracker():
    """Crea tracker compatible"""
    try:
        return cv2.legacy.TrackerCSRT_create()
    except AttributeError:
        try:
            return cv2.legacy.TrackerKCF_create()
        except:
            print("ERROR: No se pudo crear ningún tracker")
            sys.exit(1)

def verificar_cancelacion():
    """Verifica si se ha presionado una tecla para cancelar"""
    global cancelar_analisis
    
    # Esperar 1 ms por una tecla
    key = cv2.waitKey(1) & 0xFF
    
    if key == 27:  # Tecla ESC
        return True
    elif key == ord('c'):  # Tecla 'c' para cancelar
        return True
    elif key == ord('q'):  # Tecla 'q' para salir
        return True
    return False

def solicitar_confirmacion_cancelacion(frame):
    """Solicita confirmación para cancelar el análisis"""
    cv2.putText(frame, "Cancelar analisis? (s/n)", (10, 250), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Seguimiento", frame)
    
    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == ord('s'):
            return True
        elif key == ord('n'):
            return False

# Cargar video - DEFINIR video_name AL PRINCIPIO
video_path = input("Introduce la ruta del video: ").replace("\\", "/").strip('"').strip("'")
video_name = os.path.splitext(os.path.basename(video_path))[0]  # MOVER ESTA LÍNEA AQUÍ
print(f"Intentando abrir: {video_path}")
print(f"Nombre del video: {video_name}")
print("\nInstrucciones de cancelacion:")
print("- Presiona 'c' durante el analisis para cancelar")
print("- Presiona ESC en cualquier momento para cancelar")
print("- Presiona 'q' para salir durante el seguimiento")

# Verificar si el archivo existe
if not os.path.exists(video_path):
    print(f"ERROR: El archivo {video_path} no existe")
    sys.exit(1)

try:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("No se pudo abrir el video.")
        sys.exit(1)
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {total_frames}")
    
    ret, frame_original = cap.read()
    if not ret:
        print("No se pudo leer el primer frame.")
        cap.release()
        sys.exit(1)
        
except Exception as e:
    print(f"Error al cargar el video: {e}")
    sys.exit(1)

# Selección de color para ruta
print("Selecciona el color para el recorrido:")
print("1. Azul")
print("2. Rojo")
print("3. Verde")
print("4. Rosa")
color_opciones = {1: (255, 0, 0), 2: (0, 0, 255), 3: (0, 255, 0), 4: (255, 0, 255)}
try:
    color_elegido = int(input("Numero: "))
    color_ruta = color_opciones.get(color_elegido, (255, 0, 0))
except:
    color_ruta = (255, 0, 0)

# Selección de referencia
cv2.imshow("Selecciona referencia", frame_original)
cv2.setMouseCallback("Selecciona referencia", seleccionar_puntos_referencia)
print("Haz clic en dos puntos para definir la linea de referencia (0.19 m).")
print("Presiona ESC para cancelar en cualquier momento.")

while len(puntos_referencia) < 2:
    if verificar_cancelacion():
        print("Analisis cancelado por el usuario.")
        cv2.destroyAllWindows()
        if 'cap' in locals():
            cap.release()
        sys.exit(0)
    cv2.waitKey(1)

cv2.destroyWindow("Selecciona referencia")

if cancelar_analisis:
    print("Analisis cancelado.")
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

ref_pixels = math.hypot(puntos_referencia[1][0] - puntos_referencia[0][0],
                        puntos_referencia[1][1] - puntos_referencia[0][1])
meters_per_pixel = 0.19 / ref_pixels
print(f"Relacion: {meters_per_pixel:.6f} m/pixel")

# Selección de zona A
cv2.imshow("Selecciona zona A", frame_original)
cv2.setMouseCallback("Selecciona zona A", seleccionar_zona_A)
print("Haz clic en dos esquinas opuestas para definir la Zona A.")
print("Presiona ESC para cancelar en cualquier momento.")

while len(puntos_zona_A) < 2:
    if verificar_cancelacion():
        print("Analisis cancelado por el usuario.")
        cv2.destroyAllWindows()
        if 'cap' in locals():
            cap.release()
        sys.exit(0)
    cv2.waitKey(1)

cv2.destroyWindow("Selecciona zona A")

if cancelar_analisis:
    print("Analisis cancelado.")
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

x1, y1 = puntos_zona_A[0]
x2, y2 = puntos_zona_A[1]
zona_A = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

# Selección de objeto
roi = cv2.selectROI("Selecciona el objeto", frame_original, False)
cv2.destroyWindow("Selecciona el objeto")

if roi == (0, 0, 0, 0):
    print("No se selecciono ROI. Cancelando analisis.")
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

tracker = crear_tracker()
tracker.init(frame_original, roi)

# Inicialización
centroides = []
distancia_total = 0.0
distancia_zona_A = 0.0
tiempo_en_zona = 0
contador_entradas = 0
en_zona_anterior = False
ultimo_frame_valido = frame_original.copy()
bounding_box_prev = roi
frame_count = 0

def esta_en_zona_a(centro, zona):
    x, y, w, h = zona
    return x <= centro[0] <= x + w and y <= centro[1] <= y + h

print("\nIniciando analisis...")
print("Presiona 'c' o ESC en cualquier momento para cancelar.")

while True:
    # Verificar cancelación antes de procesar cada frame
    if verificar_cancelacion():
        if solicitar_confirmacion_cancelacion(frame if 'frame' in locals() else frame_original):
            print("Analisis cancelado por el usuario.")
            cancelar_analisis = True
            break
    
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    success, box = tracker.update(frame)
    if success:
        x, y, w, h = map(int, box)
        centro = (x + w // 2, y + h // 2)

        # Verificar cambio brusco de tamaño
        if bounding_box_prev[2] > 0 and bounding_box_prev[3] > 0:
            delta_size = abs(w * h - bounding_box_prev[2] * bounding_box_prev[3]) / (bounding_box_prev[2] * bounding_box_prev[3])
            if delta_size > 0.3:
                success = False
            else:
                bounding_box_prev = box
                centroides.append(centro)

                if len(centroides) > 1:
                    dx = centroides[-1][0] - centroides[-2][0]
                    dy = centroides[-1][1] - centroides[-2][1]
                    distancia = math.hypot(dx, dy) * meters_per_pixel
                    distancia_total += distancia

                    if esta_en_zona_a(centro, zona_A):
                        distancia_zona_A += distancia
                        tiempo_en_zona += 1
                        if not en_zona_anterior:
                            contador_entradas += 1
                            en_zona_anterior = True
                    else:
                        en_zona_anterior = False

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        else:
            bounding_box_prev = box
            centroides.append(centro)

    if not success:
        cv2.putText(frame, "Objeto perdido. Presiona 's' para seleccionar o 'n' para salir.",
                    (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, "Presiona 'c' para cancelar analisis", (10, 230),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.imshow("Seguimiento", frame)
        
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == ord('s'):
                roi = cv2.selectROI("Selecciona el objeto", frame, False)
                cv2.destroyWindow("Selecciona el objeto") 
                if roi == (0, 0, 0, 0):
                    print("No se selecciono ROI.")
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit(0)
                tracker = crear_tracker()
                tracker.init(frame, roi)
                bounding_box_prev = roi
                success = True
                break
            elif key == ord('n'):
                print("Finalizado por el usuario.")
                cap.release()
                cv2.destroyAllWindows()
                sys.exit(0)
            elif key == ord('c') or key == 27:
                if solicitar_confirmacion_cancelacion(frame):
                    print("Analisis cancelado por el usuario.")
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit(0)

    # Dibujar zona A y métricas
    cv2.rectangle(frame, (zona_A[0], zona_A[1]),
                  (zona_A[0] + zona_A[2], zona_A[1] + zona_A[3]), (0, 100, 255), 2)
    
    # Mostrar instrucciones de cancelación
    cv2.putText(frame, "Presiona 'c' o ESC para cancelar", (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    cv2.putText(frame, f"Dist: {distancia_total:.2f}m", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(frame, f"Zona A: {distancia_zona_A:.2f}m", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(frame, f"Tiempo Zona A: {tiempo_en_zona / fps:.1f}s", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6,(0, 0, 255), 2)
    cv2.putText(frame, f"Entradas: {contador_entradas}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    progreso = int((frame_count / total_frames) * 100)
    cv2.putText(frame, f"Progreso: {progreso}%", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Seguimiento", frame)
    
    # Verificar cancelación después de mostrar el frame
    if verificar_cancelacion():
        if solicitar_confirmacion_cancelacion(frame):
            print("Analisis cancelado por el usuario.")
            cancelar_analisis = True
            break

# Imagen final - AHORA video_name ESTÁ DEFINIDA
if len(centroides) > 1 and not cancelar_analisis:
    for i in range(1, len(centroides)):
        cv2.line(ultimo_frame_valido, centroides[i - 1], centroides[i], color_ruta, 2)

    cv2.rectangle(ultimo_frame_valido, (zona_A[0], zona_A[1]),
                  (zona_A[0] + zona_A[2], zona_A[1] + zona_A[3]), (0, 100, 255), 2)

    cv2.putText(ultimo_frame_valido, f"Video: {video_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(ultimo_frame_valido, f"Distancia total: {distancia_total:.2f}m", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(ultimo_frame_valido, f"Distancia en Zona A: {distancia_zona_A:.2f}m", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(ultimo_frame_valido, f"Tiempo en Zona A: {tiempo_en_zona / fps:.1f}s", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(ultimo_frame_valido, f"Entradas a Zona A: {contador_entradas}", (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    output_filename = f"{video_name}_resumen.png"
    cv2.imwrite(output_filename, ultimo_frame_valido)
    print(f"Imagen guardada como {output_filename}")
elif cancelar_analisis:
    print("Analisis cancelado. No se genero imagen de resumen.")

cap.release()
cv2.destroyAllWindows()

if cancelar_analisis:
    print("\nAnalisis cancelado exitosamente.")
else:
    print("\nAnalisis completado exitosamente.")