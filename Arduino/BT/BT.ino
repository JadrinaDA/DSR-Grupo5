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
float vel0;
float vel1;
float error_acumulado0 = 0;
float error_acumulado1 = 0;
float newerror0 = 0;
float newerror1 = 0;
float olderror0 = 0;
float olderror1 = 0;

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
    float Kp;
    float Kp2;
   // float Ki;
   // float Kd;
    Kp = instruccion.substring(0, 4).toFloat();
    Kp2 = instruccion.substring(4, 8).toFloat();
   // Ki = instruccion.substring(3, 6).toFloat();
   // Kd = instruccion.substring(6, 9).toFloat();
    md.setM1Speed(Kp);
    md.setM2Speed(-Kp2);
    Serial.println();
  }

  //-----------------------------------
    // Actualizando Informacion de los encoders
    newposition0 = encoder0Pos;
    newposition1 = encoder1Pos;


    //-----------------------------------
    // Calculando Velocidad del motor
          
    float ref0;
    float ref1;
    if ((newtime / 5000000) % 2){
      ref0 = 100.0;
      ref1 = -100.0;}
    else{
      ref0 = 50.0;
      ref1 = -50.0;}

    float rpm = 31250;
    vel0 = (float)(newposition0 - oldposition0) * rpm / (newtime - time_ant); //RPM
    vel1 = (float)(newposition1 - oldposition1) * rpm / (newtime - time_ant); //RPM
    newerror0 = ref0 - vel0;
    newerror1 = ref1 - vel1;
    error_acumulado0  = error_acumulado0 + newerror0;
    error_acumulado1  = error_acumulado1 + newerror1;
    oldposition0 = newposition0;
    oldposition1 = newposition1;
    

    int k = (400/350);
    int kp=5;
    float ki;
    ki = 0.0001;
    float kd;
    kd = 70;
    Serial.println(kd*((newerror0 - olderror0)/(newtime - time_ant)));
    motorout0 = k*(kp*(newerror0) + ki*error_acumulado0*(newtime - time_ant) + kd*((newerror0 - olderror0)/(newtime - time_ant)));
    motorout1 = k*(kp*(newerror1) + ki*error_acumulado1*(newtime - time_ant) + kd*((newerror1 - olderror1)/(newtime - time_ant)));
    md.setM1Speed(motorout0);
    md.setM2Speed(motorout1);
    //Serial.print("Encoder position 0:");
    //Serial.print(newposition0);
    //Serial.print(" Encoder position 1:");
    //Serial.println(newposition1);
    //Serial.print(escalon);
    //Serial.print(",");
    Serial.print("Velocidad 0: ");
    Serial.print(vel0);
    Serial.print("Velocidad 1: ");
    Serial.print(-vel1);
    Serial.println();
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
