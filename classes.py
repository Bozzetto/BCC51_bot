import math
from datetime import datetime

class User(object):
	def __init__(self):
		self.id = None
		self.email = None
		self.name = None
		self.courses = []
		self.warnings = []
		self.rc = 0

	def __str__(self):
		return str((self.id,self.email,self.name,self.courses,self.warnings,self.rc))

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

class Course(object):
	def __init__(self):
		self.name = None
		self.course_name = None
		self.professor = None
		self.code = None

	def set_name(self,name):
		self.name = name

	def set_course_name(self,course_name):
		self.course_name = course_name

	def set_professor(self,professor):
		self.professor = professor

	def set_code(self,code):
		self.code = code

	def get_name(self):
		return self.name

	def get_course_name(self):
		return self.course_name

	def get_professor(self):
		return self.professor

	def get_code(self):
		return self.code

class Warning(object):
	def __init__(self):
		self.name = None
		self.type = None
		self.course = None # Course object
		self.creator = None
		self.time = None # Datetime object
		self.repeatable = None # Bool

	def set_name(self,name):
		self.name = name

	def set_type(self,type):
		self.type = type

	def set_course(self,course):
		self.course = course

	def set_creator(self,creator):
		self.creator = creator

	def set_time(self,time):
		self.time = time

	def set_repeatable(self,repeatable):
		self.repeatable = repeatable

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type

	def get_course(self):
		return self.course

	def get_creator(self):
		return self.creator

	def get_time(self):
		return self.time

	def get_repeatable(self):
		return self.repeatable


def main():
	usuario = User("fernando_crz","fernandof@usp.com",rc=True)
	print(type(usuario))


if __name__ == "__main__":
	main()
