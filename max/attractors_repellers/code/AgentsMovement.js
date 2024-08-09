
inlets = 1;
outlets = 3;

// Define the point to be rotated, the center, the axis and the angular speed
var center = { x: 0, y: 0, z: 0 };
var movingPoint = { x: 0, y: 0, z: 0 };
var axis = { x: 0, y: 0, z: 1 }; // Make sure this is a unit vector
var w_speed = 2 * Math.PI * 0.10; // radians per second, init with 10% of a full rotation

// Simulate the rotation over time
var deltaTime = 0.01; // Small time step
var currentAngle = 0;
var initialAngle = 0;
var currentRadious = 5000;

function center_p(x, y, z) {
    center.x = x;
    center.y = y;
    center.z = z;
}


// Function to calculate the cross product of two vectors
function crossProduct(v1, v2) {
    return {
        x: v1.y * v2.z - v1.z * v2.y,
        y: v1.z * v2.x - v1.x * v2.z,
        z: v1.x * v2.y - v1.y * v2.x
    };
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

function rotate(radius, center, axis, angle){

    // You may need to define an initial 'up' vector that will help to define the circular plane
    // For simplicity, let's assume it's along the world's up-axis (0, 1, 0), but it should NOT be parallel to 'axis'
    var upVector = { x: 0, y: 1, z: 0 };

    // Calculate two perpendicular vectors to the axis that define the plane of rotation
    var planeVectorA = crossProduct(upVector, axis);
    var planeVectorB = crossProduct(axis, planeVectorA);

    // Normalize these vectors
    planeVectorA = normalize(planeVectorA);
    planeVectorB = normalize(planeVectorB);

    // Now, use trigonometry to find the initial position on the plane defined by 'axis'
    var point = {
        x: center.x + radius * (Math.cos(angle) * planeVectorA.x + Math.sin(angle) * planeVectorB.x),
        y: center.y + radius * (Math.cos(angle) * planeVectorA.y + Math.sin(angle) * planeVectorB.y),
        z: center.z + radius * (Math.cos(angle) * planeVectorA.z + Math.sin(angle) * planeVectorB.z)
    };
    return point;
}

function axis_p(x, y, z) {
    axis.x = x;
    axis.y = y;
    axis.z = z;
}

function axis_random() {
    axis.x = Math.random();
    axis.y = Math.random();
    axis.z = Math.random();
    //normalize 
    var norm = Math.sqrt(axis.x*axis.x + axis.y*axis.y + axis.z*axis.z);
    axis.x /= norm;
    axis.y /= norm;
    axis.z /= norm;
    //post("axis: " + axis.x + ", " + axis.y + ", " + axis.z + "\n");
}


function loadbang() {
    reset();
}

function reset() {
    currentAngle = initialAngle;
}

function angular_speed(speed) {
    w_speed = 2 * Math.PI * speed;
}

function delta_time(deltaTimeMM) {
    deltaTime = deltaTimeMM / 1000.0;    
}

function radius(r) {
    currentRadious = r;
}

function init_angle(angle) {
    initialAngle = angle;
    currentAngle = angle;
}

function angle_random() {
    initialAngle = Math.random() * 2 * Math.PI;
    currentAngle = initialAngle;
}

function bang() {
    currentAngle += deltaTime * w_speed;
    center_on_closer_attractor_in_radius(10000000000); 
    movingPoint = rotate(currentRadious, center, axis, currentAngle);
    repellers_apply();
    outlet(0, Math.round(movingPoint.x), Math.round(movingPoint.y), Math.round(movingPoint.z));
    var degrees = current_degrees();
    outlet(1, degrees);//send the current angle
    outlet(2, ["angle", degrees]);
    outlet(2, ["speed", get_current_speed()]);
    outlet(2, ["radius", actual_radius()]);
    if(lastCloserAttractorIdx != -1){
        outlet(2, ["attractor", attractors[lastCloserAttractorIdx].id]);
    }
}

function current_degrees() {
    var degrees = (currentAngle % (2 * Math.PI)) * 180.0 / Math.PI;
    if (degrees < 0) {
        degrees += 360;
    }
    return degrees;
}

function actual_radius(){
    var currentCenter = center;
    if(lastCloserAttractorIdx != -1){
        currentCenter = attractors[lastCloserAttractorIdx];
    }
    var distance = Math.sqrt(Math.pow(currentCenter.x - movingPoint.x, 2) + Math.pow(currentCenter.y - movingPoint.y, 2) + Math.pow(currentCenter.z - movingPoint.z, 2));
    return distance;
}

//As an external influece, when an agent receive a message, it contains the angle from
//the other agent, which is used to calculate a diffrence with the current angle, then
//this diffrence is converted to a factor of a cycle which will be the perentage of increase 
// or decrese for the angular speed of the agent.
function other_angle_degrees(otherAngle) {
    //post("other angle: " + otherAngle + "\n");
    var degrees = current_degrees();
    var diff = degrees - otherAngle;
    var factor = diff / 360.0;
    w_speed += factor;
    //post("diff: " + diff + "\n");
}

function get_current_speed() {
    return w_speed / (2 * Math.PI);
}

///////////////////////////// INFLUENCERS /////////////////////////////////

function influencer_position(id, radius, x, y, z, influencers){
    var idx = influencer_find(id, influencers);    
    if(idx == -1){
        idx = influencer_available_idx(influencers);
        if(idx == -1){
            post("Influencers array is full\n");
            return;
        }
        influencers[idx].id = id;
    }
    influencers[idx].radius = radius;
    influencers[idx].x = x;
    influencers[idx].y = y;
    influencers[idx].z = z;    
}

function influencer_remove(id, influencers){
    var idx = influencer_find(id, influencers);
    if(idx != -1){
        influencers[idx].id = -1;
    }
}

function influencer_find(id, influencers){
    for (var i = 0; i < influencers.length; i++) {
        if(influencers[i].id == id){
            return i;
        }
    }
    return -1;
}

function influencer_available_idx(influencers){
    for (var i = 0; i < influencers.length; i++) {
        if(influencers[i].id == -1){
            return i;
        }
    }
    return -1;
}

///////////////////////////// ATRACTORS /////////////////////////////////

var attractors = new Array(10);
var lastCloserAttractorIdx = -1;

for (var i = 0; i < attractors.length; i++) {
    attractors[i] = { id: -1, radius:5000, x: 0, y: 0, z: 0 };
}

function attractor_position(id, radius, x, y, z){
    influencer_position(id, radius, x, y, z, attractors);
}

function attractor_remove(id){
    influencer_remove(id, attractors);
}

function closer_attractor_in_radius(radius){
    var minDistance = 1000000;
    var minIdx = -1;
    for (var i = 0; i < attractors.length; i++) {
        if(attractors[i].id == -1){
            continue;
        }
        var distance = Math.sqrt(Math.pow(attractors[i].x - movingPoint.x, 2) + Math.pow(attractors[i].y - movingPoint.y, 2) + Math.pow(attractors[i].z - movingPoint.z, 2));
        if(distance < minDistance && distance < radius){
            minDistance = distance;
            minIdx = i;
        }
    }
    return minIdx;
}

function center_on_closer_attractor_in_radius(radius){
    var idx = closer_attractor_in_radius(radius);
    if(idx != -1){        
        lastCloserAttractorIdx = idx;
    }
    if(lastCloserAttractorIdx != -1){
        center.x = attractors[lastCloserAttractorIdx].x;
        center.y = attractors[lastCloserAttractorIdx].y;
        center.z = attractors[lastCloserAttractorIdx].z;
        currentRadious = attractors[lastCloserAttractorIdx].radius;
    }
}

///////////////////////////// REPELLERS /////////////////////////////////

var repellers = new Array(10);

for (var i = 0; i < repellers.length; i++) {
    repellers[i] = { id: -1, radius: 10000, x: 0, y: 0, z: 0 };
}

var repeller = { id: -1, x: 0, y: 0, z: 0 };

function repeller_position(id, radius, x, y, z){
    influencer_position(id, radius, x, y, z, repellers);
}

function repeller_remove(id){
    influencer_remove(id, repellers);
}

//The movement of the agent is affected by all repellers, the agent will move away from the repellers
function repellers_apply(){
    for (var i = 0; i < repellers.length; i++) {
        var repeller = repellers[i];
        if(repeller.id == -1){
            continue;
        }
        var distance = Math.sqrt(Math.pow(repeller.x - movingPoint.x, 2) + Math.pow(repeller.y - movingPoint.y, 2) + Math.pow(repeller.z - movingPoint.z, 2));
        if(distance < repeller.radius){
            var repellerVector = { x: movingPoint.x - repeller.x, y: movingPoint.y - repeller.y, z: movingPoint.z - repeller.z };
            repellerVector = normalize(repellerVector);
            var repellerDistance = repeller.radius - distance;
            movingPoint.x += repellerVector.x * repellerDistance;
            movingPoint.y += repellerVector.y * repellerDistance;
            movingPoint.z += repellerVector.z * repellerDistance;
        }
    }    
}