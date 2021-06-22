

from pymoo import factory
from pymoo.model.crossover import Crossover
import spatial_extention_pymoo
# add spatial functions to pymoo library
factory.get_sampling_options = spatial_extention_pymoo._new_get_sampling_options
factory.get_crossover_options = spatial_extention_pymoo._new_get_crossover_options
factory.get_mutation_options = spatial_extention_pymoo._new_get_mutation_options
Crossover.do = spatial_extention_pymoo._new_crossover_do



import numpy as np
import pickle
import matplotlib.pyplot as plt
import random
from matplotlib.colors import ListedColormap
from pymoo.util.misc import stack
from pymoo.model.problem import Problem

from pymoo.algorithms.nsga2 import NSGA2
from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.factory import get_termination
from pymoo.optimize import minimize




from calculate_objectives import calculate_time_differences 
from calculate_objectives import calculate_fuelUse

startpoint=(332,122)
endpoint= (233,901)

startTime="22.06.2021 12:00"
endTime="23.06.2021 11:00"
timeGrid = np.load("first_prediction.npy", allow_pickle=True)#
timeGrid = timeGrid[250:750, 1200:2200]
timeGrid = np.where((timeGrid < -1.9) & (timeGrid > -2), 1000, timeGrid)
timeGrid = np.where(timeGrid >999, timeGrid, (timeGrid*timeGrid+2))
timeGrid = np.where(timeGrid >999, timeGrid, (10/timeGrid)*0.1)

# read input data for objectives

from pymoo.model.problem import Problem
class MyProblem(Problem):

 # define the number of variables etc.
 def __init__(self):
    super().__init__(n_var=2, # nr of variables
                     n_obj=2, # nr of objectives
                     n_constr=0, # nr of constraints
                     xl=0.0, # lower boundaries
                     xu=1.0) # upper boundaries

                      # define the objective functions
 def _evaluate(self, X, out, *args, **kwargs):
    f1 = calculate_time_differences(X[:], startTime, endTime, timeGrid)
    f2 = calculate_fuelUse(X[:], timeGrid)
    out["F"] = np.column_stack([f1, f2])

problem = MyProblem()
print(problem)

from pymoo.algorithms.nsga2 import NSGA2
from pymoo.factory import get_sampling, get_crossover, get_mutation
algorithm = NSGA2(
 pop_size=20,
 n_offsprings= 10,
 sampling=get_sampling("spatial", startpoint= startpoint, endpoint=endpoint, timeGrid = timeGrid),
 crossover=get_crossover("spatial_one_point_crossover", timeGrid = timeGrid, n_points = 1.0),
 mutation=get_mutation("spatial_n_point_mutation", timeGrid=timeGrid, prob = 1.0),
 eliminate_duplicates=False
 )

from pymoo.factory import get_termination 
termination = get_termination("n_gen", 5)

from pymoo.optimize import minimize
res = minimize(problem,
               algorithm,
               termination,
               seed=1, 
               save_history=True,   
               verbose=True)

#print(res)
#print(res.X)
#print(res.F)

#save final land use maps and corresponding values of profit and area of natural vegetation for each map
np.save("./routes",res.X)
np.save("./values",res.F)

# Create an empty list to save objective values per generation
# Needed for history 
f = []
# iterate over the generations
for generation in res.history:
 # retrieve the optimal for all objectives from the generation
 opt = generation.opt
 this_f = opt.get("F")
 f.append(this_f)

fNumpy = np.asarray(f)

#save history
np.save("/history",fNumpy)


