"""
Laboratorio 7 - Optimizacion heuristica de funciones.

Este script implementa varios algoritmos de optimizacion de trayectoria unica
para aproximar el minimo de las funciones ocultas de `retos_optimizacion.py`.
"""

import math
import sys
from pathlib import Path

import numpy as np


LOWER_BOUND = -10.0
UPPER_BOUND = 10.0
DIMENSIONS = 10
TOTAL_BUDGET_PER_RUN = 10_000
GLOBAL_RANDOM_SEED = 1


class GlobalBudgetEvaluator:
    """
    Encapsula una funcion objetivo y controla un presupuesto global de llamadas.
    """

    def __init__(self, objective_function, lower_bound, upper_bound, max_evaluations):
        self.objective_function = objective_function
        self.lower_bound = float(lower_bound)
        self.upper_bound = float(upper_bound)
        self.max_evaluations = int(max_evaluations)
        self.used_evaluations = 0

    def can_evaluate(self):
        return self.used_evaluations < self.max_evaluations

    def remaining_evaluations(self):
        return self.max_evaluations - self.used_evaluations

    def evaluations_used(self):
        return self.used_evaluations

    def evaluate(self, point):
        if not self.can_evaluate():
            return None

        clipped_point = clip_point_to_bounds(point, self.lower_bound, self.upper_bound)
        point_list = []

        index = 0
        while index < len(clipped_point):
            point_list.append(float(clipped_point[index]))
            index = index + 1

        function_value = self.objective_function.evaluar(point_list)
        self.used_evaluations = self.used_evaluations + 1
        return float(function_value)


class RunBudgetEvaluator:
    """
    Crea un presupuesto local por ejecucion encima de otro evaluador.
    """

    def __init__(self, base_evaluator, local_budget):
        self.base_evaluator = base_evaluator
        self.local_budget = int(local_budget)
        self.used_local_evaluations = 0

    def can_evaluate(self):
        return self.remaining_evaluations() > 0

    def remaining_evaluations(self):
        local_remaining = self.local_budget - self.used_local_evaluations
        base_remaining = self.base_evaluator.remaining_evaluations()

        if local_remaining < base_remaining:
            return local_remaining

        return base_remaining

    def evaluations_used(self):
        return self.used_local_evaluations

    def evaluate(self, point):
        if not self.can_evaluate():
            return None

        value = self.base_evaluator.evaluate(point)

        if value is None:
            return None

        self.used_local_evaluations = self.used_local_evaluations + 1
        return value


class ExperimentResult:
    """
    Estructura simple para almacenar resultados de un experimento.
    """

    def __init__(self):
        self.function_name = ""
        self.algorithm_name = ""
        self.best_value = float("inf")
        self.best_point = np.zeros(DIMENSIONS, dtype=float)
        self.selected_parameters = {}
        self.total_evaluations = 0
        self.tuning_evaluations = 0
        self.final_evaluations = 0


def get_parameter(parameters, name, default_value):
    if parameters is None:
        return default_value

    if name in parameters:
        return parameters[name]

    return default_value


def copy_parameters(parameters):
    copied = {}

    for key in parameters:
        copied[key] = parameters[key]

    return copied


def clip_point_to_bounds(point, lower_bound, upper_bound):
    clipped = np.array(point, dtype=float)

    index = 0
    while index < len(clipped):
        if clipped[index] < lower_bound:
            clipped[index] = lower_bound
        elif clipped[index] > upper_bound:
            clipped[index] = upper_bound
        index = index + 1

    return clipped


def create_random_point(random_generator, dimensions, lower_bound, upper_bound):
    point = np.zeros(dimensions, dtype=float)

    index = 0
    while index < dimensions:
        point[index] = random_generator.uniform(lower_bound, upper_bound)
        index = index + 1

    return point


def perturb_point_uniform(point, random_generator, step_size, lower_bound, upper_bound):
    candidate = np.array(point, dtype=float)
    index = 0

    while index < len(candidate):
        delta = random_generator.uniform(-step_size, step_size)
        candidate[index] = candidate[index] + delta
        index = index + 1

    return clip_point_to_bounds(candidate, lower_bound, upper_bound)


