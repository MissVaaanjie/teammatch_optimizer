from src.input_processor import create_scenario
from src.model_builder import IP_model
from src.model_optimizer import solve_model
from src.handle_result import write_solution
# from settings import CONFIG

dancers, heats, cons_heats = create_scenario()
model = IP_model(heats, dancers, cons_heats)

stats_dict_highs = solve_model()
write_solution(heats)
