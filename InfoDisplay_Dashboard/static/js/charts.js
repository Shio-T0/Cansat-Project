
const ranged_xrotation = document.getElementById("xRotation");
const ranged_yrotation = document.getElementById("yRotation");
const ranged_refresh_rate = document.getElementById("refreshRate");

const xrotation_label = document.getElementById("xRotation_value");
const yrotation_label = document.getElementById("yRotation_value");
const refresh_rate_label = document.getElementById("refreshRate_value");

xrotation_label.innerText = ranged_xrotation.value + "º";
yrotation_label.innerText = ranged_yrotation.value + "º";
refresh_rate_label.innerText = ranged_refresh_rate.value + " Hz";

ranged_xrotation.addEventListener('input', function () {
    xrotation_label.innerText = this.value + "º";
});
ranged_yrotation.addEventListener('input', function () {
    yrotation_label.innerText = this.value + "º";
});
ranged_refresh_rate.addEventListener('input', function () {
    refresh_rate_label.innerText = this.value + " Hz";
});


