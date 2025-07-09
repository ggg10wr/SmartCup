#include <HX711.h>

// Definição dos pinos
const int PINO_DT = 3;
const int PINO_SCK = 2;

HX711 escala;
float fator_calibracao = 1;
bool calibrado = false;
bool deseja_ajustar = false;
bool aguardando_valor = false;
bool concluido = false;
bool exibir = false;

void setup() {
  Serial.begin(9600);
  escala.begin(PINO_DT, PINO_SCK);

  // Calibração com dois pontos
  float peso1 = 0.0;
  float peso2 = 0.0;

  Serial.println("\nVerifique que não há nada na balança e dê enter.");
  while (Serial.available() == 0); Serial.read();
  long leitura1 = escala.read_average(30);
  Serial.print("Leitura com 0g: ");
  Serial.println(leitura1);

  Serial.println("Agora coloque um peso conhecido (ex: 1000g), digite o valor e dê enter:");
  while (Serial.available() == 0);
  String entrada = Serial.readStringUntil('\n');
  entrada.trim();
  peso2 = entrada.toFloat();

  delay(1000); // Espera a balança estabilizar

  long leitura2 = escala.read_average(30);
  Serial.print("Leitura com ");
  Serial.print(peso2);
  Serial.println("g: ");
  Serial.println(leitura2);

  // Calibração linear
  fator_calibracao = (float)(leitura2 - leitura1) / (peso2 - peso1);
  Serial.print("Fator de calibração calculado: ");
  Serial.println(fator_calibracao);

  escala.set_offset(leitura1); // Define o zero
  escala.set_scale(fator_calibracao);

  calibrado = true;
  exibir = true;

  Serial.println("Calibração concluída!");
  Serial.println("Deseja fazer ajustes manuais na calibração? (s/n)");
}

void loop() {
  if (calibrado && !concluido) {
    escala.set_scale(fator_calibracao);

    if (!deseja_ajustar && Serial.available() > 0) {
      char resp = Serial.read();
      while (Serial.available()) Serial.read(); // Limpa buffer extra

      if (resp == 's') {
        deseja_ajustar = true;
        aguardando_valor = true;
        Serial.println("Digite o valor que deseja ajustar (ex: -100 ou 50):");
      } else if (resp == 'n') {
        concluido = true;
        Serial.println("Ok! Encerrando ajustes.");
      }
    }

    // Calcula novo fator de calibração com base no ajusto provido pelo usuário.
    if (aguardando_valor && Serial.available() > 0) {
      String valor_str = Serial.readStringUntil('\n');
      valor_str.trim();
      int valor = valor_str.toInt();
      bool valido = (valor_str == String(valor));

      if (valido && valor != 0) {
        fator_calibracao += valor;
        Serial.print("Novo fator de calibração: ");
        Serial.println(fator_calibracao);
      } else {
        Serial.println("Valor inválido.");
      }

      deseja_ajustar = false;
      aguardando_valor = false;

      Serial.println("Deseja continuar ajustando? (s/n)");
    }
  }

  // Exibe o peso lido pela balança com o ajuste do fator de calibração.
  if (exibir){
    float medida = escala.get_units(30);

    Serial.print("Peso: ");
    Serial.print(medida, 2);
    Serial.println(" g");

    delay(1000);
  }
}
