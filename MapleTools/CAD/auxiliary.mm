if kernelopts(platform) = "unix" then
    initial_directory := FileTools:-JoinPath( ["/home", "delriot", "Documents", "Repositories"], platform = kernelopts(platform)):
else:
    initial_directory := FileTools:-JoinPath( ["C:", "Users", "teres", "OneDrive - Coventry University", "Repositories"], platform = kernelopts(platform) ):
end if:

with(SMTLIB):
with(RootFinding):
with(StringTools):
with(ListTools):
with(ArrayTools):

multiplynumbers := proc(a,b)
    return a*b:
end proc: