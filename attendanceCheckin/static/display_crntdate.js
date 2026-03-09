
// -------------------------------------------------------------------------------
let dateTimerInterval;
function startDateTimerInterval() {
    if (!dateTimerInterval) {
        dateTimerInterval = setInterval(function() {
            document.getElementById('currentDateTime').innerHTML = getDisplayDate();
            document.getElementById('badgeNumber').focus();
        }, 1000);
    }
}
function stopDateTimerInterval() {
    clearInterval(dateTimerInterval);
    dateTimerInterval = null
}
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
function getDisplayDate(inpDate = new Date()) {
    const date = inpDate.toLocaleDateString();
    const time = inpDate.toLocaleTimeString();
    const day  = inpDate.toLocaleDateString('en-us',{ weekday: 'long' });
    return `${day} ${date} ${time}`;
}
