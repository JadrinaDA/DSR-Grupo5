const ppm = 400; // Pixeles por metro

let elem = document.getElementById("labcam");
    elem.onclick = function clickEvent(e){
        setRef(e);
    }

async function setRef(e){
    console.log("Click enviado");
    var rect = e.target.getBoundingClientRect();
    var x = (e.clientX - rect.left);
    var y = (e.clientY - rect.top);
    console.log("(" + x + "," + y + ")");

    await fetch('/setRef/' + x + "/" + y);
}