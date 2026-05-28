from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from pathlib import Path
from typing import Any, Generic, TypeVar, cast, Dict

# Importamos el decorador
from schema_validator import schema_validator

PERSONAL = {
    "elementos": [
        {
            "nombre": str,
            "altura": float,
            "peso": float,
            "edad": int,
            "lista_de_habilidades": list,
            "descripcion": str
        }
    ]
}

# Función para procesar el string YAML
@schema_validator(PERSONAL)
def parsear_yaml(stream_contenido: str) -> dict:
    return load(stream_contenido, Loader=Loader)

generic_t = TypeVar("generic_t")

#Clase base encargada de las operaciones lectura y escritura
class GestorArchivos:
    
    def leer_archivo(self, file_path: Path, binario: bool = False) -> Any:
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        modo = "rb" if binario else "r"
        with file_path.open(modo) as archivo:
            return archivo.read()
    
    def escribir_archivo(self, file_path: Path, contenido: Any, binario: bool = False) -> None:
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        modo = "wb" if binario else "w"
        with file_path.open(modo) as archivo:
            archivo.write(contenido)

#Clase hija para manejar YAML
class YAML_LOADER(GestorArchivos, Generic[generic_t]):
    
    __dict: generic_t

    def __init__(self) -> None:
        super().__init__()
        self.__dict = cast(generic_t, {})

    def load_file(self, name: str, file_path: Path) -> Any:
        # Obtenemos el contenido del archivo como string
        stream_contenido = self.leer_archivo(file_path, binario=False)
        
        # Aplicamos la función que tiene el validador
        config_data = parsear_yaml(stream_contenido)
        
        # Si el validador falla, retorna None
        if config_data is None:
            raise ValueError(f"Falla de validación: El archivo '{file_path}' no cumple con el Schema requerido")
        # Guardamos los datos en memoria con el nombre proporcionado
        data_interna = cast(Dict[str, Any], self.__dict)
        data_interna[name] = {
            "path": str(file_path),
            "data": config_data
        }
        return config_data

    # Método para obtener los datos en memoria
    def get_data(self, name: str) -> dict:
        data_interna = cast(Dict[str, Any], self.__dict)
        if name in data_interna:
            return data_interna[name]["data"]
        raise KeyError(f"No existe: '{name}'")

    # Método para modificar los datos en memoria
    def modify_data(self, name: str, new_data: dict) -> None:
        data_interna = cast(Dict[str, Any], self.__dict)
        if name not in data_interna:
            raise KeyError(f"Identificador no encontrado: '{name}'")
        data_interna[name]["data"].update(new_data)

    # Método para guardar los datos modificados
    def save_file(self, name: str) -> None:
        data_interna = cast(Dict[str, Any], self.__dict)
        if name not in data_interna:
            raise KeyError(f"Identificador no encontrado: '{name}'")
        
        ruta_archivo = Path(data_interna[name]["path"])
        stream_salida = dump(data_interna[name]["data"], Dumper=Dumper)
        self.escribir_archivo(ruta_archivo, stream_salida, binario=False)

if __name__ == "__main__":
    # Creamos una instancia del YAML Loader
    loader = YAML_LOADER()
    ruta_yaml = Path("Prueba.yaml")
    
    # Creamos un archivo YAML de prueba
    yaml_inicial = """
elementos:
  - nombre: "Juan"
    altura: 1.70
    peso: 64.5
    edad: 23
    lista_de_habilidades: 
      - "Poliglota"
    descripcion: "Especialista en idiomas"
"""
    # Creamos el archivo
    loader.escribir_archivo(ruta_yaml, yaml_inicial)

    try:
        # Cargamos y Validamos con PyYAML y el Decorador
        loader.load_file("archivo_1", ruta_yaml)
        
        # Obtenemos datos con el GETTER
        datos_en_memoria = loader.get_data("archivo_1")

        # Modificamos los datos en memoria
        nueva_persona = {
            "nombre": "Fabio",
            "altura": 1.78,
            "peso": 69.0,
            "edad": 26,
            "lista_de_habilidades": ["Python", "Tecnico de fibra optica"],
            "descripcion": "Especialista en tecnología"
        }
        
        # Extraemos la lista de elementos y añadimos el nuevo personaje
        datos_en_memoria["elementos"].append(nueva_persona)
        loader.modify_data("archivo_1", datos_en_memoria)

        # Guardamos los cambios físicos en el disco
        loader.save_file("archivo_1")

    except Exception as e:
        print(f"Ocurrió un error durante la ejecución: {e}")