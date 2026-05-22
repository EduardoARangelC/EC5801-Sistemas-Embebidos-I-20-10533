#Tarea 1 EC5801 Sistemas Embebidos I
#Eduardo Rangel Carnet: 20-10533

import time

# 1) Implementacion de la clase Matriz

class Matriz:
    def __init__(self, m: int, n: int):
        if n <= 0 or m <= 0:
            raise ValueError("Las dimensiones deben ser enteros positivos")
        self.filas = m # Número de filas
        self.columnas = n # Número de columnas
        self.matriz = [[0 for _ in range(n)] for _ in range(m)] # Se inicia la matriz con ceros

    def llenar_matriz(self):
        print("Ingrese los elementos de la matriz uno a uno:")
        for i in range(self.filas):
            for j in range(self.columnas):
                self.matriz[i][j] = int(input(f"Elemento [{i + 1}][{j + 1}]: "))

    def imprimir_matriz(self):
        for fila in self.matriz:
            print(fila)
    
    # Se implemento sobrecarga de operadores para simplificar
    # Referencia sobre sobrecarga de operadores en Python: https://www.programiz.com/python-programming/operator-overloading

    # Suma de matrices
    def __add__(self, otra):
        if self.columnas != otra.columnas or self.filas != otra.filas:
            raise ValueError("Para sumar matrices deben tener la misma dimensión")
        resultado = Matriz(self.filas, self.columnas)
        for i in range(self.filas):
            for j in range(self.columnas):
                resultado.matriz[i][j] = self.matriz[i][j] + otra.matriz[i][j]
        return resultado

    # Resta de matrices
    def __sub__(self, otra):
        if self.columnas != otra.columnas or self.filas != otra.filas:
            raise ValueError("Para restar matrices deben tener la misma dimensión")
        resultado = Matriz(self.filas, self.columnas)
        for i in range(self.filas):
            for j in range(self.columnas):
                resultado.matriz[i][j] = self.matriz[i][j] - otra.matriz[i][j]
        return resultado

    # Multiplicación de matrices
    def __mul__(self, otra):
        if self.columnas != otra.filas:
            raise ValueError("El número de columnas de la primera matriz debe coincidir con las filas de la segunda")
        resultado = Matriz(otra.columnas, self.filas)
        for i in range(self.filas):
            for j in range(otra.columnas):
                suma = 0
                for k in range(self.columnas):
                    suma += self.matriz[i][k] * otra.matriz[k][j]
                resultado.matriz[i][j] = suma
        return resultado

    # Deshabilitamos la división
    def __truediv__(self, otra):
        raise TypeError("Operación no soportada: La división de matrices no está matemáticamente definida")
        
    def __floordiv__(self, otra):
        raise TypeError("Operación no soportada: La división de matrices no está matemáticamente definida")
    
# 2) Implementacion de la clase Vector con herencia de una clase punto 3D

class Punto3D:
    def __init__(self, x: float, y: float, z: float):
        self.__x = x
        self.__y = y
        self.__z = z

    def get_x(self): return self.__x
    def get_y(self): return self.__y
    def get_z(self): return self.__z

    # Suma de un escalar en uno, varios o todos los ejes
    def sumar_escalar(self, escalar, *ejes):
        # Si no se pasan ejes, se aplica a todos
        if not ejes:
            self.__x += escalar
            self.__y += escalar
            self.__z += escalar
            return
        
        # Si se pasan ejes, revisamos cuáles se solicitaron
        for eje in ejes:
            if eje not in ("x", "y", "z"):
                raise ValueError(f"Error: El eje '{eje}' no existe. Use 'x', 'y' o 'z'")
        if "x" in ejes: self.__x += escalar
        if "y" in ejes: self.__y += escalar
        if "z" in ejes: self.__z += escalar

    # Multiplicación por un escalar
    def multiplicar_escalar(self, escalar, *ejes):
        # Si no se pasan ejes, se aplica a todos
        if not ejes:
            self.__x *= escalar
            self.__y *= escalar
            self.__z *= escalar
            return

        # Si se pasan ejes, revisamos cuáles se solicitaron
        for eje in ejes:
            if eje not in ("x", "y", "z"):
                raise ValueError(f"Error: El eje '{eje}' no existe. Use 'x', 'y' o 'z'")
        if "x" in ejes: self.__x *= escalar
        if "y" in ejes: self.__y *= escalar
        if "z" in ejes: self.__z *= escalar

# Clase Hija Vector
class Vector(Punto3D):
    def __init__(self, x, y, z):
        # Llamamos a la clase padre
        super().__init__(x, y, z)

    def magnitud(self):
        x = self.get_x()
        y = self.get_y()
        z = self.get_z()
        return ((x**2) + (y**2) + (z**2)) ** 0.5

