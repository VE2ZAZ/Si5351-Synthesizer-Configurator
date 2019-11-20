/*
   _===_ _           _                  ______ _     _             _ _ _
  |  ___| |         | |                 | ___ (_)   | |           (_) | |
  | |__ | | ___  ___| |_ _ __ ___ ______| |_/ /_  __| | ___  _   _ _| | | ___ _   _ _ __
  |  __|| |/ _ \/ __| __| '__/ _ \______| ___ \ |/ _` |/ _ \| | | | | | |/ _ \ | | | '__|
  | |___| |  __/ (__| |_| | | (_) |     | |_/ / | (_| | (_) | |_| | | | |  __/ |_| | |
  \____/|_|\___|\___|\__|_|  \___/      \____/|_|\__,_|\___/ \__,_|_|_|_|\___|\__,_|_|

Contrôle/Configuration du Synthétiseur Si5351
Conçu pour rouler sur un Arduino-Nano 
Électro-Bidouilleur - Juillet 2019
*/

#include "si5351.h"
#include "Wire.h"
#include <string.h>
#include <EEPROM.h>
#include <stdlib.h>

// Constantes
#define PLL_LED 11    // La LED de statut du PLL du Si5351

Si5351 si5351;

// Variables globales
char commande;
char RxChar;
char RxStr[300]= "";
int ctr =0;
int commandCtr = 0;
char TempChar;
int TempInt;
String TempStr;
unsigned long long param1; 
unsigned long long param2;
unsigned long long param3;


// Fonction de conversion de String à Long-Long (64 bits) non signé.
unsigned long long convert_str_to_ULL(String InString)
{
unsigned long long  OutULL = 0;
  for (int i = 0; i < InString.length(); i++) 
  {
    char c = InString.charAt(i);
    if (c < '0' || c > '9') break;
    OutULL *= 10;
    OutULL += (c - '0');
  }
  return OutULL;
}

// Fonction de conversion de String à Integer
unsigned char convert_str_to_int(String InString)
{
unsigned char  OutInt = 0;
  for (int i = 0; i < InString.length(); i++) 
  {
    char c = InString.charAt(i);
    if (c < '0' || c > '9') break;
    OutInt *= 10;
    OutInt += (c - '0');
  }
  return OutInt;
}

// Transfert les paramètres reçus de la RAM vers la mémoire EEPROM
void Write_RxString_to_EEPROM(int length)
{
  for (ctr=0;ctr < length;ctr++)
  {
    EEPROM.write(ctr,RxStr[ctr]);   
  }
}

// Fonction qui lit de la mémoire EEPROM les paramètres accompagnant une commande, et les formatte 
void parse_params_from_EEPROM()
{
  TempStr = "";
  while (1)   
  {   // Premier paramètre
    TempChar = char(EEPROM.read(ctr)); 
    ctr++;
    if (TempChar != '|' && TempChar != ',') TempStr = TempStr + TempChar;  // 
    else    // Caractère de séparation de champ détecté
    {
      param1 = convert_str_to_ULL(TempStr);   // Conversion en format ULL (64 bits non signés)
      break;    // Sortie de la boucle 
    }    
  }
  TempStr = "";
  while (TempChar != '|')   
  {   // Deuxième paramètre
    TempChar = char(EEPROM.read(ctr)); 
    ctr++;
    if (TempChar != '|' && TempChar != ',') TempStr = TempStr + TempChar;  // 
    else     // Caractère de séparation de champ détecté
    {
      param2 = convert_str_to_ULL(TempStr);   // Conversion en format ULL (64 bits non signés)
      break;    // Sortie de la boucle 
    }    
  }

  TempStr = "";
  while (TempChar != '|')   
  {   // Troisième paramètre
    TempChar = char(EEPROM.read(ctr)); 
    ctr++;
    if (TempChar != '|' && TempChar != ',') TempStr = TempStr + TempChar;  // 
    else     // Caractère de séparation de champ détecté
    {
      param3 = convert_str_to_ULL(TempStr);   // Conversion en format ULL (64 bits non signés)
      break;    // Sortie de la boucle 
    }    
  }
}

// Fonction de transfert de la configuration de type formatté de la mémoire EEPROM vers le Si5351
void Send_Commands_From_EEPROM_to_Si5351()
{
  // Lire la commande a envoyer
  ctr = 1;    // Sauter le "$" en position 0 du EEPROM
  while (1)
  {
    TempChar = char(EEPROM.read(ctr));  // Lire le caractère de commande du port USB
    if (TempChar == '%') break;        // Fin de la chaine de commandes. Stopper lenvoi au Si5351
    ctr = ctr + 2;                    // Sauter la virgule
    commande = TempChar;
    parse_params_from_EEPROM();       // Fonction qui interprète la commande

    if (commande == '1')              // Commande INIT
    {
      si5351.init(param1, param2, param3);      // Envoi de la commande
    }
    else if (commande == '2')         // Commande SET_PLL_INPUT
    {
      si5351.set_pll_input(param1, param2);      // Envoi de la commande   
    }
    else if (commande == '3')         // Commande SET_REF_FREQ
    {
      si5351.set_ref_freq(param1, param2);      // Envoi de la commande
    }
    else if (commande == '4')         // Commande SET_CORRECTION
    {
      si5351.set_correction(param1, param2);      // Envoi de la commande
    }
    else if (commande == '5')         // Commande SET_FREQ
    {
      si5351.set_freq(param1, param2);      // Envoi de la commande
    }
    else if (commande == '6')         // Commande OUTPUT_ENABLE
    {
      si5351.output_enable(param1, param2);      // Envoi de la commande
    }
        else if (commande == '7')     // Commande DRIVE_STRENGTH
    {
      si5351.drive_strength(param1, param2);      // Envoi de la commande
    }
        else if (commande == '8')     // Commande SET_CLOCK_INVERT
    {
      si5351.set_clock_invert(param1, param2);      // Envoi de la commande
    }
        else if (commande == '9')     // Commande PLL_RESET
    {
      si5351.pll_reset(param1);      // Envoi de la commande
    }
  }
}