def perturb_point_gaussian(point, random_generator, step_size, lower_bound, upper_bound):
    candidate = np.array(point, dtype=float)
    index = 0

    while index < len(candidate):
        delta = random_generator.normal(0.0, step_size)
        candidate[index] = candidate[index] + delta
        index = index + 1

    return clip_point_to_bounds(candidate, lower_bound, upper_bound)


def build_point_signature(point, decimals):
    signature_values = []

    index = 0
    while index < len(point):
        signature_values.append(round(float(point[index]), decimals))
        index = index + 1

    return tuple(signature_values)


def is_signature_in_tabu(signature, tabu_list):
    index = 0

    while index < len(tabu_list):
        if tabu_list[index] == signature:
            return True
        index = index + 1

    return False


def build_parameter_combinations(parameter_grid):
    keys = []
    combinations = []

    for key in parameter_grid:
        keys.append(key)

    if len(keys) == 0:
        combinations.append({})
        return combinations

    def backtrack(key_index, current_combination):
        if key_index >= len(keys):
            combinations.append(copy_parameters(current_combination))
            return

        current_key = keys[key_index]
        values = parameter_grid[current_key]

        value_index = 0
        while value_index < len(values):
            current_combination[current_key] = values[value_index]
            backtrack(key_index + 1, current_combination)
            value_index = value_index + 1

        if current_key in current_combination:
            del current_combination[current_key]

    backtrack(0, {})
    return combinations


def algorithm_random_search(
    evaluator, random_generator, dimensions, lower_bound, upper_bound, parameters
):
    best_point = np.zeros(dimensions, dtype=float)
    best_value = float("inf")

    while evaluator.can_evaluate():
        candidate = create_random_point(
            random_generator, dimensions, lower_bound, upper_bound
        )
        candidate_value = evaluator.evaluate(candidate)

        if candidate_value is None:
            break

        if candidate_value < best_value:
            best_value = candidate_value
            best_point = np.array(candidate, dtype=float)

    return best_point, best_value


def algorithm_hill_climbing(
    evaluator, random_generator, dimensions, lower_bound, upper_bound, parameters
):
    initial_step = float(get_parameter(parameters, "initial_step", 1.5))
    minimum_step = float(get_parameter(parameters, "minimum_step", 0.02))
    shrink_factor = float(get_parameter(parameters, "shrink_factor", 0.6))
    neighbors_per_iteration = int(get_parameter(parameters, "neighbors_per_iteration", 30))

    current_point = create_random_point(
        random_generator, dimensions, lower_bound, upper_bound
    )
    current_value = evaluator.evaluate(current_point)

    if current_value is None:
        return np.zeros(dimensions, dtype=float), float("inf")

    best_point = np.array(current_point, dtype=float)
    best_value = float(current_value)
    step_size = initial_step

    while evaluator.can_evaluate():
        if step_size < minimum_step:
            break

        best_neighbor_point = None
        best_neighbor_value = current_value

        neighbor_index = 0
        while neighbor_index < neighbors_per_iteration and evaluator.can_evaluate():
            candidate = perturb_point_uniform(
                current_point, random_generator, step_size, lower_bound, upper_bound
            )
            candidate_value = evaluator.evaluate(candidate)

            if candidate_value is None:
                break

            if candidate_value < best_neighbor_value:
                best_neighbor_value = candidate_value
                best_neighbor_point = np.array(candidate, dtype=float)

            neighbor_index = neighbor_index + 1

        if best_neighbor_point is None:
            step_size = step_size * shrink_factor
            continue

        current_point = best_neighbor_point
        current_value = best_neighbor_value

        if current_value < best_value:
            best_value = current_value
            best_point = np.array(current_point, dtype=float)

    return best_point, best_value


