#ifndef __NODE_H
#define __NODE_H

#include <omnetpp.h>
#include "EtherFrame.h"

using omnetpp::cSimpleModule;
using omnetpp::cMessage;

#define TABLELENGTH 256
#define ARES_HRD_ETH 1
#define ARES_OP_REQUEST 1
#define ARES_OP_REPLY 2
#define ARPTYPE 0x0806
#define ARPLENGTH 6
#define IPTYPE 0x0800
#define IPLENGTH 4
#define AMOUNT_OF_CLIENTS 6

typedef unsigned char IPAddress[4];
typedef unsigned char MACAddress[6];

// Ether Frame Header struct
struct etherFrameHeader {
    MACAddress dest_address;
    MACAddress orgn_address;
    uint16_t eth_type;
    unsigned char payload[1500];
}__attribute__((packed));


// Arp struct
struct arpPacket {
    uint16_t has;
    uint16_t pas;
    uint8_t length_has;
    uint8_t length_pas;
    uint16_t opcode;
    MACAddress hard_sender;
    IPAddress protocol_sender;
    MACAddress hardaddr_target;
    IPAddress protocoladdr_target;
}__attribute__((packed));

class Node : public cSimpleModule
{
  private:
    cMessage *timer;
    unsigned char seen[AMOUNT_OF_CLIENTS];
    MACAddress table[TABLELENGTH];

  public:
    Node();
    virtual ~Node();

  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage *msg);
    virtual void updateDisplay(void);

    /*
     * To implement!
     * Try to send `data` to a specified `ip`.
     * `data` is a buffer with IP_PAYLOAD_SIZE bytes.
     * If the MAC address for that IP is unknown, an ARP request should be sent.
     * Returns 0 on success and non-zero if it's necessary to retry later (because
     * ARP is figuring out the correct MAC address).
     */
    virtual int send_to_ip(IPAddress ip, void *data);

    /*
     * To implement!
     * Handle a packet.
     * If it's an ARP packet: Processes, if it's a regular data
     * packet then it forwards the data to the network layer using
     * receive_ip_packet.
     * `frame` is a buffer with ETHERFRAME_SIZE bytes.
        An ethernet frame has:
         - 6 bytes destination MAC
         - 6 bytes source MAC
         - 2 bytes type
         - 46-1500 bytes of data payload (in this application is always 1500)
        Total max size: 1514 bytes

     */
    virtual void receive_ethernet_frame(void *frame);

    /*
     * Delivers the `data` buffer with IP_PAYLOAD_SIZE bytes to the network layer
     * as it was delivered to send_to_ip in the node that originated the message.
     */
    virtual void receive_ip_packet(void *data);

    /*
     * Sends a frame through ethernet. `frame` is a buffer with ETHERFRAME_SIZE
     * bytes containing the frame to be sent.
        An ethernet frame has:
         - 6 bytes destination MAC
         - 6 bytes source MAC
         - 2 bytes type
         - 46-1500 bytes of data payload (in this application is always 1500)
        Total max size: 1514 bytes

     */
    virtual void send_ethernet_frame(void *frame);

    /*
     * Assigns this node's IP addresss into `ip`.
     */
    virtual void get_my_ip_address(IPAddress ip);

    /*
     * Assigns this node's MAC addresss into `mac`.
     */
    virtual void get_my_mac_address(MACAddress mac);

    /*
     * Checks if there's a mac in the table for that 'ip'.
     */
    virtual bool is_in_table(IPAddress ip);

    /*
     * Checks if 'ip' is the same as the node ip.
     */
    virtual bool is_for_me(IPAddress ip);
};

#endif
