from iconservice import *


def only_admin(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if self.msg.sender != self._admin.get():
			revert(f"SenderNotAdmin: sender({self.msg.sender}), admin({self._admin.get()})")

		return func(self, *args, **kwargs)
	return __wrapper


def only_owner(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if self.msg.sender != self.owner:
			revert(f"SenderNotOwner: sender({self.msg.sender}), owner({self.owner})")

		return func(self, *args, **kwargs)
	return __wrapper


def only_review_contract(func):
	if not isfunction(func):
		revert(f"NotAFunctionError")

	@wraps(func)
	def __wrapper(self: object, *args, **kwargs):
		if self.msg.sender != self._review_score.get():
			revert(f"SenderNotReviewscore: sender({self.msg.sender}), review_score({self._review_score.get()})")

		return func(self, *args, **kwargs)
	return __wrapper