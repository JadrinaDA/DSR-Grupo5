// Constantes Arduino
$(document).on('submit','#arduino_constants',function(e)
					 {
		console.log('hello');
		form = document.getElementById("arduino_constants");

		console.log(form['kp'].value);
		console.log(form['ki'].value);
		console.log(form['kd'].value);
		
		data = {
			kp:form['kp'].value,
			ki:form['ki'].value,
			kd:form['kd'].value
		};
		let json_data = JSON.stringify(data);
				
		e.preventDefault();
		
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
		}).then(function (text) {

		console.log('POST response: ');

		// Should be 'OK' if everything was successful
		console.log(text);
		});
		
		
	  });



// Velocidades Motores
$(document).on('submit','#motor_speeds',function(e)
					 {
		console.log('hello');
		form = document.getElementById("motor_speeds");

		data = {
			m1:form['m1'].value,
			m2:form['m2'].value,
		};
		let json_data = JSON.stringify(data);
				
		e.preventDefault();
		
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
		}).then(function (text) {

		console.log('POST response: ');

		// Should be 'OK' if everything was successful
		console.log(text);
		});
		
		
	  });



// Constantes Control Python
$(document).on('submit','#main_control_constants',function(e)
					 {
		console.log('hello');
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
				
		e.preventDefault();
		
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
		}).then(function (text) {

		console.log('POST response: ');

		// Should be 'OK' if everything was successful
		console.log(text);
		});
		
		
	  });


// Abrir camara
// Constantes Arduino
$(document).on('submit','#open_camera',function(e)
					 {
		console.log('hello');
		form = document.getElementById("open_camera");

		let data = '8';
				
		e.preventDefault();
		
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
		}).then(function (text) {

		console.log('POST response: ');

		// Should be 'OK' if everything was successful
		console.log(text);
		});
		
		
	  });