# EXPLICACIÓN DE LO REALIZADO #

En este laboratorio lo que hicimos fue implementar el protocolo ARP de acuerdo a la especificación dada en el RFC826.
Utilizamos un simulador de redes llamado Omnet para simular 6 equipos conectados por un hub, de los cuales 3 poseen nuestra implementación de ARP mientras que los 3 restantes utilizan la implementación de la cátedra.

# ESTRUCTURA DEL CODIGO #

Los archivos modificados fueron arplab.cc y node.h.

## En node.h ##
* Agregamos varias constantes que utilizamos seguido en el codigo.
* También definimos dos estructuras necesarias para la comunicación: etherFrameHeader y arpPacket.
* Para llevar rastro de las direcciones MAC que cada nodo conocía utilizamos una tabla con indices de 0 a 255, lo cual se corresponde a la ultima parte de una dirección IP, y una sola columna para la direccion MAC en sí.
* Definimos los encabezados de funciones auxiliares.

## En arplab.cc ## 
* Implementamos las funciones auxiliares definidas anteriormente.
* Implementamos send_to_ip para que cree un frame Ethernet que, en caso de que la IP dada por parámetro no se corresponda con ninguna MAC en la tabla, envie un paquete ARP. En caso contrario se envía el paquete IP que viene por parámetro.
* Implementamos receive_ethernet_frame para que desde un puntero a datos que viene por parámetro, arme el frame Ethernet y en caso de que corresponda el paquete ARP. En caso de ser un paquete ARP se lo procesa según la especificación de RFC826. En caso de ser un paquete Ethernet con datos se lo pasa a la capa de red.

# DECISIONES DE DISEÑO #
* Structs para definir las estructuras de los paquetes.
* Tabla de 255 filas y 1 columna para guardar las MAC correspondientes a cada IP.
* Uso de memcpy para copiar bytes.
* Funciones auxiliares para comprobaciones.