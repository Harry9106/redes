# INSTRUCCIONES PARA CORRERLO #

Crear entorno virtual
```
virtualenv venv
```

Activarlo y entrar al directorio:
```
$source ./venv/bin/activate
```

El prompt muestra que el entorno está activado:
```
(venv)$
```

Instalar Jupyter:
```
(venv)$cd ./venv
(venv)$pip install jupyter
```

Conseguir hget.py y correrlo:
```
(venv)$jupyter notebook
```

Se abrirá una nueva pestaña del navegador con un listado de archivos, hacer click sobre hget.ipynb .
Hacer click sobre la cell donde está el código y presionar run cell.