def algorithm_simulated_annealing(
    evaluator, random_generator, dimensions, lower_bound, upper_bound, parameters
):
    initial_temperature = float(get_parameter(parameters, "initial_temperature", 20.0))
    cooling_rate = float(get_parameter(parameters, "cooling_rate", 0.995))
    step_size = float(get_parameter(parameters, "step_size", 1.0))
    minimum_temperature = float(get_parameter(parameters, "minimum_temperature", 0.001))

    current_point = create_random_point(
        random_generator, dimensions, lower_bound, upper_bound
    )
    current_value = evaluator.evaluate(current_point)

    if current_value is None:
        return np.zeros(dimensions, dtype=float), float("inf")

    best_point = np.array(current_point, dtype=float)
    best_value = float(current_value)
    temperature = initial_temperature

    while evaluator.can_evaluate():
        candidate = perturb_point_gaussian(
            current_point, random_generator, step_size, lower_bound, upper_bound
        )
        candidate_value = evaluator.evaluate(candidate)

        if candidate_value is None:
            break

        accept_candidate = False
        delta = candidate_value - current_value

        if delta <= 0:
            accept_candidate = True
        else:
            effective_temperature = temperature

            if effective_temperature < minimum_temperature:
                effective_temperature = minimum_temperature

            acceptance_probability = math.exp(-delta / effective_temperature)
            random_number = random_generator.uniform(0.0, 1.0)

            if random_number < acceptance_probability:
                accept_candidate = True

        if accept_candidate:
            current_point = np.array(candidate, dtype=float)
            current_value = candidate_value

            if current_value < best_value:
                best_value = current_value
                best_point = np.array(current_point, dtype=float)

        temperature = temperature * cooling_rate

        if temperature < minimum_temperature:
            temperature = minimum_temperature

    return best_point, best_value


def algorithm_coordinate_search(
    evaluator, random_generator, dimensions, lower_bound, upper_bound, parameters
):
    initial_step = float(get_parameter(parameters, "initial_step", 1.5))
    minimum_step = float(get_parameter(parameters, "minimum_step", 0.02))
    reduction_factor = float(get_parameter(parameters, "reduction_factor", 0.6))

    current_point = create_random_point(
        random_generator, dimensions, lower_bound, upper_bound
    )
    current_value = evaluator.evaluate(current_point)

    if current_value is None:
        return np.zeros(dimensions, dtype=float), float("inf")

    best_point = np.array(current_point, dtype=float)
    best_value = float(current_value)
    step_size = initial_step

    while evaluator.can_evaluate():
        if step_size < minimum_step:
            break

        improved = False
        iteration_best_point = np.array(current_point, dtype=float)
        iteration_best_value = current_value

        dimension_index = 0
        while dimension_index < dimensions and evaluator.can_evaluate():
            direction = -1

            while direction <= 1 and evaluator.can_evaluate():
                if direction == 0:
                    direction = direction + 1
                    continue

                candidate = np.array(current_point, dtype=float)
                candidate[dimension_index] = (
                    candidate[dimension_index] + direction * step_size
                )
                candidate = clip_point_to_bounds(candidate, lower_bound, upper_bound)
                candidate_value = evaluator.evaluate(candidate)

                if candidate_value is None:
                    break

                if candidate_value < iteration_best_value:
                    iteration_best_value = candidate_value
                    iteration_best_point = np.array(candidate, dtype=float)
                    improved = True

                direction = direction + 1

            dimension_index = dimension_index + 1

        if improved:
            current_point = iteration_best_point
            current_value = iteration_best_value

            if current_value < best_value:
                best_value = current_value
                best_point = np.array(current_point, dtype=float)
        else:
            step_size = step_size * reduction_factor

    return best_point, best_value


