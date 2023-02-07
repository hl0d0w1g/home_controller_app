#include <Time.h>
#include <Wire.h>
#include <SoftwareSerial.h>
#include <RTClib.h>
#include <LiquidCrystal_I2C.h>

/*
 * Control de los estados de apertura y cierre de una válvula eléctrica
 * a partir de las entradas del sistema.
 *
 * Autor: Cambero Piqueras
 * 12/10/2020
*/

/* Número máximo de registros que se almacenan */
#define maxRegistros 6
/* Valores máximo y mínimo que se pueden programar y que el contador puede alcanzar (en minutos)*/
#define minContador 10
#define maxContador 1440
/* Valor en minutos del tiempo que permanece la pantalla encendida antes de apagarse */
#define tiempoEncendidoPantalla 10

/* Se declara el RTC DS3231 */
RTC_DS3231 rtc;

/* Fecha y hora del RTC */
DateTime fecha;

/* Utilizado para actualizar el reloj una vez por minuto */
int minutoAnterior = 0;

/* Define la estructura que guarda los datos de los registros */
struct registro
{
  DateTime inicio;
  DateTime fin;
  int totalMinutos;
  int totalLitros;
};

/* Almacena los registros */
struct registro registros[maxRegistros];
/* Indica el número de registros almacenados */
int numeroRegistros = 0;
/* Controla que regisgtro se muestra por pantalla de todos los disponibles */
int registroMostrado = 0;

/* Se declara la pantalla LCD */
LiquidCrystal_I2C lcd(0x27, 16, 2);

/* Flag que indica si el micro se ha reiniciado desde la última vez que se usó */
bool reinicio = true;

/* Posibles pantallas por las que se puede navegar en el LCD */
enum pantallas
{
  pPrincipal,
  pRegistros,
  pProgramacion,
  pFecha
};
enum pantallas pantallaActual = pPrincipal;
/* Indica el número total de pantallas disponibles */
const int numeroPantallas = 4;

/* Posibles elementos de la fecha que se pueden editar */
enum eAjusteFecha
{
  anio,
  mes,
  dia,
  hora,
  minuto
};
enum eAjusteFecha elementoAjusteFechaActual = anio;
/* Indica el número total de elemetos en la fecha editables */
const int numeroElementosFecha = 5;

/* Valor programado por el usuario para detener el contador (2h por defecto) */
int programacionContador = 120;
/* Contador del tiempo que lleva activada la señal FLUJO (en minutos) */
int contador = 0;
/* Indica si el contador está activado o no */
bool contadorActivado = false;

/* Pines donde estan las entradas del sistema */
int viviendaPin = 14, riegoPin = 15, flujoPin = 16;
/* Estado de las entradas del sistema */
bool vivienda = false, riego = false;
int flujo = false;

/* Marca el estado anterior de la señal flujo para poder detectar el cambio de 0 a 1 */
int flujoAnterior = false;

/* Pines donde estan las salidas del sistema */
int valvulaPin = 10;
/* Estado de las salidas del sistema */
bool valvula = false;

/* Botón para que le usuario pueda cambiar entre las pantallas disponibles */
int botonCambiarPantallaPin = 7;
/* Botones para subir y bajar, interactuar con los datos */
int botonArribaPin = 8, botonAbajoPin = 9;
/* Estado de los botones */
bool botonCambiarPantalla = false, botonArriba = false, botonAbajo = false;
/* Estado anterior de los botones */
bool botonCambiarPantallaAnterior = false, botonArribaAnterior = false, botonAbajoAnterior = false;

void setup()
{
  // Configurar los leds TX y RX como entrada los apaga
  //pinMode(LED_BUILTIN_TX,INPUT);
  //pinMode(LED_BUILTIN_RX,INPUT);

  Serial.begin(9600);

  lcd.init();
  lcd.backlight();

  lcd.print("Iiniciando...");

  pinMode(viviendaPin, INPUT);
  pinMode(riegoPin, INPUT);
  pinMode(flujoPin, INPUT);
  pinMode(valvulaPin, OUTPUT);

  pinMode(botonCambiarPantallaPin, INPUT);
  pinMode(botonArribaPin, INPUT);
  pinMode(botonAbajoPin, INPUT);

  //attachInterrupt(digitalPinToInterrupt(botonCambiarPantallaPin), cambioPantalla, RISING);
  //attachInterrupt(digitalPinToInterrupt(botonArribaPin), botonSubir, RISING);
  //attachInterrupt(digitalPinToInterrupt(botonAbajoPin), botonBajar, RISING);

  lcd.setCursor(0, 0);
  if (!rtc.begin())
  {
    lcd.print("No se encontró el reloj RTC");
    while (1);
  }
  if (rtc.lostPower())
  {
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    fecha = rtc.now();
  }
  //rtc.adjust(DateTime(2019,11,23,10,17,0));
  //rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  delay(1000);
  controlPantallasLcd();
}

