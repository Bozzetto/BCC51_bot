import math

class User(object):
	def __init__(self):
		self.id = None
		self.email = None
		self.name = None
		self.courses = []
		self.warnings = []
		self.rc = 0

	def __str__(self):
		print(self.id,self.email,self.name,self.materias,self.rc)

	def set_id(id):
		self.id = id

	def set_email(email):
		self.email = email

	def set_name(name):
		self.name = name

	def set_rc(rc):
		self.rc = rc

	def set_warnings(self,warnings):
		self.warnings = warnings

	def add_course(self,course):
		number = math.pow(2,course)
		self.materias.append(number)

	def get_id(self):
		return self.id

	def get_name(self):
		return self.name

	def get_email(self):
		return self.email

	def get_courses(self):
		return self.materias

	def get_warnings(self):
		return self.alertas

	def is_rc(self):
		return self.rc

def main():
	usuario = User("fernando_crz","fernandof@usp.com",rc=True)
	print(type(usuario))


if __name__ == "__main__":
	main()
