def round_down(x, nums):
	"""
	Rounds x down to the number in nums that it is closest to, but larger than or equal to
	"""	
	nums.sort(reverse=True)
	for num in nums:
		if x < num:
			continue
		return num