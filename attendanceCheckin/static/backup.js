




//    // ---------------------------------------------------------------------------
//    // respond to the 'ranks' button click
//    // ---------------------------------------------------------------------------
//    document.body.addEventListener("show_rank_required", function(event) {
//        console.log(`show_rank_required was activated`);
//
//        const id_required_stripes = document.getElementById('id_required_stripes');
//        id_required_stripes.options.length = 0;
//        event.detail.required_stripes.forEach(stripe_record => {
//          const opt = new Option(stripe_record[0], stripe_record[1]);
//          id_required_stripes.add(opt);
//        });
//        for (const stripe_record of event.detail.required_stripes) {
//            console.log(stripe_record);
//            const option       = document.createElement("option");
//            option.value       = stripe_record[0];
//            option.textContent = stripe_record[1];
//            id_required_stripes.appendChild(option);
//        }
//    });



//    // ---------------------------------------------------------------------------
//    // Listen for the htmx:afterSettle event on the show ranks required to
//    // populate the stripes dropdown
//    // ---------------------------------------------------------------------------
//    document.body.addEventListener('htmx:afterSettle', function(evt) {
//        // Check if the event target is part of your modal, then show it
//        const modal = document.getElementById('modal_rank_required');
//        if (modal) {
//            console.log(`modal_rank_required was shown, triggering stripes populate`);
//            htmx.ajax('GET', '/get_stripes', { target:'#div_belt_stripes', swap:'innerHTML' });
//        }
//    }, { once: true });

    //'hx-get': reverse_lazy('get_stripes'),  # Use reverse_lazy to get the URL
    //'hx-trigger': 'change',
    //'hx-target': '#div_belt_stripes',
    //htmx.ajax('GET', '/get_stripes', { target:'#div_belt_stripes', swap:'innerHTML' });

//    document.body.addEventListener("rank_updated", function(event) {
//        console.log(`rank_updated was received`);
//        document.getElementById('modal_rank_required').close();
//        document.getElementById('badgeNumber').disabled = false;
//        const otherMessage     = document.getElementById('otherMessage');
//        otherMessage.innerHTML = event.detail.rank_update_message;
//        if (event.detail.rank_update_status === "error") {
//            otherMessage.classList.add    ("text-error");
//            otherMessage.classList.remove ("text-success");
//        }
//        else {
//            otherMessage.classList.remove ("text-error");
//            otherMessage.classList.add    ("text-success");
//        }
//    });
