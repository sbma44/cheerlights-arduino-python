// GE Color Effects Arduino Interface
// by Tom Lee <thomas.j.lee at gmail.com>


// based on code ported by Scott Harris <scottrharris@gmail.com>  
// scottrharris.blogspot.com  
// which was in turn based on :  
   
/*!     Christmas Light Control  
**     By Robert Quattlebaum <darco@deepdarc.com>  
**     Released November 27th, 2010  
**  
**     For more information,  
**     see <http://www.deepdarc.com/2010/11/27/hacking-christmas-lights/>.
**  
**     Originally intended for the ATTiny13, but should  
**     be easily portable to other microcontrollers.  
*/  
   
#define xmas_color_t uint16_t // typedefs can cause trouble in the Arduino environment  
   
// Eliminate the .h file  
   
#define XMAS_LIGHTS_PER_STRING          (50) //I only have a 36 light strand. Should be 50 or 36  
#define XMAS_STRING_COUNT         (2)
#define XMAS_LIGHT_COUNT          (XMAS_LIGHTS_PER_STRING * XMAS_STRING_COUNT)
#define XMAS_CHANNEL_MAX          (0xF)  
#define XMAS_DEFAULT_INTENSITY     (0xCC)  
#define XMAS_HUE_MAX               ((XMAS_CHANNEL_MAX+1)*6-1)  
#define XMAS_COLOR(r,g,b)     ((r)+((g)<<4)+((b)<<8))  
#define XMAS_COLOR_WHITE     XMAS_COLOR(XMAS_CHANNEL_MAX,XMAS_CHANNEL_MAX,XMAS_CHANNEL_MAX)  
#define XMAS_COLOR_BLACK     XMAS_COLOR(0,0,0)  
#define XMAS_COLOR_RED          XMAS_COLOR(XMAS_CHANNEL_MAX,0,0)  
#define XMAS_COLOR_GREEN     XMAS_COLOR(0,XMAS_CHANNEL_MAX,0)  
#define XMAS_COLOR_BLUE          XMAS_COLOR(0,0,XMAS_CHANNEL_MAX)  
#define XMAS_COLOR_CYAN          XMAS_COLOR(0,XMAS_CHANNEL_MAX,XMAS_CHANNEL_MAX)  
#define XMAS_COLOR_MAGENTA     XMAS_COLOR(XMAS_CHANNEL_MAX,0,XMAS_CHANNEL_MAX)  
#define XMAS_COLOR_YELLOW     XMAS_COLOR(XMAS_CHANNEL_MAX,XMAS_CHANNEL_MAX,0)  
#define XMAS_COLOR_ORANGE     XMAS_COLOR(XMAS_CHANNEL_MAX,(XMAS_CHANNEL_MAX/6),0)     
   
// Pin setup  
#define STATUSPIN 13 // The LED  

xmas_color_t light_hue_array[XMAS_LIGHT_COUNT];
uint8_t light_intensity_array[XMAS_LIGHT_COUNT];
   

void xmas_reflect_array_2(xmas_color_t bulb_hue_array[], uint8_t bulb_intensity_array[]) {
  uint8_t j, k, l;
  xmas_color_t m, n;

  noInterrupts();  
  
  for(uint8_t i=0;i<XMAS_LIGHT_COUNT/XMAS_STRING_COUNT;i++) {
    
    // set xmas_begin frame on both pins - 4 and 5
    PORTD |= B00110000;
    delayMicroseconds(10);
    PORTD &= B11001111;
    
    
    // set address for each string    
    k = i;
    for (j=6;j;j--) {
      if(k & (1<<5)) {
        // XMAS_ONE
        // 1. set low
        PORTD &= B11001111;
        // 2. delay 20us
        delayMicroseconds(20);
        // 3. set high
        PORTD |= B00110000;
        // 4. delay 10us
        delayMicroseconds(10);
      }
      else {
        // XMAS_ZERO
        // 1. set low
        PORTD &= B11001111;
        // 2. delay 10us
        delayMicroseconds(10);
        // 3. set high
        PORTD |= B00110000;
        // 4. delay 20us
        delayMicroseconds(20);                
      }            
      k <<= 1;
    }
   
   
    // set intensity
    k = bulb_intensity_array[i]; // pin 5
    l = bulb_intensity_array[i + XMAS_LIGHTS_PER_STRING]; // pin 4
    for(j=8;j;j--) {
      // first 10us are low either way
      PORTD &= B11001111;
      delayMicroseconds(10);
                  
      // these bits stay low if it's a one
      if(k & (1<<7)) {
        PORTD &= B11011111;        
      }
      else {
        PORTD |= B00100000;
      }
      if(l & (1<<7)) {
        PORTD &= B11101111;
      }
      else {
        PORTD |= B00010000;
      }
      delayMicroseconds(10);
      
      // last 10us are high either way
      PORTD |= B00110000;
      delayMicroseconds(10);            
      
      k <<= 1;
      l <<= 1;
    }
          
    // set hue
    m = bulb_hue_array[i]; // pin 5
    n = bulb_hue_array[i + XMAS_LIGHTS_PER_STRING]; // pin 4
    for(j=12;j;j--) {
      // first 10us are low either way
      PORTD &= B11001111;
      delayMicroseconds(10);
                  
      // these bits stay low if it's a one
      if(m & (1<<11)) {
        PORTD &= B11011111;        
      }
      else {
        PORTD |= B00100000;
      }
      if(n & (1<<11)) {
        PORTD &= B11101111;
      }
      else {
        PORTD |= B00010000;
      }
      delayMicroseconds(10);
      
      // last 10us are high either way
      PORTD |= B00110000;
      delayMicroseconds(10);            
      
      m <<= 1;
      n <<= 1;
    }
    
        
    // xmas_end
    PORTD &= B11001111;
    delayMicroseconds(40);      
  }
  
  interrupts();
}
   
   
xmas_color_t xmas_color(uint8_t r,uint8_t g,uint8_t b) {  
    return XMAS_COLOR(r,g,b);  
}  
   
  
void setup()  
{  
    // these pins are hardcoded in the manipulation of PORTD. no way around it to achieve the speed we need.
    pinMode(5, OUTPUT);
    pinMode(4, OUTPUT);

    pinMode(STATUSPIN, OUTPUT);  
 
    Serial.begin(115200);
  
  
    randomSeed(analogRead(0));
    xmas_color_t random_colors[] = { XMAS_COLOR_RED, XMAS_COLOR_GREEN, XMAS_COLOR_ORANGE, XMAS_COLOR_BLUE, XMAS_COLOR_MAGENTA, XMAS_COLOR_YELLOW, XMAS_COLOR_CYAN };
    xmas_color_t chosen = random_colors[random(255) % 7];
    xmas_color_t chosen2 = random_colors[random(255) % 7];
  
    for(int i=0;i<XMAS_LIGHT_COUNT;i++) {
        light_hue_array[i] = (i<XMAS_LIGHTS_PER_STRING) ? chosen : chosen2;
        light_intensity_array[i] = XMAS_DEFAULT_INTENSITY;
    } 

    xmas_reflect_array_2(light_hue_array, light_intensity_array);
}  
   
