inlets = 1;
outlets = 1;

var targetValue = 0;
var currentValue = 0;
var delayTimeMs = 0.2;
var deltaTimeMs = 0.01;
var speed = 0.01;
var firstTime = true;

function msg_float(f) {
    targetValue = f;
    if(firstTime){
        currentValue = f;
        firstTime = false;
    }
    speed = Math.abs(targetValue - currentValue) / delayTimeMs;
    //post("Speed: ", speed, "\n");
}

function set_time(f) {
    delayTimeMs = f;
    //post("Delay time: ", delayTimeMs, "\n");
}

function set_delta_time(f) {
    deltaTimeMs = f;
    //post("Delta time: ", deltaTimeMs, "\n");
}

function bang() {
    if(currentValue < targetValue){
        currentValue += speed * deltaTimeMs;
        if(currentValue > targetValue){
            currentValue = targetValue;
        }
    }else if(currentValue > targetValue){
        currentValue -= speed * deltaTimeMs;
        if(currentValue < targetValue){
            currentValue = targetValue;
        }
    }
    outlet(0, currentValue);
}