// Fonction de transfert de la configuration de type Raw de la mémoire EEPROM vers le Si5351
void Send_RawData_From_EEPROM_to_Si5351()
{
unsigned char address_5351;
unsigned char data_5351;

  ctr = 1;    // Sauter le @
  TempStr = "";
  while (1)   
  {
    TempChar = char(EEPROM.read(ctr)); 
    if (TempChar == '%') break;        // Fin de la chaine de commandes. Stopper lenvoi au Si5351
    ctr++;
    if (TempChar != ',' && TempChar != ';' && TempChar != '\n') TempStr = TempStr + TempChar;  // 
    else if (TempChar == ',') 
    {
      address_5351 = convert_str_to_int(TempStr); 
      TempStr = "";
    }
    else if (TempChar == ';')    // C'est donc un ';'
    {
      data_5351 = convert_str_to_int(TempStr); 
      TempStr = "";
Si5351_write(address_5351,data_5351);
      delay(100);
    }
  }    
}

// Fonction de lecture d'un registre du Si5351. Cette fonction est requise car le si5351.si5351_read() de la 
// librairie ne fonctionne pas bien. Il y a auto-increment non désiré de l'adresse.
unsigned char Si5351_read(unsigned char addr)
{
  Wire.begin();
  Wire.beginTransmission(SI5351_BUS_BASE_ADDR);
  Wire.write(addr);
  Wire.endTransmission();
  Wire.requestFrom(SI5351_BUS_BASE_ADDR, 1, true);
  return Wire.read();
}

// Fonction d'écriture de registre du Si5351. 
unsigned char Si5351_write(unsigned char addr, unsigned char data)
{
  Wire.begin();
  Wire.beginTransmission(SI5351_BUS_BASE_ADDR);
  Wire.write(addr);
  Wire.write(data);
  return Wire.endTransmission();
}

void setup()
{
  TempStr.reserve(20);    // Réservation de 
  Serial.begin(1200);     // Ouverture du port série (USB) à 1200 bps.
  pinMode(PLL_LED, OUTPUT);     // Définition de la broche de la LED de statut du PLL

  // Transferer les parametres du EEPROM au Si5151 lors de la mise sous tension
  TempChar = char(EEPROM.read(0)); 
  if (TempChar == '$') Send_Commands_From_EEPROM_to_Si5351();     // Si Paramètres de type formatté (du programme Si5351 Control).
  else if (TempChar == '@') Send_RawData_From_EEPROM_to_Si5351();   // Si paramètres de type "Registre Raw"
  Serial.print("R");      // Avise le programme PC de la complétion du Reset de l'Arduino
  delay(500);   // Pause de 500 ms.
}

//Boucle principale de l'Arduino. Sert à recevoir les paramètre de configuration du programme PC 
// à faire la surveillance du PLL (mise à jour de la LED). 
void loop()
{
  bool rawData;     // Variable de 1 bit pour marquer si les données sont de type Raw
  if (Serial.available()>0)     // Caractères disponibles dans le tampon de réception du port série?
  {     // Oui
    RxChar = Serial.read();     // Lecture d'un caractère
    if (RxChar == '$'|| RxChar == '@')    // Est-ce un caractère de début de paramètres?
    {      //Oui
      rawData = false;
      if (RxChar == '@') rawData = true;    // Caractère indiquant le format Raw des données? Activer le marqueur Raw
      RxStr[0] = RxChar;      // Lire le premier caractère
      ctr = 1;
      while (RxChar != '%')    // Tant que le caractère reçus n'est pas celui de fin de paramètres
      {
        if (Serial.available()>0)     // Caract;res disponibles dans le tampon Rx?
        {     // Oui
          RxChar = Serial.read();     // Lire le caractère
          RxStr[ctr] = RxChar;        // Le transférer dans la chaîne de caractère en RAM
          ctr++;                      // Incrémenter le compteur
        }
      }
      Serial.print("O"); //   // Avise le programme PC de la complétion de la réception des paramètres
      
      // Sauvegarder les commandes et parametres en memoire EEPROM
      Write_RxString_to_EEPROM(ctr);            
      Serial.print("E");    // Avise le programme PC de la complétion se la sauvegarde sur EEPROM
      
      // Transferer les parametres du EEPROM au Si5151
      if (rawData) Send_RawData_From_EEPROM_to_Si5351();  // Si paramètres de type "Registre Raw"
      else Send_Commands_From_EEPROM_to_Si5351();         // Si Paramètres de type formatté (du programme Si5351 Control).
      Serial.println("S");    // Avise le programme PC de la complétion du transfert de la comfiguration au Si5351  
    }
  }
      // Détection du signal référence externe pour activer la LED. Lecture directe du registre de statut 
      // car les commandes de statut de la librairie ne semblent pas bien fonctionner.
      digitalWrite(PLL_LED,!((si5351.si5351_read(0) & 0b00100000)>>5));  // Le statut LOL est plus stable que le LOS
}
