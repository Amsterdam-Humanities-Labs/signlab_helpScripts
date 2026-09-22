<?php

include('../mysql_config.php');
error_reporting(E_ALL);
ini_set('display_errors', 1);
// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);



// First, extract the gloss ID from the CSV file
$fields = extractThirdField('dictExport.csv');

foreach($fields as $field){
    echo $field;
    $url = getVideoUrl($field);

    if($url){
        echo $url;
        echo  "<br>";
        echo downloadVideoWithAuth($url, '../uploads/'.$field . '.mp4');
    }

    //check if file exists, then update mysql record accordingly
    if (file_exists('../uploads/'.$field).'.mp4') {
        //check first if gloss is already in db
        $sql = "SELECT * FROM form_data WHERE glos = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param('s', $field);
        $stmt->execute();
        $result = $stmt->get_result();
        if($result->num_rows > 0){
            $thema = "Opname Signbank";
            $wie = '["1","2","3","4","5","6","7"]';

            $row = $result->fetch_assoc();
            $zelfopnameArray = $row['zelfopname'];
            echo $zelfopnameArray; 
            //get zelfopname from result
            $updatedZelfopname = json_decode($zelfopnameArray);
            //check first of $field is already in array

            //check first if it is an array
            if(!is_array($updatedZelfopname)){
                $updatedZelfopname = [];
                   $updatedZelfopname[] = $field . '.mp4';
            $updatedZelfopname = json_encode($updatedZelfopname);
            print_r($updatedZelfopname);
            
            //update record
            $sql = "UPDATE form_data SET zelfopname = ?, thema = ?, wie = ? WHERE glos = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param('sss', $updatedZelfopname, $thema, $field);
            $stmt->execute();
            }
            else
            {
             if(in_array($field . '.mp4', $updatedZelfopname)){
                echo "file already exists";
            }
            else
            {
            //add new video to array
            $updatedZelfopname[] = $field . '.mp4';
            $updatedZelfopname = json_encode($updatedZelfopname);
            print_r($updatedZelfopname);
            
            //update record
            $sql = "UPDATE form_data SET zelfopname = ?, thema = ?, wie = ? WHERE glos = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param('sss', $updatedZelfopname, $thema, $field);
            $stmt->execute();
            }
            }

     

        } else {
             $zelfopnameArray = [];
            $zelfopnameArray[] = $field . '.mp4';
            $zelfopnameArray = json_encode($zelfopnameArray);
            //insert new record
            $glos = $field;
            $zelfopname = $zelfopnameArray;

            $query = "INSERT INTO form_data (glos, wie, zelfopname, thema) VALUES (?, ?, ?, ?)";
            $stmt = $conn->prepare($query);
            $stmt->bind_param("ssss", $glos, $wie, $zelfopname, $thema);
            $stmt->execute();
            
        }

    }
}


function downloadVideoWithAuth($url, $pathToSave) {

    //first check if file exists
    if (file_exists($pathToSave)) {
        echo "The file $pathToSave exists";
        return;
    }

    $cookieDetails = [
    'cookie_notification' => 'functional',
    'cookies_consent' => '-1',
    'sessionid' => (getenv('SIGNBANK_SESSIONID') ?: ''),
    'csrftoken' => (getenv('SIGNBANK_CSRFTOKEN') ?: '')
];
   $ch = curl_init();
   curl_setopt($ch, CURLOPT_VERBOSE, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

    curl_setopt($ch, CURLOPT_URL, $url);
    
    // Format and set the cookie string based on the provided details
    $cookieString = http_build_query($cookieDetails, '', '; ');
    curl_setopt($ch, CURLOPT_COOKIE, $cookieString);
    curl_setopt($ch, CURLOPT_FILE, fopen($pathToSave, 'w')); // Path to save the video

    $result = curl_exec($ch);
    $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    print_r($url);

    if ($result === false || $httpcode != 200) {
        echo "Error downloading video: " . curl_error($ch);
    } else {
        echo "Video downloaded successfully.";
    }

    curl_close($ch);
}


function extractThirdField($filename) {
    $result = array();
    if (($handle = fopen($filename, "r")) !== FALSE) {
        $header = fgetcsv($handle); // Skip header row
        while (($data = fgetcsv($handle)) !== FALSE) {
            if (isset($data[2])) { // Check if the third field exists
                $result[] = $data[2]; // Add the third field to the result array
            }
        }
        fclose($handle);
    }
    return $result;
}


function getVideoUrl($pattern) {
    //open video_urls.json and convert with json_decode
    $videoUrls = json_decode(file_get_contents('video_urls.json'), true);

// Filter lines with ".mp4" and match the desired pattern
$matches = array_filter($videoUrls, function ($key) use ($pattern) {
    return strpos(strtoupper($key), $pattern) !== false;
}, ARRAY_FILTER_USE_KEY);

// Base URL for the video
$baseUrl = 'https://signbank.cls.ru.nl';

// Append the query string for cache busting or versioning as needed
$version = '?v=20240220200512';

// Check if there are matches, if not return an error
if (empty($matches)) {
    return false;
    
} else {
    // Assuming you're dealing with a single entry and want to use it for streaming
    $videoPath = array_values($matches)[0]; // Gets the first value (path) from the matches
    $videoPath = str_replace('_small', '', $videoPath); // Remove '_small' from the filename
    $videoUrl = $baseUrl . $videoPath . $version; // Complete video URL

    // Instead of redirecting, output the video URL for streaming
    // You could also return this as JSON if you prefer
    return $videoUrl;
}    
}
?>