void loop()
{
  // mostrarDatosSerial();

  comprobarBotones();

  fecha = rtc.now();

  vivienda = digitalRead(viviendaPin);
  riego = digitalRead(riegoPin);
  flujo = calcularFlujo(flujoPin);

  controlAutomaticoValvula();

  controlContador();

  if (((fecha.minute() % tiempoEncendidoPantalla) == 0) && (fecha.second() < 5))
  {
    apagarPantalla();
  }

  if ((fecha.minute() != minutoAnterior) && (pantallaActual == pPrincipal))
  {
    controlPantallasLcd();
  }
  minutoAnterior = fecha.minute();
}

/* Comprueba el valor de los pulsadores */
void comprobarBotones()
{
  botonCambiarPantalla = digitalRead(botonCambiarPantallaPin);
  botonArriba = digitalRead(botonArribaPin);
  botonAbajo = digitalRead(botonAbajoPin);
  if ((botonCambiarPantalla == HIGH) && (botonCambiarPantallaAnterior == LOW))
  {
    encenderPantalla();
    cambioPantalla();
  }
  if ((botonArriba == HIGH) && (botonArribaAnterior == LOW))
  {
    encenderPantalla();
    botonSubir();
  }
  if ((botonAbajo == HIGH) && (botonAbajoAnterior == LOW))
  {
    encenderPantalla();
    botonBajar();
  }
  delay(25);
  botonCambiarPantallaAnterior = botonCambiarPantalla;
  botonArribaAnterior = botonArriba;
  botonAbajoAnterior = botonAbajo;
}

/* Rutina que se ejecuta cuando el usuario desea cambiar de pantalla */
void cambioPantalla()
{
  flagReinicio();
  cambiarPantallaActual();
  controlPantallasLcd();
}

/* Rutina que se ejecuta cuando se pulsa el botón arriba */
void botonSubir()
{
  switch (pantallaActual)
  {
  case pPrincipal:
    break;
  case pRegistros:
    actualizarRegistroMostrado(true);
    break;
  case pProgramacion:
    modificarProgramacionContador(true);
    break;
  case pFecha:
    modificarFecha(true);
    break;
  default:
    break;
  }
  controlPantallasLcd();
}

/* Rutina que se ejecuta cuando se pulsa el botón abajo */
void botonBajar()
{
  switch (pantallaActual)
  {
  case pPrincipal:
    break;
  case pRegistros:
    actualizarRegistroMostrado(false);
    break;
  case pProgramacion:
    modificarProgramacionContador(false);
    break;
  case pFecha:
    modificarFecha(false);
    break;
  default:
    break;
  }
  controlPantallasLcd();
}

/* Control automatico de la válvula de agua en función de las entradas */
void controlAutomaticoValvula()
{
  if (riego == 1)
  {
    valvula = 1;
  }
  else if ((vivienda == 1) && (contador < programacionContador))
  {
    valvula = 1;
  }
  else
  {
    valvula = 0;
  }
  digitalWrite(valvulaPin, valvula);
}

/* Control de activación del contador */
void controlContador()
{
  if (riego == 0)
  {
    if (flujo == 0)
    {
      contadorActivado = 0;
    }
    else if (flujo != 0)
    {
      if (flujo != 0 && flujoAnterior == 0)
      {
        anadirRegistro();
      }
      contadorActivado = 1;
      incrementarContador();
    }
  }
  flujoAnterior = flujo;
  resetContador();
}

/* Incrementa el valor del tiempo del registro y de los litros en un segundo */
void incrementarContador()
{
  if (contadorActivado == 1)
  {
    registros[0].fin = fecha;
    contador = calcularTiempoTranscurrido(registros[0]);
    registros[0].totalMinutos = contador;
    registros[0].totalLitros += (int)(flujo / 60);
  }
}

/* Pone el valor del contador de tiempo a 0 pasadas 24h */
void resetContador()
{
  if ((fecha.hour() == 0) && (fecha.minute() == 0))
  {
    contador = 0;
  }
}