def algorithm_tabu_search(
    evaluator, random_generator, dimensions, lower_bound, upper_bound, parameters
):
    step_size = float(get_parameter(parameters, "step_size", 1.5))
    minimum_step = float(get_parameter(parameters, "minimum_step", 0.2))
    step_decay = float(get_parameter(parameters, "step_decay", 0.998))
    neighbors_per_iteration = int(get_parameter(parameters, "neighbors_per_iteration", 40))
    tabu_tenure = int(get_parameter(parameters, "tabu_tenure", 30))
    signature_decimals = int(get_parameter(parameters, "signature_decimals", 2))

    current_point = create_random_point(
        random_generator, dimensions, lower_bound, upper_bound
    )
    current_value = evaluator.evaluate(current_point)

    if current_value is None:
        return np.zeros(dimensions, dtype=float), float("inf")

    best_point = np.array(current_point, dtype=float)
    best_value = float(current_value)
    tabu_list = []

    current_signature = build_point_signature(current_point, signature_decimals)
    tabu_list.append(current_signature)

    while evaluator.can_evaluate():
        best_candidate_point = None
        best_candidate_value = float("inf")
        best_candidate_signature = None

        neighbor_index = 0
        while neighbor_index < neighbors_per_iteration and evaluator.can_evaluate():
            candidate = perturb_point_uniform(
                current_point, random_generator, step_size, lower_bound, upper_bound
            )
            candidate_signature = build_point_signature(candidate, signature_decimals)
            candidate_value = evaluator.evaluate(candidate)

            if candidate_value is None:
                break

            candidate_is_tabu = is_signature_in_tabu(candidate_signature, tabu_list)
            aspiration_satisfied = candidate_value < best_value

            if candidate_is_tabu and not aspiration_satisfied:
                neighbor_index = neighbor_index + 1
                continue

            if candidate_value < best_candidate_value:
                best_candidate_point = np.array(candidate, dtype=float)
                best_candidate_value = candidate_value
                best_candidate_signature = candidate_signature

            neighbor_index = neighbor_index + 1

        if best_candidate_point is None:
            step_size = step_size * step_decay

            if step_size < minimum_step:
                step_size = minimum_step

            continue

        current_point = best_candidate_point
        current_value = best_candidate_value

        if current_value < best_value:
            best_value = current_value
            best_point = np.array(current_point, dtype=float)

        tabu_list.append(best_candidate_signature)

        if len(tabu_list) > tabu_tenure:
            del tabu_list[0]

        step_size = step_size * step_decay

        if step_size < minimum_step:
            step_size = minimum_step

    return best_point, best_value


def algorithm_random_restart_hill_climbing(
    evaluator, random_generator, dimensions, lower_bound, upper_bound, parameters
):
    restart_budget = int(get_parameter(parameters, "restart_budget", 350))
    local_initial_step = float(get_parameter(parameters, "initial_step", 1.5))
    local_minimum_step = float(get_parameter(parameters, "minimum_step", 0.02))
    local_shrink_factor = float(get_parameter(parameters, "shrink_factor", 0.6))
    local_neighbors = int(get_parameter(parameters, "neighbors_per_iteration", 30))

    local_hill_parameters = {
        "initial_step": local_initial_step,
        "minimum_step": local_minimum_step,
        "shrink_factor": local_shrink_factor,
        "neighbors_per_iteration": local_neighbors,
    }

    best_point = np.zeros(dimensions, dtype=float)
    best_value = float("inf")

    while evaluator.can_evaluate():
        budget_for_restart = restart_budget
        remaining_budget = evaluator.remaining_evaluations()

        if budget_for_restart > remaining_budget:
            budget_for_restart = remaining_budget

        if budget_for_restart <= 0:
            break

        restart_evaluator = RunBudgetEvaluator(evaluator, budget_for_restart)
        restart_point, restart_value = algorithm_hill_climbing(
            restart_evaluator,
            random_generator,
            dimensions,
            lower_bound,
            upper_bound,
            local_hill_parameters,
        )

        if restart_value < best_value:
            best_value = restart_value
            best_point = np.array(restart_point, dtype=float)

    return best_point, best_value


