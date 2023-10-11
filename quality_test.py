total = -1
experiment_type_fail = 0
platform_fail = 0
organism_fail = 0

with open('output/Example_Results.csv','r') as texto:
	for line in texto:
		total += 1
		if 'Two or more types' in line:
			experiment_type_fail += 1
		if 'GPL' not in line:
			platform_fail += 1
		if 'Two or more organisms' in line:
			organism_fail += 1
			
print('Experiment type fail: ' + str(experiment_type_fail) + '/' + str(total) + '\nPlatform fail: '+ str(platform_fail) + '/' + str(total) + '\nOrganism fail: ' + str(organism_fail) + '/' + str(total))
