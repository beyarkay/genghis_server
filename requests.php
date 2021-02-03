<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header('Content-type:application/json;charset=utf-8');
// This is the all-purpose php script for the Genghis Server
// It handles multiple types of POST requests, so as to
// simplify the file structure of the Genghis Server project
//
// Each post request should be a JSON formatted object, and
// the 'case' parameter will declare what the request is
// for and what must be done.

// First, prospective clients enter their URL, from which
// their github username and repository name are extracted,
// which are then added to .new_clients.json along with
// a creation timestamp. The requests finishes successfully,
// but a new long-polling request is sent immediately.
//
// A cronjob picks up these changes to .new_clients.json,
// and generates an ed25516 keypair, the public key of
// which is added to the client's entry in .new_clients.json.
//
// The long-polling request will notice the public key entry
// in .new_clients.json, and return the public key to the
// web-browser so that the new client can add it into
// their GitHub repo's Deploy Keys setting page.
//
// Another long-poll back to the server will be sent when
// the user clicks 'click here to copy public deploy key'.
//
// The cronjob will also make requests every client in
// .new_clients.json that has a public_key, trying to
// access their repository. This cronjob will only succeed
// once the client has added the generated public key
// to their github deploy keys.
//
// Once this cronjob succeeds, it will remove the client from
// .new_clients.json and add it to clients.json.
//
// The long-poll will notice that the user has been removed
// from .new_clients.json, and if it was also added to
// client.json, return a success back to the client. Otherwise
// a failure will be sent out

