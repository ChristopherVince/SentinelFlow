#include <Modulino.h>

ModulinoPixels leds;
ModulinoVibro vibro;

void setup() {
  Serial.begin(115200);
  Modulino.begin();
  leds.begin();
  vibro.begin();

  // Azul = sistema listo
  for (int i = 0; i < 8; i++) {
    leds.set(i, BLUE, 25);
  }
  leds.show();
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "NORMAL") {
      for (int i = 0; i < 8; i++) leds.set(i, GREEN, 25);
      leds.show();
      vibro.off();

    } else if (cmd == "WARNING") {
      for (int i = 0; i < 8; i++) leds.set(i, YELLOW, 25);
      leds.show();
      vibro.on(300);  // vibra 300ms

    } else if (cmd == "DANGER") {
      for (int i = 0; i < 8; i++) leds.set(i, RED, 25);
      leds.show();
      vibro.on(2000); // vibra 2 segundos
    }
  }
}