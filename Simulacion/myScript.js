document.addEventListener('keydown', recordKey);
let x,y, theta;
x = 0;
y = 0;
theta = 0;
function recordKey(e) {
    var elem = document.getElementById("myAnimation"); 
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

var id = null;
function color() {
  var elem = document.getElementById("myAnimation");   
  elem.style.background = 'blue'; 
}