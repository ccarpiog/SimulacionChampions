import random
import pandas as pd
from itertools import combinations
from collections import Counter, defaultdict
from tqdm import tqdm  # Importar tqdm para la barra de progreso

# Definir una función que simule una temporada de 8 jornadas y devuelva la tabla de clasificación final
def simular_temporada():
    equipos = [f"Equipo {i+1}" for i in range(32)]

    # Asignar una fuerza a cada equipo (entre 1 y 100, donde 100 es el más fuerte)
    fuerzas = {equipo: random.randint(50, 100) for equipo in equipos}

    # Crear una tabla de clasificación vacía
    tabla = pd.DataFrame({
        'Equipo': equipos,
        'Puntos': [0] * 32,
        'Partidos Jugados': [0] * 32,
        'Ganados': [0] * 32,
        'Empatados': [0] * 32,
        'Perdidos': [0] * 32,
        'Goles a Favor': [0] * 32,
        'Goles en Contra': [0] * 32,
        'Diferencia de Goles': [0] * 32
    })

    # Generar el calendario de enfrentamientos (todos contra todos)
    def generar_calendario(equipos):
        partidos = list(combinations(equipos, 2))
        random.shuffle(partidos)  # Mezclar los partidos para que el calendario sea aleatorio
        calendario = []
        while partidos:
            jornada = []
            equipos_usados = set()
            partidos_restantes = []
            for partido in partidos:
                equipo1, equipo2 = partido
                if equipo1 not in equipos_usados and equipo2 not in equipos_usados:
                    jornada.append(partido)
                    equipos_usados.add(equipo1)
                    equipos_usados.add(equipo2)
                else:
                    partidos_restantes.append(partido)
            calendario.append(jornada)
            partidos = partidos_restantes
        return calendario

    # Simular una jornada con probabilidades ajustadas por la fuerza del equipo
    def simular_jornada(jornada):
        for partido in jornada:
            equipo1 = partido[0]
            equipo2 = partido[1]
            fuerza1 = fuerzas[equipo1]
            fuerza2 = fuerzas[equipo2]

            equipo1_idx = equipos.index(equipo1)
            equipo2_idx = equipos.index(equipo2)

            # Calcular probabilidades basadas en la diferencia de fuerzas
            prob_ganar1 = fuerza1 / (fuerza1 + fuerza2)
            prob_empate = 0.2 + 0.4 * (1 - abs(fuerza1 - fuerza2) / 100)  # más empate si fuerzas son similares
            prob_ganar2 = 1 - prob_ganar1 - prob_empate

            resultado = random.choices(
                ['ganar1', 'empate', 'ganar2'],
                weights=[prob_ganar1, prob_empate, prob_ganar2],
                k=1
            )[0]

            # Generar goles basados en el resultado
            goles_equipo1 = random.randint(0, 5) if resultado == 'ganar1' else random.randint(0, 2)
            goles_equipo2 = random.randint(0, 5) if resultado == 'ganar2' else random.randint(0, 2)

            if resultado == 'empate':
                goles_equipo1 = goles_equipo2 = random.randint(0, 2)

            # Actualizar la tabla
            tabla.loc[equipo1_idx, 'Partidos Jugados'] += 1
            tabla.loc[equipo2_idx, 'Partidos Jugados'] += 1
            tabla.loc[equipo1_idx, 'Goles a Favor'] += goles_equipo1
            tabla.loc[equipo1_idx, 'Goles en Contra'] += goles_equipo2
            tabla.loc[equipo2_idx, 'Goles a Favor'] += goles_equipo2
            tabla.loc[equipo2_idx, 'Goles en Contra'] += goles_equipo1
            tabla.loc[equipo1_idx, 'Diferencia de Goles'] = tabla.loc[equipo1_idx, 'Goles a Favor'] - tabla.loc[equipo1_idx, 'Goles en Contra']
            tabla.loc[equipo2_idx, 'Diferencia de Goles'] = tabla.loc[equipo2_idx, 'Goles a Favor'] - tabla.loc[equipo2_idx, 'Goles en Contra']

            if resultado == 'ganar1':
                tabla.loc[equipo1_idx, 'Ganados'] += 1
                tabla.loc[equipo2_idx, 'Perdidos'] += 1
                tabla.loc[equipo1_idx, 'Puntos'] += 3
            elif resultado == 'ganar2':
                tabla.loc[equipo2_idx, 'Ganados'] += 1
                tabla.loc[equipo1_idx, 'Perdidos'] += 1
                tabla.loc[equipo2_idx, 'Puntos'] += 3
            else:
                tabla.loc[equipo1_idx, 'Empatados'] += 1
                tabla.loc[equipo2_idx, 'Empatados'] += 1
                tabla.loc[equipo1_idx, 'Puntos'] += 1
                tabla.loc[equipo2_idx, 'Puntos'] += 1

        # Ordenar la tabla por puntos, diferencia de goles y goles a favor
        tabla.sort_values(by=['Puntos', 'Diferencia de Goles', 'Goles a Favor'], ascending=False, inplace=True)
        tabla.reset_index(drop=True, inplace=True)

    # Generar el calendario
    calendario = generar_calendario(equipos)

    # Simular las primeras 8 jornadas
    for jornada_num, jornada in enumerate(calendario[:8], start=1):
        simular_jornada(jornada)

    # Devolver la tabla de clasificación final
    return tabla

# Ejecutar la simulación 1000 veces con una barra de progreso
resultados = defaultdict(list)

for _ in tqdm(range(10000)):
    tabla_final = simular_temporada()
    for posicion in range(1, 33):
        puntos = tabla_final.loc[posicion - 1, 'Puntos']
        resultados[puntos].append(posicion)

# Crear la tabla de resultados
columnas = ["Octavo o Mejor (%)", "Vigésimo Cuarto o Mejor (%)", "Vigésimo Quinto o Peor (%)"]
tabla_resultados = pd.DataFrame(0.0, index=range(25), columns=columnas)

# Llenar la tabla con los porcentajes redondeados a un decimal
for puntos, posiciones in resultados.items():
    total_simulaciones = len(posiciones)
    octavo_o_mejor = round(sum(1 for pos in posiciones if pos <= 8) / total_simulaciones * 100, 1)
    vigesimo_cuarto_o_mejor = round(sum(1 for pos in posiciones if pos <= 24) / total_simulaciones * 100, 1)
    vigesimo_quinto_o_peor = round(sum(1 for pos in posiciones if pos > 24) / total_simulaciones * 100, 1)
    
    if puntos <= 24:  # Solo llenamos la tabla para puntos entre 0 y 24
        tabla_resultados.loc[puntos, "Octavo o Mejor (%)"] = octavo_o_mejor
        tabla_resultados.loc[puntos, "Vigésimo Cuarto o Mejor (%)"] = vigesimo_cuarto_o_mejor
        tabla_resultados.loc[puntos, "Vigésimo Quinto o Peor (%)"] = vigesimo_quinto_o_peor

# Mostrar la tabla de resultados
print(tabla_resultados)