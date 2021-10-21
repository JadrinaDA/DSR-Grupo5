char msgEnd = '\r\n';
String instruccion;
bool newMsg = false;

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
  Serial.begin(9600);   // Inicializamos  el puerto serie
  Serial3.begin(38400);
}

void loop()
{
  
  if (Serial3.available() > 0) {
    instruccion = readBuff(); //Leer el mensaje entrante
    Serial.print("Mensaje recibido: ");
    Serial.println(instruccion);
  }

}
