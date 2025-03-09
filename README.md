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
docker-compose up -d
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
