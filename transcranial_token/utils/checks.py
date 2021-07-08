from iconservice import *


def only_admin(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if self.msg.sender != self._admin.get():
			revert(f"Only admin can call this function.")

		return func(self, *args, **kwargs)
	return __wrapper

def only_owner(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if self.msg.sender != self.owner:
			revert("Onlygit stat owner can call this function.")

		return func(self, *args, **kwargs)
	return __wrapper

def only_minters(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if not self.msg.sender in self._minters:
			revert(f"Only minters can call this function.")

		return func(self, *args, **kwargs)
	return __wrapper

def only_burners(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if not self.msg.sender in self._burners:
			revert(f"Only burners can call this function.")

		return func(self, *args, **kwargs)
	return __wrapper