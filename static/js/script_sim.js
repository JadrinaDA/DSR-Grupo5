<<<<<<< HEAD
const par = {
    "field" : {
        "width": 2,
        "height": 5/4   
    },

    "robot" : {
        "width": 0.15,
        "height": 0.15   
    }
    
}

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


const ppm = 400; // Pixeles por metro

var field_par;

let kp_l = 0;
let kd_l = 0;
let ki_l = 0;
let kp_a = 0;
let kd_a = 0;
let ki_a = 0;
=======
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
    //document.getElementById("topper").innerHTML += "<br>" + "message received";
    updateState(x, y, theta);
});

function send(){

    socket.emit('update',
    {
        'value':0
    })
}
>>>>>>> main

let x = 0;
let y = 0;
let theta = 0;
let reference = [0,0];


field_par = par["field"];
robot_par = par["robot"]

field = document.getElementById('field');
field.style.width = field_par["width"]*ppm+"px";
field.style.height = field_par["height"]*ppm+"px";

let grobot = document.getElementById('botin');
grobot.style.width = robot_par["width"]*ppm+"px";
grobot.style.height = robot_par["height"]*ppm+"px";

let frente = document.getElementById("frente_botin");
frente.style.height = "5px";
frente.style.marginTop = (robot_par["height"]*ppm - 5) / 2 + "px";

let robot = new BaseMovil();
let controler = new MobileBasePID(robot, reference);


async function setConstants()
{
    kp_l = document.getElementById('kp_l').value;
    kd_l = document.getElementById('kd_l').value;
    ki_l = document.getElementById('ki_l').value;
    kp_a = document.getElementById('kp_a').value;
    kd_a = document.getElementById('kd_a').value;
    ki_a = document.getElementById('ki_a').value;
<<<<<<< HEAD
    controler.SetLinearConstants(kp_l, kd_l, ki_l);
    controler.SetAngularConstants(kp_a, kd_a, ki_a);
=======
    await fetch('/set_constants/'+kp_l+'/'+kd_l+'/'+ki_l+'/'+kp_a+'/'+kd_a+'/'+ki_a);
>>>>>>> main
}

function updateState()
{
    controler.Update();
    var elem = document.getElementById("botin");
<<<<<<< HEAD
    var state = robot.GetSensor();
    var x = state[0];
    var y = state[1];
    var theta = state[2]; 
=======
    console.log("Robot a " + x + ", " + y );
>>>>>>> main

    elem.style.left = ppm*x + 'px';
    elem.style.top = ppm*y + 'px';
    elem.style.transform = "rotate(" + theta* 180 / Math.PI + "deg)";

    robot.UpdateState();
    return;
}

function load(){
    console.log("Ejecutando Load");
    let elem = document.getElementById("field");
    elem.onclick = function clickEvent(e){
        setGoal(e);
    }
}

<<<<<<< HEAD
function setGoal(e){
=======
async function setGoal(e){
    console.log("Set Goal ejecutado");
    console.log(e);
>>>>>>> main
    var rect = e.target.getBoundingClientRect();
    var x = (e.clientX - rect.left)/ppm;
    var y = (e.clientY - rect.top)/ppm;
    goal = document.getElementById("goal")
    goal.style.left = x*ppm + 'px';
    goal.style.top = y*ppm + 'px';
    goal.style.visibility = 'visible';

<<<<<<< HEAD
    controler.SetReference(x,y);
    setConstants();
=======
    await fetch('/setGoal/' + x + "/" + y);
    setConstants()
>>>>>>> main
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

update = setInterval(updateState, 10);
