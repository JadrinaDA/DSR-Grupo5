
    
var socket = io.connect('http://127.0.0.1:5000');

socket.on('connect', function() {
    socket.send('User has connected!');
    console.log("User has connected");
});

socket.on('message', function(msg) {
    let x,y, theta;
    x 	  = msg['x'];
    y 	  = msg['y'];
    theta = msg['theta'];
    updateStateNico(x, y, theta);
    // Dibujar
});

function send(){

    socket.emit('update',
    {
        'value':0
    })
}

sending = setInterval(send, 1)

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
    // console.log("Robot a " + x + ", " + y );

    elem.style.left = x + 'px';
    elem.style.top = y + 'px';
    elem.style.transform = "rotate(" + theta* 180 / Math.PI + "deg)";
    // console.log("x: "+x);
    // console.log("theta: "+y);
    // console.log("rotate(" + theta* 180 / Math.PI + "deg)");
    return;
}

function load(){
    console.log("Ejecutando Load");
    let elem = document.getElementById("field");
    elem.onclick = function clickEvent(e){
        setGoal(e);
    }
    // elem.addEventListener("click",function(){setGoal(e)});
}

function setGoal(e){
    console.log("Set Goal ejecutado");
    console.log(e);
    var rect = e.target.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;
    console.log("(" + x + "," + y + ")");
    goal = document.getElementById("goal")
    goal.style.left = x + 'px';
    goal.style.top = y + 'px';
    goal.style.visibility = 'visible';
}

load();

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