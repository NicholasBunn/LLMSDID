# Packages
import PySimpleGUI as sg
import mysql.connector
import secrets

errorSelFlag = False
guest_user_flag = False
unresolved_errors = [] # MEEP, could probably do without this in the refactor
current_error = {
	'fault_id': 'Null',
	'fault_status': 'Null',
	'fault_description': 'Null',
	'voyage': 'Null',
	'time_of_fault': 'Null',
	'time_of_solution': 'Null',
	'fault_type': 'Null',
	'location': 'Null',
	'sensor_id': 'Null',
	'sensor_type': 'Null',
	'fault_message': 'Null',
	'log_date': 'Null'
}

class MyDB():
	
	def __init__(self, host, user, password, database):
		try:
			self.connection = mysql.connector.connect(
				host=host,
				user=user,
				passwd=password,
				database=database,
				auth_plugin='mysql_native_password'
			)
			self.cursor = self.connection.cursor()
		except mysql.connector.Error as e:
			print("Error %d: %s", (e.args[0], e.args[1]))
			# sys.exit(69)

	def save_to_errors(self, fault_status, fault_desciption, voyage, time_of_fault, time_of_solution, fault_type, location, sensor_id, sensor_type, fault_message):
		if time_of_fault == '':
			time_of_fault = "NULL"

		if time_of_solution == '':
			time_of_solution = "NULL"

		if fault_status == '':
			fault_status = "Unresolved"

		insert_query = "INSERT INTO errors (FaultDescription, FaultMessage, FaultStatus, FaultType, Location, SensorID, SensorType, TimeOfFault, TimeOfSolution, Voyage) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, '{}')".format(fault_desciption, fault_message, fault_status, fault_type, location, sensor_id, sensor_type, time_of_fault, time_of_solution, voyage)
		print(insert_query)

		self.cursor.execute(insert_query)

		self.connection.commit()

	def save_to_downtime(self, voyage, stop_time, start_time, reason, assosciated_error, downtime_id):
		insert_query = "INSERT INTO errors (Voyage, StopTime, StartTime, Reason, AssosciatedError, downtimeID) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(voyage, stop_time, start_time, reason, assosciated_error, downtime_id)
		print(insert_query)

		self.cursor.execute(insert_query)

		self.connection.commit()

	def fetch(self, fetch_query):
		print("Fetch " + str(fetch_query))

		_ = self.cursor.execute(fetch_query)
		result = self.cursor.fetchall()

		return result

	def update(self, fault_status, fault_desciption, voyage, time_of_fault, time_of_solution, fault_type, location, sensor_id, sensor_type, fault_message, fault_id):
		# ToDo Test the robustness of this, seems like it doens't like updating with unchanged fields
		if time_of_fault == 'None':
			time_of_fault = "NULL"

		if time_of_solution =='None':
			time_of_solution = "NULL"

		update_query = "UPDATE errors SET FaultStatus = '{}', FaultDescription = '{}', Voyage = '{}', TimeOfFault = {}, TimeOfSolution = {}, FaultType = '{}', Location = '{}', SensorID = '{}', SensorType = '{}', FaultMessage = '{}' WHERE FaultID = {}".format(fault_status, fault_desciption, voyage, time_of_fault, time_of_solution, fault_type, location, sensor_id, sensor_type, fault_message, fault_id)

		print(update_query)
		self.cursor.execute(update_query)

		self.connection.commit()

		print("Updated")

	def search(self):
		pass
	
