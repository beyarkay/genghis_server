<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$json_params = file_get_contents("php://input");
$decoded_params = json_decode($json_params, true);

//echo json_encode( $decoded_params , JSON_PRETTY_PRINT);

// Get the last seen tick from the client
$last_seen_tick = (int)$decoded_params['last_seen_tick'];

// Get the game id
$game_id = $decoded_params['game_id'];

// Get the current game tick
//echo "getting file games/$game_id/game.json ....<br>";
$game_json = file_get_contents("games/$game_id/game.json");
$game_obj = json_decode($game_json, true);
$curr_game_tick = (int)$game_obj['tick'];
//echo "Curr game tick is $curr_game_tick<br><br>";

// Calculate which change files need to be sent
for ($from = $last_seen_tick; $from < $curr_game_tick; $from ++) {
    $to = $from + 1;
    echo "===$game_id/patch_${from}_${to}.txt===<br>";
    $contents = file_get_contents("games/${game_id}/patch_${from}_${to}.txt");
    echo $contents;
    echo "<br>";

}

// Package all the change files together into one file


// Actually send that one file back to the client




?>
