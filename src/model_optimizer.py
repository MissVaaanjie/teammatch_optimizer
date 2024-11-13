import highspy
from ortools.linear_solver.python import model_builder
from settings import CONFIG
import time


def solve_with_HiGHs():
    highs = highspy.Highs()
    highs.readModel(CONFIG.output_mps_name)

    if not CONFIG.presolve_enabled:
        options = highs.getOptions()
        options.presolve = "off"
        highs.passOptions(options)

    if not CONFIG.output_enabled:
        highs.silent()

    start_time = time.time()
    highs.run()
    end_time = time.time()
    info = highs.getInfo()
    highs.writeSolution(CONFIG.solution_file_name, 4)
    return {
        "solver": "HiGHs",
        "objective_value": info.objective_function_value,
        "time_taken": end_time - start_time
    }


def solve_with_ortools(solver_name):
    model = model_builder.ModelBuilder()
    model.import_from_mps_file(CONFIG.output_mps_name)
    solver = model_builder.ModelSolver(solver_name)
    # print(solver.solver_is_supported())

    if CONFIG.output_enabled:
        solver.enable_output(True)

    start_time = time.time()
    status = solver.solve(model)
    end_time = time.time()
    return {"solver": f'or-tools: {solver_name}',
            "objective_value": solver.objective_value,
            "time_taken": end_time - start_time}


def solve_model(solver_name="HiGHs"):
    if solver_name == "HiGHs":
        stats_dict = solve_with_HiGHs()
    elif solver_name == "CBC" or solver_name == "SCIP":
        stats_dict = solve_with_ortools(solver_name)
    else:
        print("Error: unknown solver")
    return stats_dict
