from iconservice import isfunction, revert, wraps

def only_admin(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if self.msg.sender != self._admin.get():
			revert(f"SenderNotAdmin: sender({self.msg.sender}), admin({self._admin.get()})")

		return func(self, *args, **kwargs)
	return __wrapper
