mysqldump.exe : mysqldump.exe: Got error: 2002: "Can't connect to MySQL server on 'localhost' (10061)" when trying to 
connect
At line:3 char:1
+ & $mysqldump -u root --no-tablespaces staymatch 2>&1 | Out-File -File ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (mysqldump.exe: ...ying to connect:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
