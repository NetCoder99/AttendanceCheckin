// ---------------------------------------------------------------------------
// respond to the checkin response
// ---------------------------------------------------------------------------
document.body.addEventListener("checkin_response", function(event) {
    console.log(`checkin_response was received`);

    const checkinMessage   = document.getElementById('checkinMessage');
    const promotionMessage = document.getElementById('promotionMessage');
    const otherMessage     = document.getElementById('otherMessage');

    const checkin_img_student = document.getElementById('checkin_img_student');
    const image_src_string    = `/media/student_images/${event.detail.student_image_name}`;
    checkin_img_student.src   = image_src_string;

    if (event.detail.checkin_status === "error") {
        checkinMessage.innerHTML   = event.detail.checkin_message;
        promotionMessage.innerHTML = "";
        otherMessage.innerHTML     = "";
        checkinMessage.classList.add    ("text-error");
        //checkinMessage.classList.remove ("text-success");
    }
    else {
        checkinMessage.innerHTML   = event.detail.checkin_message;
        promotionMessage.innerHTML = "";
        otherMessage.innerHTML     = "";
        //checkinMessage.classList.add    ("text-success");
        checkinMessage.classList.remove ("text-error");
    }

    startResetTimer();
});

// ---------------------------------------------------------------------------
// manage count down to checkin screen reset
// ---------------------------------------------------------------------------
function startResetTimer() {
    console.log(`startResetTimer was invoked`);
        let count = 5;
        const intervalID = setInterval(() => {
          console.log(`Tick: ${count}`);
          document.getElementById('checkinTimer'+count).classList.add("hidden");
          count--;
          checkinTimer5
        }, 1000);

        setTimeout(() => {
          clearInterval(intervalID);
          console.log("Interval stopped.");
        }, 6000);

        setTimeout(() => {
          resetCheckinScreen();
        }, 6000);
}

// ---------------------------------------------------------------------------
// common function to reset the checkin messages section
// ---------------------------------------------------------------------------
function resetCheckinScreen() {
    console.log(`resetCheckinScreen`);
    document.getElementById('badgeNumber').value       = '';
    document.getElementById('checkin_img_student').src = "/static/RSM_Logo_002.jpg"
    resetCheckinResponseMessages();
}
function resetCheckinResponseMessages() {
    console.log(`resetCheckinResponseMessages`);
    document.getElementById('badgeNumber').disabled = false;
    document.getElementById('checkinMessage').innerHTML = "";
    document.getElementById('promotionMessage').innerHTML = "";
    document.getElementById('otherMessage').innerHTML = "";
}
