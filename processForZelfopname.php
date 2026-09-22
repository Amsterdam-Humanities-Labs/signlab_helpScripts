<?php

//generate files from mysql db and then move them to rclone directory, use left/center/right folders
//select files from glosses tohse are taken captured and then update the fields in videocenter,left,right_post with processing status
//create loop function to check every hour if there are new files in post folders and then move them back to local post folders
//then update again the fields with processing status

include('../mysql_config.php');

//disable php warning
error_reporting(E_ERROR | E_PARSE);

// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

// Check the connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$stmt = $conn->prepare("SELECT * FROM form_data 
WHERE process_zelfopname = '1' 
AND signbank IS NOT NULL
AND videoTop IS NULL
AND (processed <> '2' OR processed IS NULL)
;
");
$stmt->execute();
$result = $stmt->get_result();

// Loop through the result set
while ($row = $result->fetch_assoc()) {
    // Get the necessary data from the row
    $id = $row['id'];
    $gloss = $row['glos'];
    $zelfopname = $row['zelfopname'];
    echo $zelfopname;

    if($zelfopname != "[]")
    {
    // Perform the necessary operations for each row
    echo "Processing record with ID: " . $id . "\n";
    echo "Gloss: " . $gloss . "\n";

    //extract JSON from zelfopname
    $zelfopname = json_decode($row['zelfopname'], true);
    // get the first item from zelfopname
    $zelfopname = $zelfopname[0];
    //create the postdir
    $postDir = "/web/uploads/".$zelfopname;

    // Add your code logic here

    echo "uploading video for gloss: ".$gloss."\n";
    echo $postDir;


 //get gloss name from database via $stmt->execute; 
    //then use gloss name to upload to signbank

//for now its only videoCenter because of Signbank limitations

 //also autoupload the new videoCenter file to Signbank
//   url: "https://leffe.science.uva.nl:8043/signBankAPI/upload_video",

$url = "https://leffe.science.uva.nl:8043/signBankAPI/upload_video";
$postData = [
    'gloss' => $gloss,
    'videoNaam' => $postDir
];

//JSON stringify the postdata
$postData = json_encode($postData);


//SEND THE PAYLOAD
//      |
//     / \
//    / _ \
//   |.o '.|
//   |'._.'|
//   |     |
//  ,'|  | |`.
// /  |  | |  \
// |,-'--|--'-.|


$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_VERBOSE, true);
//disable ssl cert check
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
//send as JSON
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));


echo $url."\n";

$response = curl_exec($ch); // Execute the cURL request and retrieve the response

// echo $row['id'];

// //update the record with processed = 2
$stmt = $conn->prepare("UPDATE form_data SET process_zelfopname = 2, logboek = CONCAT(logboek, '\nZelfopname ".$postDir."verstuurd aan Signbank') WHERE id = ?");
$stmt->bind_param("i", $row['id']);
$stmt->execute();

curl_close($ch);
}}





?>