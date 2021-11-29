const ppm = 400; // Pixeles por metro

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