def execute_algorithm_with_grid_search(
    algorithm_definition, function_name, function_instance, random_generator
):
    result = ExperimentResult()
    result.function_name = function_name
    result.algorithm_name = algorithm_definition["name"]

    if hasattr(function_instance, "reiniciar_contador"):
        function_instance.reiniciar_contador()

    global_evaluator = GlobalBudgetEvaluator(
        function_instance, LOWER_BOUND, UPPER_BOUND, TOTAL_BUDGET_PER_RUN
    )

    algorithm_function = algorithm_definition["function"]
    parameter_grid = algorithm_definition["parameter_grid"]
    default_parameters = algorithm_definition["default_parameters"]
    tuning_fraction = float(algorithm_definition["tuning_fraction"])
    minimum_trial_budget = int(algorithm_definition["minimum_trial_budget"])
    minimum_final_budget = int(algorithm_definition["minimum_final_budget"])

    parameter_combinations = build_parameter_combinations(parameter_grid)

    if len(parameter_combinations) == 0:
        parameter_combinations.append(copy_parameters(default_parameters))

    best_parameters = copy_parameters(default_parameters)
    best_point_from_tuning = np.zeros(DIMENSIONS, dtype=float)
    best_value_from_tuning = float("inf")

    tuning_budget = int(TOTAL_BUDGET_PER_RUN * tuning_fraction)
    maximum_tuning_budget = TOTAL_BUDGET_PER_RUN - minimum_final_budget

    if tuning_budget > maximum_tuning_budget:
        tuning_budget = maximum_tuning_budget

    if tuning_budget < 0:
        tuning_budget = 0

    tuning_evaluations = 0
    base_trial_budget = 0

    if len(parameter_combinations) > 0:
        base_trial_budget = int(tuning_budget / len(parameter_combinations))

    if base_trial_budget < minimum_trial_budget:
        base_trial_budget = minimum_trial_budget

    combination_index = 0

    while combination_index < len(parameter_combinations):
        if tuning_budget <= 0:
            break

        if tuning_evaluations >= tuning_budget:
            break

        remaining_tuning_budget = tuning_budget - tuning_evaluations
        remaining_global_budget = global_evaluator.remaining_evaluations()
        available_now = remaining_global_budget - minimum_final_budget

        if available_now <= 0:
            break

        trial_budget = base_trial_budget

        if trial_budget > remaining_tuning_budget:
            trial_budget = remaining_tuning_budget

        if trial_budget > available_now:
            trial_budget = available_now

        if trial_budget <= 0:
            break

        trial_parameters = parameter_combinations[combination_index]
        trial_evaluator = RunBudgetEvaluator(global_evaluator, trial_budget)
        trial_point, trial_value = algorithm_function(
            trial_evaluator,
            random_generator,
            DIMENSIONS,
            LOWER_BOUND,
            UPPER_BOUND,
            trial_parameters,
        )

        tuning_evaluations = tuning_evaluations + trial_evaluator.evaluations_used()

        if trial_value < best_value_from_tuning:
            best_value_from_tuning = trial_value
            best_point_from_tuning = np.array(trial_point, dtype=float)
            best_parameters = copy_parameters(trial_parameters)

        combination_index = combination_index + 1

    final_budget = global_evaluator.remaining_evaluations()
    final_evaluations = 0
    best_point_from_final = np.zeros(DIMENSIONS, dtype=float)
    best_value_from_final = float("inf")

    if final_budget > 0:
        final_evaluator = RunBudgetEvaluator(global_evaluator, final_budget)
        best_point_from_final, best_value_from_final = algorithm_function(
            final_evaluator,
            random_generator,
            DIMENSIONS,
            LOWER_BOUND,
            UPPER_BOUND,
            best_parameters,
        )
        final_evaluations = final_evaluator.evaluations_used()

    result.best_point = np.array(best_point_from_final, dtype=float)
    result.best_value = best_value_from_final

    if best_value_from_tuning < result.best_value:
        result.best_value = best_value_from_tuning
        result.best_point = np.array(best_point_from_tuning, dtype=float)

    result.selected_parameters = copy_parameters(best_parameters)
    result.tuning_evaluations = tuning_evaluations
    result.final_evaluations = final_evaluations
    result.total_evaluations = global_evaluator.evaluations_used()

    return result


def get_best_value_for_sort(result):
    return result.best_value


def format_parameters(parameters):
    keys = []

    for key in parameters:
        keys.append(key)

    if len(keys) == 0:
        return "(sin parametros)"

    keys.sort()
    parts = []

    index = 0
    while index < len(keys):
        key = keys[index]
        parts.append(str(key) + "=" + str(parameters[key]))
        index = index + 1

    return ", ".join(parts)


def format_point(point):
    values = []
    index = 0

    while index < len(point):
        values.append(f"{float(point[index]):.4f}")
        index = index + 1

    return "[" + ", ".join(values) + "]"


