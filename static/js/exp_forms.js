function ArduinoConstants()
					 {
		form = document.getElementById("arduino_constants");
		
		data = {
			kp:form['kp'].value,
			ki:form['ki'].value,
			kd:form['kd'].value
		};
		let json_data = JSON.stringify(data);
		
		fetch('/experiencia_base_movil/arduino_constants', {

		// Declare what type of data we're sending
		headers: {
		'Content-Type': 'application/json'
		},

		// Specify the method
		method: 'POST',

		// A JSON payload
		body: json_data
		}).then(function (response) { // At this point, Flask has printed our JSON
		return response.text();
		});
		
		
	  }

function MotorSpeeds()
					 {
		form = document.getElementById("motor_speeds");

		data = {
			m1:form['m1'].value,
			m2:form['m2'].value,
		};
		let json_data = JSON.stringify(data);
		
		fetch('/experiencia_base_movil/motor_speeds', {

		// Declare what type of data we're sending
		headers: {
		'Content-Type': 'application/json'
		},

		// Specify the method
		method: 'POST',

		// A JSON payload
		body: json_data
		}).then(function (response) { // At this point, Flask has printed our JSON
		return response.text();
		});
		
		
	  }

function mainControlConstants()
					 {
		form = document.getElementById("main_control_constants");

		data = {
            kpl:form['kpl'].value,
			kil:form['kil'].value,
			kdl:form['kdl'].value,

            kpa:form['kpa'].value,
			kia:form['kia'].value,
			kda:form['kda'].value
		};
		let json_data = JSON.stringify(data);
		
		fetch('/experiencia_base_movil/main_control_constants', {

		// Declare what type of data we're sending
		headers: {
		'Content-Type': 'application/json'
		},

		// Specify the method
		method: 'POST',

		// A JSON payload
		body: json_data
		}).then(function (response) { // At this point, Flask has printed our JSON
		return response.text();
		});	
	  }

function OpenCamera()
					 {
		form = document.getElementById("open_camera");

		let data = '8';
		
		fetch('/experiencia_base_movil/open_camera', {

		// Declare what type of data we're sending
		headers: {
		'Content-Type': 'string'
		},

		// Specify the method
		method: 'POST',

		// A JSON payload
		body: data
		}).then(function (response) { // At this point, Flask has printed our JSON
		return response.text();
		});
		
		
	  }

// Constantes Arduino
$(document).on('submit','#arduino_constants',
function(e){
	e.preventDefault();
	ArduinoConstants();
});

// Velocidades Motores
$(document).on('submit','#motor_speeds', 
function(e){
	e.preventDefault();
	MotorSpeeds();
});

// Constantes Control Python
$(document).on('submit','#main_control_constants',
function(e){
	e.preventDefault();
	mainControlConstants();
});

// Abrir camara
$(document).on('submit','#open_camera',
function(e){
	e.preventDefault();
	OpenCamera();
});