# 3) Polimorfismo: Disco Duro, RAM y SRAM
class Memoria:
    def __init__(self, tamano, retardo):
        self.memoria = [0] * tamano  # Tamaño de la memoria
        self.retardo = retardo       # Retardo 

    def escribir(self, direccion, dato):
        if 0 <= direccion < len(self.memoria):
            time.sleep(self.retardo) # Simulamos el retardo
            self.memoria[direccion] = dato
            print(f"[{self.__class__.__name__}] Dato '{dato}' escrito en {direccion}.")
        else:
            print(f"[{self.__class__.__name__}] Error: Dirección de memoria fuera de rango.")

    def leer(self, direccion):
        if 0 <= direccion < len(self.memoria):
            time.sleep(self.retardo) # Simulamos el retardo
            dato = self.memoria[direccion]
            print(f"[{self.__class__.__name__}] Dato '{dato}' leído de  {direccion}.")
            return dato
        else:
            print(f"[{self.__class__.__name__}] Error: Dirección de memoria fuera de rango.")
            return None

# Clases Hijas
class SRAM(Memoria):
    def __init__(self, tamano):
        super().__init__(tamano, retardo= 2) # Rápido

class RAM(Memoria):
    def __init__(self, tamano):
        super().__init__(tamano, retardo= 4)  # Medio

class DiscoDuro(Memoria):
    def __init__(self, tamano):
        super().__init__(tamano, retardo= 8)  # Lento

# Funciones Polimórficas del Bus Manejador
def bus_escribir(dispositivo, direccion, dato):
    dispositivo.escribir(direccion, dato)

def bus_leer(dispositivo, direccion):
    return dispositivo.leer(direccion)

# Ejemplo de uso
def main():
    print("PRUEBA DE LA PARTE 1: MATRICES")
    # Creamos dos matrices de 2x2 para probar las operaciones
    m1 = Matriz(2, 2)
    m2 = Matriz(2, 2)
    
    # Llenamos ambas matrices con datos de ejemplo
    m1.llenar_matriz()
    m2.llenar_matriz()
    
    # Imprimimos las matrices ingresadas
    print("\nMatriz 1 ingresada:")
    m1.imprimir_matriz()
    print("Matriz 2 ingresada:")
    m2.imprimir_matriz()
    
    # Prueba de la Suma
    print("Resultado de la Suma (M1 + M2):")
    matriz_suma = m1 + m2
    matriz_suma.imprimir_matriz()
    
    # Prueba de la Resta
    print("Resultado de la Resta (M1 - M2):")
    matriz_resta = m1 - m2
    matriz_resta.imprimir_matriz()
    
    # Prueba de la Multiplicación
    print("Resultado de la Multiplicación (M1 * M2):")
    matriz_mult = m1 * m2
    matriz_mult.imprimir_matriz()
    
    # Prueba de Intento de División
    print("Intentando dividir M1 / M2:")
    try:
        m1 / m2
    except TypeError as e:
        print(f"Error detectado exitosamente: {e}\n")

    print("PRUEBA DE LA PARTE 2: PUNTO 3D Y VECTOR")
    # Prueba del Punto3D y sus operaciones por ejes
    punto = Punto3D(1, 2, 3)
    print(f"Punto original: X={punto.get_x()}, Y={punto.get_y()}, Z={punto.get_z()}")
    
    # Suma de un escalar solo a X e Y
    punto.sumar_escalar(5, "x", "y")
    print(f"Punto tras sumar 5 a X e Y: X={punto.get_x()}, Y={punto.get_y()}, Z={punto.get_z()}")
    
    # Multiplicacion de un escalar en todos los ejes
    punto.multiplicar_escalar(2)
    print(f"Punto tras multiplicar todo por 2: X={punto.get_x()}, Y={punto.get_y()}, Z={punto.get_z()}")
    
    # Prueba del error de eje inválido
    try:
        punto.sumar_escalar(10, "w")
    except ValueError as e:
        print(f"Error de seguridad detectado exitosamente: {e}")
        
    # Prueba de la clase hija Vector y su magnitud
    vector1 = Vector(3, 4, 0)
    print(f"Vector de prueba: ({vector1.get_x()}, {vector1.get_y()}, {vector1.get_z()})")
    print(f"Magnitud del vector de prueba (3, 4, 0): {vector1.magnitud()}\n")

    print("PRUEBA DE LA PARTE 3: POLIMORFISMO")
    # Creamos instancias de memorias de tamaño 10
    memoria_sram = SRAM(10)
    memoria_ram = RAM(10)
    disco_duro = DiscoDuro(10)

    # El bus escribe y lee sin importarle qué tipo de memoria es
    print("Operaciones en SRAM:")
    bus_escribir(memoria_sram, direccion=2, dato=250)
    bus_leer(memoria_sram, direccion=2)

    print("\nOperaciones en RAM:")
    bus_escribir(memoria_ram, direccion=4, dato=500)
    bus_leer(memoria_ram, direccion=4)

    print("\nOperaciones en Disco Duro:")
    bus_escribir(disco_duro, direccion=8, dato=1000)
    bus_leer(disco_duro, direccion=8)

    print("\nPrueba de error de rango")
    bus_leer(memoria_ram, direccion=20)

if __name__ == "__main__":
    main()