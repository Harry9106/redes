EXPLICACIÓN DE LO REALIZADO

En este laboratorio diseñamos e implementamos un programa servidor de archivos basado en el protocolo HFTP, con el detalle de que el servidor solo maneja una conexión a la vez, es decir, es secuencial. Los clientes pueden hacer 4 tipos de solicitudes al servidor, son las siguientes: listar todos los archivos que se encuentran en el servidor(get_file_listing), obtener el tamaño de algún archivo en el servidor(get_metadata), obtener un fragmento del un archivo en el servidor(get_slice) e interrumpir la conexión (quit).


DISEÑO EN EL SERVIDOR

Agregamos al esqueleto dado por la cátedra la implementación del socket del servidor, al cual se le asignan los datos ip y puerto pasados por la persona que inicie el servidor o por defecto localhost y 19500. Una vez que el cliente se conecta se envía el socket conectado para que sea manejado por handle para recibir las peticiones y contestarlas. Si otro cliente se conecta mientras ya hay un cliente conectado, el servidor va a atender las peticiones del primer cliente hasta que este se desconecte, y después va a atender todas las peticiones que hubiera hecho el otro cliente.

DISEÑO DE MANEJO DE PETICIONES 

El método handle es el encargado de manejar las peticiones del cliente, lo hace creando un buffer de comandos y lo atiende de la forma FIRST IN FIRST OUT, es decir, si manda muchas peticiones atiende la que primero fue enviada. También funciona que hasta que el cliente no manda un EOL(End Of Line) el comando no es procesado y se queda esperando hasta que mande uno. y se agrega al buffer y después es tratado como una petición normal. Es decir, el cliente puede enviar una petición correcta en varias partes y al final enviar un EOL. La petición es divido por los EOL, puesto en el buffer y se envía cada elemento del Buffer al método execute, una vez en execute mira que tipo de solicitud es y la manda a su correspondiente método (Hay un método por cada tipo de solicitud).

MÉTODOS DE CADA SOLICITUD

Listing(get_file_listing)

Primero se fija en la cantidad de argumentos que el usuario envío, si es incorrecto envía mensaje de error y la petición no es respondida, hasta una nueva petición correcta, si es correcto en este caso el numero de argumentos tiene que ser 0 continua ejecución. imprime mensaje de aprobación, busca en los archivos del servidor e imprime en los nombres en pantalla.

Metadata(get_metadata filename)

Igual que el anterior se fija si los argumentos son correctos, en este caso tiene que ser 1. Si es correcto se fija si el nombre del archivo pasado como argumento es valido, es decir se encuentra en el servidor. En ese caso busca el tamaño del archivo en bytes y lo devuelve al cliente imprimiendo el archivo en pantalla.

Slice(get_slice filename offsset size)

Se fija al igual que todos los anteriores la cantidad de argumentos pasados por el cliente, en este caso 3 argumentos es el correcto. Si es la cantidad correcta, se fija que el archivo este en el servidor. Ademas busca excepciones en los demás argumentos, es decir, si el offset y el size no se salen del largo del archivo. Luego lee e imprime el archivo en pantalla del cliente del tamaño solicitado en el offset solicitado.

