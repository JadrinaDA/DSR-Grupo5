document.addEventListener('keydown', recordKey);
let x,y, theta;
x = 0;
y = 0;
theta = 0;
function recordKey(e) {
    var elem = document.getElementById("botin"); 
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

function updateState()
{
    var elem = document.getElementById("botin");
    x = document.getElementById("x_pos").value;
    y = document.getElementById("y_pos").value;
    theta = document.getElementById("theta_ang").value;

    console.log("Robot a " + x + ", " + y );

    elem.style.left = x + 'px';
    elem.style.top = y + 'px';
    elem.style.transform = "rotate(" + theta + "deg)";
    console.log("x: "+x);
    console.log("theta: "+theta);
    console.log("rotate(" + theta + "deg)");
    return;
}


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