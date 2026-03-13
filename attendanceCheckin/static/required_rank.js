// ---------------------------------------------------------------------------
// This is activated when we need to show the student rank modal dialog
// ---------------------------------------------------------------------------
document.body.addEventListener('show_rank_required_dialog', () => {
    console.log(`show_rank_required_dialog was activated`);
    document.getElementById('badgeNumber').disabled = true;
    const modal_rank_required_elmnt = document.getElementById('modal_rank_required');
    const modal_rank_required_bs5   = new bootstrap.Modal(modal_rank_required_elmnt, {backdrop: 'static'});
    modal_rank_required_bs5.show();
    console.log(`modal_rank_required was shown`);
});

// ---------------------------------------------------------------------------
// Update stripes dropdown after changing rank
// ---------------------------------------------------------------------------
document.body.addEventListener("update_stripes_list", function(event) {
    console.log(`update_stripes_list was received`);
    const id_required_stripes = document.getElementById('id_required_stripes');
    id_required_stripes.innerHTML = '';
    for (const stripe of event.detail.stripes_list) {
        console.log(stripe);
        const option = new Option(stripe[1], stripe[0]);
        id_required_stripes.appendChild(option);
    }
});

// ---------------------------------------------------------------------------
// Process response from update rank/stipe submit, display on the rank modal
// ---------------------------------------------------------------------------
document.body.addEventListener("modal_rank_required_response", function(event) {
    console.log(`modal_rank_required_response was received`);
    rank_update_message = document.getElementById('rank_update_message');
    rank_update_message.innerHTML = event.detail.checkin_message;
    if (event.detail.checkin_status === "error") {
        rank_update_message.classList.remove ("text-success");
        rank_update_message.classList.add    ("text-danger");
    }
    else {
        rank_update_message.classList.add    ("text-danger");
        rank_update_message.classList.remove ("text-success");
    }
});


// ---------------------------------------------------------------------------
// Process response from update rank/stipe submit
// ---------------------------------------------------------------------------
document.body.addEventListener("show_ranks_error", function(event) {
    console.log(`show_ranks_error was received`);
    const badgeMessage     = document.getElementById('badgeMessage');
    const badgeNumber      = document.getElementById('badgeNumber');
    badgeMessage.innerHTML = event.detail.checkin_message;
    badgeMessage.classList.remove ("text-success");
    badgeMessage.classList.add    ("text-danger");
    badgeNumber.disabled = true;
    document.getElementById('checkinMessage').innerHTML   = "&nbsp";
    document.getElementById('promotionMessage').innerHTML = "&nbsp;";
    document.getElementById('otherMessage').innerHTML     = "&nbsp";

    setTimeout(function() {
        badgeMessage.innerHTML = "";
        badgeMessage.classList.remove ("text-success");
        badgeMessage.classList.remove ("text-danger");
        badgeNumber.value = '';
        badgeNumber.disabled = false;
    }, 3000);
});

// ---------------------------------------------------------------------------
// respond to the rank_updated events
// ---------------------------------------------------------------------------
document.body.addEventListener("rank_update_response", function(event) {
    console.log(`rank_update_response was received`);
    //document.getElementById('modal_rank_required').close();
    document.getElementById('btn_rank_modal_close').click();
    document.getElementById('badgeNumber').disabled = false;
    const badgeMessage     = document.getElementById('badgeMessage');
    badgeMessage.innerHTML = event.detail.rank_update_message;
    if (event.detail.rank_update_status === "error") {
        badgeMessage.classList.add    ("text-danger");
        badgeMessage.classList.remove ("text-success");
    }
    else {
        badgeMessage.classList.remove ("text-danger");
        badgeMessage.classList.add    ("text-success");
    }
    resetCheckinResponseMessages();
    setTimeout(function() {
        badgeMessage.innerHTML = "";
        badgeMessage.classList.remove ("text-danger");
        badgeMessage.classList.remove ("text-success");
        badgeNumber.value = '';
        document.getElementById('badgeNumber').disabled = false;
    }, 3000);
});

