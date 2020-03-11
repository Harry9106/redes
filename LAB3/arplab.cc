#include "node.h"
#include <arpa/inet.h>


bool Node::is_in_table(IPAddress ip){
    bool intable = false;
    for (int i = 0; i < ARPLENGTH; ++i)
    {
        if (table[ip[3]][i] != 0xff)
            {
                intable = true;
                break;
            }
    }
    return intable;
}

bool Node::is_for_me(IPAddress ip){
    IPAddress myip = {};
    get_my_ip_address(myip);
    bool isforme = true;

    for (int i = 0; i < IPLENGTH; ++i)
    {
        if (ip[i] != myip[i])
            {
                isforme = false;
                break;
            }
    }
    return isforme;
}

/*
 * Implementar!
 * Intentar enviar `data` al `ip` especificado.
 * `data` es un buffer con IP_PAYLOAD_SIZE bytes.
 * Si la dirección MAC de ese IP es desconocida, debería enviarse un pedido ARP.
 * Devuelve 0 en caso de éxito y distinto de 0 si es necesario reintentar luego
 * (porque se está bucando la dirección MAC usando ARP)
 */
int Node::send_to_ip(IPAddress ip, void *data) {
    etherFrameHeader efh;
    get_my_mac_address(efh.orgn_address);
    int index = ip[3];

    for (int i = 0; i < ARPLENGTH; ++i)
    {
        efh.dest_address[i] = table[index][i];
    }

    bool broadcast = true;
    for (int i = 0; i < ARPLENGTH; ++i)
    {
        if (efh.dest_address[i] != 0xff)
        {
            broadcast = false;
            break;
        }
    }

    if (broadcast) {
        arpPacket ap;
        efh.eth_type = htons(ARPTYPE);
        ap.has = htons(ARES_HRD_ETH);
        ap.pas = htons(IPTYPE);
        ap.length_has = ARPLENGTH;
        ap.length_pas = IPLENGTH;
        ap.opcode = htons(ARES_OP_REQUEST);
        get_my_mac_address(ap.hard_sender);
        get_my_ip_address(ap.protocol_sender);
        
        for (int i = 0; i < IPLENGTH; ++i)
        {
            ap.protocoladdr_target[i] = ip[i];
        }

        memcpy(efh.payload, &ap, IP_PAYLOAD_SIZE);

        send_ethernet_frame(&efh);
        return 1;
    }

    efh.eth_type = htons(IPTYPE);

    memcpy(efh.payload, data, IP_PAYLOAD_SIZE);

    send_ethernet_frame(&efh);
    return 0;
}


/*
 * Implementar!
 * Manejar el recibo de un paquete.
 * Si es un paquete ARP: procesarlo.
 * Si es un paquete con datos: pasarlo a la capa de red con receive_ip_packet.
 * `packet` es un buffer de ETHERFRAME_SIZE bytes.
    Un frame Ethernet tiene:
     - 6 bytes MAC destino
     - 6 bytes MAC origen
     - 2 bytes tipo
     - 46-1500 bytes de payload (en esta aplicación siempre son 1500)
    Tamaño total máximo: 1514 bytes
 */
