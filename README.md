# SourcePerms

Easy to use permissions for SourcePython

Configuration:

The configuration file for permissions is located at cfg/source-python/auth/

The group config format is:
```json
{
	"<groupname>" : 
	{
		"parents" :
		[
			"group1",
			"group2"
		],
		"permissions" :
		[
			"permission1",
			"permission2"
		]
	}
}
```

The admin config format is:
```json
{
	"<steamid>" :
	{
		"parents" :
		[
			"group1",
			"group2"
		],
		"permissions" :
		[
			"permission1",
			"permission2"
		]
	}
}
```

Example group config:
```json
{
	"admin" :
	{
		"permissions" :
		[
			"sp.fun.*"
		]
	}
}
```

Example admin config:
```json
{
	"STEAM_0:0:11672517": 
	{
		"parents" :
		[
			"admins"
		],
		"permissions" :
		[
			"sp.map.map"
		]
	}
}
```
This would give the player access to the following commands: sp_ignite, sp_freeze, sp_unfreeze and sp_map.

Simple. Easy. Powerful.
