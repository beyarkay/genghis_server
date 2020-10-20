<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

function isValidJSON($str) {
    json_decode($str);
    return json_last_error() == JSON_ERROR_NONE;
}

$json_params = file_get_contents("php://input");

if (strlen($json_params) > 0 && isValidJSON($json_params)){
    $decoded_params = json_decode($json_params, true);
    // Get the proposed username
    $username = $decoded_params['username'];
    // Get existing usernames
    $server_json_str = file_get_contents('server_state.json');
    $server_json = json_decode($server_json_str, true);
    $return_state = ['state' => 'good'];
    foreach ((array) $server_json['clients'] as $client) {
        if($client['username'] == $username) {
            header('Content-type:application/json;charset=utf-8');
            $return_state = [
                'state' => 'error',
                'cause' => 'username already taken'
            ];
            break;
        } 
    }
    echo json_encode( $return_state );
}

?>
