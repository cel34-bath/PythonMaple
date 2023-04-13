import os
import detect


this_file_directory = os.path.dirname(os.path.abspath(__file__))
if "Repositories" in this_file_directory:
    initial_directory = this_file_directory.split("Repositories")[0]+"Repositories"
else:
    raise Exception("You're too far from Repositories.")
    
import subprocess
import time # This can be use to return how long the call lasts
import pickle
#import resource
import signal

# Maximal virtual memory for subprocesses (in bytes).
#MAX_VIRTUAL_MEMORY = 10 * 1024 * 1024 # 10 MB
###%MAX_VIRTUAL_MEMORY = 10 * 1024 # 10 KB

###%def limit_virtual_memory():
    # The tuple below is of the form (soft limit, hard limit). Limit only
    # the soft part so that the limit can be increased later (setting also
    # the hard limit would prevent that).
    # When the limit cannot be changed, setrlimit() raises ValueError.
    ###%resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))



def create_run_maple_from_python(file_location = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_file.mpl"), libnames_needed = [], packages_needed = [], files_to_read_needed = [], initializations = [],functions_to_call = [], output_files = [], timelimit = 5, sleeping_time = 0):
    '''
    This function will create and run a Maple file in 'file_location' containing:
    - The packages requiered in the list 'packages_needed'.
    - The files of code required in the list 'files_to_read_needed'.
    - The initialization of variables described in 'initializations'; 'initializations' should be a list of 2-tuples of the form (string::variable name, content of the variable).
    - The calling of functions as described in 'functions_to_call'; 'functions_to_call' should be a list of 3-tuples of the form (string::function name, list of strings::arguments to send, string::name of output variable).
    - The creation of files to write the outputs on as described on 'output_files'; 'output_files' should be a list of 2-tuples of the form (string::file_name, string::variable to output there).

    This function will return:
    - "Time over" if the timelimit is exceed
    - A list containing as first element how long did it took to run the program created and as the rest of the elements the variables that were encoded into the desired files
    '''

    # The correct location of maple is taken
    if detect.windows:
        maple_location = "C:\\Program Files\\Maple 2020\\bin.X86_64_WINDOWS\\cmaple.exe"           
    elif detect.linux:
        #maple_location = os.path.join( "/opt", "maple2021", "bin", "maple")
        maple_location = "maple"

    # the text of the desired program is created
    file_text = "randomize():"
    # the libnames wanted are added to the file
    for libname in libnames_needed:
        file_text += "libname ,=\"" + libname.replace("\\","\\\\") + "\":"
    # the packages are added to the file
    for package in packages_needed:
        file_text += "with(" + package + "):"
    # the files to read are added to the file
    for file_to_read in files_to_read_needed:
        file_text += "read(\"" + file_to_read.replace("\\","\\\\") + "\"):"
    # the variables are initialised
    for var in initializations:
        var_name = var[0]
        var_content = var[1]
        if type(var_content) == str:
            file_text += var_name + ":=" + "\"" + var_content.replace("\\","\\\\") + "\":"
        else:
            file_text += var_name + ":=" + str(var_content) + ":"
    # the functions are called with the indicated arguments and saving the output in the adecuate variables
    for function in functions_to_call:
        fun_name = function[0]
        fun_arguments = function[1]
        fun_output = function[2]
        fun_arguments_text = ",".join(fun_arguments)
        file_text += fun_output + ":=" + fun_name + "(" + fun_arguments_text + "):"
    # the necessary packages to encode the variables are added
    file_text += "with(Python):ImportModule(pickle):"
    # the code to create the output files sending the indicated variables is added
    for output_file in output_files:
        file_name = output_file[0]
        output_var = output_file[1]
        # the file to write the output is created
        file_text += "SetVariable(\"file_name\",\"" + file_name.replace("\\","\\\\") + "\"):"
        file_text += "SetVariable(\"f\", EvalString(\"open(file_name,'wb')\")):"
        # the output variable is encoded into the file
        file_text += "SetVariable(\"output_var_py\"," + output_var + "):EvalString(\"pickle.dump(output_var_py,f)\"):"
        file_text += "EvalString(\"f.close()\"):"

    # and the text is added to it
    f = open(file_location,'w')
    f.write(file_text)
    f.close()

    # the subprocess to run the program in Maple is created
    final_list_subprocess = [maple_location] + ["-i"] + [file_location] + ["-c"] + ["quit():"]

    if detect.windows:
        print(final_list_subprocess)
        task = subprocess.Popen(
            final_list_subprocess, stdout=subprocess.PIPE) 
    elif detect.linux:
        task = subprocess.Popen(
            final_list_subprocess, stdout=subprocess.PIPE, preexec_fn=os.setsid) 


    ###%elif detect.linux:
        ###%task = subprocess.Popen(final_list_subprocess, stdout=subprocess.PIPE, preexec_fn=limit_virtual_memory)

    # the program is run and timed
    start_time = time.time()
    subprocess_works = 1
    try:
        result, errs = task.communicate(timeout=timelimit)
    except subprocess.TimeoutExpired:
        if detect.windows:
            task.kill()
        elif detect.linux:
            taskid = task.pid
            os.killpg(os.getpgid(taskid), signal.SIGTERM)
            os.system("kill -9 "+str(taskid))
        subprocess_works = 2
    except:
        if detect.windows:
            task.kill()
        elif detect.linux:
            taskid = task.pid
            os.killpg(os.getpgid(taskid), signal.SIGTERM)
            os.system("kill -9 "+str(taskid))
        print("Calling Maple gave some kind of error")
        subprocess_works = 0
    time_to_run = time.time()-start_time

    # if the program finished within the required time the variables encoded into the output files will be recovered and returned in a vector
    if subprocess_works == 1:
        things_to_return = [time_to_run]
        for file_to_recover in output_files:
            if os.stat(file_to_recover[0]).st_size != 0: # if the file is not empty...
                with open(file_to_recover[0], "rb") as open_file_to_recover:
                    try:
                        things_to_return += [pickle.load(open_file_to_recover)]
                    except:
                        print("There has been a problem unpickling")
                        things_to_return += [[]] # this is a patch that will solve some problems
            else:
                things_to_return += [[]] # this is a patch that will solve some problems
    elif subprocess_works == 2:
        things_to_return = [time_to_run, "Time over"]
        time.sleep(sleeping_time)
    else:
        things_to_return = [time_to_run, "Something went wrong"]
        time.sleep(sleeping_time)
    
    return things_to_return

id = "oyl"
timeout = 10
initial_directory = os.path.join( "C:\\", "Users", "teres", "OneDrive - Coventry University", "03Repositories")
polynomials=[[[1, 0, 1]], [[0, 1, 1]], [[0, 0, -213], [0, 1, 655]]]
variable = 1
auxiliar_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_file_proj"+id+".mpl")
output_file = os.path.join(initial_directory, '03CADVariableOrdering', "Auxiliar", "maple_from_python_output"+id+".txt")
aux = create_run_maple_from_python(file_location=auxiliar_file, libnames_needed=[os.path.join(initial_directory, "02Tools", "MapleTools")], packages_needed=["TeresoTools"],  initializations=[("polynomials_python",polynomials)], functions_to_call=[("projection_step_from_python", ["polynomials_python",str(variable)], "proj_polys")] ,output_files=[(output_file,"proj_polys")], timelimit=timeout)
print(aux)