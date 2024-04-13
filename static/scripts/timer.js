<script src="https://open.spotify.com/embed/iframe-api/v1" async></script>

var countdownId;
var isRunning = false;

function makeRequestAndStartTimer(time) {
    if (!isRunning) {
        return;
    }
   

    $.ajax({
        url: '/set_status',
        success: function(response) {
            console.log(response)
            if (response.item != null){
                document.getElementById("player").textContent = "Currently playing " + response.item.name + " by " + response.item.artists[0].name + " on Spotify"
            }
            else{
                document.getElementById("player").textContent = "No song is being played on Spotify!"
            }
            // clear the previous countdown interval
            clearInterval(countdownId);
            // reset the countdown after each request
            var countdown = time;
            $('#countdown').text('Time to next request: ' + countdown + ' seconds');
            countdownId = setInterval(function() {
                countdown--;
                if(countdown >= 0) {
                    $('#countdown').text('Time to next request: ' + countdown + ' seconds');
                } else {
                    clearInterval(countdownId);
                }
            }, 1000);
            // schedule the next request
            setTimeout(function() {
                makeRequestAndStartTimer(time);
            }, time * 1000);
        },
        error: function(error) {
            document.getElementById("player").textContent = "Not playing anything right now!"
            console.log('Error updating status: ', error);
        }
    });
    console.log('Updating status...');
}

$('#start-stop').click(function() {
    if(!isRunning) {
        var time = parseInt($('#time').val());
        if(time > 0) {
            isRunning = true;
            $('#start-stop').text('Stop');
            makeRequestAndStartTimer(time);
        } else {
            alert('Please enter a valid time');
        }
    } else {
        isRunning = false;
        $('#start-stop').text('Start');
        clearTimeout(countdownId);
    }
});