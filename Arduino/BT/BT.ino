char msgEnd = '\r\n';
String instruccion;
bool newMsg = false;
#include "DualVNH5019MotorShield.h"
#include "ArduinoJson.h"
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
float ref_0;
float ref_1;

// Definición de referencia
float ref0 = 0;
float ref1 = 0;

// Definición de errores y velocidades
float vel0;
float vel1;
float error_acumulado0 = 0;
float error_acumulado1 = 0;
float newerror0 = 0;
float newerror1 = 0;
float olderror0 = 0;
float olderror1 = 0;

// Constantes angulares y lineales.
float Kp_angular = 2;
float Ki_angular = 0;
float Kd_angular = 0;
float Kp_lineal = 0;
float Ki_lineal = 0;
float Kd_lineal = 0;

// Diccionario a enviar por BT
DynamicJsonDocument dict(1024);
char json_dict[1024]; 

unsigned long previousMillis = millis();
int sending_inverval = 1000; // ms

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

  unsigned long currentMillis = millis();
  
  
  if ((micros() - time_ant) >= Period)
  {
    newtime = micros();


  if (Serial3.available() > 0) 
  {
    instruccion = readBuff(); //Leer el mensaje entrante
    Serial.println(instruccion);
    int i;
    int j = 0;
    int l = 0;
    int n = 0;

    
    // Instrucción de seteo de constantes instruccion = "KS{Kp}${Ki}${Kd}$"
  
    if (instruccion.substring(0, 3) == "KSD")
    {
      // Setear las constantes
      j = return_pos(3, instruccion.length(), instruccion);
      Kp_lineal = instruccion.substring(3,j).toFloat();

      l = return_pos(j+1, instruccion.length(), instruccion);
      Ki_lineal = instruccion.substring(j+1,l).toFloat();

      n = return_pos(l+1, instruccion.length(), instruccion);
      Kd_lineal = instruccion.substring(l+1,n).toFloat();
    }

 /// Seteo constantes angulares
    if (instruccion.substring(0, 3) == "KSA")
    {
      // Setear las constantes
      j = return_pos(3, instruccion.length(), instruccion);
      Kp_angular = instruccion.substring(3,j).toFloat();

      l = return_pos(j+1, instruccion.length(), instruccion);
      Ki_angular = instruccion.substring(j+1,l).toFloat();

      n = return_pos(l+1, instruccion.length(), instruccion);
      Kd_angular = instruccion.substring(l+1,n).toFloat();
      Serial.print("kp: ");
      Serial.print(Kp_angular);
      Serial.print(" | ki: ");
      Serial.print(Ki_angular);
      Serial.print(" | kd: ");
      Serial.print(Kd_angular);
    }

// ---- Término seteo constantes ---------------

   // Seteo de referencia
   j = 0;
   if (instruccion.substring(0, 3) == "REF") // Error angular
   {
      
      // Se enviarán los errores, entonces solo es necesario setearlo
      j = return_pos(3, instruccion.length(), instruccion);
      ref_0 = instruccion.substring(3,j).toFloat();
      l = return_pos(j+1, instruccion.length(), instruccion);
      ref_1 = instruccion.substring(j+1,l).toFloat(); 
    }
  }

  int maxu = 250;
  float delta_t = newtime - time_ant;

  //-----------------------------------
    // Actualizando Informacion de los encoders
    newposition0 = encoder0Pos;
    newposition1 = encoder1Pos;
    //-----------------------------------
    // Calculando Velocidad del motor
    float rpm = 31250;
    vel0 = (float)(newposition0 - oldposition0) * rpm / (delta_t); //RPM
    vel1 = (float)(newposition1 - oldposition1) * rpm / (delta_t); //RPM

    newerror0 = ref_0 - vel0;
    newerror1 = ref_1 - vel1;
    
    error_acumulado0  = error_acumulado0 + newerror0;
    error_acumulado1  = error_acumulado1 + newerror1;

    error_acumulado0 =  min(max(error_acumulado0,-maxu/(Ki_angular*delta_t)), maxu/(Ki_angular*delta_t));
    error_acumulado1 =  min(max(error_acumulado1,-maxu/(Ki_angular*delta_t)), maxu/(Ki_angular*delta_t));
    
    oldposition0 = newposition0;
    oldposition1 = newposition1;
    
    int k = (400/350);

    /*
    Serial.print("ref0  ");
    Serial.print(ref_0);
    Serial.print("   error0  ");
    Serial.print(newerror0);
    */
    motorout0 = k*(Kp_angular*(newerror0) + Ki_angular*error_acumulado0*(delta_t) + Kd_angular*((newerror0 - olderror0)/(delta_t)));
    motorout1 = k*(Kp_angular*(newerror1) + Ki_angular*error_acumulado1*(delta_t) + Kd_angular*((newerror1 - olderror1)/(delta_t)));
    /*
    //Serial.println(Kp_angular);
    Serial.print("  motorout0  ");
    Serial.print(motorout0);
    //Serial.println("Estoy en el loop");
    Serial.print("  motorout1  ");
    Serial.print(motorout1);
    Serial.print("  vel0  ");
    Serial.print(vel0);
    //Serial.println("Estoy en el loop");
    Serial.print("  vel1  ");
    Serial.print(vel1);
    */
 
    motorout0 = min(max(motorout0,-maxu), maxu);
    motorout1 = min(max(motorout1,-maxu), maxu);
    md.setM2Speed(motorout1);
    md.setM1Speed(motorout0);
    
    //Serial.println(md.getM1CurrentMilliamps());

    /*
    Serial.print("  motorout0  ");
    Serial.print(motorout0);
    //Serial.println("Estoy en el loop");
    Serial.print("  motorout1  ");
    Serial.println(motorout1);
    */

    dict["M1"] = motorout0;
    dict["M2"] = motorout1;
    dict["vel1"] = vel0;
    dict["vel2"] = vel1;
    dict["ref_vel1"] = ref_0;
    dict["ref_vel2"] = ref_1;
    
    serializeJson(dict, json_dict);

    //Serial3.println(json_dict);
    //Serial3.println("Que ondax");
    //Serial.println(json_dict);
    if(millis() - previousMillis > sending_inverval) {
     previousMillis = millis();
    Serial3.println(json_dict);
    Serial.println(json_dict);
    }
  
  time_ant = newtime;
  olderror0 = newerror0;
  olderror1 = newerror1;
  }
}

// Función que retorna la posición hasta donde está ubicado un número en lo entregado por Bluetooth
float return_pos(int inicio, int length, String string)
{
  int j;
  for(int i = inicio ; i<length ; i++)
  {
    if (string[i] == '$')
        {
          j = i;
          break;
         }
  }
  return j;
}
