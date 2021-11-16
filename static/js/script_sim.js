console.log("Hola!")
var socket = io();

const ppm = 400; // Pixeles por metro

socket.on('connect', function() {
    socket.send('User has connected!');
    console.log("User has connected");
});

socket.on('message', function(msg) {
    let x,y, theta;
    x 	  = msg['x'];
    y 	  = msg['y'];
    theta = msg['theta'];
    updateState(x, y, theta);
});

function send(){

    socket.emit('update',
    {
        'value':0
    })
}

//sending = setInterval(send, 1000)
sending = setInterval(send, 20)


function setConstants()
{
    kp_l = document.getElementById('kp_l').value;
    kd_l = document.getElementById('kd_l').value;
    ki_l = document.getElementById('ki_l').value;
    kp_a = document.getElementById('kp_a').value;
    kd_a = document.getElementById('kd_a').value;
    ki_a = document.getElementById('ki_a').value;
    fetch('/set_constants/'+kp_l+'/'+kd_l+'/'+ki_l+'/'+kp_a+'/'+kd_a+'/'+ki_a);
}

function updateState(x, y, theta)
{
    var elem = document.getElementById("botin");
    // console.log("Robot a " + x + ", " + y );

    elem.style.left = ppm*x + 'px';
    elem.style.top = ppm*y + 'px';
    elem.style.transform = "rotate(" + theta* 180 / Math.PI + "deg)";

    return;
}

function load(){
    console.log("Ejecutando Load");
    let elem = document.getElementById("field");
    elem.onclick = function clickEvent(e){
        setGoal(e);
    }
}

function setGoal(e){
    console.log("Set Goal ejecutado");
    console.log(e);
    var rect = e.target.getBoundingClientRect();
    var x = (e.clientX - rect.left)/ppm;
    var y = (e.clientY - rect.top)/ppm;
    console.log("(" + x + "," + y + ")");
    goal = document.getElementById("goal")
    goal.style.left = x*ppm + 'px';
    goal.style.top = y*ppm + 'px';
    goal.style.visibility = 'visible';

    fetch('/setGoal/' + x + "/" + y);
    setConstants()
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

}