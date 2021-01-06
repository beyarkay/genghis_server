<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Use ls command to shell_exec 
// function 
$output = shell_exec('ls'); 
  
// Display the list of all file 
// and directory 
echo "<pre>$output</pre>";
?>
