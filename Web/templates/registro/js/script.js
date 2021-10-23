document.getElementById("institucion").onchange = changeListenerCar;
document.getElementById("cargo").onchange = changeListenerCar;
document.getElementById("carrera").onchange = changeListenerMaj;
  
  function changeListenerCar(){
    var ins = document.getElementById("institucion").value;
    var cargo = document.getElementById("cargo").value;
    console.log(ins);
    
    if (ins == "UC" && cargo == "alumno"){
        document.getElementById("carrera_div").style.display="block";
    }else{
        document.getElementById("carrera_div").style.display="none";
    }
    
  }

  function changeListenerMaj(){
    var value = this.value
      console.log(value);
      
      if (value == "ing"){
          document.getElementById("major_div").style.display="block";
      }else{
          document.getElementById("major_div").style.display="none";
      }
      
    }