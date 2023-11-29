# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 02:34:44 2023

@author: trucs
"""
import os
import re
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from concurrent.futures import ThreadPoolExecutor

nltk.download("stopwords")

url_pattern = r'http[s]?://(?!.*(?:google|bing))(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

carpeta_logs = 'logs'
archivo_salida = 'output.txt'
stop_words = set(stopwords.words("spanish"))
stemmer = SnowballStemmer("spanish")

# Función para extraer texto del cuerpo de una URL y contar las palabras sin "stop words"
def contar_palabras_en_url(url):
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            body = soup.find('body')
            if body:
                body_text = body.get_text()
                body_text = re.sub(r'[^A-Za-z0-9\s\w]+', ' ', body_text)
                body_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', body_text)
                body_text = body_text.replace('\n', ' ')
                words = re.findall(r'\w+(?:[A-Z][a-z]*)*', body_text.lower())
                words_without_stopwords = [word for word in words if word not in stop_words]
                stemmed_words = [stemmer.stem(word) for word in words_without_stopwords]
                word_count = {}
                for word in stemmed_words:
                    if word in word_count:
                        word_count[word] += 1
                    else:
                        word_count[word] = 1
                return word_count
            else:
                print(f"No se encontró el cuerpo (body) en la URL: {url}")
                return {}
        else:
            print(f"La URL no tiene un estado 200: {url}")
            return {}
    except Exception as e:
        print(f"Error al procesar la URL: {url}")
        return {}

# Diccionario para almacenar las palabras y sus frecuencias en cada URL
palabras_frecuencias_por_raiz = {}

# Lista de URLs a procesar
urls_a_procesar = []

# Iterar sobre los archivos en la carpeta de logs y recopilar URLs
for archivo_entrada in os.listdir(carpeta_logs):
    if archivo_entrada.endswith('.log'):
        archivo_entrada = os.path.join(carpeta_logs, archivo_entrada)
        with open(archivo_entrada, 'r', encoding="utf-8") as file:
            content = file.read()
            urls = re.findall(url_pattern, content)
            urls_a_procesar.extend(urls)

# Procesar las URLs en paralelo
with ThreadPoolExecutor(max_workers=4) as executor:  # Puedes ajustar el número de hilos según tu CPU
    resultados = list(executor.map(contar_palabras_en_url, urls_a_procesar))

# Agregar los resultados al diccionario
for i, word_count in enumerate(resultados):
    url = urls_a_procesar[i]
    for word, count in word_count.items():
        if word in palabras_frecuencias_por_raiz:
            palabras_frecuencias_por_raiz[word].append((url, count))
        else:
            palabras_frecuencias_por_raiz[word] = [(url, count)]

# Guardar los resultados
with open(archivo_salida, 'a', encoding="utf-8") as output_file:
    for word, url_counts in palabras_frecuencias_por_raiz.items():
        output_file.write(f"[Raíz: {word}:")
        for url, count in url_counts:
            output_file.write(f" ({url}, Frecuencia: {count})")
        output_file.write("]\n")

print("Proceso completado")
