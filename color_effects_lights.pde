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
   
#define XMAS_LIGHT_COUNT          (50) //I only have a 36 light strand. Should be 50 or 36  
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
#define XMASPIN 4 // I drive the LED strand from pin #4  
#define STATUSPIN 13 // The LED  

xmas_color_t light_hue_array[XMAS_LIGHT_COUNT];
uint8_t light_intensity_array[XMAS_LIGHT_COUNT];
   
// The delays in the begin, one, and zero functions look funny, but they give the correct  
// pulse durations when checked with a logic analyzer. Tested on an Arduino Uno.  
   
void xmas_begin() {  
    digitalWrite(XMASPIN,1);  
    delayMicroseconds(7); //The pulse should be 10 uS long, but I had to hand tune the delays. They work for me  
    digitalWrite(XMASPIN,0);   
}     

void xmas_one() {  
    digitalWrite(XMASPIN,0);  
    delayMicroseconds(11); //This results in a 20 uS long low  
    digitalWrite(XMASPIN,1);  
    delayMicroseconds(7);   
    digitalWrite(XMASPIN,0);  
}  

void xmas_zero() {  
    digitalWrite(XMASPIN,0);  
    delayMicroseconds(2);   
    digitalWrite(XMASPIN,1);  
    delayMicroseconds(17);   
    digitalWrite(XMASPIN,0);  
}  

void xmas_end() {  
    digitalWrite(XMASPIN,0);  
    delayMicroseconds(40); // Can be made shorter  
}  
   
void xmas_fill_color(uint8_t begin,uint8_t count,uint8_t intensity,xmas_color_t color) {  
    while(count--) {  
       xmas_set_color(begin++,intensity,color);  
    }  
}  
   
void xmas_fill_color_same(uint8_t begin,uint8_t count,uint8_t intensity,xmas_color_t color) {  
    while(count--) {  
        xmas_set_color(0,intensity,color);  
    }  
}  
 
void xmas_reflect_array(xmas_color_t bulb_hue_array[], uint8_t bulb_intensity_array[]) {
    for(int i=0;i<XMAS_LIGHT_COUNT;i++) {
        xmas_set_color(i, bulb_intensity_array[i], bulb_hue_array[i]);
    }
}
   
   
void xmas_set_color(uint8_t led,uint8_t intensity,xmas_color_t color) {  
    uint8_t i;  
    xmas_begin();  
    for(i=6;i;i--,(led<<=1))  
        if(led&(1<<5))  
            xmas_one();  
        else  
            xmas_zero();  
    for(i=8;i;i--,(intensity<<=1))  
        if(intensity&(1<<7))  
            xmas_one();  
        else  
            xmas_zero();  
    for(i=12;i;i--,(color<<=1))  
        if(color&(1<<11))  
            xmas_one();  
        else  
            xmas_zero();  
    xmas_end();  // sad :-(
}  
   
   
xmas_color_t xmas_color(uint8_t r,uint8_t g,uint8_t b) {  
    return XMAS_COLOR(r,g,b);  
}  
   
xmas_color_t xmas_color_hue(uint8_t h) {  
    switch(h>>4) {  
        case 0:     h-=0; return xmas_color(h,XMAS_CHANNEL_MAX,0);  
        case 1:     h-=16; return xmas_color(XMAS_CHANNEL_MAX,(XMAS_CHANNEL_MAX-h),0);  
        case 2:     h-=32; return xmas_color(XMAS_CHANNEL_MAX,0,h);  
        case 3:     h-=48; return xmas_color((XMAS_CHANNEL_MAX-h),0,XMAS_CHANNEL_MAX);  
        case 4:     h-=64; return xmas_color(0,h,XMAS_CHANNEL_MAX);  
        case 5:     h-=80; return xmas_color(0,XMAS_CHANNEL_MAX,(XMAS_CHANNEL_MAX-h));  
    }  
}  

void setup()  
{  
    pinMode(XMASPIN, OUTPUT);  
    pinMode(STATUSPIN, OUTPUT);  
 
    Serial.begin(115200);
  
    for(int i=0;i<XMAS_LIGHT_COUNT;i++) {
        light_hue_array[i] = XMAS_COLOR_RED;
        light_intensity_array[i] = XMAS_DEFAULT_INTENSITY;
    } 

    xmas_fill_color(0,XMAS_LIGHT_COUNT,XMAS_DEFAULT_INTENSITY,XMAS_COLOR_BLACK); //Enumerate all the lights  

    xmas_reflect_array(light_hue_array, light_intensity_array);
}  
 
   
void loop()  
{ 
    boolean changed = false;
  
    if(Serial.available()>0) {
    
        // hue or intensity?
        char command = Serial.read();
        if (command=='I') {
      
            // wait until there's 50 bytes of hue data -- 1 byte per light
            while(Serial.available()<(XMAS_LIGHT_COUNT)) {
                delayMicroseconds(5);
            }
      
            // read the intensity data & assign it
            for(int i=0;i<XMAS_LIGHT_COUNT;i++) {
                light_intensity_array[i] = min(XMAS_DEFAULT_INTENSITY, Serial.read());        
            }
            changed = true;
            Serial.println('#');
        }    
        else if(command=='H') {
            // wait until there's 75 bytes of hue data -- 12 bits per light
            while(Serial.available()<(XMAS_LIGHT_COUNT*1.5)) {
                delayMicroseconds(5);
            }
      
            // read the hue data and assign it
            for(int i=0;i<(XMAS_LIGHT_COUNT/2);i++) {
                byte b1 = Serial.read();
                byte b2 = Serial.read();
                byte b3 = Serial.read();
                light_hue_array[i*2] = xmas_color((b1>>4), (b1 & 0xF), (b2>>4));      
                light_hue_array[(i*2)+1] = xmas_color((0xF & b2), (b3>>4), (0xF & b3));      
            }
            changed = true;
            Serial.println('#');
        }
    }
  
    if(changed) {
        xmas_reflect_array(light_hue_array, light_intensity_array);
    }
}   