/* Añade un nuevo registro a la lista */
void anadirRegistro()
{
  for (int i = (maxRegistros - 1); i > 0; i--)
  {
    registros[i] = registros[i - 1];
  }
  registros[0].inicio = fecha;
  if (numeroRegistros < maxRegistros)
  {
    numeroRegistros++;
  }
}

/* Calcula el tiempo en minutos entre el inicio y el final de un registro */
int calcularTiempoTranscurrido(struct registro registro)
{
  TimeSpan diferenciaEntreFechas = registro.fin - registro.inicio;
  return diferenciaEntreFechas.totalseconds() / 60;
}

/* Desactiva el flag de reinicio */
void flagReinicio()
{
  reinicio = false;
}

/* Permuta entre las distintas pantallas de visualización de datos disponibles */
void cambiarPantallaActual()
{
  if ((pantallaActual == 3) & (elementoAjusteFechaActual != 4))
  {
    cambioElementoAjusteFecha();
  }
  else
  {
    // Solo se permite el cambio de pantalla si no se está ajustando la fecha
    if (pantallaActual < (numeroPantallas - 1))
    {
      pantallaActual = pantallaActual + 1;
    }
    else
    {
      pantallaActual = 0;
    }
    elementoAjusteFechaActual = 0;
  }
}

/* Itera sobre los distintos elementos editables de la fecha */
void cambioElementoAjusteFecha()
{
  if (elementoAjusteFechaActual < (numeroElementosFecha - 1))
  {
    elementoAjusteFechaActual = elementoAjusteFechaActual + 1;
  }
  else
  {
    elementoAjusteFechaActual = 0;
  }
}

/* Selecciona la pantalla a mostrar en funcion de la elegida por el usuario */
void controlPantallasLcd()
{
  switch (pantallaActual)
  {
  case pPrincipal:
    pantallaPrincipalLcd();
    break;
  case pRegistros:
    pantallaRegistrosLcd();
    break;
  case pProgramacion:
    pantallaProgramacionLcd();
    break;
  case pFecha:
    pantallaAjusteFecha();
    break;
  default:
    break;
  }
}

/* Muestra la información de la pantalla principal en la lcd */
void pantallaPrincipalLcd()
{
  lcd.clear();
  /* Muestra la fecha actual */
  lcd.setCursor(0, 0);
  mostrarFechaLcd(fecha);

  /* Indica el tiempo que lleva el contador acrivado (en minutos) */
  lcd.setCursor(0, 1);
  lcd.print(contador);
  /* Indica las unidades del contador */
  lcd.print(" min");

  /* Indica el número de veces que se activó el contador */
  lcd.setCursor(10, 1);
  lcd.print(numeroRegistros);

  /* Indica si la valvula está activada */
  if (valvula)
  {
    lcd.setCursor(14, 1);
    lcd.print("V");
  }

  /* Indica si el micro se ha reiniciado desde el último uso del usuario */
  if (reinicio)
  {
    lcd.setCursor(15, 1);
    lcd.print("*");
  }
}

/* Muestra la información de los últimos registros de activación del contador */
void pantallaRegistrosLcd()
{
  lcd.clear();
  /* Muestra un registro de la memmoria */
  mostrarEventoRegistrado(registroMostrado);
}

/* Muestra la información para la programación del contador */
void pantallaProgramacionLcd()
{
  lcd.clear();
  /* Muestra el titulo */
  lcd.setCursor(0, 0);
  lcd.print("PROG CONTADOR");
  /* Muestra el tiempo actual al que está programado el contador */
  lcd.setCursor(0, 1);
  lcd.print(programacionContador);
  lcd.print(" min");
}

/* Muestra la fecha que está configurada y permite modificarla*/
void pantallaAjusteFecha()
{
  lcd.clear();
  /* Muestra la fecha actual */
  lcd.setCursor(0, 0);
  mostrarFechaLcd(fecha);
  switch (elementoAjusteFechaActual)
  {
  case anio:
    lcd.setCursor(0, 1);
    lcd.print("^^^^");
    break;
  case mes:
    lcd.setCursor(5, 1);
    lcd.print("^^");
    break;
  case dia:
    lcd.setCursor(8, 1);
    lcd.print("^^");
    break;
  case hora:
    lcd.setCursor(11, 1);
    lcd.print("^^");
    break;
  case minuto:
    lcd.setCursor(14, 1);
    lcd.print("^^");
    break;
  default:
    break;
  }
}

/* Modifica el registro que será mostrado por pantalla */
void actualizarRegistroMostrado(bool direccion)
{
  if (direccion)
  {
    if (registroMostrado > 0)
    {
      registroMostrado--;
    }
  }
  else
  {
    if (registroMostrado < (maxRegistros - 1))
    {
      registroMostrado++;
    }
  }
}