# Create window functions
def create_login_window():
	# Setup
	login_layout = [[sg.Text('Hostname: '), sg.In(size = (25, 0), key = '-HOST-')],
				   [sg.Text('Username: '), sg.In(size = (25, 0), key = '-USER-')],
				   [sg.Text('Password: '), sg.In(size = (25, 0), pad = (3, 0), password_char = '*', key='-PASS-')],
				   [sg.Button('Login', size = (14, 0),  pad = ((0, 10), (5, 0)), enable_events = True, bind_return_key = True, key = '-LOGIN-'), sg.Button('Guest Login.', size = (14, 0), pad = ((10, 0), (5, 0)), enable_events = True, key = '-LOGIN GUEST-')]
				   ]

	login_window = sg.Window("LLMSDID - Login",
							layout=login_layout,
							margins=(20, 10),
							grab_anywhere=True,
							default_button_element_size=(12, 1)
							)

	# Logic
	while True:
		login_event, login_values = login_window.read()

		# TODO add in and AND for enter keystroke event
		if login_event == '-LOGIN-':
			current_db = MyDB(login_values['-HOST-'], login_values['-USER-'], login_values['-PASS-'], "LLMSDID")
			login_window.close()
			return current_db

		if login_event == '-LOGIN GUEST-':
			current_db = MyDB('localhost', secrets.guestUsername, secrets.guestPassword, "LLMSDID")
			global guest_user_flag
			guest_user_flag = True
			login_window.close()
			return current_db

		# If the user closes the window, exit this loop so that the program can close
		if login_event == sg.WIN_CLOSED:
			login_window.close()
			exit(69)

def create_update_window(selected_error, database):
	update_col_1 = sg.Column([[sg.Frame('Current values', [[sg.Column([[sg.Text("Voyage: ", size=(12,1)), sg.Text(selected_error['voyage'])],
																	  [sg.Text("Status: ", size=(12,1)), sg.Text(selected_error['fault_status'])],
																	 [sg.Text("Description: ", size=(12,4)), sg.Multiline(selected_error['fault_description'], size=(40, 4))],
																	 [sg.Text("Fault message: ", size=(12,2)), sg.Multiline(selected_error['fault_message'], size=(40,2))],
																	  [sg.Text("Fault type: ", size=(12,1)), sg.Text(selected_error['fault_type'])],
																	  [sg.Text("Fault location: ", size=(12,1)), sg.Text(selected_error['location'])],
																	  [sg.Text("Sensor ID: ", size=(12,1)), sg.Text(selected_error['sensor_id'])],
																	  [sg.Text("Sensor type: ", size=(12,1)), sg.Text(selected_error['sensor_type'])],
																	  [sg.Text("From: ", size=(12,1)), sg.Text(selected_error['time_of_fault'])],
																	  [sg.Text("To: ", size=(12,1)), sg.Text(selected_error['time_of_solution'])]],
																	 )]])]])

	update_col_2 = sg.Column([[sg.Frame('Updated values', [[sg.Column([[sg.Text("Voyage: ", size=(12,1)), sg.In(selected_error['voyage'], size=(40,1), key='-NEW VOYAGE-')],
																	  [sg.Text("Status: ", size=(12,1)), sg.InputCombo(["Unresolved", "Resolved"], default_value=selected_error['fault_status'], key='-NEW STATUS-')],
																	 [sg.Text("Description: ", size=(12,4)), sg.Multiline(selected_error['fault_description'], size=(40,4), key='-NEW DESC-')],
																	 [sg.Text("Fault message: ", size=(12,2)), sg.Multiline(selected_error['fault_message'], size=(40,2), key='-NEW MESSAGE-')],
																	  [sg.Text("Fault type: ", size=(12,1)), sg.In(selected_error['fault_type'], size=(40,1), key='-NEW FTYPE-')],
																	  [sg.Text("Fault location: ", size=(12,1)), sg.In(selected_error['location'], size=(40,1), key='-NEW LOC-')],
																	  [sg.Text("Sensor ID: ", size=(12,1)), sg.In(selected_error['sensor_id'], size=(40,1), key='-NEW ID-')],
																	  [sg.Text("Sensor type: ", size=(12,1)), sg.In(selected_error['sensor_type'], size=(40,1), key='-NEW STYPE-')],
																	  [sg.Text("From: ", size=(12,1)), sg.In(selected_error['time_of_fault'], size=(40,1), key='-NEW FROM-')],
																	  [sg.Text("To: ", size=(12,1)), sg.In(selected_error['time_of_solution'], size=(40,1), key='-NEW TO-')]],
																	)]])]])

	update_col_3 = sg.Column([[sg.Frame('Actions', [[sg.Column([[sg.Button("Update", enable_events=True,
																		tooltip="Press me if you'd like to update this fault.",
																		key='-SAVE UPDATE-'),
															  sg.Button("Cancel", enable_events=True,
																		tooltip="Press me if you'd like to cancel this update.",
																		key='-CANCEL UPDATE-')]])]])]])

	updateLayout = [[update_col_1, update_col_2], [update_col_3]]

	update_window = sg.Window("LLMSDID - Update",
							layout=updateLayout,
							margins=(200, 100),
							grab_anywhere=True,
							default_button_element_size=(12, 1)
							)

	print("Updating " + str(selected_error['fault_id']))
	while True:
		update_event, update_value = update_window.read()

		if update_event == '-SAVE UPDATE-':
			database.update(update_value['-NEW STATUS-'], update_value['-NEW DESC-'], update_value['-NEW VOYAGE-'], update_value['-NEW FROM-'], update_value['-NEW TO-'], update_value['-NEW FTYPE-'], update_value['-NEW LOC-'], update_value['-NEW ID-'], update_value['-NEW STYPE-'], update_value['-NEW MESSAGE-'], selected_error['fault_id'])
			update_window.close()
			break

		# If the user closes the window, exit this loop so that the program can close
		if update_event == sg.WIN_CLOSED or update_event == '-CANCEL UPDATE-':
			update_window.close()
			break

