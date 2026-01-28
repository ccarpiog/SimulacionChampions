import random
import pandas as pd
from itertools import combinations
from collections import Counter, defaultdict
from tqdm import tqdm  # Importar tqdm para la barra de progreso

# Parameter that controls how much strength affects results (0-10)
# 0 = all teams equally likely to win, 10 = strength dominates completely
IMPORTANCIA_FORTALEZA = 9  # Default middle value

# Number of Monte Carlo simulations to run
NUM_SIMULACIONES = 10000

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

            # Calculate probabilities based on strength difference and IMPORTANCIA_FORTALEZA
            factor = IMPORTANCIA_FORTALEZA / 10.0  # 0.0 to 1.0
            diff_fuerza = fuerza1 - fuerza2  # Can range from -50 to +50

            # Base probability (equal chances when factor=0)
            prob_base_ganar1 = 0.33

            # Strength-based probability (amplified by factor)
            # Normalize difference to -1 to +1 range, then apply power for amplification
            diff_normalizado = diff_fuerza / 50.0
            # Use sign-preserving power to amplify differences at high factor values
            if diff_normalizado >= 0:
                amplified_diff = diff_normalizado ** (1 / (1 + factor))
            else:
                amplified_diff = -(abs(diff_normalizado) ** (1 / (1 + factor)))
            # End of sign-preserving power calculation

            # Calculate strength-influenced win probability (0.05 to 0.95 range)
            prob_fuerza_ganar1 = 0.5 + 0.45 * amplified_diff
            prob_fuerza_ganar1 = max(0.05, min(0.95, prob_fuerza_ganar1))

            # Interpolate between base (equal) and strength-based probability
            prob_ganar1 = prob_base_ganar1 * (1 - factor) + prob_fuerza_ganar1 * factor

            # Draw probability decreases with strength difference and importance
            prob_empate = 0.34 * (1 - factor * abs(diff_fuerza) / 50)
            prob_empate = max(0.05, prob_empate)

            prob_ganar2 = 1 - prob_ganar1 - prob_empate
            prob_ganar2 = max(0.01, prob_ganar2)

            # Normalize to ensure they sum to 1
            total = prob_ganar1 + prob_empate + prob_ganar2
            prob_ganar1 /= total
            prob_empate /= total
            prob_ganar2 /= total

            resultado = random.choices(
                ['ganar1', 'empate', 'ganar2'],
                weights=[prob_ganar1, prob_empate, prob_ganar2],
                k=1
            )[0]

            # Generate goals based on result, strength difference, and IMPORTANCIA_FORTALEZA
            diff_fuerza_abs = abs(diff_fuerza) / 50.0  # 0 to 1

            if resultado == 'ganar1':
                # More goals for winner when strength gap is large and importance is high
                min_goles_ganador = int(1 + 3 * factor * diff_fuerza_abs)
                goles_equipo1 = random.randint(min_goles_ganador, min(5, min_goles_ganador + 3))
                max_goles_perdedor = max(0, 2 - int(2 * factor * diff_fuerza_abs))
                goles_equipo2 = random.randint(0, max_goles_perdedor)
            elif resultado == 'ganar2':
                # Same logic but reversed
                min_goles_ganador = int(1 + 3 * factor * diff_fuerza_abs)
                goles_equipo2 = random.randint(min_goles_ganador, min(5, min_goles_ganador + 3))
                max_goles_perdedor = max(0, 2 - int(2 * factor * diff_fuerza_abs))
                goles_equipo1 = random.randint(0, max_goles_perdedor)
            else:  # empate
                goles_equipo1 = goles_equipo2 = random.randint(0, 2)
            # End of goal generation based on result

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

# Ejecutar la simulación NUM_SIMULACIONES veces con una barra de progreso
resultados = defaultdict(list)

for _ in tqdm(range(NUM_SIMULACIONES)):
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