void Node::receive_ethernet_frame(void *frame) {
    MACAddress mymac = {};
    IPAddress myip ={};
    get_my_mac_address(mymac);
    get_my_ip_address(myip);

    unsigned char *str = (unsigned char *)frame;

    etherFrameHeader efh;
    arpPacket ap;

    memcpy(efh.dest_address, str, sizeof(MACAddress));
    str += sizeof(MACAddress);

    memcpy(efh.orgn_address, str, sizeof(MACAddress));
    str += sizeof(MACAddress);

    memcpy(&efh.eth_type, str, sizeof(uint16_t));
    efh.eth_type = ntohs(efh.eth_type);
    str += sizeof(uint16_t);

    if (efh.eth_type == ARPTYPE)
    {
        memcpy(&ap.has, str, sizeof(uint16_t));
        ap.has = ntohs(ap.has);
        str += sizeof(uint16_t);

        memcpy(&ap.pas, str, sizeof(uint16_t));
        ap.pas = ntohs(ap.pas);
        str += sizeof(uint16_t);

        memcpy(&ap.length_has, str, sizeof(uint8_t));
        str += sizeof(uint8_t);

        memcpy(&ap.length_pas, str, sizeof(uint8_t));
        str += sizeof(uint8_t);

        memcpy(&ap.opcode, str, sizeof(uint16_t));
        ap.opcode = ntohs(ap.opcode);
        str += sizeof(uint16_t);

        memcpy(ap.hard_sender, str, sizeof(MACAddress));
        str += sizeof(MACAddress);

        memcpy(ap.protocol_sender, str, sizeof(IPAddress));
        str += sizeof(IPAddress);

        if (ap.opcode == ARES_OP_REPLY){
            memcpy(ap.hardaddr_target, str, sizeof(MACAddress));
        }
        str += sizeof(MACAddress);

        memcpy(ap.protocoladdr_target, str, sizeof(IPAddress));

        memcpy(efh.payload, &ap, IP_PAYLOAD_SIZE);
    }
    else{
        memcpy(efh.payload, str, IP_PAYLOAD_SIZE);
    }
    
    if (efh.eth_type == ARPTYPE)
    {
        if (ap.has == ARES_HRD_ETH)
        {
            if (ap.length_has == ARPLENGTH)
            {
                if (ap.pas == IPTYPE)
                {
                    if (ap.length_pas == IPLENGTH)
                    {
                        bool merge_flag = false;
                        bool already = is_in_table(ap.protocol_sender);

                        if (already)
                        {
                            for (int i = 0; i < ARPLENGTH; ++i)
                            {
                                table[ap.protocol_sender[3]][i] = ap.hard_sender[i];
                            }
                            merge_flag = true;
                        }

                        bool forme = is_for_me(ap.protocoladdr_target);

                        if (forme)
                        {
                            if (!merge_flag)
                            {
                                for (int i = 0; i < ARPLENGTH; ++i)
                                {
                                    table[ap.protocol_sender[3]][i] = ap.hard_sender[i];
                                }
                            }

                            if (ap.opcode == ARES_OP_REQUEST)
                            {   
                                // Swapeo los campos del paquete existente para responder.

                                get_my_mac_address(efh.orgn_address);
                                for (int i = 0; i < ARPLENGTH; ++i)
                                {
                                    efh.dest_address[i] = ap.hard_sender[i];
                                }
                                efh.eth_type = htons(ARPTYPE);

                                ap.has = htons(ARES_HRD_ETH);
                                ap.pas = htons(IPTYPE);
                                ap.length_has = ARPLENGTH;
                                ap.length_pas = IPLENGTH;
                                ap.opcode = htons(ARES_OP_REPLY);
                                for (int i = 0; i < ARPLENGTH; ++i)
                                {
                                    ap.hardaddr_target[i] = ap.hard_sender[i];
                                }
                                get_my_mac_address(ap.hard_sender);
                                for (int i = 0; i < IPLENGTH; ++i)
                                {
                                    ap.protocoladdr_target[i] = ap.protocol_sender[i];
                                }
                                get_my_ip_address(ap.protocol_sender);

                                memcpy(efh.payload, &ap, IP_PAYLOAD_SIZE);

                                send_ethernet_frame(&efh);
                            }
                        }
                    }
                    else
                    {
                        printf("IP address length error.\n");
                    }
                }
                else
                {
                    printf("Ethernet protocol error.\n");
                }
            }
            else
            {
                printf("MAC address length error.\n");
            }
        }
        else
        {
            printf("Hardware protocol error.\n");
        }
    }
    else
    {
        bool receive = true;
        for (int i = 0; i < ARPLENGTH; ++i)
        {
            if (efh.dest_address[i] != mymac[i])
                receive = false;
        }
        if (receive)
        {
            receive_ip_packet(&efh.payload);
        } 
    }
}


/*
 * Constructor de la clase. Poner inicialización aquí.
 */
Node::Node()
{
    timer = NULL;
    for (unsigned int i = 0; i != AMOUNT_OF_CLIENTS; ++i) {
        seen[i] = 0;
    }

    for (int i = 0 ; i < TABLELENGTH ; ++i) {
        for (int j = 0; j < ARPLENGTH; ++j)
        {
            table[i][j] = 0xff;
        }
    }
}
