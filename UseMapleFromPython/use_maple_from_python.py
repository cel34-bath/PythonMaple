"""This module provides an easy way of calling Maple from Python."""
# IF THIS CODE WERE TO STOP WORKING CHECK THE " AND THE ' WHEN CALLING MAPLE
import os
import subprocess
import time
import pickle
import signal

# The correct location of maple is taken
# if detect.windows:
maple_location = ('C:\\Program Files\\Maple 2023\\'
                      'bin.X86_64_WINDOWS\\cmaple.exe')
# elif detect.linux:
#     # maple_location = os.path.join( "/opt", "maple2021", "bin", "maple")
#     maple_location = "maple"


def create_run_maple_from_python(
    file_location,
    libnames_needed=[],
    packages_needed=[],
    files_to_read_needed=[],
    initializations=[],
    functions_to_call=[],
    output_files=[],
    timelimit=5,
    sleeping_time=0
        ):
    """
    Create a Maple file in 'file_location' and run it.

    This file will:
        install the packages in 'packages_needed'.
        read the files of code in 'files_to_read_needed'.
        initialize the variables as described in 'initializations'
        run functions as described in 'functions_to_call'
        create the files for outputs as described in 'output_files'
    Parameters
    ----------
    file_location: str
    libnames_needed: list of str
    packages_needed: list of str
    files_to_read_needed: list of str
    initializations: list of 2-tuples of the form
        (string::variable name, content of the variable).
    functions_to_call: list of 3-tuples of the form (
        string::function name,
        list of strings::arguments to send,
        string::name of output variable
        ).
    output_files: list of 2-tuples of the form
        (string::file_name, string::variable to output there).
    Returns
    -------
    A list with
    - a number indicating the success of the call:
        - 1 -> the call was successful
        - 2 -> the call timedout
        - 0 -> there was an error
    - the time the call took or "Time over" if the timelimit was exceed
    - the desired outputs
    """
    # the text of the desired program is created
    file_text = "randomize():"
    # the libnames wanted are added to the file
    for libname in libnames_needed:
        file_text += "libname ,=\"" + libname.replace("\\", "\\\\") + "\":"
    # the packages are added to the file
    for package in packages_needed:
        file_text += "with(" + package + "):"
    # the files to read are added to the file
    for file_to_read in files_to_read_needed:
        file_text += "read(\"" + file_to_read.replace("\\", "\\\\") + "\"):"
    # the variables are initialised
    for var in initializations:
        var_name = var[0]
        var_content = var[1]
        if type(var_content) == str:
            file_text += (var_name + ":=" + "\""
                          + var_content.replace("\\", "\\\\") + "\":")
        else:
            file_text += var_name + ":=" + str(var_content) + ":"
    # the functions are called with the indicated arguments
    # and saving the output in the adecuate variables
    for function in functions_to_call:
        fun_name = function[0]
        fun_arguments = function[1]
        fun_output = function[2]
        fun_arguments_text = ",".join(fun_arguments)
        file_text += (fun_output + ":=" + fun_name
                      + "(" + fun_arguments_text + "):")
    # the necessary packages to encode the variables are added
    file_text += "with(Python):ImportModule(pickle):"
    # create the output files sending the indicated variables is added
    for output_file in output_files:
        file_name = output_file[0]
        output_var = output_file[1]
        # the file to write the output is created
        file_text += ("SetVariable(\"file_name\",\""
                      + file_name.replace("\\", "\\\\") + "\"):")
        file_text += ("SetVariable(\"f\", "
                      "EvalString(\"open(file_name,'wb')\")):")
        # the output variable is encoded into the file
        file_text += ("SetVariable(\"output_var_py\"," + output_var
                      + "):EvalString(\"pickle.dump(output_var_py,f)\"):")
        file_text += "EvalString(\"f.close()\"):"

    # and the text is added to it
    f = open(file_location, 'w')
    f.write(file_text)
    f.close()

    # the subprocess to run the program in Maple is created
    final_list_subprocess = ([maple_location] + ["-i"] + [file_location]
                             + ["-c"] + ["quit():"])

    print(final_list_subprocess)
    task = subprocess.Popen(
            final_list_subprocess, stdout=subprocess.PIPE)

    # the program is run and timed
    start_time = time.time()
    subprocess_works = 1
    try:
        result, errs = task.communicate(timeout=timelimit)
    except subprocess.TimeoutExpired:
        task.kill()
        subprocess_works = 2
    except: # noqa E722
        task.kill()
        print("Calling Maple gave some error.")
        subprocess_works = 0
    time_to_run = time.time()-start_time

    # if the program finished within the required time the variables encoded
    # into the output files will be recovered and returned in a vector
    if subprocess_works == 1:
        things_to_return = [subprocess_works, time_to_run]
        for file_to_recover in output_files:
            if os.stat(file_to_recover[0]).st_size != 0:
                # if the file is not empty...
                with open(file_to_recover[0], "rb") as open_file_to_recover:
                    try:
                        things_to_return += [pickle.load(open_file_to_recover)]
                    except: # noqa E722
                        print("There has been a problem unpickling.")
                        things_to_return += [[]]
                        # this is a patch that will solve some problems
            else:
                things_to_return += [[]]
                # this is a patch that will solve some problems
    elif subprocess_works == 2:
        things_to_return = [subprocess_works, time_to_run, "Time over"]
        time.sleep(sleeping_time)
    else:
        things_to_return = [subprocess_works, time_to_run,
                            "Calling Maple gave some error."]
        time.sleep(sleeping_time)

    return things_to_return
