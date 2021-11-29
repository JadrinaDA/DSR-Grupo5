char msgEnd = '\r\n';
String instruccion;
bool newMsg = false;
#include "DualVNH5019MotorShield.h"
DualVNH5019MotorShield md;
// Definición de PINs
#define encoder0PinA  19
#define encoder0PinB  18
#define encoder1PinA  20
#define encoder1PinB  21

// Variables Tiempo
unsigned long time_ant = 0;
const int Period = 10000;   // 10 ms = 100Hz
float escalon = 0;
const float dt = Period *0.000001f;
float motorout    = 0.0;

// Variables de los Encoders y posicion
volatile long encoder0Pos = 0;
volatile long encoder1Pos = 0;
long newposition0;
long oldposition0 = 0;
long newposition1;
long oldposition1 = 0;
unsigned long newtime;


float ref0 = 0;
float ref1 = 0;


float vel0;
float vel1;
float error_acumulado0 = 0;
float error_acumulado1 = 0;
float newerror0 = 0;
float newerror1 = 0;
float olderror0 = 0;
float olderror1 = 0;

float Kp_angular = 0;
float Ki_angular = 0;
float Kd_angular = 0;
//-----------------------------------
// CONFIGURANDO INTERRUPCIONES
void doEncoder0A()
{
  if (digitalRead(encoder0PinA) == digitalRead(encoder0PinB)) {
    encoder0Pos++;
  } else {
    encoder0Pos--;
  }
}

void doEncoder0B()
{
  if (digitalRead(encoder0PinA) == digitalRead(encoder0PinB)) {
    encoder0Pos--;
  } else {
    encoder0Pos++;
  }
}

void doEncoder1A()
{
  if (digitalRead(encoder1PinA) == digitalRead(encoder1PinB)) {
    encoder1Pos++;
  } else {
    encoder1Pos--;
  }
}

void doEncoder1B()
{
  if (digitalRead(encoder1PinA) == digitalRead(encoder1PinB)) {
    encoder1Pos--;
  } else {
    encoder1Pos++;
  }
}

String readBuff() {
  String buffArray;

  while (Serial3.available() > 0) { //Entro a este while mientras exista algo en el puerto serial
    char buff = Serial3.read(); //Leo el byte entrante
    if (buff == msgEnd) {
      newMsg = true;
      break; //Si el byte entrante coincide con mi delimitador, me salgo del while
    } else {
      buffArray += buff; //Si no, agrego el byte a mi string para construir el mensaje
    }
    delay(10);
  }

  return buffArray;  //Retorno el mensaje
}

void setup()
{
  Serial.begin(115200);   // Inicializamos  el puerto serie
  Serial3.begin(38400);



    // Configurar MotorShield
    md.init();

  // Configurar Encoders
  pinMode(encoder0PinA, INPUT);
  digitalWrite(encoder0PinA, HIGH);       // Incluir una resistencia de pullup en le entrada
  pinMode(encoder0PinB, INPUT);
  digitalWrite(encoder0PinB, HIGH);       // Incluir una resistencia de pullup en le entrada
  pinMode(encoder1PinA, INPUT);
  digitalWrite(encoder1PinA, HIGH);       // Incluir una resistencia de pullup en le entrada
  pinMode(encoder1PinB, INPUT);
  digitalWrite(encoder1PinB, HIGH);       // Incluir una resistencia de pullup en le entrada
  attachInterrupt(digitalPinToInterrupt(encoder0PinA), doEncoder0A, CHANGE);  // encoder 0 PIN A
  attachInterrupt(digitalPinToInterrupt(encoder0PinB), doEncoder0B, CHANGE);  // encoder 0 PIN B
  attachInterrupt(digitalPinToInterrupt(encoder1PinA), doEncoder1A, CHANGE);  // encoder 1 PIN A
  attachInterrupt(digitalPinToInterrupt(encoder1PinB), doEncoder1B, CHANGE);  // encoder 1 PIN B
  
}

