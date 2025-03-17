#include <LiquidCrystal.h>

#define LED_GREEN 8
#define LED_RED 9
#define BUZZER_PIN 10

unsigned long ti, ta, tiLcd, resetTime;
bool edoLed = false;
int cntLcd;
String nombre;
bool mostrandoMensaje = false;

LiquidCrystal lcd(2, 3, 4, 5, 6, 7);

void setup() {
  Serial.begin(9600);  
  lcd.begin(16, 2);    
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  lcd.setCursor(3, 0);
  lcd.print("Bienvenido");
}

void loop() {
  ta = millis();
  
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  

    if (command == "A") {
      digitalWrite(LED_GREEN, HIGH);
      digitalWrite(LED_RED, LOW);
      tone(BUZZER_PIN, 1000, 200);
    } 
    else if (command == "D") {
      digitalWrite(LED_GREEN, LOW);
      digitalWrite(LED_RED, HIGH);
      tone(BUZZER_PIN, 500, 1000);
    } 
    else if (command == "O") {
      digitalWrite(LED_GREEN, LOW);
      digitalWrite(LED_RED, LOW);
      digitalWrite(BUZZER_PIN, LOW);
    } 
    else if (command.startsWith("M:")) {
      nombre = command.substring(2);
      cntLcd = 0;
      mostrandoMensaje = true;
      resetTime = ta + 5000;
    }
  }

  if (mostrandoMensaje) {
    if (ta - tiLcd >= 200) {
      lcd.setCursor(0, 1);
      lcd.print(nombre.substring(cntLcd, cntLcd + 10) + "          ");
      cntLcd++;
      if (cntLcd > nombre.length() - 10) {
        cntLcd = 0;
      }
      tiLcd = ta;
    }

    if (ta >= resetTime) {
      lcd.setCursor(0, 1);
      lcd.print("                ");
      mostrandoMensaje = false;
    }
  }
}
