blank_lights = [];
for(var i=0;i<100;i++) blank_lights.push([0,0,0]);

var data = [
    {
        lights: blank_lights.map(function(light) { return [15, 0, 0]; }),
        delay: 0.5
    },
    {
        lights: blank_lights.map(function(light, i) { return ((i % 2) === 0) ? [0, 15, 0] : [15, 0, 0]; }),
        delay: 0.5
    },
    {
        lights: blank_lights.map(function(light) { return [0, 15, 0]; }),
        delay: 0.5
    }
];

console.log(JSON.stringify(data));

// curl --data "q=`node xmas.js`" http://rpi-lights:8080/