def create_log_window(database):
	log_layout = [
		[sg.Text("Fault description", size=(12,1)), sg.In(size=(40, 40), key='-DESCRIPTION-')],
		[sg.Text("Fault message", size=(12,1)), sg.In(size=(40, 40), key='-MESSAGE-')],
		[sg.Text("Status", size=(12,1)), sg.InputCombo(["Unresolved", "Resolved"], key='-STATUS-')],
		[sg.Text("Fault type", size=(12,1)), sg.In(size = (25, 1), key='-TYPE-')],
		[sg.Text("Location", size=(12,1)), sg.In(size=(25, 1), key='-LOCATION-')],
		[sg.Text("Sensor ID", size=(12,1)), sg.In(size=(25, 1), key='-SENSOR ID-')],
		[sg.Text("Sensor type", size=(12,1)), sg.In(size=(25, 1), key='-SENSOR TYPE-')],
		[sg.Text("Time of fault", tooltip = "dd-mm-yy hh:mm:ss", size=(12,1)), sg.In(size=(25, 1), key='-START-')],
		[sg.Text("Time of solution", tooltip = "dd-mm-yy hh:mm:ss", size=(12,1)), sg.In(size=(25, 1), key='-END-')],
		[sg.Text("Voyage", size=(12,1)), sg.In(size=(25, 1), key='-VOYAGE-')],
		[sg.Button("Save", enable_events=True, key='-LOG SAVE-'), sg.Button("Cancel", enable_events=True, key='-LOG CANCEL-')]
	]

	log_window = sg.Window("LLMSDID - Log an error",
							layout=log_layout,
							margins=(200, 100),
							grab_anywhere=True,
							default_button_element_size=(12, 1)
							)

	while True:
		log_event, log_values = log_window.read()
		
		if  log_event == '-LOG SAVE-':
			database.save(log_values['-STATUS-'], log_values['-DESCRIPTION-'], log_values['-VOYAGE-'], log_values['-START-'], log_values['-END-'], log_values['-TYPE-'], log_values['-LOCATION-'], log_values['-SENSOR ID-'], log_values['-SENSOR TYPE-'], log_values['-MESSAGE-'])
			log_window.close()
			break

		# If the user closes the window, exit this loop so that the program can close
		if log_event == sg.WIN_CLOSED or log_event == '-LOG CANCEL-':
			log_window.close()
			break

