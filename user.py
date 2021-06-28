class User(object):
	def __init__(self,id,email,rc=False):
		self.id = id
		self.email = email
		self.materias = None
		self.alertas = None
		self.rc = rc

	def add_materia(self,materia):
		self.materias.append(materia)

	def add_alerta(self,alerta):
		self.alertas.append(alertas)

	def encript_materias(self):
		pass

	def get_id(self):
		return self.id

	def get_email(self):
		return self.email

	def get_materias(self):
		return self.materias

	def get_alertas(self):
		return self.alertas

	def is_rc(self):
		return self.rc

def main():
	usuario = User("fernando_crz","fernandof@usp.com",rc=True)
	print(type(usuario))


if __name__ == "__main__":
	main()