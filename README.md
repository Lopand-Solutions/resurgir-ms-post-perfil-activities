# Labs-template-microservice-python-lambda

## Entorno de desarrollo

Creación de un entorno virtual:

```
python -m venv venv
```


Active el entorno virtual en sistemas windows:

```
venv\Scripts\activate
```

Active el entorno virtual en sistemas unix:

```
source venv/bin/activate
```

Si obtienes un error al activar el entorno virtual en windows, ejecuta el siguiente comando en powershell:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

> Con este comando se dan los permisos necesarios para la activación del entorno vistual.

## Instalación de despendencias

Instale las dependencias ejecutando el siguiente comando:

```
pip install -r requirements.txt
```

## Empaquetado de aplicación

Genere un nuevo directorio donde se instalaran las dependencias especificas para la función lambda:

```
mkdir package
```

Instale las dependencias ejecutando el siguiente comando (sistemas windows):

```
pip install --target .\package\ -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all:
```

> Es importante que las dependencias se instalen con la compatibilidad para sistemas  x86_x64 para que pueda ejecutarse sin problemas en una función lambda.

Instale las dependencias ejecutando el siguiente comando (sistemas unix):

```
pip install --target .\package\ -r requirements.txt

Copie el archivo main.py al directorio package:

```
cp main.py package/
```

Para el empaquetado de la aplicación ejecute el siguiente comando en windows:

```
Compress-Archive -Path * -DestinationPath ../app.zip
```

En sistemas unix (linux/MAC), puedes utilizar el siguiente comando:

```
zip -r ../app.zip .
```

> Asegurese de incluir todos los archivos necesarios en el empaquetado de la aplicación.

## Variables de entorno

En la funcion lambda se deben de crear las siguientes variables de entorno para su correcto funcionamiento:

```
TEST_ENV -> true para DEV, false para PROD
MONGO_URI -> Conexión a la base de datos
```

## Configurar el punto de entrada en AWS

Configurelo de la siguiente forma:

```
main:lambda_handler
```

## Fe de erratas

Si encuentras un error, puedes reportarlo al siguiente correo electrónico:

lopand.solutions@gmail.com