# SourcePerms
Easy to use permissions for SourcePython
Configuration:
The configuration file for permissions is located at cfg/source-python/auth/admins.json
The format is:
{
	"<steamid>" :
	[
		"permission1",
		"permission2"
	]
}

Example using permissions from my admin_commands plugin:
{
	"STEAM_0:0:11672517": 
	[
		"sp.fun.*",
		"sp.map.map",
	]
}
This would give the player access to the following commands: sp_ignite, sp_freeze, sp_unfreeze and sp_map.

Simple. Easy. Powerful.

Groups and inheritance are planned for the future.