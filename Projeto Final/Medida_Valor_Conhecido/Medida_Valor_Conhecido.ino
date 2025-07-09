#include <SPI.h> // Protocolo de comunicação entre o RFID e o Arduino
#include <MFRC522.h> // Módulo do RFID
#include <HX711.h> // Módulo do amplificador
#include <FastLED.h>

// Definição dos pinos:
#define SS_PIN  53
#define RST_PIN 49
#define pinDT 3
#define pinSCK 2
#define fator_calibracao 460.42
# define NUM_LEDS  24   // Número total de LEDs na fita
# define DATA_PIN  4    // Pino de dados conectado à fita
# define MAX_NOMES 7    // Número máximo de nomes/cores

MFRC522 mfrc522(SS_PIN, RST_PIN);
HX711 escala;

float medida = 0;
bool jaMediuHoje = false;
float percent;

// Definição da struct de cor
struct Color {
  uint8_t r;
  uint8_t g;
  uint8_t b;
};

// Array de LEDs
CRGB leds[NUM_LEDS];

// Listas de nomes e cores correspondentes
const char* nomes[MAX_NOMES] = {"Alê", "d0 a0 4a 10", "Anna", "Lenna", "e0 ad 46 13", "Jan", "Gustavo"};
Color cores[MAX_NOMES] = {
  {255, 0, 0},    // Vermelho
  {0, 255, 0},    // Verde
  {0, 0, 255},    // Azul
  {255, 255, 0},  // Amarelo
  {234, 54, 128}, // Rosa
  {240, 134, 80}, // Laranja
  {255, 255, 255} // Branco
};

String tagAtual = "";

// Estados da animação
enum AnimationState { IDLE, REGISTERTAG, REGISTERTARA, ALL_ON, ROTATING, FINAL };
AnimationState estAtual = IDLE;

unsigned long millisAnterior = 0;
int corIndex = -1;
int numLedsToLight = 0;
int animationCycle = 0;
int startLed = 0;
const long tempoOn = 1000;          // 1 segundo para todos os LEDs ligarem
const long velocidadeRot = 25;      // Velocidade da rotação 25ms
const int sixthLeds = NUM_LEDS / 6;


void setup() {
  Serial.begin(9600);
  delay(2000);

  // Inicializa LED
  FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(8);
  clearStrip();

  // Inicialização do RFID:
  SPI.begin();
  mfrc522.PCD_Init();
  
  // Calibração da balança:
  escala.begin(pinDT, pinSCK);
  escala.tare(); // Zera a balança
  Serial.println("Balança Zerada");

  escala.set_scale(fator_calibracao);
}

