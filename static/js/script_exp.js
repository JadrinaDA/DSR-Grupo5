const ppm = 400; // Pixeles por metro


const queryString = window.location.search;

const urlParams = new URLSearchParams(queryString);

const constants = ["kpl", "kil", "kdl", "kpa", "kia", "kda" ];
constants.forEach(updateConstants);

// window.addEventListener('beforeunload', reset);
let data_arduino = {};
let data_experiencia = {};
let arduino = false ;
let names = {
  'vel1' : 'Referencia y Rapidez de Motor 1',
  'vel2' : 'Referencia y Rapidez de Motor 2',
  'error_angular': 'Error angular en el tiempo',
  'error_lineal' : 'Error de distancia en el tiempo'
}

let eje_y =
{
  'error_lineal' : 'Error de distancia',
  'error_angular' : 'Error angular (°)',
  'vel1' : 'Rapidez motor 1',
  'vel2' : 'Rapidez motor 2'
}
function reset(){
    var inputs = document.getElementsByTagName("input");
    for (var i=0 ,max=inputs.length; i<max; i++){
            if (inputs[i].type == "number")
            {
                inputs[i].value = 0;
            }
    }
    ArduinoConstants();
    /*setTimeout(() => { MotorSpeeds(); }, 500);*/
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
    var rect = e.target.getBoundingClientRect();
    var x = (e.clientX - rect.left);
    var y = (e.clientY - rect.top);
    var new_x = x*640/elem.clientWidth;
    var new_y = y*480/elem.clientHeight;

    await fetch('/setRef/' + new_x + "/" + new_y);
}

function SetConstants(){
    // set_constants?kpl=0&kil=0&kdl=0&kpa=0&kia=0&kda=0
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
        if ('error_lineal' in data)
        {
            var label_list = '';
            document.getElementById('error_dist').value = data['error_lineal']/ppm;  
            document.getElementById('error_ang').value = data['error_angular']*180/Math.PI;
            data['error_angular'] = data['error_angular']*180/Math.PI;  
            data_experiencia = data;
            console.log(data_experiencia);
            addData();
        }
        // if ('ref' in data)
        // {
        //     document.getElementById('ref_x').value = data['ref'][0];
        //     document.getElementById('ref_y').value = data['ref'][1];
        // } 
    });
}
// Creación de gráficos 
// Parte creada por Nico


let trace1 = {
    x: [0],
    y: [0],
    name: 'Error angular',
    type: 'scatter',
    id: ''
    
  };

  var layout = {
    width:750,
    heigth:300,
    title: {
      text:'',
      font: {
        family: "'Montserrat', sans-serif",
        size: 22
      },
      xref: 'paper',
      x: 0.50,
    },
    xaxis: {
      title: {
        text: 'Segundos',
        font: {
          family: "'Montserrat', sans-serif",
          size: 12,
          color: '#7f7f7f'
        }
      },
    },
    yaxis: {
      title: {
        text: '',
        font: {
          family: "'Montserrat', sans-serif",
          size: 12,
          color: '#7f7f7f'
        }
      }
    }
  };
  var trace2 = {
    x: [0],
    y: [0],
    name: 'Referencia',
    type: 'scatter',
    id: ''
    
  };
data_plot = [trace1];
TESTER = document.getElementById('myDiv');
Plotly.newPlot(TESTER, data_plot, layout);
function setDataid()
{
  var id = document.getElementById('mySelect')
  trace1['id'] = id;
}
function addData() 
{
  var id = document.getElementById('mySelect');
  var y_value;

  if (id.value in data_arduino)
  {
    arduino = true;
    y_value = data_arduino[id.value];
    data_plot = [trace1, trace2];
    // if (id.value == 'vel1')
    // {
    //   trace2['x'].push(trace2['x'].slice(-1)[0] + 1);
    //   trace2['y'].push(data_arduino['ref_vel1']);
    // }
    // if (id.value == 'vel2')
    // {
    //   trace2['x'].push(trace2['x'].slice(-1)[0] + 1);
    //   trace2['y'].push(data_arduino['ref_vel2']);
    // }
  }
  else
  {
    arduino = false;
    y_value = data_experiencia[id.value];
    data_plot = [trace1];
  }
  if (id.value != trace1['id'])
  { 
      trace1['x'] = [0];
      trace1['y'] = [0];
      trace2['x'] = [0];
      trace2['y'] = [0];
      trace1['id'] = id.value;
      layout.title = names[id.value];
      trace1.name = name[id.value];
      layout.yaxis['title']['text']= eje_y[id.value];
  }
  if (trace1['x'].length >= 30)
  {
    if (arduino)
    {
      trace2['x'].push(trace2['x'].slice(-1)[0] + 1);
      if (id.value == 'vel1')
      {
        trace2['y'].push(data_arduino['ref_vel1']);
      }
      else(id.value == 'vel2')
      {
        trace2['y'].push(data_arduino['ref_vel2']);
      }
      
      trace2['x'].shift();
      trace2['y'].shift();
    }
    trace1['x'].push(trace1['x'].slice(-1)[0] + 1);
    trace1['y'].push(y_value);
    trace1['x'].shift();
    trace1['y'].shift();
  }
  else
  {
    trace1['x'].push(trace1['x'].slice(-1)[0] + 1);
    trace1['y'].push(y_value);
    if (arduino)
    {
      if (id.value == 'vel1')
      {
        trace2['y'].push(data_arduino['ref_vel1']);
      }
      else{
        trace2['y'].push(data_arduino['ref_vel2']);
      }
    trace2['x'].push(trace2['x'].slice(-1)[0] + 1);
    
    }
  }


  
  Plotly.newPlot('myDiv', data_plot, layout);
}




function getArdData(){
    fetch('/experiencia_base_movil/ard_data')
    .then(function (response) {
        return response.json();
    }).then(function (data) {
        if ('M1' in data)
        {
            document.getElementById('M1').value = data['M1']/ppm;  
            document.getElementById('M2').value = data['M2']*180/Math.PI;
            data_arduino = data;
            console.log(data);
            addData();
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