void wahoowa() {
  for(int i=0;i<XMAS_LIGHT_COUNT;i++) {
    light_hue_array[i] = ((i%2)==0) ? XMAS_COLOR_BLUE : XMAS_COLOR_ORANGE;
  }
  xmas_reflect_array_2(light_hue_array, light_intensity_array);
  delay(500);
}  

void wahoowa2() {
  for(int i=0;i<XMAS_LIGHT_COUNT;i++) {
    light_hue_array[i] = ((i%2)!=0) ? XMAS_COLOR_BLUE : XMAS_COLOR_ORANGE;
  }
  xmas_reflect_array_2(light_hue_array, light_intensity_array);
  delay(500);
}  


   
void loop()  
{ 
    noInterrupts();
    boolean changed = false;
  
    if(Serial.available()>0) {
    
      // hue or intensity?
      char command = Serial.read();
      if (command=='I') {      
          changed = true;
          
          int light_index = 0;
          
          // really unsure why this sent char is necessary, but w/o it the Serial.available() loop seems to stick
          Serial.println('#');
          
          while(Serial.available()<XMAS_LIGHTS_PER_STRING) {  
            delayMicroseconds(1);
          } 
          
          // read the intensity data & assign it
          for(int i=0;i<XMAS_LIGHTS_PER_STRING;i++) {
            uint8_t b = Serial.read();
            light_intensity_array[light_index] = b & 0xFF;     
            light_index++;
          }

          Serial.println('#');         

          while(Serial.available()<XMAS_LIGHTS_PER_STRING) {  
            delayMicroseconds(1);
          } 
          
          // read the intensity data & assign it
          for(int i=0;i<XMAS_LIGHTS_PER_STRING;i++) {
            uint8_t b = Serial.read();
            light_intensity_array[light_index] = b & 0xFF;     
            light_index++;
          }

          Serial.println('#');
      }    
      else if(command=='H') {                             
                
        int current_light = 0;
         
        while(Serial.available()<(XMAS_LIGHTS_PER_STRING*1.5)) {
          delayMicroseconds(1);
        }
          
        // read the hue data and assign it
        for(int i=0;i<(XMAS_LIGHTS_PER_STRING/2);i++) {
          byte b1 = Serial.read();
          byte b2 = Serial.read();
          byte b3 = Serial.read();
          light_hue_array[current_light] = xmas_color((b1>>4), (b1 & 0xF), (b2>>4));      
          current_light++;
          light_hue_array[current_light] = xmas_color((0xF & b2), (b3>>4), (0xF & b3));      
          current_light++;
        }  
           
        Serial.println('#');
            
        while(Serial.available()<(XMAS_LIGHTS_PER_STRING*1.5)) {
          delayMicroseconds(1);
        }
          
        // read the hue data and assign it
        for(int i=0;i<(XMAS_LIGHTS_PER_STRING/2);i++) {
          byte b1 = Serial.read();
          byte b2 = Serial.read();
          byte b3 = Serial.read();
          light_hue_array[current_light] = xmas_color((b1>>4), (b1 & 0xF), (b2>>4));      
          current_light++;
          light_hue_array[current_light] = xmas_color((0xF & b2), (b3>>4), (0xF & b3));      
          current_light++;
        }  
           
        Serial.println('#');  

        changed = true;
      }
    }
    interrupts();
  
    if(changed) { 
      xmas_reflect_array_2(light_hue_array, light_intensity_array);
    }
}   

