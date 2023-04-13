import pickle
# import detect 
import os
import sys

def flatten_list(list_of_lists):
    flat_list = []
    for item in list_of_lists:
        if type(item) == list:
            flat_list += flatten_list(item)
        else:
            flat_list.append(item)
    
    return flat_list


initial_directory = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")

# sys.path.append("./")

input_location = open(os.path.join(initial_directory, "03CADVariableOrdering", "create_CAD_data", "all_QF_NRA_three_variables_problems_2.txt"), "rb")
fld = pickle.load(input_location)
input_location.close()

without_repetition=True
return_ncells=True

for without_repetition in [True, False]:
    features, targets, timings, heuristics_costs, ncells = fld.transform_to_dataset(features_type="projections", return_timings=True,return_heuristics_costs=True, without_repetition=without_repetition, return_ncells=return_ncells)
    projections = [feature for feature in features]
    dataset = [features, targets, timings, heuristics_costs, ncells]
    output_location_filename = os.path.join(initial_directory, "DEWCADCoventry","Papers","TeresoMatthew","2022CASC-mods_heuristic","Datasets", "dataset_with"+"out"*without_repetition+"_repetition_return_ncells.txt")
    with open(output_location_filename, 'wb') as output_location_file:
        pickle.dump(dataset, output_location_file)


    for i in range(6):
        cnt = [1 for target in targets if target == i]
        print("There are "+str(sum(cnt))+" instances with target "+str(i))



# without_repetition=False
# features, targets, timings, heuristics_costs, ncells = fld.transform_to_dataset(features_type="projections", return_timings=True,return_heuristics_costs=True, without_repetition=without_repetition, return_ncells=return_ncells)
# projections = [feature for feature in features]
# dataset_with_repetition = [features, targets, timings, heuristics_costs, ncells]
# output_with_location = open(os.path.join(initial_directory, "DEWCADCoventry","Papers","TeresoMatthew","2022CASC-mods_heuristic","Datasets", "dataset_with_repetition_return_ncells.txt"),'wb')
# pickle.dump(dataset_with_repetition, output_with_location)