def print_results(results):
    function_names = []
    index = 0

    while index < len(results):
        current_function_name = results[index].function_name

        if current_function_name not in function_names:
            function_names.append(current_function_name)

        index = index + 1

    print("\n" + "=" * 110)
    print("COMPARATIVA DE ALGORITMOS DE OPTIMIZACION (TRAYECTORIA UNICA)")
    print("=" * 110)
    print(
        "Presupuesto por ejecucion: "
        + str(TOTAL_BUDGET_PER_RUN)
        + " evaluaciones (incluye grid-search y fase final)."
    )
    print(
        "Intervalo de busqueda: ["
        + str(LOWER_BOUND)
        + ", "
        + str(UPPER_BOUND)
        + "], dimensiones="
        + str(DIMENSIONS)
        + "."
    )

    function_index = 0
    while function_index < len(function_names):
        function_name = function_names[function_index]
        function_results = []

        result_index = 0
        while result_index < len(results):
            if results[result_index].function_name == function_name:
                function_results.append(results[result_index])
            result_index = result_index + 1

        function_results = sorted(function_results, key=get_best_value_for_sort)

        print("\n" + "-" * 110)
        print("Funcion:", function_name)
        print("-" * 110)
        print(
            f"{'Rank':<5}{'Algoritmo':<34}{'Mejor valor':>16}"
            f"{'Eval total':>14}{'Eval tuning':>14}{'Eval final':>14}"
        )

        rank = 1
        local_index = 0
        while local_index < len(function_results):
            item = function_results[local_index]
            print(
                f"{rank:<5}{item.algorithm_name:<34}{item.best_value:>16.8f}"
                f"{item.total_evaluations:>14}{item.tuning_evaluations:>14}{item.final_evaluations:>14}"
            )
            rank = rank + 1
            local_index = local_index + 1

        winner = function_results[0]
        print("Mejor algoritmo para", function_name + ":", winner.algorithm_name)
        print("Parametros elegidos:", format_parameters(winner.selected_parameters))
        print("Mejor punto encontrado:", format_point(winner.best_point))

        function_index = function_index + 1

    print("\n" + "=" * 110)


def save_results_csv(results, output_path):
    header = (
        "function_name,algorithm_name,best_value,total_evaluations,"
        "tuning_evaluations,final_evaluations,selected_parameters,best_point\n"
    )

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(header)

        index = 0
        while index < len(results):
            item = results[index]
            parameters_text = format_parameters(item.selected_parameters).replace(",", ";")
            point_text = format_point(item.best_point).replace(",", ";")

            line = (
                f"{item.function_name},{item.algorithm_name},{item.best_value},"
                f"{item.total_evaluations},{item.tuning_evaluations},{item.final_evaluations},"
                f"\"{parameters_text}\",\"{point_text}\"\n"
            )

            output_file.write(line)
            index = index + 1


def load_retos_module():
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    retos_path = project_root / "data" / "win_314" / "dist"

    if not retos_path.exists():
        raise FileNotFoundError(
            "No se encontro la carpeta con el modulo codificado en: " + str(retos_path)
        )

    sys.path.insert(0, str(retos_path))
    import retos_optimizacion as reto  # pylint: disable=import-outside-toplevel

    return reto


