#include <Ethernet.h>
#include <EthernetUdp.h>
#include <SPI.h>

byte mac[] = {
    ,
    ,
    ,
    ,
    ,
};
IPAddress ip(, , , );
unsigned int localPort = ;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
String datReq;
int packetSize;
EthernetUDP Udp;

const unsigned int buttonPin = 7;

int buttonState = 0;
int oldButtonState = 0;
int x = 0;

void setUp()
{
    Serial.begin(9600);
    Ethernet.begin(mac, ip);
    Udp.begin(localPort);
    delay(1500);
    pinMode(x, OUTPUT);
    pinMode(buttonPin, INPUT_PULLUP);
}

void loop()
{
    packetSize = Udp.parsePacket();

    if (packetSize > 0)
    {
        Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
        String dataReq(packetBuffer);

        if (dataReq == 'high')
        {
            int digitalVal = digitalRead(buttonPin);
            buttonState = digitalVal;

            if (digitalVal == HIGH)
            {
                x = 0;
                buttonState = 0;
                if (buttonState != oldButtonState)
                {
                    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
                    Udp.print(x);
                    Udp.endPacket();
                }
                oldButtonState = 0;
            }
            else
            {
                x = 255;
                buttonState = 255;
                if (buttonState != oldButtonState)
                {
                    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
                    Udp.print(x);
                    Udp.endPacket();
                }
                oldButtonState = 255;
            }
        }
    }
    memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE);
}