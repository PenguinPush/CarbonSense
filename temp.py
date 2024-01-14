import random

percent_proximity = 0.8
max_range = 10

list_of_objects = ["plastic water bottle(s)", "plastic bag(s)", "world domination(s)"]

object_one_index = random.randint(0, len(list_of_objects))
object_two_index = random.randint(0, len(list_of_objects))

amt_of_object_one = random.randint(1, max_range)

# do the fancy chat gpt thing and get both object 1 and 2 emissions (should be per unit)
object_one_emissions = 0
object_two_emissions = 0

total_object_one_emissions = object_one_emissions * amt_of_object_one

approx_total_object_two_emissions = object_one_emissions + (random.uniform(-1, 1) * percent_proximity * object_one_emissions)

amt_of_object_two = approx_total_object_two_emissions // object_two_emissions
total_object_two_emissions = amt_of_object_two * object_two_emissions

# comapre total object two emissions and total object one emissions or smth and display stuff idk 