function isValidJSON($str) {
    json_decode($str);
    return json_last_error() == JSON_ERROR_NONE;
}
$json_params = file_get_contents("php://input");
if (strlen($json_params) > 0 && isValidJSON($json_params)){
    $params = json_decode($json_params, true);
    $return_status = ['is_ok' => true];
    if ($params['case'] == 'add_new_client') {
        // Write client to .new_clients.json, the cronjob
        // will see this and add a new public key to the entry
        // we need to check the new client doesn't already exist in the clients.json file
        $clients_file = 'clients.json';
        $clients = json_decode(file_get_contents($clients_file), true);
        if (!array_key_exists('clients', $clients)) { $clients['clients'] = array(); }
        $new_clients_file = '.new_clients.json';
        $new_clients = json_decode(file_get_contents($new_clients_file), true);
        if (!array_key_exists('clients', $new_clients)) { $new_clients['clients'] = array(); }

        // Check that the new client doesn't already exist in the .new_client.json
        // nor the client.json files
        $existing_clients = array_merge($clients['clients'], $new_clients['clients']);
        foreach ((array) $existing_clients as $client) {
            if($client['url'] == $params['url']) {
                $return_status = [
                    'is_ok' => false,
                    'type' => 'client_already_exists',
                    'message' => 'client with username='.$client['username'].' and url='.$client['url'].' already exists'
                ];
                break;
            }
        }
        // If we didn't find any pre-existing clients with the same details, then
        // add the current client to the .new_clients.json file
        if ($return_status["is_ok"]) {
            array_push($new_clients['clients'], $params);
            file_put_contents($new_clients_file, json_encode($new_clients, JSON_PRETTY_PRINT));
            $return_status = [
                'is_ok' => true,
                'type' => 'client_registered',
                'message' => 'client with username='.$params['username'].' and url='.$params['url'].' has been registered successfully'
            ];
        }
    } elseif ($params['case'] == 'wait_for_public_key') {
        $key_exists = false;
        $new_clients_file = '.new_clients.json';
        $attempts_left = 30;
        while (!$key_exists) {
            $new_clients = json_decode(file_get_contents($new_clients_file), true);
            if (!array_key_exists('clients', $new_clients)) { $new_clients['clients'] = array(); }
            // Go through the new_clients array and check to see if our client has a public key yet
            foreach ((array) $new_clients['clients'] as $client) {
                if(array_key_exists('url', $client) && array_key_exists('url', $params) &&  $client['url'] == $params['url']) {
                    if (array_key_exists('public_key', $client)) {
                        $return_status = [
                            'is_ok' => true,
                            'type' => 'public_key_found',
                            'message' => 'client with username='.$params['username'].' and url='.$params['url'].' now has a keypair',
                            'public_key' => $client['public_key']
                        ];
                    }
                }
            }
            $attempts_left--;
            if ($attempts_left == 0) {
                $return_status = [
                    'is_ok' => false,
                    'type' => 'infinite_while_loop',
                    'message' => 'client with username='.$params['username'].' and url='.$params['url'].' caused an infinite loop while waiting for a keypair to be generated'
                ];
                break;
                // Loop through and find the client to remove
                for ($i = 0; $i < $new_clients['clients'].length; $i++) {
                    if($client['url'] == $params['url']) {
                        unset($new_clients['clients'][$i]);
                        break;
                    }
                }
                file_put_contents($new_clients_file, json_encode($new_clients, JSON_PRETTY_PRINT));
            }
            if (array_key_exists('public_key', $return_status)) {
                break;
            }
            sleep(1);           
        }
    } elseif ($params['case'] == 'wait_for_access_granted') {
        $access_granted = false;
        $new_clients_file = '.new_clients.json';
        $attempts_left = 60;       // Give the user 10 minutes to add the public key to their github
        while (!$access_granted) {
            $new_clients = json_decode(file_get_contents($new_clients_file), true);
            if (!array_key_exists('clients', $new_clients)) { $new_clients['clients'] = array(); }
            // First check that our client's been removed from .new_clients.json
            $client_has_been_removed = true;
            foreach ((array) $new_clients['clients'] as $new_client) {
                if($new_client['url'] == $params['url']) {
                    $client_has_been_removed = false;
                    $return_status = [
                        'is_ok' => false,
                        'type' => 'removed_from_new_clients_json',
                        'message' => 'client with username='.$params['username'].' and url='.$params['url'].' has been successfully removed from .new_clients.json but hasnt been added to clients.json'
                    ];
                    break;
                }
            }
            // Check that the client's been added to clients.json
            if ($client_has_been_removed) {
                $clients_file = 'clients.json';
                $clients = json_decode(file_get_contents($clients_file), true);
                if (!array_key_exists('clients', $clients)) { $clients['clients'] = array(); }
                foreach ((array) $clients['clients'] as $client) {
                    if($client['url'] == $params['url']) {
                        $access_granted = true;
                        $return_status = [
                            'is_ok' => true,
                            'type' => 'registration_successfull',
                            'message' => 'client with username='.$params['username'].' and url='.$params['url'].' has been successfully moved into the clients.json file and will be included in the next Genghis game.'
                        ];
                        break;
                    }
                }
            } else { 
                $attempts_left--;
                if ($attempts_left == 0) {
                    $return_status = [
                        'is_ok' => false,
                        'type' => 'infinite_while_loop',
                        'message' => 'client with username='.$params['username'].' and url='.$params['url'].' caused an infinite loop while waiting for the client to add the deploy key to their github repo.'
                    ];
                    // Loop through and find the client to remove
                    for ($i = 0; $i < $new_clients['clients'].length; $i++) {
                        if(array_key_exists('url', $client) && array_key_exists('url', $params) && $client['url'] == $params['url']) {
                            unset($new_clients['clients'][$i]);
                            break;
                        }
                    }
                    file_put_contents($new_clients_file, json_encode($new_clients, JSON_PRETTY_PRINT));
                    break;
                }
                sleep(1);
           }
        }
    } elseif ($params['case'] == 'register_client') {
        // DEPRECATED
        // we need to check the new client doesn't already exist in the clients.json file
        $clients_file = 'clients.json';
        $clients = json_decode(file_get_contents($clients_file), true);
        if (!array_key_exists('clients', $clients)) { $clients['clients'] = array(); }
        $new_clients_file = '.new_clients.json';
        $new_clients = json_decode(file_get_contents($new_clients_file), true);
        if (!array_key_exists('clients', $new_clients)) { $new_clients['clients'] = array(); }

        // Check that the new client doesn't already exist in the .new_client.json
        // nor the client.json files
        $existing_clients = array_merge($clients['clients'], $new_clients['clients']);
        foreach ((array) $existing_clients as $client) {
            if($client['url'] == $params['url']) {
                $return_status = [
                    'is_ok' => false,
                    'type' => 'client_already_exists',
                    'message' => 'client with username='.$client['username'].' and url='.$client['url'].' already exists'
                ];
                break;
            }
        }
        // If we didn't find any pre-existing clients with the same details, then
        // add the current client to the .new_clients.json file
        if ($return_status["is_ok"]) {
            array_push($new_clients['clients'], $params);
            file_put_contents($new_clients_file, json_encode($new_clients, JSON_PRETTY_PRINT));
            $return_status = [
                'is_ok' => true,
                'type' => 'client_registered',
                'message' => 'client with username='.$params['username'].' and url='.$params['url'].' has been registered successfully'
            ];
        }
    } elseif ($params['case'] == 'verify_client') {
        // DEPRECATED
        // The case 'verify_client' is used to check if a client
        // has been verified and therefore has been removed
        // from '.new_client.json' and has been moved into
        // the permenant clients file: 'client.json'

        // Keep checking .new_clients.json until the given client
        // has been removed, or we time out
        $attempts = 10;
        $sleep_duration = 10;
        $clients_been_removed = false;
        $new_clients_file = '.new_clients.json';
        $new_clients = json_decode(file_get_contents($new_clients_file), true); // Re-read the .new_clients.json
        if (!array_key_exists('clients', $new_clients)) { $new_clients['clients'] = array(); }

        while (!$clients_been_removed) {
            // Go through the new clients array, and check if it's been updated
            $clients_been_removed = true;
            foreach ((array) $new_clients['clients'] as $client) {
                if($client['url'] == $params['url']) {
                    $clients_been_removed = false;
                    break;
                }
            }
            if ($clients_been_removed) { break; }
            $new_clients = json_decode(file_get_contents($new_clients_file), true); // Re-read the .new_clients.json
            sleep(sleep_duration);
            $attempts--;
            if ($attempts == 0) {
                $return_status = [
                    'is_ok' => false,
                    'type' => 'verification_timeout',
                    'message' => 'Client with username='.$params['username'].' and url='.$params['url'].' timed out while waiting for cronjob'
                ];
                break;
            }
        }
        if ($return_status['is_ok']) {
            // Client has been removed from .new_clients.json, so check if they're in clients.json
            $clients_file = 'clients.json';
            $clients = json_decode(file_get_contents($clients_file), true); // Re-read the clients.json
            if (!array_key_exists('clients', $clients)) { $clients['clients'] = array(); }
            $clients_been_verified = true;
            foreach ((array) $clients['clients'] as $client) {
                if($client['url'] == $params['url']) {
                    $clients_been_verified = false;
                    $return_status = [
                        'is_ok' => false,
                        'type' => 'Verification failed',
                        'message' => 'Client with username='.$client['username'].' and url='.$client['url'].' was not verified by cronjob.'
                    ];
                    break;
                }
            }
            if ($clients_been_verified) {
                $return_status = [
                    'is_ok' => true,
                    'type' => 'Verification successful',
                    'message' => 'Client with username='.$params['username'].' and url='.$params['url'].' was successfully added to clients.json.'
                ];
            }
        }
    } else {
        $return_status = [
            'is_ok' => false,
            'type' => 'case_unknown',
            'message' => 'The "case" parameter does not match any valid case option.'
        ];
    }
    if (!$return_status["is_ok"]) {
        http_response_code(500);
    }
    echo json_encode( $return_status , JSON_PRETTY_PRINT);
} else {
    echo "JSON invalid.";
}
?>
