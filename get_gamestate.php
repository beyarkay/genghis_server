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

$from_tick = $decoded_params['from_tick']

echo json_encode( $return_status , JSON_PRETTY_PRINT);
//
// // check that the username is good
// if (strlen($json_params) > 0 && isValidJSON($json_params)){
//     $decoded_params = json_decode($json_params, true);
//     // Get the proposed username
//     $username = $decoded_params['username'];
//     // Get existing usernames
//     $server_json_str = file_get_contents('server_state.json');
//     $server_json = json_decode($server_json_str, true);
//     $return_status = ['status' => 'good'];
//     foreach ((array) $server_json['clients'] as $client) {
//         if($client['username'] == $username) {
//             header('Content-type:application/json;charset=utf-8');
//             $return_status = [
//                 'status' => 'error',
//                 'cause' => 'username'
//             ];
//             break;
//         }
//     }
//     if ($return_status["status"] == "good") {
//         $file = "server_state.json";
//         $server_state = json_decode(file_get_contents($file), TRUE);
//
//         array_push($server_state["clients"], $decoded_params);
//
//         file_put_contents($file, json_encode($server_state, JSON_PRETTY_PRINT));
//     }
//     echo json_encode( $return_status , JSON_PRETTY_PRINT);
// }
?>