def build_algorithm_catalog():
    algorithms = []

    algorithms.append(
        {
            "name": "Random Search",
            "function": algorithm_random_search,
            "parameter_grid": {},
            "default_parameters": {},
            "tuning_fraction": 0.0,
            "minimum_trial_budget": 0,
            "minimum_final_budget": TOTAL_BUDGET_PER_RUN,
        }
    )

    algorithms.append(
        {
            "name": "Hill Climbing",
            "function": algorithm_hill_climbing,
            "parameter_grid": {
                "initial_step": [2.0, 1.2],
                "minimum_step": [0.03],
                "shrink_factor": [0.5, 0.7],
                "neighbors_per_iteration": [20, 40],
            },
            "default_parameters": {
                "initial_step": 1.5,
                "minimum_step": 0.03,
                "shrink_factor": 0.6,
                "neighbors_per_iteration": 30,
            },
            "tuning_fraction": 0.30,
            "minimum_trial_budget": 220,
            "minimum_final_budget": 3500,
        }
    )

    algorithms.append(
        {
            "name": "Simulated Annealing",
            "function": algorithm_simulated_annealing,
            "parameter_grid": {
                "initial_temperature": [10.0, 30.0],
                "cooling_rate": [0.99, 0.995],
                "step_size": [0.8, 1.5],
                "minimum_temperature": [0.001],
            },
            "default_parameters": {
                "initial_temperature": 20.0,
                "cooling_rate": 0.995,
                "step_size": 1.0,
                "minimum_temperature": 0.001,
            },
            "tuning_fraction": 0.30,
            "minimum_trial_budget": 220,
            "minimum_final_budget": 3500,
        }
    )

    algorithms.append(
        {
            "name": "Coordinate Search",
            "function": algorithm_coordinate_search,
            "parameter_grid": {
                "initial_step": [2.0, 1.2],
                "minimum_step": [0.02],
                "reduction_factor": [0.5, 0.7],
            },
            "default_parameters": {
                "initial_step": 1.5,
                "minimum_step": 0.02,
                "reduction_factor": 0.6,
            },
            "tuning_fraction": 0.30,
            "minimum_trial_budget": 300,
            "minimum_final_budget": 3500,
        }
    )

    algorithms.append(
        {
            "name": "Tabu Search",
            "function": algorithm_tabu_search,
            "parameter_grid": {
                "step_size": [1.0, 2.0],
                "minimum_step": [0.2],
                "step_decay": [0.997, 0.999],
                "neighbors_per_iteration": [30, 50],
                "tabu_tenure": [20, 40],
                "signature_decimals": [2],
            },
            "default_parameters": {
                "step_size": 1.5,
                "minimum_step": 0.2,
                "step_decay": 0.998,
                "neighbors_per_iteration": 40,
                "tabu_tenure": 30,
                "signature_decimals": 2,
            },
            "tuning_fraction": 0.30,
            "minimum_trial_budget": 120,
            "minimum_final_budget": 3500,
        }
    )

    algorithms.append(
        {
            "name": "Random Restart Hill",
            "function": algorithm_random_restart_hill_climbing,
            "parameter_grid": {
                "restart_budget": [250, 450],
                "initial_step": [1.2, 2.0],
                "minimum_step": [0.03],
                "shrink_factor": [0.6],
                "neighbors_per_iteration": [20, 35],
            },
            "default_parameters": {
                "restart_budget": 350,
                "initial_step": 1.5,
                "minimum_step": 0.03,
                "shrink_factor": 0.6,
                "neighbors_per_iteration": 30,
            },
            "tuning_fraction": 0.30,
            "minimum_trial_budget": 200,
            "minimum_final_budget": 3500,
        }
    )

    return algorithms


def run_full_experiment():
    np.random.seed(GLOBAL_RANDOM_SEED)
    reto = load_retos_module()
    algorithms = build_algorithm_catalog()

    functions = [
        ("Funcion_1", reto.Funcion_1),
        ("Funcion_2", reto.Funcion_2),
        ("Funcion_3", reto.Funcion_3),
        ("Funcion_4", reto.Funcion_4),
    ]

    results = []

    function_index = 0
    while function_index < len(functions):
        function_name = functions[function_index][0]
        function_constructor = functions[function_index][1]

        algorithm_index = 0
        while algorithm_index < len(algorithms):
            algorithm_definition = algorithms[algorithm_index]
            run_seed = (
                GLOBAL_RANDOM_SEED
                + function_index * 100
                + algorithm_index * 1000
            )
            random_generator = np.random.RandomState(run_seed)
            function_instance = function_constructor()

            result = execute_algorithm_with_grid_search(
                algorithm_definition,
                function_name,
                function_instance,
                random_generator,
            )
            results.append(result)

            algorithm_index = algorithm_index + 1
        function_index = function_index + 1

    return results


def main():
    results = run_full_experiment()
    print_results(results)

    output_csv = Path(__file__).resolve().parent / "resultados_lab7.csv"
    save_results_csv(results, output_csv)

    print("Resumen guardado en:", output_csv)


if __name__ == "__main__":
    main()

