=====================
Token
=====================

api/v1/token/
-------------

----------  ----------
Method      GET
----------  ----------
Description Realiza el login del usuario, retorna el api_key que sirve para validar cualquier otra conexion que requiera autenticacion
Auth BasicAuthentication
Parameters
Header:
Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
Return
{
	“key” : “API_KEY”
}


