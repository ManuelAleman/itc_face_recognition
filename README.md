# Proyecto de Reconocimiento Facial con Prisma y PostgreSQL para el Instituto Tecnologico de Culiacan

Este proyecto configura un entorno de desarrollo utilizando **Docker**, **Python** y **Prisma** con **PostgreSQL**. Sigue los pasos a continuación para configurar y ejecutar el proyecto.

## Requisitos

- Docker
- Python 3
- Prisma
- PostgreSQL
---

## 1. Configuración del entorno

### 1.1. Iniciar contenedor Docker

Primero, debes levantar los servicios definidos en el archivo `docker-compose.yml` utilizando el siguiente comando:

```bash
docker compose up -d
```

## 2. Crear y activar el entorno virtual
### 2.1. Crear el entorno virtural
```bash
python3 -m venv face_recognition
```
### 2.2. Levantar el entorno virtual
```bash
source face_recognition/bin/activate
```

## 3. Instalar las dependencias necesarias
```bash
pip install face_recognition opencv-python python-dotenv setuptools openpyxl pandas
pip install -U prisma
```
## 4. Repositorio con modelos de detección
### 4.1 Clonar el repositorio
```bash
git clone https://github.com/ageitgey/face_recognition_models.git
```
### 4.2 Ejecutar setup.py
```bash
python face_recognition_models/setup.py
```
## 5. Inicializar la base de datos
```bash
prisma init
prisma db push
prisma db pull
```
## 6. Verificar la base de datos en docker
### 6.1 Acceder al contenedor de Docker
```bash
docker exec -it <container-name> bash
```
### 6.2 Conectarse a la base de datos PostgreSQL
```bash
psql -U admin -d <database-name>
```

## 7. Configura salida al arduino
```bash
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

```
