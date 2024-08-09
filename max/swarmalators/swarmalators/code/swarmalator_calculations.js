inlets = 1;
outlets = 3;

var agents = {};
var phase = 0;
var position = {
    x: Math.random() * 2 - 1,
    y: Math.random() * 2 - 1,
    z: Math.random() * 2 - 1
};
var J = 0;
var K = 0;
var speed = 0;
var delta_time = 0.02;
var this_id = 0;
var agents_size = 0;

function set_id(id){
    this_id = id;
}

function set_phase(p){
    phase = p;
}

function set_position(x, y, z){ 
    position = {x: x, y: y, z: z};
}

function set_J(j){
    J = j;
}

function set_K(k){
    K = k;
}

function set_speed(s){
    speed = s;
}

function set_other_phase(id, phase){    
    if (id != this_id){
        if (agents[id] === undefined){
            agents[id] = {phase: 0, position: {x: 0, y: 0, z: 0}};
            agents_size++;
        }else{
            agents[id].phase = phase;
        }
    }
}

function set_other_position(id, x, y, z){
    if (id != this_id){
        if (agents[id] === undefined){
            agents[id] = {phase: 0, position: {x: 0, y: 0, z: 0}};
            agents_size++;
        }else{
            agents[id].position = {x: x, y: y, z: z};
        }
    }
}

function set_delta_time(dt){
    delta_time = dt;
}

//function to get the magnitude of a vector
function magnitudeVect(v) {
    return Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

// Function to normalize a vector (make it a unit vector)
function normalize(v) {
    var magnitude = magnitudeVect(v);
    return {
        x: v.x / magnitude,
        y: v.y / magnitude,
        z: v.z / magnitude
    };
}

function bang(){
    var params = calculate_params(delta_time, J, K, speed); 
    position = params[0];
    phase = params[1];
    var norm_phase = params[2];

    outlet(0, [position.x, position.y,position.z]);// position
    outlet(1, phase);// phase
    outlet(2, norm_phase);// norm_phase

}

function calculate_params(dt, J, K, speed) {
    var Xi = {x: 0, y: 0, z: 0};
    var Oi = 0;
    var num_others = agents_size; // it is assumed that othersPhases and othersPositions have the same length
    for (var j in agents) {
        var Xji = {
            x: agents[j].position.x - position.x,
            y: agents[j].position.y - position.y,
            z: agents[j].position.z - position.z
        };
        var Oji = agents[j].phase - phase + Math.random() * 0.0001;
        var Xji_magnitude = magnitudeVect(Xji);

        var J_cos_Oji = J * Math.cos(Oji);
        var Xji_magnitude_3 = Xji_magnitude * Xji_magnitude * Xji_magnitude;
        Xi.x += (Xji.x / Xji_magnitude) * (1 + J_cos_Oji) - Xji.x / Xji_magnitude_3;
        Xi.y += (Xji.y / Xji_magnitude) * (1 + J_cos_Oji) - Xji.y / Xji_magnitude_3;
        Xi.z += (Xji.z / Xji_magnitude) * (1 + J_cos_Oji) - Xji.z / Xji_magnitude_3;
        Oi += Math.sin(Oji) / Xji_magnitude;
    }
    var N = num_others + 1; // +1 because agents does not contain "this" agent
    Xi.x /= N;
    Xi.y /= N;
    Xi.z /= N;
    Oi *= (K / N);

    var pi2 = 2 * Math.PI;
    var myNewPosition = {
        x: position.x + Xi.x * speed * dt,
        y: position.y + Xi.y * speed * dt,
        z: position.z + Xi.z * speed * dt
    };
    var myNewPhase = (phase + Oi * speed * dt) % pi2;
    myNewPhase = myNewPhase < 0 ?  myNewPhase + pi2 : myNewPhase;
    myNewNormPhase = myNewPhase / pi2; 
    return [myNewPosition, myNewPhase, myNewNormPhase];
}