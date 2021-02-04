#!/usr/bin/php
<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

date_default_timezone_set("Africa/Johannesburg");
header("Content-Type: text/event-stream");
header("Cache-Control: no-cache");
header("Connection: keep-alive");

// header("Access-Control-Allow-Headers: Origin, Methods, Content-Type");
// header("Access-Control-Allow-Methods: GET, OPTIONS");
// header("Access-Control-Allow-Methods: POST");
// header('Access-Control-Allow-Origin: *');

//echo 'start dump';
//var_dump($_SERVER);
//var_dump($_GET);
//echo 'end dump';

if (isset($_GET['game_id'])){
    $game_id = $_GET['game_id'];
    //echo $game_id;
} else {
    parse_str($_SERVER['QUERY_STRING'], $get_arr);
    $game_id = $get_arr['game_id'];
    //print_r($get_arr);
}
if (isset($_GET['last_seen_tick'])) {
    $last_seen_tick = (int)$_GET["last_seen_tick"];
    //echo $last_seen_tick;
} else {
    parse_str($_SERVER['QUERY_STRING'], $get_arr);
    $last_seen_tick = (int)$get_arr["last_seen_tick"];
    //print_r($get_arr);
}


while (true) {
    // echo 'data: last_seen_tick = ' . $last_seen_tick, "\n\n";
    // Get the current game tick
    $game_json = file_get_contents("games/$game_id/game.json");
    $game_obj = json_decode($game_json, true);
    $curr_game_tick = (int)$game_obj['tick'];
    if ($curr_game_tick > $last_seen_tick) {
        for ($from = $last_seen_tick; $from < $curr_game_tick; $from ++) {
            $to = $from + 1;
            $contents = file_get_contents("games/${game_id}/patch_${from}_${to}.txt");
            $sse_formatted = preg_replace('/\n/', '\ndata: ', trim($contents));
            echo "event: patch\n";
            echo 'data: ' . $sse_formatted , "\n\n";
        }

        while (ob_get_level() > 0) { ob_end_flush(); }
        flush();
        if ( connection_aborted() ) break;
        $last_seen_tick = $curr_game_tick;
        usleep(50000);
    }
    usleep(50000);
}
?>
