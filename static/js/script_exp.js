const ppm = 400; // Pixeles por metro


const queryString = window.location.search;
console.log(queryString);

const urlParams = new URLSearchParams(queryString);

const constants = ["kpl", "kil", "kdl", "kpa", "kia", "kda" ];
constants.forEach(updateConstants);

// window.addEventListener('beforeunload', reset);

function reset(){
    var inputs = document.getElementsByTagName("input");
    for (var i=0 ,max=inputs.length; i<max; i++){
            if (inputs[i].type == "number")
            {
                inputs[i].value = 0;
            }
    }
    ArduinoConstants();
    setTimeout(() => { MotorSpeeds(); }, 500);
    setTimeout(() => { mainControlConstants(); }, 1000);
}

function updateConstants(k, index, array) {
    if (urlParams.has(k))
    {
        document.getElementById(k).value = urlParams.get(k);
    }
}

let elem = document.getElementById("labcam");
elem.onclick = function clickEvent(e){
    setRef(e);
    }

async function setRef(e){
    let elem = document.getElementById("labcam");
    console.log("Click enviado");
    var rect = e.target.getBoundingClientRect();
    var x = (e.clientX - rect.left);
    var y = (e.clientY - rect.top);
    var new_x = x*640/elem.clientWidth;
    var new_y = y*480/elem.clientHeight;

    console.log("(" + new_x + "," + new_y + ")");

    await fetch('/setRef/' + new_x + "/" + new_y);
}

function SetConstants(){
    // set_constants?kpl=0&kil=0&kdl=0&kpa=0&kia=0&kda=0
    console.log("Constantes Seteadas");
    let kpl = document.getElementById("kp_l").value;
    let kil = document.getElementById("ki_l").value;
    let kdl = document.getElementById("kd_l").value;
    let kpa = document.getElementById("kp_a").value;
    let kia = document.getElementById("ki_a").value;
    let kda = document.getElementById("kd_a").value;
    fetch ('/experiencia_base_movil/set_constants'+'?kpl='+kpl+'&kil='+kil+'&kdl='+kdl+'&kpa='+kpa+'&kia='+kia+'&kda='+kda);
}

function getExpData(){
    fetch('/experiencia_base_movil/exp_data')
    .then(function (response) {
        return response.json();
    }).then(function (data) {
        console.log('GET response text:');
        console.log(data); // Print the greeting as text
        if ('error_lineal' in data)
        {
            document.getElementById('error_dist').value = data['error_lineal']/ppm;  
            document.getElementById('error_ang').value = data['error_angular']*180/Math.PI;  
        }
        // if ('ref' in data)
        // {
        //     document.getElementById('ref_x').value = data['ref'][0];
        //     document.getElementById('ref_y').value = data['ref'][1];
        // } 
    });
}

function getArdData(){
    fetch('/experiencia_base_movil/ard_data')
    .then(function (response) {
        return response.json();
    }).then(function (data) {
        console.log('GET response text:');
        console.log(data); // Print the greeting as text
        if ('M1' in data)
        {
            document.getElementById('M1').value = data['M1']/ppm;  
            document.getElementById('M2').value = data['M2']*180/Math.PI;  
        }
        if ('vel1' in data)
        {
            document.getElementById('vel1').value = data['vel1'][0];
            document.getElementById('vel2').value = data['vel2'][1];
        } 
    });
}

reset();
setInterval(getExpData, 1000);
setInterval(getArdData, 1000);