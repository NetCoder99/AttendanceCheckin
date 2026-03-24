// ---------------------------------------------------------------------------
// respond to the checkin response
// ---------------------------------------------------------------------------
document.body.addEventListener("checkin_error", function(event) {
    console.log(`checkin_error was received`);
    const badgeMessage       = document.getElementById('badgeMessage');
    badgeMessage.innerHTML   = event.detail.checkin_message;
    badgeMessage.classList.add("text-danger");
    document.getElementById('checkinMessage').innerHTML   = "&nbsp";
    document.getElementById('promotionMessage').innerHTML = "&nbsp";
    document.getElementById('otherMessage').innerHTML     = "&nbsp";
    document.getElementById('badgeNumber').disabled       = true;
    setTimeout(function() {
        badgeMessage.innerHTML = "";
        badgeMessage.classList.remove ("text-success");
        badgeMessage.classList.remove ("text-danger");
        badgeNumber.value = '';
        document.getElementById('badgeNumber').disabled = false;
    }, 3000);
});


// ---------------------------------------------------------------------------
// respond to the checkin response
// ---------------------------------------------------------------------------
document.body.addEventListener("checkin_panel", function(event) {
    console.log(`checkin_panel was received`);
    //hdn_badge_message = document.getElementById('hdn_badge_message').value;
    //document.getElementById('badgeMessage').innerHTML   = hdn_badge_message;
    //document.getElementById('badgeMessage').classList.remove ("text-success");
    //document.getElementById('badgeMessage').classList.remove ("text-danger");
    //document.getElementById('badgeMessage').classList.add ("text-success");
    startResetTimer();
});


// ---------------------------------------------------------------------------
// respond to the checkin response
// ---------------------------------------------------------------------------
document.body.addEventListener("checkin_message", function(event) {
    console.log(`checkin_message was received`);

    const checkinMessage   = document.getElementById('checkinMessage');
    const promotionMessage = document.getElementById('promotionMessage');
    const otherMessage     = document.getElementById('otherMessage');

    //const checkin_img_student = document.getElementById('checkin_img_student');
    //const image_src_string    = `/media/student_images/${event.detail.student_image_name}`;
    //checkin_img_student.src   = image_src_string;

    if (event.detail.checkin_status === "error") {
        checkinMessage.innerHTML   = event.detail.checkin_message;
        promotionMessage.innerHTML = "";
        otherMessage.innerHTML     = "";
        checkinMessage.classList.add    ("text-danger");
        //checkinMessage.classList.remove ("text-success");
    }
    else {
        checkinMessage.innerHTML   = event.detail.checkin_message;
        promotionMessage.innerHTML = "";
        otherMessage.innerHTML     = "";
        //checkinMessage.classList.add    ("text-success");
        checkinMessage.classList.remove ("text-danger");
    }

    if (event.detail.rank_required) {
        console.log("Showing rank required dialog!");
        const btn_show_ranks = document.getElementById('btn_show_ranks');
        btn_show_ranks.click();
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
          document.getElementById('checkinTimer'+count).classList.add("invisible");
          count--;
          checkinTimer5
        }, 1000);

        setTimeout(() => {
          clearInterval(intervalID);
          console.log("Interval stopped.");
        }, 6000);

        setTimeout(() => {
          resetCheckinResponseMessages();
        }, 6000);
}

// ---------------------------------------------------------------------------
// common function to reset the checkin messages section
// ---------------------------------------------------------------------------
function resetCheckinResponseMessages() {
    console.log(`resetCheckinResponseMessages`);
    document.getElementById('badgeNumber').value    = '';
    document.getElementById('badgeNumber').disabled = false;
    document.getElementById('badgeMessage').innerHTML   = "&nbsp";
    document.getElementById('checkinMessage').innerHTML   = "&nbsp";
    document.getElementById('promotionMessage').innerHTML = "&nbsp";
    document.getElementById('otherMessage').innerHTML     = "&nbsp";
    document.getElementById('checkin_img_student').src = "/static/images/RSM_Logo_002.jpg"

    document.getElementById('checkinTimer1').classList.remove("invisible");
    document.getElementById('checkinTimer2').classList.remove("invisible");
    document.getElementById('checkinTimer3').classList.remove("invisible");
    document.getElementById('checkinTimer4').classList.remove("invisible");
    document.getElementById('checkinTimer5').classList.remove("invisible");
}
