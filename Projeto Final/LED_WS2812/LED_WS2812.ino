#include <FastLED.h>
#include <SPI.h>
#include <MFRC522.h>

#define NUM_LEDS  24   // Número total de LEDs na fita
#define DATA_PIN  4    // Pino de dados conectado à fita
#define MAX_NOMES 5    // Número máximo de nomes/cores

#define SS_PIN  53     // Pino SDA (Chip Select)
#define RST_PIN 49     // Pino de reset

// Definição da struct de cor
struct Color {
  uint8_t r;
  uint8_t g;
  uint8_t b;
};

// Array de LEDs
CRGB leds[NUM_LEDS];

// Listas de nomes e cores correspondentes
const char* nomes[MAX_NOMES] = {"Alê", "d0 a0 4a 10", "c4 d9 31 02", "Anna", "Lenna"};
Color cores[MAX_NOMES] = {
  {255, 0, 0},    // Vermelho
  {0, 255, 0},    // Verde
  {0, 0, 255},    // Azul
  {255, 255, 0},  // Amarelo
  {255, 255, 255} // Branco
};

MFRC522 mfrc522(SS_PIN, RST_PIN); // Instancia o MFRC522
String tagAtual = "";

// Estados da animação
enum AnimationState { IDLE, WAITING_PERCENT, ALL_ON, ROTATING, FINAL };
AnimationState estAtual = IDLE;

unsigned long millisAnterior = 0;
int corIndex = -1;
int numLedsToLight = 0;
int animationCycle = 0;
int startLed = 0;
const long tempoOn = 1000;          // 1 segundo para todos os LEDs ligarem
const long velocidadeRot = 25;      // Velocidade da rotação 25ms 
const int thirdLeds = NUM_LEDS / 6;

void setup() {
  Serial.begin(9600);
  FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(8);
  clearStrip();
  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {

  unsigned long millisAtual = millis();

  // Leitura da tag RFID

  // Verifica se há uma nova tag presente
  if (estAtual == IDLE && mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String tag = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      // Adiciona zero à esquerda para bytes < 16
      tag += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
      // Converte byte para hex
      tag += String(mfrc522.uid.uidByte[i], HEX);
      if (i < mfrc522.uid.size - 1) tag += " ";
    }
    tag.trim();
    Serial.println("Tag UID: " + tag);
    mfrc522.PICC_HaltA();

    // Busca tag/cor correspondente
    corIndex = -1;
    for (int i = 0; i < MAX_NOMES; i++) {
      if (tag.equalsIgnoreCase(nomes[i])) {
        corIndex = i;
        break;
      }
    }

    if (corIndex != -1) {
      Serial.println("Tag encontrada: " + String(nomes[corIndex]) + ". Enter percentage (0-100):");
      estAtual = WAITING_PERCENT; // Espera entrada do percentual
    } else {
      Serial.println("Tag inválida");
      clearStrip();
      estAtual = IDLE;
    }
  }

  // Entrada na Serial
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (estAtual == WAITING_PERCENT && corIndex != -1) {
      // Lê porcentagem e verifica se é válida
      int percent = input.toInt();
      if (percent < 0 || percent > 100) {
        Serial.println("Percentual inválido (0-100)");
        estAtual = IDLE; // Reseta para o IDLE para entrada inválida
      }
      else {
        numLedsToLight = (NUM_LEDS * percent) / 100;
        Serial.println("Percentual: " + String(percent) + "% (" + String(numLedsToLight) + " LEDs)");
        estAtual = ALL_ON;
        millisAnterior = millisAtual;
        updateStripAllOn(corIndex);
      }
    }
    else if (estAtual == FINAL && input == "0") {
      // Apaga LEDs com entrada '0' (copo saiu da balança)
      Serial.println("Clearing LED strip");
      clearStrip();
      estAtual = IDLE;
    }
  }

  // Máquina de estados da animação
  switch (estAtual) {
    case WAITING_PERCENT:
      // Espera input de percentual na serial
      break;

    case ALL_ON:
      if (millisAtual - millisAnterior >= tempoOn) {
        estAtual = ROTATING;
        animationCycle = 0;
        startLed = 0;
        millisAnterior = millisAtual;
      }
      break;

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
      // Espera sinal '0' na serial que o copo saiu da balança
      break;

    case IDLE:
      // Espera por uma nova tag
      break;
  }
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
  for (int i = 0; i < thirdLeds; i++) {
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