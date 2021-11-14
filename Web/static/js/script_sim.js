const kpa = document.getElementById("kp_a");

kpa.addEventListener('change', setConstants)

document.getElementById("kp_a").addEventListener('change', setConstants)
document.getElementById("ki_a").addEventListener('change', setConstants)
document.getElementById("kd_a").addEventListener('change', setConstants)
document.getElementById("kp_l").addEventListener('change', setConstants)
document.getElementById("ki_l").addEventListener('change', setConstants)
document.getElementById("kd_l").addEventListener('change', setConstants)

document.getElementById("kp_a").onchange = function(){setConstants};
document.getElementById("ki_a").onchange = function(){setConstants};
document.getElementById("kd_a").onchange = function(){setConstants};
document.getElementById("kp_l").onchange = function(){setConstants};
document.getElementById("ki_l").onchange = function(){setConstants};
document.getElementById("kd_l").onchange = function(){setConstants};

console.log("Hola!")
var socket = io.connect('http://127.0.0.1:5000');

const ppm = 400; // Pixeles por metro

socket.emit('get_parameters',
{
    'value':0
});

var field_par;

socket.on('parameters', function(msg)
{
    console.log("Recibi mis parametros");
    par = JSON.parse(msg);
    field_par = par.field;
    robot_par = par.robot

    field = document.getElementById('field');
    field.style.width = field_par.width*ppm+"px";
    field.style.height = field_par.height*ppm+"px";

    robot = document.getElementById('botin');
    robot.style.width = robot_par.width*ppm+"px";
    robot.style.height = robot_par.height*ppm+"px";

    frente = document.getElementById("frente_botin");
    frente.style.height = "5px";
    frente.style.marginTop = (robot_par.height*ppm - 5) / 2 + "px";

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
sending = setInterval(send, 40)


function setConstants()
{
    kp_l = document.getElementById('kp_l').value;
    kd_l = document.getElementById('kd_l').value;
    ki_l = document.getElementById('ki_l').value;
    kp_a = document.getElementById('kp_a').value;
    kd_a = document.getElementById('kd_a').value;
    ki_a = document.getElementById('ki_a').value;
    console.log("constantes seteadas");
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