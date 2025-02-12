# from mrjob.job import MRJob
# from mrjob.step import MRStep


# class RatingsBreak(MRJob):
# 	def steps(self):
# 		return [
# 			MRstep(mapper=self.mapper_get_ratings,
# 				reducer=self.reducer_count_ratings)
# 		]
# 		# MAPPER CODE

# 	def mapper_get_ratings(self, _, line):
# 		(User_id, Movie_id, Rating, Timestamp) = line.split('/t')
# 		yield rating,
# 		# REDUCER CODE

# 	def reducer_count_ratings(self, key, values):
# 		yield key, sum(values)