void loop()
{
  float motorout0;
  float motorout1;

  
  if ((micros() - time_ant) >= Period)
  {
    newtime = micros();


  if (Serial3.available() > 0) {
    instruccion = readBuff(); //Leer el mensaje entrante
    Serial.println(instruccion);
    float Kp;

    
    // Anterior
    //float Kp2;
   // float Ki;
   // float Kd;
    //Kp = instruccion.substring(0, 4).toFloat();
    //Kp2 = instruccion.substring(4, 8).toFloat();
   // Ki = instruccion.substring(3, 6).toFloat();
   // Kd = instruccion.substring(6, 9).toFloat();
    //md.setM1Speed(Kp);
    //md.setM2Speed(-Kp2);
    //Serial.println();
  //}
    
    float Ki;
    float Kd;
    


    int i;
    int j = 0;
    int l = 0;
    int n = 0;
     
    // Instrucción de seteo de constantes instruccion = "KS{Kp}${Ki}${Kd}$"

    if (instruccion.substring(0, 3) == "KSD")
    {
      // Setear las constantes

      for (i = 3; i< instruccion.length(); i++)
      {
        if (instruccion[i] == '$')
        {
          j = i;
          break;
         }
       }
    Kp = instruccion.substring(3,j).toFloat();

    for (i=j+1; i< instruccion.length(); i++)
    {
        if (instruccion[i] == '$')
        {
          l = i;
          break;
        }
    }
    Ki = instruccion.substring(j+1,l).toFloat();

    for (i=l+1; i< instruccion.length(); i++)
      {
        if (instruccion[i] == '$')
        {
          n = i;
          break;
        }
      }
    Kd = instruccion.substring(l+1,n).toFloat();
    }



 /// Seteo constantes angulares
    if (instruccion.substring(0, 3) == "KSA")
    {
      // Setear las constantes

      for (i = 3; i< instruccion.length(); i++)
      {
        if (instruccion[i] == '$')
        {
          j = i;
          break;
         }
       }
    Kp_angular = instruccion.substring(3,j).toFloat();
    Serial.println(Kp_angular);

    for (i=j+1; i< instruccion.length(); i++)
    {
        if (instruccion[i] == '$')
        {
          l = i;
          break;
        }
    }
    Ki_angular = instruccion.substring(j+1,l).toFloat();
    Serial.println(Ki_angular);
    for (i=l+1; i< instruccion.length(); i++)
      {
        if (instruccion[i] == '$')
        {
          n = i;
          break;
        }
      }
    Kd_angular = instruccion.substring(l+1,n).toFloat();
    Serial.println(Kd_angular);
    }

// ---- Término seteo constantes ---------------

   // Seteo de referencia
   j = 0;
   if (instruccion.substring(0, 3) == "ERA") // Error angular
   {
      // Se enviarán los errores, entonces solo es necesario setearlo

      for (i = 3; i< instruccion.length(); i++)
      {
        if (instruccion[i] == '$')
        {
          j = i;
          break;
         }
       }
    newerror0 = instruccion.substring(3,j).toFloat();
    newerror1 = instruccion.substring(3,j).toFloat();
      
    }
   }
    //Kp = instruccion.substring(0, 4).toFloat();
    //Kp2 = instruccion.substring(4, 8).toFloat();
   // Ki = instruccion.substring(3, 6).toFloat();
   // Kd = instruccion.substring(6, 9).toFloat();
    //Serial.println(instruccion);
    

  //-----------------------------------
    // Actualizando Informacion de los encoders
    newposition0 = encoder0Pos;
    newposition1 = encoder1Pos;


    //-----------------------------------
    // Calculando Velocidad del motor

    
    
//    if ((newtime / 5000000) % 2){
//      ref0 = 100.0;
//      ref1 = -100.0;}
//    else{
//      ref0 = 50.0;
//      ref1 = -50.0;}


    float rpm = 31250;
    vel0 = (float)(newposition0 - oldposition0) * rpm / (newtime - time_ant); //RPM
    vel1 = (float)(newposition1 - oldposition1) * rpm / (newtime - time_ant); //RPM

    //newerror0 = ref0 - vel0;
    //newerror1 = ref1 - vel1;

    error_acumulado0  = error_acumulado0 + newerror0;
    error_acumulado1  = error_acumulado1 + newerror1;
    oldposition0 = newposition0;
    oldposition1 = newposition1;
    

    int k = (400/350);


    motorout0 = k*(Kp_angular*(newerror0) + Ki_angular*error_acumulado0*(newtime - time_ant) + Kd_angular*((newerror0 - olderror0)/(newtime - time_ant)));
    motorout1 = k*(Kp_angular*(newerror1) + Ki_angular*error_acumulado1*(newtime - time_ant) + Kd_angular*((newerror1 - olderror1)/(newtime - time_ant)));
    Serial.println(Kp_angular);
    Serial.println(newerror0);

    md.setM1Speed(motorout0);
    md.setM2Speed(motorout1);
    //Serial.print("Encoder position 0:");
    //Serial.print(newposition0);
    //Serial.print(" Encoder position 1:");
    //Serial.println(newposition1);
    //Serial.print(escalon);
    //Serial.print(",");

    
//    Serial.print("Velocidad 0: ");
//    Serial.print(vel0);
//    Serial.print("Velocidad 1: ");
//    Serial.print(-vel1);
//    Serial.println();

    
    //Serial.print(motorout);
    //Serial.print(",");
    //Serial.print(md.getM1CurrentMilliamps());
    //Serial.print(",");
    //Serial.print(md.getM2CurrentMilliamps());
    //Serial.println(",");
 
  time_ant = newtime;
  olderror0 = newerror0;
  olderror1 = newerror1;
}}
