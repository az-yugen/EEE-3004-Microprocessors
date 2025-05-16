/*
3004-MICROPROCESSORS. GROUP PROJECT.

220702706 - Ahmad Zameer Nazarı
220702705 - Ahmed Mahmoud Elsayed Hussein
210702725 - Fevzi Keshta
210702723 - Mohamed Shawki Eid Elsayed

Gesture Detection-Based Security System
*/

#include <LiquidCrystal.h>

// initializin LCD. pins in order: RS, E, D4, D5, D6, D7
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);  

// initializing LEDs
#define BLUE_LED 7
#define YELLOW_LED 8
#define GREEN_LED 9
#define RED_LED 10

// some states
bool blinkingYellow = false;
unsigned long lastBlink = 0;
bool yellowState = false;
String command = "";

// main setup
void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);

  pinMode(BLUE_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  resetAll();
}

// main loop
void loop() {
  // Blink yellow LED if active
  if (blinkingYellow && millis() - lastBlink > 500) {
    lastBlink = millis();
    yellowState = !yellowState;
    digitalWrite(YELLOW_LED, yellowState);
  } else if (!blinkingYellow) {
    digitalWrite(YELLOW_LED, LOW);
  }

  // Handle serial input
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      processCommand(command);
      command = "";
    } else {
      command += c;
    }
  }
}

// main function
void processCommand(String cmd) {
  cmd.trim();

  // Stage 0. Face detection
  if (cmd == "FACE_ON") {
    digitalWrite(BLUE_LED, HIGH);
    lcd.clear();
    lcd.print("FACE DETECTED");
  } else if (cmd == "FACE_OFF") {
    digitalWrite(BLUE_LED, LOW);

  // Stage 1. Wait for open hand
  } else if (cmd == "READY") {
    lcd.clear();
    lcd.print("PASSWORD?");
    blinkingYellow = true;

  // Stage 2. Password entry
  } else if (cmd.startsWith("FINGERS:")) {
    blinkingYellow = true;
    int sep = cmd.indexOf(',');
    if (sep > 0) {
      int count = cmd.substring(8, sep).toInt();
      int timeLeft = cmd.substring(sep + 1).toInt();
      lcd.clear();  
      lcd.print("Fingers: ");
      lcd.print(count);
      lcd.setCursor(0, 1);
      lcd.print("Hold: ");
      lcd.print(timeLeft);
      lcd.print("s");
    }

  // Result 
  } else if (cmd == "PASS_OK") {
    lcd.clear();
    lcd.print("Password correct!");
    blinkLED(GREEN_LED, 5);
    blinkingYellow = false;
    resetAll();
  } else if (cmd == "PASS_FAIL") {
    lcd.clear();
    lcd.print("Wrong password!");
    blinkLED(RED_LED, 5);
    delay(2000);
    lcd.clear();
    lcd.print("Show hand again");
    blinkingYellow = false;
  } else if (cmd == "RESET") {
    resetAll();
  }
}

// blinking LED function
void blinkLED(int pin, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(300);
    digitalWrite(pin, LOW);
    delay(200);
  }
}

// when idle
void resetAll() {
  digitalWrite(BLUE_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);

  lcd.clear();

  // dot animation on LCD display.
  while (true) {
    for (int i = 1; i <= 3; i++) {
      lcd.setCursor(0, 0);
      lcd.print("Waiting");
      for (int j = 0; j < i; j++) {
        lcd.print(".");
      }
      lcd.print("   ");

      delay(1500);

      if (Serial.available() > 0) {
        return;
      }
    }
  }
}

