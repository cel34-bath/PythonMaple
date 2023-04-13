# an initial directory where everything is the same in my PC than in brosnan is stablished
if kernelopts(platform) = "unix" then
    initial_directory := FileTools:-JoinPath( ["/home", "delriot", "Documents", "Repositories"], platform = kernelopts(platform)):
else:
    initial_directory := FileTools:-JoinPath( ["C:", "Users", "teres", "OneDrive - Coventry University", "Repositories"], platform = kernelopts(platform) ):
end if:

folder_mla := FileTools:-JoinPath( [initial_directory, "Tools", "MapleTools"], platform = kernelopts(platform)):
name_mla := "tools1.0.9.mla":
location_mla := FileTools:-JoinPath([folder_mla, name_mla], platform = kernelopts(platform)):

folder_main := FileTools:-JoinPath( [initial_directory, "Tools", "MapleTools"], platform = kernelopts(platform)):
name_main := "main.mpl":
location_main := FileTools:-JoinPath([folder_main, name_main], platform = kernelopts(platform)):

read(location_main):

LibraryTools:-Create(location_mla):
savelib('TeresoTools',location_mla):