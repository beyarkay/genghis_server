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
  $fp = fopen('new_nodes.txt', 'a');
  fwrite($fp, $decoded_params['root'].PHP_EOL);
  fclose($fp);   
}

?>
