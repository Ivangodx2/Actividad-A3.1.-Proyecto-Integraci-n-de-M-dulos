from django.shortcuts import render
import os
import time

def index(request):
    return render(request, 'index.html')

def search(request):
    if request.method == 'GET':
        search = request.GET['search']
        
        # Obtén la ruta completa al archivo raiz_ind_inv.txt
        file_path = os.path.join(os.path.dirname(__file__), 'raiz_ind_inv.txt')

        # Lee el contenido del archivo especificando la codificación
        with open(file_path, 'r', encoding='utf-8') as file:
            dictionary_content = file.read()

        # Divide el contenido en líneas y procesa cada línea
        dictionary_lines = dictionary_content.split('\n')

        final_result = []
        result_found = False
        start_time = time.time()

        # Busca la palabra de búsqueda en el diccionario
        for line in dictionary_lines:
            # Suponiendo que cada línea comienza con la palabra y luego las URLs con frecuencia entre paréntesis
            parts = line.strip().split(')(')
            
            # Extrae la palabra
            word = parts[0].split(' ')[0]

            # Compara la palabra de búsqueda con la palabra en el diccionario (ignorando mayúsculas/minúsculas)
            if search.lower() == word.lower():
                print(f"Valor de search: {search}")
                # Extrae las URLs y frecuencias
                url_frequency_pairs = [pair.replace('(', '').replace(')', '') for pair in parts[1:]]
                
                # Agrega la palabra, la frecuencia y las URLs al resultado final
                for pair in url_frequency_pairs:
                    url, frequency = pair.split()
                    final_result.append((word, int(frequency), url))

        end_time = time.time()

        # Calcula el tiempo transcurrido
        elapsed_time = end_time - start_time
        final_result = sorted(final_result, key=lambda x: x[1], reverse=True)

        # Agrega el tiempo de ejecución al diccionario de contexto
        context = {
            'search_term': search,
            'final_result': final_result,
            'elapsed_time': elapsed_time
        }

        # Verifica si hay resultados antes de renderizar la plantilla
        if not final_result:
            context['no_results_message'] = f"No se encontraron resultados para '{search}'."

        return render(request, 'search.html', context)

    else:
        return render(request, 'search.html')
