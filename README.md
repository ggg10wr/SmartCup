# Relatório do Projeto: Microcontroladores ENG4033


### CONCEITO

O projeto desenvolvido pelo nosso grupo consiste em um porta-copos inteligente que monitora o consumo diário de água de até sete pessoas. Cada usuário é identificado por uma tag RFID, e um LED de cor personalizada acende sempre que o dispositivo é utilizado.
O porta-copos tem a função de lembrar o usuário da importância de beber água ao longo do dia. A medição do consumo é realizada por meio da pesagem do copo, calculando a diferença de sua massa antes e depois do usuário beber a água.


### COMPONENTES

Para utilizar o dispositivo, o usuário deve conectar a porta USB ao computador, estabelecendo a conexão entre a interface de cadastro de usuários e o Arduino. O computador precisa estar conectado à internet para garantir que os dados sejam atualizados na base de dados do MongoDB e do Grafana, além de permitir o envio de alertas via Telegram e a integração com o widget do Macrobot.

Os componentes necessários para montar o SmartCup são:

- Módulo RFID MFRC-522
- Célula de Carga / Sensor de Peso
- Módulo Conversor Amplificador HX711
- Módulo WS2812 LED RGB (24 bits)
- Resistor de 330 Ohms
- Protoboard
- Arduino Mega 2560


### INTERFACE COM O USUÁRIO

A interface com o usuário foi construída utilizando a biblioteca TkInter, e conta com quatro janelas principais:

1. Recepção: Exibe a lista de usuários cadastrados, com botões para editar a lista, cadastrar novos usuários ou visualizar o ranking de consumo.
2. Cadastro: O usuário fornece informações como nome, ID do Telegram, meta diária de consumo, tara do copo, tag RFID, URL do widget e a cor do LED desejada. Também é possível realizar a leitura automática da tara do copo e da tag RFID nesta tela.
3. Edição: Semelhante à janela de cadastro, mas destinada a usuários já cadastrados. Permite a atualização dos dados existentes.
4. Ranking: Exibe os três usuários que consumiram mais água no dia.


### ALERTAS AOS USUÁRIOS

A cada 2 horas, o sistema envia uma notificação pelo Telegram para cada usuário, lembrando-os de beber água e informando seu progresso em relação à meta diária. No final do dia, o widget é atualizado com base no atingimento da meta de consumo.


### IDENTIFICAÇÃO E MEDIÇÃO

Para identificar cada um dos sete usuários, seus copos possuem uma tag RFID fixada no fundo. Ao posicionar o copo na balança do dispositivo, a tag RFID é lida, acendendo o LED na cor personalizada do usuário. Além disso, o número de células acesas no LED representa o progresso em relação à meta de consumo.

A comunicação entre o Arduino e o código Python ocorre via porta serial, permitindo a atualização e modificação dos dados na base MongoDB.


### ESQUEMÁTICO DO CIRCUITO

O esquemático do circuito foi desenvolvido utilizando o software Fritzing.

![image](https://github.com/user-attachments/assets/23736810-9b34-4645-b6cb-b6d4a4eb3174)


