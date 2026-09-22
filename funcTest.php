<?php


echo convertTimeToSeconds("15:24:06:02");
echo "<br>";
echo convertTimeToSecondss("2024-03-05T14:24:07.590Z")+3599;

function convertTimeToSeconds($time) {
    // Assuming the input format is HH:MM:SS:FF and FF is ignored for the conversion
    list($hours, $minutes, $seconds) = explode(':', $time);

    // Make sure each part is treated as an integer
    $hours = (int)$hours;
    $minutes = (int)$minutes;
    $seconds = (int)$seconds;

    // Calculate total time in seconds
    return ($hours * 3600) + ($minutes * 60) + $seconds;
}
function convertTimeToSecondss($dateTime) {
    $date = new DateTime($dateTime);
    $time = $date->format('H:i:s'); // Extracting time in HH:MM:SS format

    list($hours, $minutes, $seconds) = explode(':', $time);
    return ($hours * 3600) + ($minutes * 60) + $seconds;
}

function getDatefromString($dateTime) {
    $date = new DateTime($dateTime);
    return $date->format('Y-m-d');
}

?>