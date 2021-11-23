console.log("Hola!")
var socket = io.connect('http://127.0.0.1:5000');

const ppm = 400; // Pixeles por metro

let kp_l = 0;
let kd_l = 0;
let ki_l = 0;
let kp_a = 0;
let kd_a = 0;
let ki_a = 0;

let x = 0;
let y = 0;
let theta = 0;

console.log("que ondax");
function setConstants()
{
    kp_l = document.getElementById('kp_l').value;
    kd_l = document.getElementById('kd_l').value;
    ki_l = document.getElementById('ki_l').value;
    kp_a = document.getElementById('kp_a').value;
    kd_a = document.getElementById('kd_a').value;
    ki_a = document.getElementById('ki_a').value;
}

function updateState()
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
    var xg = (e.clientX - rect.left)/ppm;
    var yg = (e.clientY - rect.top)/ppm;
    console.log("(" + xg + "," + yg + ")");
    goal = document.getElementById("goal")
    goal.style.left = xg*ppm + 'px';
    goal.style.top = yg*ppm + 'px';
    goal.style.visibility = 'visible';

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


class MobileBasePID {
    constructor(mobile_base, reference, kp_l=0, kd_l=0, ki_l=0, kp_a=0, kd_a=0, ki_a=0, error=np.array([0.0, 0.0]), past_error=np.array([0.0, 0.0]), ac_error=np.array([0.0, 0.0]))
    {
        this.kp_l = kp_l;
        this.kd_l = kd_l;
        this.ki_l = ki_l;
        this.kp_a = kp_a;
        this.kd_a = kd_a;
        this.ki_a = ki_a;
        this.error = error;
        this.past_error = past_error;
        this.ac_error = ac_error;
        this.mobile_base = mobile_base;
        this.reference = reference;
    }

    set_linear_constants(self, kp, kd, ki)
    {
        this.kp_l = kp;
        this.kd_l = kd;
        this.ki_l = ki;
    }

    set_angular_constants(self, kp, kd, ki)
    {
        this.kp_a = kp;
        this.kd_a = kd;
        this.ki_a = ki;
    }

    update_error()
    {
        this.past_error = this.error;
        state = this.mobile_base.GetSensor();
        ref = this.reference;
    }
}

while(true)
{
    console.log("Actualizando estado");
    robot
}