/* Modifica el valor porgamado por el usuario para el contador */
void modificarProgramacionContador(bool direccion)
{
  if ((programacionContador < maxContador) && (direccion == 1))
  {
    programacionContador += 10;
  }
  else if ((programacionContador > minContador) && (direccion == 0))
  {
    programacionContador -= 10;
  }
}

/* Modifica la fecha elemento a elemento en sentido ascendente y descendente */
void modificarFecha(bool direccion)
{
  DateTime newDate;
  TimeSpan timedelta;
  switch (elementoAjusteFechaActual)
  {
  case anio:
    timedelta = TimeSpan(365,0,0,0);
    break;
  case mes:
    timedelta = TimeSpan(30,0,0,0);
    break;
  case dia:
    timedelta = TimeSpan(1,0,0,0);
    break;
  case hora:
    timedelta = TimeSpan(0,1,0,0);
    break;
  case minuto:
    timedelta = TimeSpan(0,0,1,0);
    break;
  default:
    break;
  }
  if (direccion)
  {
    newDate = fecha + timedelta;
  }
  else
  {
    newDate = fecha - timedelta;
  }
  rtc.adjust(newDate);
  fecha = rtc.now();
}

/* Muestra la fecha y hora en la LCD */
void mostrarFechaLcd(DateTime date)
{
  lcd.print(fecha.year(), DEC);
  lcd.print("-");
  if (fecha.month() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.month(), DEC);
  lcd.print("-");
  if (fecha.day() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.day(), DEC);
  lcd.print(" ");
  if (fecha.hour() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.hour(), DEC);
  lcd.print(":");
  if (fecha.minute() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.minute(), DEC);
}

/* Muestra un elemento de los registros almacenados en memoria */
void mostrarEventoRegistrado(int indice)
{
  lcd.setCursor(0, 0);
  lcd.print(indice + 1);
  lcd.print(" ");

  if (fecha.day() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.day(), DEC);
  lcd.print("/");
  if (fecha.month() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.month(), DEC);
  lcd.print(" ");
  if (fecha.hour() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.hour(), DEC);
  lcd.print(":");
  if (fecha.minute() < 10)
  {
    lcd.print("0");
  }
  lcd.print(fecha.minute(), DEC);

  lcd.setCursor(0, 1);
  lcd.print(registros[indice].totalMinutos);
  lcd.print("min");

  lcd.print(" ");
  lcd.print(registros[indice].totalLitros);
  lcd.print("L");
}

/* Calcula el flujo en litros/minuto medido por el caudalimetro */
int calcularFlujo(int pin)
{
  unsigned long timeout = 100 * 1000;
  float valorSensor = 2 * pulseIn(pin, HIGH, timeout);
  Serial.println(pulseIn(pin, HIGH, timeout));
  float PPS;

  if (valorSensor == 0) {
    PPS = 0;
  } else {
    PPS = 1000000 / valorSensor;
  }

  float flow = (PPS + 8) / 6;

  if (flow < 1.35){
    flow = 0;
  }

  return (int)flow;
}

/* Enciende la retroiluminación de la pantalla */
void encenderPantalla()
{
  lcd.backlight();
}

/* Apaga la retroiluminación de la pantalla */
void apagarPantalla()
{
  lcd.noBacklight();
}

// Muestra el estado de las variables por el puerto serial
void mostrarDatosSerial()
{
  mostrarFechaSerial(fecha);
  Serial.print("Vivienda: ");
  Serial.println(vivienda);
  Serial.print("Riego: ");
  Serial.println(riego);
  Serial.print("Flujo: ");
  Serial.println(flujo);
  Serial.print("Valvula: ");
  Serial.println(valvula);
  Serial.print("Contador: ");
  Serial.println(contador);
  Serial.print("Registros: ");
  Serial.println(numeroRegistros);
  Serial.println("/////////////////////////////////");
}

//Muestra la fecha y hora del RTC por el puerto serie
void mostrarFechaSerial(DateTime date)
{
  Serial.print(date.year(), DEC);
  Serial.print('/');
  Serial.print(date.month(), DEC);
  Serial.print('/');
  Serial.print(date.day(), DEC);
  Serial.print(" ");
  Serial.print(date.hour(), DEC);
  Serial.print(':');
  Serial.print(date.minute(), DEC);
  Serial.print(':');
  Serial.print(date.second(), DEC);
  Serial.println();
}
