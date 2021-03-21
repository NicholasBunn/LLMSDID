# Packages
import PySimpleGUI as sg
import mysql.connector
# MEEP - run python script on startup
# MEEP Startup mysql server on script initialisation
# TODO Close Mysql server and python script on window close

errorSelFlag = False
guestUserFlag = False
unresolvedErrors = []

# TODO Implement theme selector
# Set Theme
sg.LOOK_AND_FEEL_TABLE['DarkOcean'] = {'BACKGROUND': '#000000',
                                        'TEXT': '#FFFFFF',
                                        'INPUT': '#000000',
                                        'TEXT_INPUT': '#FFFFFF',
                                        'SCROLL': '#green',
                                        'BUTTON': ('black', 'teal'),
                                        'PROGRESS': ('pink', 'purple'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        }
sg.LOOK_AND_FEEL_TABLE['SVRG'] = {'BACKGROUND': '#FFFFFF',
                                        'TEXT': '#000000',
                                        'INPUT': 'cyan',
                                        'TEXT_INPUT': '#000000',
                                        'SCROLL': 'cyan',
                                        'BUTTON': ('black', 'Yellow'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
									 	'FRAME': 'red',
                                        }
sg.LOOK_AND_FEEL_TABLE['Agulhas'] = {'BACKGROUND': '#FFFFFF',
                                        'TEXT': '#000000',
                                        'INPUT': 'red',
                                        'TEXT_INPUT': '#000000',
                                        'SCROLL': '#c7e78b',
                                        'BUTTON': ('black', 'red'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
									 	'FRAME': 'red',
                                        }

sg.theme('Agulhas')

sg.set_options(element_padding=(1, 1))

# TODO Tune sizes and placement and make the window look nice
# TODO Implement guest limits
def CreateLoginWindow():
	loginLayout = [[sg.Text('Hostname: '), sg.In(size = (25, 0), key = '-HOST-')],
				   [sg.Text('Username: '), sg.In(size = (25, 0), key = '-USER-')],
				   [sg.Text('Password: '), sg.In(size = (25, 0), pad = (3, 0), password_char = '*', key='-PASS-')],
				   [sg.Button('Login', size = (14, 0),  pad = ((0, 10), (5, 0)), enable_events = True, bind_return_key = True, key = '-LOGIN-'), sg.Button('Guest Login.', size = (14, 0), pad = ((10, 0), (5, 0)), enable_events = True, key = '-LOGIN GUEST-')]
              ]

	loginWindow = sg.Window("LLMSDID - Login",
						  layout=loginLayout,
						  margins=(20, 10),
						  grab_anywhere=True,
						  default_button_element_size=(12, 1)
						  )

	while True:
		loginEvent, loginValues = loginWindow.read()

		# TODO add in and AND for enter keystroke event
		if loginEvent == '-LOGIN-':
			LoginToDB(loginValues['-HOST-'], loginValues['-USER-'], loginValues['-PASS-'])
			loginWindow.close()
			break

		if loginEvent == '-LOGIN GUEST-':
			LoginToDB("localhost", "Guest", "Gu3st")
			global guestUserFlag
			guestUserFlag = True
			loginWindow.close()
			break

		# If the user closes the window, exit this loop so that the program can close
		if loginEvent == sg.WIN_CLOSED:
			loginWindow.close()
			exit(69)

def CreateLogWindow():
	logLayout = [
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

	logWindow = sg.Window("LLMSDID - Log an error",
						  layout = logLayout,
						  margins = (200, 100),
						  grab_anywhere = True,
						  default_button_element_size = (12, 1)
						  )
	while True:
		logEvent, logValues = logWindow.read()

		if  logEvent == '-LOG SAVE-':
			SaveToErrors(logValues['-DESCRIPTION-'], logValues['-MESSAGE-'], logValues['-STATUS-'], logValues['-TYPE-'], logValues['-LOCATION-'], logValues['-SENSOR ID-'], logValues['-SENSOR TYPE-'], logValues['-START-'], logValues['-END-'], logValues['-VOYAGE-'])
			logWindow.close()
			break

		# If the user closes the window, exit this loop so that the program can close
		if logEvent == sg.WIN_CLOSED or logEvent == '-LOG CANCEL-':
			logWindow.close()
			break

def CreateUpdateWindow(selectedFault):
	searchQuery = "SELECT * FROM errors WHERE FaultID = " + str(selectedFault)
	bla = FetchFromErrors(searchQuery)
	updateCol1 = sg.Column([[sg.Frame('Current values', [[sg.Column([[sg.Text("Voyage: ", size=(12,1)), sg.Text(bla[0][3])],
																	  [sg.Text("Status: ", size=(12,1)), sg.Text(bla[0][1])],
																	 [sg.Text("Description: ", size=(12,4)), sg.Multiline(bla[0][2], size=(40, 4))],
																	 [sg.Text("Fault message: ", size=(12,2)), sg.Multiline(bla[0][10], size=(40,2))],
																	  [sg.Text("Fault type: ", size=(12,1)), sg.Text(bla[0][6])],
																	  [sg.Text("Fault location: ", size=(12,1)), sg.Text(bla[0][7])],
																	  [sg.Text("Sensor ID: ", size=(12,1)), sg.Text(bla[0][8])],
																	  [sg.Text("Sensor type: ", size=(12,1)), sg.Text(bla[0][9])],
																	  [sg.Text("From: ", size=(12,1)), sg.Text(bla[0][4])],
																	  [sg.Text("To: ", size=(12,1)), sg.Text(bla[0][5])]],
																	 )]])]])

	updateCol2 = sg.Column([[sg.Frame('Updated values', [[sg.Column([[sg.Text("Voyage: ", size=(12,1)), sg.In(bla[0][3], size=(40,1), key='-NEW VOYAGE-')],
																	  [sg.Text("Status: ", size=(12,1)), sg.InputCombo(["Unresolved", "Resolved"], default_value=bla[0][1], key='-NEW STATUS-')],
																	 [sg.Text("Description: ", size=(12,4)), sg.Multiline(bla[0][2], size=(40,4), key='-NEW DESC-')],
																	 [sg.Text("Fault message: ", size=(12,2)), sg.Multiline(bla[0][10], size=(40,2), key='-NEW MESSAGE-')],
																	  [sg.Text("Fault type: ", size=(12,1)), sg.In(bla[0][6], size=(40,1), key='-NEW FTYPE-')],
																	  [sg.Text("Fault location: ", size=(12,1)), sg.In(bla[0][7], size=(40,1), key='-NEW LOC-')],
																	  [sg.Text("Sensor ID: ", size=(12,1)), sg.In(bla[0][8], size=(40,1), key='-NEW ID-')],
																	  [sg.Text("Sensor type: ", size=(12,1)), sg.In(bla[0][9], size=(40,1), key='-NEW STYPE-')],
																	  [sg.Text("From: ", size=(12,1)), sg.In(bla[0][4], size=(40,1), key='-NEW FROM-')],
																	  [sg.Text("To: ", size=(12,1)), sg.In(bla[0][5], size=(40,1), key='-NEW TO-')]],
																	)]])]])

	updateCol3 = sg.Column([[sg.Frame('Actions', [[sg.Column([[sg.Button("Update", enable_events=True,
																		tooltip="Press me if you'd like to update this fault.",
																		key='-SAVE UPDATE-'),
															  sg.Button("Cancel", enable_events=True,
																		tooltip="Press me if you'd like to cancel this update.",
																		key='-CANCEL UPDATE-')]])]])]])

	updateLayout = [[updateCol1, updateCol2], [updateCol3]]

	updateWindow = sg.Window("LLMSDID - Update",
							layout=updateLayout,
							margins=(200, 100),
							grab_anywhere=True,
							default_button_element_size=(12, 1)
							)

	print("Update " + str(selectedFault))
	while True:
		updateEvent, updateValue = updateWindow.read()

		if updateEvent == '-SAVE UPDATE-':
			UpdateErrors(updateValue['-NEW STATUS-'], updateValue['-NEW DESC-'], updateValue['-NEW VOYAGE-'], updateValue['-NEW FROM-'], updateValue['-NEW TO-'], updateValue['-NEW FTYPE-'], updateValue['-NEW LOC-'], updateValue['-NEW ID-'], updateValue['-NEW STYPE-'], updateValue['-NEW MESSAGE-'], selectedFault)
			updateWindow.close()
			break

		# If the user closes the window, exit this loop so that the program can close
		if updateEvent == sg.WIN_CLOSED or updateEvent == '-CANCEL UPDATE-':
			updateWindow.close()
			break

def CreateMoreWindow(selectedFault):
	fetchQuery = "SELECT * FROM errors WHERE FaultID = " + str(selectedFault)
	print("More " + fetchQuery)
	errorInfo = FetchFromErrors(fetchQuery)
	print(errorInfo)
	moreCol1 = sg.Column([[sg.Frame('Parameter', [[sg.Column([[sg.Text("Fault ID: ")],
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

	moreCol2 = sg.Column([[sg.Frame('Value', [[sg.Column([[sg.Text("Fault ID: ", size=(12,1)), sg.Text(errorInfo[0][0], size=(40,1))],
														  [sg.Text("Voyage: ", size=(12,1)), sg.Text(errorInfo[0][3], size=(40,1))],
														  [sg.Text("Status: ", size=(12,1)), sg.Text(errorInfo[0][1], size=(40,1))],
														  [sg.Text("Description: ", size=(12,4)), sg.Multiline(errorInfo[0][2], size=(40,4))],
														  [sg.Text("Fault message: ", size=(12,2)), sg.Multiline(errorInfo[0][10], size=(40,2))],
														  [sg.Text("Fault type: ", size=(12,1)), sg.Text(errorInfo[0][6], size=(40,1))],
														  [sg.Text("Fault location: ", size=(12,1)), sg.Text(errorInfo[0][7], size=(40,1))],
														  [sg.Text("Sensor ID: ", size=(12,1)), sg.Text(errorInfo[0][8], size=(40,1))],
														  [sg.Text("Sensor type: ", size=(12,1)), sg.Text(errorInfo[0][9], size=(40,1))],
														  [sg.Text("From: ", size=(12,1)), sg.Text(errorInfo[0][4], size=(40,1))],
														  [sg.Text("To: ", size=(12,1)), sg.Text(errorInfo[0][5], size=(40,1))],
														 [sg.Text("Log date: ", size=(12,1)), sg.Text(errorInfo[0][11], size=(40,1))]],
														 )]])]])

	moreCol3 = sg.Column([[sg.Frame('Actions', [[sg.Column([[sg.Button("Thanks", enable_events=True,
																		tooltip="Press me if you're done having a look.",
																		key='-THANKS-')
															  ]])]])]])

	moreLayout = [[moreCol2], [moreCol3]]

	moreWindow = sg.Window("LLMSDID - More",
							 layout=moreLayout,
							 margins=(200, 100),
							 grab_anywhere=True,
							 default_button_element_size=(12, 1)
							 )

	while True:
		moreEvent, moreValue = moreWindow.read()

		# If the user closes the window, exit this loop so that the program can close
		if moreEvent == sg.WIN_CLOSED or moreEvent == '-THANKS-':
			moreWindow.close()
			break

def CreateDowntimeWindow():
	# TODO RETURN Adjust this config for downtime
	logLayout = [
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

	logWindow = sg.Window("LLMSDID - Log an error",
						  layout=logLayout,
						  margins=(200, 100),
						  grab_anywhere=True,
						  default_button_element_size=(12, 1)
						  )
	while True:
		logEvent, logValues = logWindow.read()

		if logEvent == '-LOG SAVE-':
			SaveToErrors(logValues['-DESCRIPTION-'], logValues['-MESSAGE-'], logValues['-STATUS-'], logValues['-TYPE-'],
						 logValues['-LOCATION-'], logValues['-SENSOR ID-'], logValues['-SENSOR TYPE-'],
						 logValues['-START-'], logValues['-END-'], logValues['-VOYAGE-'])
			logWindow.close()
			break

		# If the user closes the window, exit this loop so that the program can close
		if logEvent == sg.WIN_CLOSED or logEvent == '-LOG CANCEL-':
			logWindow.close()
			break
	SaveToDowntime(voyage, stopTime, startTime, reason, assosciatedError, downtimeID)

def LoginToDB(host, user, password):
	print("Login test: " + host, user, password)

	global connection
	connection = mysql.connector.connect(
		host=host,
		user=user,
		passwd=password,
		database="llmsdid"
	)

	print(connection)

	global cursor
	cursor = connection.cursor()

	print(cursor)

def SaveToErrors(description, message, status, type, location, sensorID, sensorType, startTime, endTime, voyage):
	if startTime == '':
		startTime = "NULL"

	if endTime == '':
		endTime = "NULL"

	if status == '':
		status = "Unresolved"

	insertDB = "INSERT INTO errors (FaultDescription, FaultMessage, FaultStatus, FaultType, Location, SensorID, SensorType, TimeOfFault, TimeOfSolution, Voyage) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, '{}')".format(description, message, status, type, location, sensorID, sensorType, startTime, endTime, voyage)
	print(insertDB)

	cursor.execute(insertDB)

	connection.commit()

def SaveToDowntime(voyage, stopTime, startTime, reason, assosciatedError, downtimeID):
	insertDB = ""
	print(insertDB)

	cursor.execute(insertDB)

	connection.commit()

def FetchFromErrors(updateQuery):
	print("Fetch " + str(updateQuery))

	unresolvedErrorList = cursor.execute(updateQuery)
	result = cursor.fetchall()

	return result

def UpdateErrors(faultStatus, faultDesciption, Voyage, TimeOfFault, TimeOfSolution, FaultType, Location, SensorID, SensorType, FaultMessage, FaultID):
	if TimeOfFault == 'None':
		TimeOfFault = "NULL"

	if TimeOfSolution =='None':
		TimeOfSolution = "NULL"

	updateQuery = "UPDATE errors SET FaultStatus = '{}', FaultDescription = '{}', Voyage = '{}', TimeOfFault = {}, TimeOfSolution = {}, FaultType = '{}', Location = '{}', SensorID = '{}', SensorType = '{}', FaultMessage = '{}' WHERE FaultID = {}".format(faultStatus, faultDesciption, Voyage, TimeOfFault, TimeOfSolution, FaultType, Location, SensorID, SensorType, FaultMessage, FaultID)

	print(updateQuery)
	cursor.execute(updateQuery)

	connection.commit()

	print("Updated")

# TODO Sort out right_click_menu
# Main window layout
mainCol1 = sg.Column([[sg.Frame('Advanced search', [[sg.Column([[sg.Text("Voyage: ", tooltip = "Let me know which voyage you'd like to see the errors for."), sg.In(size = (15, 1), pad = ((34, 0), (0, 0)), key = '-VOYAGE SEARCH-')],
																[sg.Text("Status: ", tooltip = "Would you like to look at errors we've already solved? Let me know here!"), sg.In(size = (15, 1), pad = ((40, 0), (0, 0)), key = '-STATUS SEARCH-')],
																[sg.Text("Fault type: ", tooltip = "Here you can let me know what type of fault you'd like to search for."), sg.In(size = (15, 1), pad = ((20, 0), (0, 0)), right_click_menu = ("Cable", "Hardware", "Sensor", "Connector"), key = '-TYPE SEARCH-')],
																[sg.Text("Fault location: ", tooltip = "If you suspect that your fault might be location-specific, say so here to see previous errors that have occurred in that location."), sg.In(size = (15, 1), pad = ((0, 0), (0, 0)), key = '-LOCATION SEARCH-')],
																[sg.Text("Sensor ID: ", tooltip = "Think that your error could be sensor-specific? Find previous issues with your exact sensor by entering it's asset number here."), sg.In(size = (15, 1), pad = ((21, 0), (0, 0)), key = '-SENSOR ID SEARCH-')],
																[sg.Text("Sensor type: ", tooltip = "Search for previous errors that have been encountered with your specific type of sensor."), sg.In(size = (15, 1), pad = ((8, 0), (0, 0)), key = '-SENSOR TYPE SEARCH-')],
																[sg.Text("From: ", tooltip = "Enter the start date for your search."), sg.In(size = (15, 1), pad = ((48, 0), (0, 0)), key = '-FROM SEARCH-')],
																[sg.Text("To: ", tooltip = "Enter the end date for your search."), sg.In(size = (15, 1), pad = ((64, 0), (0, 0)), key = '-TO SEARCH-')],
																[sg.Button("Search errors", size = (12, 1), pad = ((93, 0), (7, 0)), enable_events=True, tooltip = "Press me if you'd like to search for specific error characteristics.",key = '-SEARCH ERROR-')]], pad = (3, 3))]])]])

# TODO Add a downtime graph
mainCol2 = sg.Column([[sg.Frame('Faults:', [[sg.Column([[sg.Listbox(unresolvedErrors, enable_events = True, size=(20, len(unresolvedErrors)), key = '-ERROR LIST-')]]),
														sg.Column([[sg.Text("Error ID: ", size=(14,1)), sg.Text("", size=(20,1), key='-OUT ID-')],
																   [sg.Text("Error Description: ", size=(14,15)), sg.Multiline("", size=(20,15), key='-OUT DESC-')],
																   ]) ],
													   [sg.Button("Update", enable_events = True, tooltip = "Press me if you'd like to update some of the information about the selected error.", key = '-UPDATE ERROR-'),
														sg.Button("Give me more!", enable_events = True, tooltip = "Press me if you'd like to view all the information about this specific error.", key = '-SHOW ME MORE-')]], pad=(0, 0))]])

mainCol3 = sg.Column([[sg.Frame('Actions', [[sg.Column([[sg.Button("Log a new error", enable_events=True, tooltip = "Press me if you'd like to log a new error.", key = '-LOG ERROR-'),
														  sg.Button("Log some downtime", enable_events=True, tooltip="Press me if you'd like to log system downtime as a result of a logged error.", key='-LOG DOWNTIME-')]])]])]])

mainLayout = [[mainCol1, mainCol2], [mainCol3]]

mainWindow = sg.Window("LLMSDID - Home",
					   layout = mainLayout,
					   margins = (200, 100),
					   grab_anywhere=True,
					   default_button_element_size=(12, 1))

# TODO implement __main__ here
'''
1) Ask user for database login details and cache them

2) Create blank dicts for unresolved errors and current error
	- Open DB connection
	- Fill unresolved dict
	- Close DB Connection


while True:
    event, values = main_window.read()
	
	if ERROR LIST SELECT EVENT
		load error info from dict

	if UPDATE ERROR EVENT
		log into DB and update current error dict
		close DB connection
		invoke update for unresolved error dict

	if LOG ERROR EVENT
		log into DB and log error
		close DB connection
		invoke update for unresolved error dict

	if SEARCH ERROR EVENT
		search for error

	if SHOW ME MORE EVENT
		load error info from dict

	if LOG DOWNTIME EVENT
		log into DB and get downtime info
		close DB connection

	if CLOSE EVENT
		close application

'''

# Login to database before entering into GUI
CreateLoginWindow()

# Create an event loop
while True:
	event, values = mainWindow.read()
	
	updateQuery = "SELECT FaultID, FaultDescription FROM errors WHERE FaultStatus = 'Unresolved'"
	unresolvedErrors = FetchFromErrors(updateQuery)
	mainWindow['-ERROR LIST-'].update(unresolvedErrors)

	if values['-ERROR LIST-']:
		selectedError = values['-ERROR LIST-'][0]
		errorSelFlag = True
		fetchQuery = "SELECT FaultID, FaultDescription FROM errors WHERE FaultId = " + str(selectedError[0])
		FetchFromErrors(fetchQuery)
		mainWindow['-OUT ID-'].update(values['-ERROR LIST-'][0][0])
		mainWindow['-OUT DESC-'].update(values['-ERROR LIST-'][0][1])

	if event == '-UPDATE ERROR-':
		if guestUserFlag:
			print("User does not have privileges to update issues")
		else:
			if errorSelFlag:
				CreateUpdateWindow(selectedError[0])
			else:
				mainWindow['-OUT ID-'].update("Please select a fault for us to update.")
				print("No fault selected")

	if event == '-LOG ERROR-':
		if guestUserFlag:
			print("User does not have privileges to log an error")
		else:
			CreateLogWindow()
			# TODO Set current issue as logged issue if it is unresolved

	if event == '-SEARCH ERROR-':
		# TODO Implement error search
		print("TP3")

	if event == '-SHOW ME MORE-':
		if errorSelFlag:
			CreateMoreWindow(selectedError[0])
		else:
			mainWindow['-OUT ID-'].update("Please select a fault for us to have a look at.")
			print("No fault selected")

	if event == '-LOG DOWNTIME-':
		if(guestUserFlag):
			print("User does not have privileges to log downtime")
		else:
			# TODO log downtime
			CreateDowntimeWindow()

	# If the user closes the window, exit this loop so that the program can close
	if event == sg.WIN_CLOSED:
		break