def create_more_window(selected_error, database):
	more_col_1 = sg.Column([[sg.Frame('Parameter', [[sg.Column([[sg.Text("Fault ID: ")],
															  		[sg.Text("Voyage: ")],
																   	[sg.Text("Status: ")],
																	[sg.Text("Description: ")],
																	[sg.Text("Fault message: ")],
																	[sg.Text("Fault type: ")],
																   	[sg.Text("Fault location: ")],
																   	[sg.Text("Sensor ID: ")],
																   	[sg.Text("Sensor type: ")],
																   	[sg.Text("From: ")],
																   	[sg.Text("To: ")],
															 		[sg.Text("Log date: ")]],
																  )]])]])

	more_col_2 = sg.Column([[sg.Frame('Value', [[sg.Column([[sg.Text("Fault ID: ", size=(12,1)), sg.Text(selected_error['fault_id'], size=(40,1))],
														  [sg.Text("Voyage: ", size=(12,1)), sg.Text(selected_error['voyage'], size=(40,1))],
														  [sg.Text("Status: ", size=(12,1)), sg.Text(selected_error['fault_status'], size=(40,1))],
														  [sg.Text("Description: ", size=(12,4)), sg.Multiline(selected_error['fault_description'], size=(40,4))],
														  [sg.Text("Fault message: ", size=(12,2)), sg.Multiline(selected_error['fault_message'], size=(40,2))],
														  [sg.Text("Fault type: ", size=(12,1)), sg.Text(selected_error['fault_type'], size=(40,1))],
														  [sg.Text("Fault location: ", size=(12,1)), sg.Text(selected_error['location'], size=(40,1))],
														  [sg.Text("Sensor ID: ", size=(12,1)), sg.Text(selected_error['sensor_id'], size=(40,1))],
														  [sg.Text("Sensor type: ", size=(12,1)), sg.Text(selected_error['sensor_type'], size=(40,1))],
														  [sg.Text("From: ", size=(12,1)), sg.Text(selected_error['time_of_fault'], size=(40,1))],
														  [sg.Text("To: ", size=(12,1)), sg.Text(selected_error['time_of_solution'], size=(40,1))],
														 [sg.Text("Log date: ", size=(12,1)), sg.Text(selected_error['log_date'], size=(40,1))]],
														 )]])]])

	more_col_3 = sg.Column([[sg.Frame('Actions', [[sg.Column([[sg.Button("Thanks", enable_events=True,
																		tooltip="Press me if you're done having a look.",
																		key='-THANKS-')
															  ]])]])]])

	moreLayout = [[more_col_2], [more_col_3]]

	more_window = sg.Window("LLMSDID - More",
							 layout=moreLayout,
							 margins=(200, 100),
							 grab_anywhere=True,
							 default_button_element_size=(12, 1)
							 )

	while True:
		more_event, more_value = more_window.read()

		# If the user closes the window, exit this loop so that the program can close
		if more_event == sg.WIN_CLOSED or more_event == '-THANKS-':
			more_window.close()
			break