void loop() {
  unsigned long millisAtual = millis();
  String input;
  
  if (Serial.available() > 0) {
    input = Serial.readStringUntil('\n');
    input.trim();

    // Verifica se recebeu "Le a tag"
    if (input.equalsIgnoreCase("Le o tag")) {
      estAtual = REGISTERTAG;
    }

    else if (input.equalsIgnoreCase("Mede tara")) {
      medida = escala.get_units(20);
      Serial.print("Tara");
      Serial.println(medida);
      estAtual = REGISTERTARA;
    }
  }

  // Verifica se há uma nova tag presente
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      // Adiciona zero à esquerda para bytes < 16
      uid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
      // Converte byte para hex
      uid += String(mfrc522.uid.uidByte[i], HEX);
      if (i < mfrc522.uid.size - 1) uid += " ";
    }
    uid.trim();
    mfrc522.PICC_HaltA();

    switch (estAtual) {
      case REGISTERTAG:
        Serial.print("Tag");
        Serial.println(uid);
        estAtual = IDLE;
      
      case REGISTERTARA:
        Serial.print("Tara");
        Serial.println(uid);
        estAtual = IDLE;

      case IDLE:
        Serial.print("TAG:");
        Serial.println(uid);
        //delay(500);

        // Aguarda dados do Python
        String recebido = "";
        while (Serial.available() == 0) {}
        recebido = Serial.readStringUntil('\n');

        // Se a tag lida houver sido cadastrada:
        if (recebido != "NAO_ENCONTRADO") {
          String partes[10];  // 10 campos: nome, meta, tara, idtag, peso, streak, dias[], volumes[], hoje, cor
          int idx = 0;
          int pos = 0;
          while (idx < 10) {
            int next = recebido.indexOf(';', pos);
            if (next == -1) next = recebido.length();
            partes[idx++] = recebido.substring(pos, next);
            pos = next + 1;
          }

          String nome = partes[0];
          float meta = partes[1].toFloat();
          float tara = partes[2].toFloat();
          String idtag = partes[3];
          float ultimo_peso = partes[4].toFloat();
          int streak = partes[5].toInt();
          String ultimo_dia = partes[6];
          float consumo_dia = partes[7].toFloat();
          String hoje = partes[8];
          corIndex = partes[9].toInt();

          Serial.print("Olá, ");
          Serial.print(nome);
          Serial.println("! :)");
          // delay(2000);
          
          millisAnterior = millisAtual;
          updateStripAllOn(corIndex);
          estAtual = ALL_ON;

          medida = escala.get_units(20);
          medida -= tara;

          if (ultimo_dia != hoje){jaMediuHoje = false;}
          else{jaMediuHoje = true;}

          if (!jaMediuHoje) {
            Serial.print("Sua meta hoje é de beber ");
            Serial.print(meta);
            Serial.print(" mL. Seu copo contém ");
            Serial.print(abs(medida), 1);
            Serial.println(" mL.");
            Serial.print("tag:");
            Serial.print(idtag);
            Serial.print(";data:");
            Serial.print(hoje);
            Serial.print(";volume:");
            Serial.print(0);
            Serial.print(";peso:");
            Serial.println(medida, 1);
            percent = 0;
            
          }
          else {
            float delta = medida - ultimo_peso;

            if (medida >= meta || consumo_dia+delta >= meta) {
              Serial.print("Parabéns, ");
              Serial.print(nome);
              Serial.print("! Você bateu sua meta de ");
              Serial.print(meta);
              Serial.println(" mL!");
            } 
            else {
              if (delta != 0) {
                if (delta > 0) {
                  Serial.print("Você adicionou ");
                  Serial.print(abs(delta));
                  Serial.println(" mL desde a última medida.");
                  Serial.print("Faltam ");
                  Serial.print((meta - consumo_dia));
                  Serial.println(" mL para bater sua meta.");

                  Serial.print("tag:");
                  Serial.print(idtag);
                  Serial.print(";data:");
                  Serial.print(hoje);
                  Serial.print(";volume:");
                  Serial.print(consumo_dia);
                  Serial.print(";peso:");
                  Serial.println(medida, 1);

                  percent = (consumo_dia)/meta;
                } 
                else {
                  Serial.print("Você bebeu ");
                  Serial.print(abs(delta));
                  Serial.println(" mL desde a última medida.");
                  Serial.print("Faltam ");
                  Serial.print((meta + delta));
                  Serial.println(" mL para bater sua meta.");

                  Serial.print("tag:");
                  Serial.print(idtag);
                  Serial.print(";data:");
                  Serial.print(hoje);
                  Serial.print(";volume:");
                  Serial.print(consumo_dia-delta);
                  Serial.print(";peso:");
                  Serial.println(medida, 1);
                  percent = (consumo_dia-delta)/meta;
                }
              } 
              else {
                Serial.println("Você não bebeu ou adicionou água desde a última medida.");
                Serial.print("Faltam ");
                Serial.print((consumo_dia));
                Serial.println(" mL para bater sua meta.");
                percent = (consumo_dia)/meta;
              }
              numLedsToLight = (NUM_LEDS * percent);
              Serial.println("Percentual: " + String(percent*100) + "% (" + String(numLedsToLight) + " LEDs)");
            }
          }
        }
    }
  }
  

  switch (estAtual) {
    case ALL_ON:
      if (millisAtual - millisAnterior >= tempoOn) {
        estAtual = ROTATING;
        animationCycle = 0;
        startLed = 0;
        millisAnterior = millisAtual;
      }

    case ROTATING:
      if (millisAtual - millisAnterior >= velocidadeRot) {
        updateStripRotating(corIndex);
        startLed++;
        if (startLed >= NUM_LEDS) {
          startLed = 0;
          animationCycle++;
        }
        if (animationCycle >= 2) {
          estAtual = FINAL;
          updateStripFinal(corIndex, numLedsToLight);
          Serial.println("Animation complete. Send '0' to clear LEDs.");
        }
        millisAnterior = millisAtual;
      }
      break;

    case FINAL:
      if (input == "0") {
        // Apaga LEDs com entrada '0' (copo saiu da balança)
        Serial.println("Clearing LED strip");
        clearStrip();
        estAtual = IDLE;
      }
      break;
  }
  /*
  escala.power_down();
  delay(1000);
  escala.power_up();
  */
}

// Liga todos os LEDs
void updateStripAllOn(int corIndex) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB(cores[corIndex].r, cores[corIndex].g, cores[corIndex].b);
  }
  FastLED.show();
}

// Liga 1/3 dos LEDs, rotação
void updateStripRotating(int corIndex) {
  clearStrip();
  for (int i = 0; i < sixthLeds; i++) {
    int index = (startLed + i) % NUM_LEDS;
    leds[index] = CRGB(cores[corIndex].r, cores[corIndex].g, cores[corIndex].b);
  }
  FastLED.show();
}

// Liga os LEDs de acordo com a porcentagem da meta
void updateStripFinal(int corIndex, int numLeds) {
  clearStrip();
  for (int i = 0; i < numLeds; i++) {
    leds[i] = CRGB(cores[corIndex].r, cores[corIndex].g, cores[corIndex].b);
  }
  FastLED.show();
}

// Apaga todos os LEDs
void clearStrip() {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB::Black;
  }
  FastLED.show();
}