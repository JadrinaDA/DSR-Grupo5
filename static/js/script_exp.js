const ppm = 400; // Pixeles por metro

const queryString = window.location.search;
console.log(queryString);

const urlParams = new URLSearchParams(queryString);

const constants = ["kpl", "kil", "kdl", "kpa", "kia", "kda" ];
constants.forEach(updateConstants);

function updateConstants(k, index, array) {
    if (urlParams.has(k))
    {
        document.getElementById(k).value = urlParams.get(k);
    }
}

// if (urlParams.has('kpa'))
// {
//     document.getElementById("kpa").value = urlParams.get('kpa');
// }



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