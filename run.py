import control


if __name__ == "__main__":
	"""This is the main method 
	which drives the control"""

	print "\n\nWould you like to rebuild the indexes? Y/N "

	choice = raw_input()
	if choice == 'Y':
		rebuild = True 
	else:
		rebuild = False

	if rebuild:
		print "Please expect 2 minutes for the indexes to be built."
		control.rebuild_indexes()
	else:
		print "Please wait 5 seconds for the indexes and term lists to load."

	s_term_list, s_lexicon, st_term_list, st_lexicon = control.read_single_stem()
	
	quit = False
	while quit != True:
		choice = control.query_options()
		if choice == 'Q':
			quit = True
			break
		elif choice == 'P':
			print "Please expect 45 seconds for both reports to finish processing."
			control.P_option(s_term_list, s_lexicon, st_term_list, st_lexicon)
		elif choice == 'C':
			print "Please expect 1.5 minutes for the all 8 tests to finish running."
			control.C_option(s_term_list, s_lexicon)
		else:
			print "Invalid Selection"


	
