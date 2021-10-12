

  
    
    var socket = io.connect('http://127.0.0.1:5000');
    socket.on('connect', function() {
		socket.send('User has connected!');
	});
    socket.on('message', function(msg) {
        let x,y, theta;
        x 	  = msg['x'];
        y 	  = msg['y'];
        theta = msg['theta'];
        console.log('wena cabros')
        updateStateNico(x, y, theta);
      // Dibujar
    });



document.addEventListener('keydown', recordKey);
let x,y, theta;
x = 0;
y = 0;
theta = 0;
function recordKey(e) {
    var elem = document.getElementById("botin"); 
    console.log("You pressed" + e.key);
    
    switch (e.key) {
        case "Right":
        case "ArrowRight":
    x = x + 10; 
        break

        case "ArrowLeft":
        case "Left":
    x = x - 10;
        break

        case "Up":
        case "ArrowUp":
    y = y - 10; 
        break

        case "ArrowDown":
        case "Down":
    y = y + 10;
        break

        case "d":
    theta = theta + 10;
        break

        case "a":
    theta = theta - 10;
        break
        default:
        return
    }
elem.style.left = x + 'px';
elem.style.top = y + 'px';
elem.style.transform = "rotate(" + theta + "deg)";
console.log("x: "+x);
console.log("theta: "+theta);
console.log("rotate(" + theta + "deg)");
}

function updateState()
{
    var elem = document.getElementById("botin");
    x = document.getElementById("x_pos").value;
    y = document.getElementById("y_pos").value;
    theta = document.getElementById("theta_ang").value;

    console.log("Robot a " + x + ", " + y );

    elem.style.left = x + 'px';
    elem.style.top = y + 'px';
    elem.style.transform = "rotate(" + theta + "deg)";
    console.log("x: "+x);
    console.log("theta: "+theta);
    console.log("rotate(" + theta + "deg)");
    return;
}

function updateStateNico(x, y, theta)
{
    var elem = document.getElementById("botin");
    console.log("Robot a " + x + ", " + y );

    elem.style.left = x + 'px';
    elem.style.top = y + 'px';
    elem.style.transform = "rotate(" + theta* 180 / Math.PI + "deg)";
    console.log("x: "+x);
    console.log("theta: "+y);
    console.log("rotate(" + theta* 180 / Math.PI + "deg)");
    return;
}


var id = null;
function color() {
  var elem = document.getElementById("botin");  
  console.log(getComputedStyle(elem).backgroundColor);
  switch(getComputedStyle(elem).backgroundColor){
      case 'rgb(255, 0, 0)':
        elem.style.background = 'green'; 
        break;
    case 'rgb(0, 128, 0)':
        elem.style.background = 'blue'; 
        break;
    case 'rgb(0, 0, 255)':
        elem.style.background = 'red'; 
        break;
  }


  
  /* socket.on('connect', function() {
      socket.send('User has connected!');
  }); */
}