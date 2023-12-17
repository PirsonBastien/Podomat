#include <Wire.h> // Gestion de l'I2C
#include "MCP4xxx.h" // Gestion des potentiomètres numériques
#include <Arduino_AdvancedAnalog.h> // Gestion des ADC
#include <SDRAM.h>  // Gestion de la RAM externe

//C'est le nombre d'échantillon par capteur, ne pas augmenter, la ram externe ne peut pas supporter plus de mesures
// 800000 mesures * 16 bits * 5 capteurs = 64000000 bits => 8 Mb ce qui correspond à la capcité max de la RAM
#define maxSensorValue 800000 
// Correspond à la fréquence de d'échantillonage pour une batterie de mesures de tous les capteurs,
// Ne pas changer, doit correspondre au code python,
// si modif quand même veiller à controler la fréquence d'échantillonage (surtout en cas d'augmentation)
// Le temps de mesure maximum sera aussi à modifier dans l'application python.
#define chosenSamplingFrequency 2000 
// Ne pas changer, il faut modifier d'autres parties du code arduino et python le cas échéant, 
// n'influe pas sur la ram car pas utilisé lors du rangement des echantillons par soucis pratique
#define nbreSensor 5 

// Déclaration de la Ram externe
SDRAMClass mySDRAM;
uint16_t *sdramMem;
uint16_t *sdramSensorValue;

// Déclaration des ADC, veuillez vous référer au tableau des entrées analogiques
// par adc (https://reference.arduino.cc/reference/en/libraries/arduino_advancedanalog/)
// si vous souhaitez changer les caneaux utiliser
AdvancedADC adc1(A0, A1);
AdvancedADC adc2(A5);
AdvancedADC adc3(A2, A3);

// Déclaration des potentiomètres numériques
MCP4461 pot0;
MCP4461 pot1;

// Déclaration des variables globales
int bascule = 0;
int nombre_cycle = 0;
int potentiometre[8];

void setup() {
  // Initialisation de la communication série, I²C, et de la mémoire SDRAM, le baudrate du serial doit correspondre à celui du code Python
  Serial.begin(115200);
  Wire1.begin();
  mySDRAM.begin();
  sdramMem = (uint16_t *)mySDRAM.malloc(maxSensorValue * nbreSensor * sizeof(uint16_t));

  // Initialisation des ADC avec des résolutions, fréquences d'échantillonnage, nombres d'échantillons par canal et taille de file d'attente
  if (!adc1.begin(AN_RESOLUTION_16, 3600000, 1, 8) || !adc2.begin(AN_RESOLUTION_16, 3600000, 1, 8) || !adc3.begin(AN_RESOLUTION_16, 3600000, 1, 8)) {
    // En cas d'échec de l'initialisation, boucle infinie
    while (1);
  }
}

void loop() {
  // Fonction pour recevoir les données de l'application Python
  reception_donnee();
  // Si la bascule est activée, effectue les étapes suivantes
  if (bascule == 1) {
    // Règle les potar numériques en fonction du code Python
    reglage_pot();
    // Appelle la fonction d'acquisition de données
    acquisition(nombre_cycle, chosenSamplingFrequency);
    // Envoie les données acquises via la communication série vers le l'application python
    envoie_donnee();
    // Réinitialise la bascule
    bascule = 0;
  }
}

void reception_donnee() {
  // Vérifie si des données sont disponibles sur la communication série
  if (Serial.available() > 0) {
    // Boucle pour lire 9 lignes de données
    for (int i = 0; i < 9; i++) {
      // Lit une ligne de données sous forme de chaîne
      String data = Serial.readStringUntil('\n');
      // Convertit la chaîne en entier
      int data2 = data.toInt();
      // Traite les données en fonction de l'indice actuel
      if (i == 0) {
        nombre_cycle = min(data2, maxSensorValue);
      } else {
        potentiometre[i - 1] = data2;
      }
    }
    // Active la bascule pour indiquer que les données ont été reçues
    bascule = 1;
  }
}

void reglage_pot() {
  // Configuration du potentiomètre numérique 0, potar U6 dans le Kicad
  pot0.setMCP4461Address(0x2D);
  pot0.setVolatileWiper(0, potentiometre[0]);
  pot0.setVolatileWiper(1, potentiometre[1]);
  pot0.setVolatileWiper(2, potentiometre[2]);
  pot0.setVolatileWiper(3, potentiometre[3]);

  // Configuration du potentiomètre numérique 1, potar U4 dans le Kicad
  pot1.setMCP4461Address(0x2F);
  pot1.setVolatileWiper(0, potentiometre[4]);
  pot1.setVolatileWiper(1, potentiometre[5]);
  pot1.setVolatileWiper(2, potentiometre[6]);
  pot1.setVolatileWiper(3, potentiometre[7]);
}

void adc_read_buf(AdvancedADC &adc) {
  // Vérifie si des données sont disponibles dans le tampon de l'ADC
  if (adc.available()) {
    // Transfère le tampon de l'ADC dans la mémoire SDRAM
    SampleBuffer buf = adc.read();
    memmove(sdramSensorValue, buf.data(), 4);
    // Libère le tampon
    buf.release();
  }
}

void acquisition(uint nbreCycle, uint samplingFrequency) {
  unsigned long microsTimer;
  unsigned long samplingTimer;
  // Calcule le temps entre les échantillons en microsecondes
  samplingTimer = pow(10, 6) / samplingFrequency;
  // Initialise le pointeur de la mémoire SDRAM
  sdramSensorValue = sdramMem;

  // Boucle pour le nombre de cycles spécifié
  for (uint indPointer = 0; indPointer < nbreCycle; indPointer++) {
    // Enregistre le temps actuel en microsecondes
    microsTimer = micros();
    // Lecture du deuxième et troisième capteur (adc2)
    adc_read_buf(adc2);
    sdramSensorValue = sdramSensorValue + 1;
    // Lecture du premier capteur (adc3)
    adc_read_buf(adc3);
    sdramSensorValue = sdramSensorValue + 2;
    // Lecture du quatrième et cinquième capteur (adc1)
    adc_read_buf(adc1);
    sdramSensorValue = sdramSensorValue + 2;
    // Attend jusqu'à la prochaine lecture pour définir la vitesse d'échantillonnage
    while (micros() - microsTimer < samplingTimer);
  }
}

void envoie_donnee() {
  // Envoie le signal que l'envoi de données commence
  Serial.println("Envoi");
  // Envoie le nombre de cycles
  Serial.println(nombre_cycle);
  // Envoie le nombre de capteurs
  Serial.println(nbreSensor);
  // Réinitialise le pointeur de la mémoire SDRAM
  sdramSensorValue = sdramMem;

  // Boucle pour envoyer toutes les données acquises
  for (uint i = 0; i < nombre_cycle * nbreSensor; i++) {
    Serial.println(*(sdramSensorValue + i), DEC);
  }
}
