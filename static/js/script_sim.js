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
    controler.SetLinearConstants(kp_l, kd_l, ki_l);
    controler.SetAngularConstants(kp_a, kd_a, ki_a);
    await fetch('/set_constants/'+kp_l+'/'+kd_l+'/'+ki_l+'/'+kp_a+'/'+kd_a+'/'+ki_a);
}

function updateState()
{
    controler.Update();
    var elem = document.getElementById("botin");
    var state = robot.GetSensor();
    var x = state[0];
    var y = state[1];
    var theta = state[2]; 

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


async function setGoal(e){
    console.log("Set Goal ejecutado");
    console.log(e);
    var rect = e.target.getBoundingClientRect();
    var x = (e.clientX - rect.left)/ppm;
    var y = (e.clientY - rect.top)/ppm;
    goal = document.getElementById("goal")
    goal.style.left = xg*ppm + 'px';
    goal.style.top = yg*ppm + 'px';
    goal.style.visibility = 'visible';

    controler.SetReference(x,y);
    setConstants();

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

