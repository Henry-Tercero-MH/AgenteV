# -*- coding: utf-8 -*-
"""
Módulo de preprocesamiento avanzado de imágenes para OCR de placas
Mejora significativamente la calidad de las imágenes antes del OCR
"""
import cv2
import numpy as np


class PreprocessorPlacas:
    """Preprocesador especializado para imágenes de placas vehiculares"""

    def __init__(self):
        """Inicializa el preprocesador"""
        self.ancho_minimo = 450  # Ancho mínimo para OCR óptimo (optimizado)
        self.ancho_maximo = 800  # Ancho máximo para evitar sobredimensionamiento
        self.usar_super_resolucion = True  # Activar super-resolución para placas muy pequeñas
        self.factor_escalado_extra = 1.5  # Factor adicional para placas diminutas (reducido para evitar distorsión)

    def preprocesar_multiple(self, imagen):
        """
        Genera múltiples variaciones de preprocesamiento para mejorar OCR.

        Args:
            imagen (numpy.ndarray): Imagen original de la placa

        Returns:
            list: Lista de imágenes preprocesadas (diferentes técnicas)
        """
        variaciones = []

        # 1. Versión escalada y mejorada (principal)
        img_mejorada = self._preprocesar_principal(imagen)
        variaciones.append(("mejorada", img_mejorada))

        # 2. Versión con binarización Otsu
        img_otsu = self._binarizar_otsu(imagen)
        variaciones.append(("otsu", img_otsu))

        # 3. Versión con binarización adaptativa
        img_adaptativa = self._binarizar_adaptativa(imagen)
        variaciones.append(("adaptativa", img_adaptativa))

        # 4. Versión con corrección de contraste agresiva
        img_contraste = self._mejorar_contraste_agresivo(imagen)
        variaciones.append(("contraste", img_contraste))

        # 5. Versión invertida (para placas con fondo oscuro)
        img_invertida = self._invertir_colores(img_mejorada)
        variaciones.append(("invertida", img_invertida))

        # 6. Versión con detección de bordes + morfología
        img_morfologia = self._aplicar_morfologia(imagen)
        variaciones.append(("morfologia", img_morfologia))

        return variaciones

    def _preprocesar_principal(self, imagen):
        """
        Preprocesamiento principal optimizado para placas.

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen preprocesada
        """
        # 1. Redimensionar si es necesario
        img = self._redimensionar_optimo(imagen)

        # 2. Convertir a escala de grises
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # 3. Aplicar desenfoque bilateral (preserva bordes)
        blur = cv2.bilateralFilter(gray, 11, 17, 17)

        # 4. Mejorar contraste con CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blur)

        # 5. Reducir ruido con filtro gaussiano suave
        denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)

        # 6. Aplicar sharpening
        sharpened = self._aplicar_sharpening(denoised)

        return sharpened

    def _redimensionar_optimo(self, imagen):
        """
        Redimensiona la imagen a un tamaño óptimo para OCR con super-resolución.

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen redimensionada
        """
        alto, ancho = imagen.shape[:2]

        # Si es muy pequeña, escalar agresivamente con super-resolución
        if ancho < self.ancho_minimo:
            # Para placas DIMINUTAS (< 70px), usar escalado EXTRA agresivo
            if ancho < 70:
                factor = self.ancho_minimo * self.factor_escalado_extra / ancho
                print(f"[PREPROC] Placa diminuta detectada ({ancho}px), aplicando escalado x{factor:.1f}")
            # Para placas muy pequeñas (< 150px), usar factor agresivo
            elif ancho < 150:
                factor = self.ancho_minimo * 1.8 / ancho
            else:
                factor = self.ancho_minimo / ancho

            nuevo_ancho = int(ancho * factor)
            nuevo_alto = int(alto * factor)

            # Usar super-resolución si está habilitado y la imagen es muy pequeña
            if self.usar_super_resolucion and ancho < 200:
                img_redimensionada = self._aplicar_super_resolucion(imagen, nuevo_ancho, nuevo_alto)
            else:
                # Usar interpolación LANCZOS4 para mejor calidad al escalar
                img_redimensionada = cv2.resize(imagen, (nuevo_ancho, nuevo_alto),
                                                interpolation=cv2.INTER_LANCZOS4)
        # Si es muy grande, reducir
        elif ancho > self.ancho_maximo:
            factor = self.ancho_maximo / ancho
            nuevo_ancho = self.ancho_maximo
            nuevo_alto = int(alto * factor)
            img_redimensionada = cv2.resize(imagen, (nuevo_ancho, nuevo_alto),
                                            interpolation=cv2.INTER_AREA)
        else:
            return imagen

        return img_redimensionada

    def _aplicar_super_resolucion(self, imagen, nuevo_ancho, nuevo_alto):
        """
        Aplica super-resolución usando interpolación bicúbica mejorada.
        Técnica: Escalar en dos pasos con filtrado para preservar detalles.

        Args:
            imagen (numpy.ndarray): Imagen original
            nuevo_ancho (int): Ancho objetivo
            nuevo_alto (int): Alto objetivo

        Returns:
            numpy.ndarray: Imagen con super-resolución
        """
        # Paso 1: Escalar a tamaño intermedio con INTER_CUBIC
        alto_actual, ancho_actual = imagen.shape[:2]
        ancho_intermedio = int((ancho_actual + nuevo_ancho) / 2)
        alto_intermedio = int((alto_actual + nuevo_alto) / 2)

        img_intermedia = cv2.resize(imagen, (ancho_intermedio, alto_intermedio),
                                    interpolation=cv2.INTER_CUBIC)

        # Aplicar sharpening en tamaño intermedio
        if len(img_intermedia.shape) == 3:
            gray = cv2.cvtColor(img_intermedia, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_intermedia

        # Sharpening suave
        kernel_sharpen = np.array([[-1,-1,-1],
                                   [-1, 9,-1],
                                   [-1,-1,-1]]) / 1.0
        img_sharp = cv2.filter2D(gray, -1, kernel_sharpen)

        # Paso 2: Escalar al tamaño final con LANCZOS4
        img_final = cv2.resize(img_sharp, (nuevo_ancho, nuevo_alto),
                               interpolation=cv2.INTER_LANCZOS4)

        return img_final

    def _binarizar_otsu(self, imagen):
        """
        Aplica binarización Otsu para separar texto de fondo.

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen binarizada
        """
        img = self._redimensionar_optimo(imagen)

        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Aplicar desenfoque para reducir ruido
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Binarización Otsu
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    def _binarizar_adaptativa(self, imagen):
        """
        Aplica binarización adaptativa para iluminación no uniforme.

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen binarizada adaptativamente
        """
        img = self._redimensionar_optimo(imagen)

        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Aplicar desenfoque
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Binarización adaptativa
        binary = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        return binary

    def _mejorar_contraste_agresivo(self, imagen):
        """
        Mejora el contraste de forma agresiva.

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen con contraste mejorado
        """
        img = self._redimensionar_optimo(imagen)

        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # CLAHE con parámetros más agresivos
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)

        # Normalizar
        normalized = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)

        return normalized

    def _invertir_colores(self, imagen):
        """
        Invierte los colores (útil para placas con fondo oscuro).

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen invertida
        """
        return cv2.bitwise_not(imagen)

    def _aplicar_morfologia(self, imagen):
        """
        Aplica operaciones morfológicas para limpiar la imagen.

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen con morfología aplicada
        """
        img = self._redimensionar_optimo(imagen)

        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Binarizar primero
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Operaciones morfológicas para limpiar
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        # Cerrar pequeños agujeros
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Abrir para eliminar ruido
        morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel, iterations=1)

        return morph

    def _aplicar_sharpening(self, imagen):
        """
        Aplica filtro de sharpening para resaltar bordes.

        Args:
            imagen (numpy.ndarray): Imagen original

        Returns:
            numpy.ndarray: Imagen con sharpening aplicado
        """
        # Kernel de sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])

        sharpened = cv2.filter2D(imagen, -1, kernel)

        return sharpened

    def detectar_region_texto(self, imagen):
        """
        Detecta la región con el texto principal de la placa.
        Elimina bordes, marcos y texto secundario (CENTROAMERICA, país, etc.)

        Args:
            imagen (numpy.ndarray): Imagen de la placa

        Returns:
            numpy.ndarray: Región recortada con solo el texto principal
        """
        if len(imagen.shape) == 3:
            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        else:
            gray = imagen.copy()

        # Binarizar
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Encontrar contornos
        contornos, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contornos:
            return imagen

        # Filtrar contornos por área (eliminar ruido pequeño)
        alto_img, ancho_img = imagen.shape[:2]
        area_minima = (alto_img * ancho_img) * 0.01  # 1% del área total

        contornos_validos = [c for c in contornos if cv2.contourArea(c) > area_minima]

        if not contornos_validos:
            return imagen

        # Encontrar el bounding box que contiene todos los contornos válidos
        x_min, y_min = ancho_img, alto_img
        x_max, y_max = 0, 0

        for contorno in contornos_validos:
            x, y, w, h = cv2.boundingRect(contorno)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)

        # Agregar padding
        padding = 5
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(ancho_img, x_max + padding)
        y_max = min(alto_img, y_max + padding)

        # Recortar región
        region = imagen[y_min:y_max, x_min:x_max]

        # Si la región es muy pequeña, retornar imagen original
        if region.shape[0] < 20 or region.shape[1] < 40:
            return imagen

        return region

    def analizar_calidad(self, imagen):
        """
        Analiza la calidad de la imagen para determinar si es apta para OCR.

        Args:
            imagen (numpy.ndarray): Imagen a analizar

        Returns:
            dict: Métricas de calidad
        """
        if len(imagen.shape) == 3:
            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        else:
            gray = imagen.copy()

        # 1. Calcular nitidez (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        nitidez = laplacian.var()

        # 2. Calcular contraste
        contraste = gray.std()

        # 3. Calcular brillo promedio
        brillo = gray.mean()

        # 4. Tamaño de la imagen
        alto, ancho = gray.shape

        return {
            "nitidez": nitidez,
            "contraste": contraste,
            "brillo": brillo,
            "ancho": ancho,
            "alto": alto,
            "apta_ocr": nitidez > 100 and 30 < contraste < 100 and 50 < brillo < 200
        }
