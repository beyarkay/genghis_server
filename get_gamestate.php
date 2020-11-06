<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// function isValidJSON($str) {
//    json_decode($str);
//    return json_last_error() == JSON_ERROR_NONE;
// }
$json_params = file_get_contents("php://input");
$decoded_params = json_decode($json_params, true);
$return_status = [
    'input' => $decoded_params['input']
];

//$from_tick = $decoded_params['from_tick']
echo json_encode( $return_status , JSON_PRETTY_PRINT);

// Get the last seen tick from the client
$last_seen_tick = $decoded_params['last_seen_tick'];

// Get the game id
$game_id = $decoded_params['game_id'];


// Get the current game tick


// Calculate which change files need to be sent


// Package all the change files together into one file


// Actually send that one file back to the client




?>