def create_downtime_window(database):
	# TODO RETURN Adjust this config for downtime
	log_layout = [
		[sg.Text("Fault description"), sg.In(size=(40, 40), key='-DESCRIPTION-')],
		[sg.Text("Fault message"), sg.In(size=(40, 40), key='-MESSAGE-')],
		[sg.Text("Status"), sg.InputCombo(["Unresolved", "Resolved"], key='-STATUS-')],
		[sg.Text("Fault type"), sg.In(size=(25, 1), key='-TYPE-')],
		[sg.Text("Location"), sg.In(size=(25, 1), key='-LOCATION-')],
		[sg.Text("Sensor ID"), sg.In(size=(25, 1), key='-SENSOR ID-')],
		[sg.Text("Sensor type"), sg.In(size=(25, 1), key='-SENSOR TYPE-')],
		[sg.Text("Time of fault", tooltip="dd-mm-yy hh:mm:ss"), sg.In(size=(25, 1), key='-START-')],
		[sg.Text("Time of solution", tooltip="dd-mm-yy hh:mm:ss"), sg.In(size=(25, 1), key='-END-')],
		[sg.Text("Voyage"), sg.In(size=(25, 1), key='-VOYAGE-')],
		[sg.Button("Save", enable_events=True, key='-LOG SAVE-'),
		 sg.Button("Cancel", enable_events=True, key='-LOG CANCEL-')]
	]

	log_window = sg.Window("LLMSDID - Log some downtime",
						  layout=log_layout,
						  margins=(200, 100),
						  grab_anywhere=True,
						  default_button_element_size=(12, 1)
						  )
	while True:
		log_event, log_values = log_window.read()

		if log_event == '-LOG SAVE-':
			database.save_to_downtime(log_values['-VOYAGE-'], log_values['-START-'], log_values['-END-'], log_values['-REASON-'],
						 log_values['-ASSOSCIATED ERROR-'], log_values['-DOWNTIME ID)
			log_window.close()
			break

		# If the user closes the window, exit this loop so that the program can close
		if log_event == sg.WIN_CLOSED or log_event == '-LOG CANCEL-':
			log_window.close()
			break
	SaveToDowntime(voyage, stopTime, startTime, reason, assosciatedError, downtimeID)

# Main window layout
main_column_1 = sg.Column([[sg.Frame('Advanced search', [[sg.Column([[sg.Text("Voyage: ", tooltip = "Let me know which voyage you'd like to see the errors for."), sg.In(size = (15, 1), pad = ((34, 0), (0, 0)), key = '-VOYAGE SEARCH-')],
																[sg.Text("Status: ", tooltip = "Would you like to look at errors we've already solved? Let me know here!"), sg.In(size = (15, 1), pad = ((40, 0), (0, 0)), key = '-STATUS SEARCH-')],
																[sg.Text("Fault type: ", tooltip = "Here you can let me know what type of fault you'd like to search for."), sg.In(size = (15, 1), pad = ((20, 0), (0, 0)), right_click_menu = ("Cable", "Hardware", "Sensor", "Connector"), key = '-TYPE SEARCH-')],
																[sg.Text("Fault location: ", tooltip = "If you suspect that your fault might be location-specific, say so here to see previous errors that have occurred in that location."), sg.In(size = (15, 1), pad = ((0, 0), (0, 0)), key = '-LOCATION SEARCH-')],
																[sg.Text("Sensor ID: ", tooltip = "Think that your error could be sensor-specific? Find previous issues with your exact sensor by entering it's asset number here."), sg.In(size = (15, 1), pad = ((21, 0), (0, 0)), key = '-SENSOR ID SEARCH-')],
																[sg.Text("Sensor type: ", tooltip = "Search for previous errors that have been encountered with your specific type of sensor."), sg.In(size = (15, 1), pad = ((8, 0), (0, 0)), key = '-SENSOR TYPE SEARCH-')],
																[sg.Text("From: ", tooltip = "Enter the start date for your search."), sg.In(size = (15, 1), pad = ((48, 0), (0, 0)), key = '-FROM SEARCH-')],
																[sg.Text("To: ", tooltip = "Enter the end date for your search."), sg.In(size = (15, 1), pad = ((64, 0), (0, 0)), key = '-TO SEARCH-')],
																[sg.Button("Search errors", size = (12, 1), pad = ((93, 0), (7, 0)), enable_events=True, tooltip = "Press me if you'd like to search for specific error characteristics.",key = '-SEARCH ERROR-')]], pad = (3, 3))]])]])

# TODO Add a downtime graph
main_column_2 = sg.Column([[sg.Frame('Faults:', [[sg.Column([[sg.Listbox(unresolved_errors, enable_events = True, size=(20, len(unresolved_errors)), key = '-ERROR LIST-')]]),
														sg.Column([[sg.Text("Error ID: ", size=(14,1)), sg.Text("", size=(20,1), key='-OUT ID-')],
																   [sg.Text("Error Description: ", size=(14,15)), sg.Multiline("", size=(20,15), key='-OUT DESC-')],
																   ]) ],
													   [sg.Button("Update", enable_events = True, tooltip = "Press me if you'd like to update some of the information about the selected error.", key = '-UPDATE ERROR-'),
														sg.Button("Give me more!", enable_events = True, tooltip = "Press me if you'd like to view all the information about this specific error.", key = '-SHOW ME MORE-')]], pad=(0, 0))]])

main_column_3 = sg.Column([[sg.Frame('Actions', [[sg.Column([[sg.Button("Log a new error", enable_events=True, tooltip = "Press me if you'd like to log a new error.", key = '-LOG ERROR-'),
														  sg.Button("Log some downtime", enable_events=True, tooltip="Press me if you'd like to log system downtime as a result of a logged error.", key='-LOG DOWNTIME-')]])]])]])

main_layout = [[main_column_1, main_column_2], [main_column_3]]

main_window = sg.Window("LLMSDID - Home",
					   layout = main_layout,
					   margins = (200, 100),
					   grab_anywhere=True,
					   default_button_element_size=(12, 1))


if __name__ == "__main__":

	# Login to database before entering into GUI
	db_object = create_login_window()

	while True:
		event, values = main_window.read()

		update_query = "SELECT FaultID, FaultDescription FROM errors WHERE FaultStatus = 'Unresolved'"
		unresolved_errors = db_object.fetch(update_query)
		main_window['-ERROR LIST-'].update(unresolved_errors)
		main_window.refresh() # ToDo this still isn't working
		
		if values['-ERROR LIST-']:
			selected_error = values['-ERROR LIST-'][0]
			error_sel_flag = True
			fetch_query = "SELECT * FROM errors WHERE FaultId = " + str(selected_error[0])
			current_error_list = db_object.fetch(fetch_query)
			
			current_error['fault_id'] = current_error_list[0][0]
			current_error['fault_status'] = current_error_list[0][1]
			current_error['fault_description'] = current_error_list[0][2]
			current_error['voyage'] = current_error_list[0][3]
			current_error['time_of_fault'] = current_error_list[0][4]
			current_error['time_of_solution'] = current_error_list[0][5]
			current_error['fault_type'] = current_error_list[0][6]
			current_error['location'] = current_error_list[0][7]
			current_error['sensor_id'] = current_error_list[0][8]
			current_error['sensor_type'] = current_error_list[0][9]
			current_error['fault_message'] = current_error_list[0][10]
			current_error['log_date'] = current_error_list[0][11]

			main_window['-OUT ID-'].update(current_error['fault_id'])
			main_window['-OUT DESC-'].update(current_error['fault_description'])

		if event == '-UPDATE ERROR-':
			if guest_user_flag:
				print("User does not have privileges to update issues")
			else:
				if error_sel_flag:
					create_update_window(current_error, db_object) # MEEP: point to db_object?
				else:
					# ToDo: Add a system feedback window instead of putting this in the out id textbox
					main_window['-OUT ID-'].update("Please select a fault for us to update.")
					print("No fault selected")
		
		if event == '-LOG ERROR-':
			if guest_user_flag:
				print("User does not have privileges to log an error")
			else:
				create_log_window(db_object)
				# TODO Set current issue as logged issue if it is unresolved

		if event == '-SEARCH ERROR-':
			print("Functionality is still being implemented")
			# Could do this with a list/tuple

		if event == '-SHOW ME MORE-':
			if error_sel_flag:
				create_more_window(current_error, db_object)
			else:
				main_window['-OUT ID-'].update("Please select a fault for us to have a look at.")
				print("No fault selected")

		if event == '-LOG DOWNTIME':
			if(guest_user_flag):
				print("User does not have privileges to log downtime")
			else:
				create_downtime_window(db_object)

		if event == sg.WIN_CLOSED:
			break