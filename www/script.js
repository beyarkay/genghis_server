$(document).ready(function () {
    $.ajaxSetup({cache: false});
    let interval = 250;
    function update() {
        $.when($.ajax('state.json'))
            .then(function (stateResponse) {
                //console.log(stateResponse);

                updateWithState(stateResponse);

            }, function () {
                console.log('Error while loading gamestate/layout');
            });
        setTimeout(update, interval);
    }

    setTimeout(update, interval);


});
