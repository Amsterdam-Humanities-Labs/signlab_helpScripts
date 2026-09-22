<?php
require 'vendor/autoload.php';
$ffmpeg = FFMpeg\FFMpeg::create();

include('../mysql_config.php');
error_reporting(E_ALL);
ini_set('display_errors', 1);
// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

//json headers
header('Content-Type: application/json');

//am i allowed to start today?
$asd = "SELECT * FROM studio_data WHERE date = CURDATE()";
$asd = $conn->query($asd);
$rowa = $asd->fetch_assoc();

//response array
$response = array();

  $mediaFiles = array();
    $mediaFiles = array_merge($mediaFiles, glob('/web/gebarenoverleg_media/studioFiles/*/*/*'));

    


    foreach($mediaFiles as $file){
            //if raw is in file
            if(strpos($file, 'raw')){

            
        // Check if the file has .MP4 extension
        // echo $file . "<br>";
        if (pathinfo($file, PATHINFO_EXTENSION) === 'MP4') {
            $tags = getVideoTime($file);
            // echo $file . " " . $tags['timecode'] . " " . $tags['creationDate'] . "<br>";
        }
    }
}




//when ready output response
// echo json_encode($response);

//update sql row
$sql = "UPDATE studio_data SET processed = 1 WHERE date = CURDATE()";
$stmt = $conn->prepare($sql);
$stmt->execute();
$stmt->close();
writeToJson();



function getVideoTime($file){
    global $ffmpeg;
    global $conn;

    //first check if the videofile is already in the database

    $sql = "SELECT * FROM videoMetaData WHERE videoPath = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param('s', $file);
    $stmt->execute();
    $result = $stmt->get_result();
    if(!$result->num_rows > 0){


    try {
        $video = $ffmpeg->open($file);
            $tags = array(); // Create an array to collect the tags

    $streams = $video->getStreams();   // Select only the video streams

    foreach ($streams as $stream) {
            // Here you can access each video stream
            $streamTags = $stream->get('tags');
            $tags[] = $streamTags; // Collect the tags in the array
    }
    $timecode = null;
    $creationDate = null;
    foreach ($tags as $item) {

    if (isset($item['handler_name'])) {
           if (isset($item['timecode'])) {
            $timecode = convertTimeToSeconds($item['timecode']);
        }
        
        if (isset($item['creation_time'])) {
            // Parse the creation_time and extract the date
            $dateTime = new DateTime($item['creation_time']);
            $creationDate = $dateTime->format('Y-m-d');
        }
}
}


    $sql = "INSERT INTO videoMetaData (videoPath, tags, date, time) VALUES ('".$file."', '".json_encode($tags)."','".$creationDate."','".$timecode."')";
    $stmt = $conn->prepare($sql);
    $stmt->execute();
    $response[] = $timecode;

    return $tags; // Return the collected tags
    } catch (Exception $e) {
        // Handle the error here
        // You can log the error or perform any necessary actions
        // For example, you can continue the loop or break it
        $tags = [];
    }

    
    //we might want to save the values in db to reduce load time
    //insert into videoMetaData

}
else{
    $row = $result->fetch_assoc();
    $timecode = $row['time'];
    $date = $row['date'];
//add to response header

}
return ['timecode' => $timecode, 'creationDate' => $date];

}


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

function writeToJson() {
    $filePath = "/web/servicesRecords.json";
    
    // Read the existing JSON data from the file
    $jsonString = file_get_contents($filePath);
    $data = json_decode($jsonString, true);
    
    // Define the service name
    $service_name = "generateTimeCode";
    $found = false;
    
    // Search for an existing entry with the same service name
    foreach ($data as &$entry) {
        if ($entry['service'] === $service_name) {
            // Update the date for the existing entry
            $entry['date'] = date("Y-m-d H:i:s");
            $found = true;
            break;
        }
    }
    
    // If no existing entry found, append a new one
    if (!$found) {
        $newRecord = [
            "service" => $service_name,
            "date" => date("Y-m-d H:i:s")
        ];
        $data[] = $newRecord;
    }
    
    // Write the updated data back to the JSON file
    $newJsonString = json_encode($data, JSON_PRETTY_PRINT);
    file_put_contents($filePath, $newJsonString);
}

?>