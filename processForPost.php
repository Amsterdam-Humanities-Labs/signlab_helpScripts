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

//forloop through movie files in raw folder and then check if same filenames exist in post folder, when it does exist then update the record with processed=1 of the filename equal to filename in videoCenter, videoLeft, videoRight

$rawDir = '/web/gebarenoverleg_media/studioFilesMini/raw/';
$postDir = '/web/gebarenoverleg_media/studioFilesMini/post/';

$files = scandir($rawDir);

//forloop through all files
foreach($files as $file){
   //check if the file is in post 
        if(file_exists($postDir.$file) && strpos($file, '.MP4') !== false){
            //update the record with processed=1

        //first check if it is already processed
        $stmt = $conn->prepare("SELECT * FROM form_data WHERE videoCenter LIKE CONCAT('%', ?, '%') AND signbank IS NOT NULL");
        $stmt->bind_param("s", $file);
        $stmt->execute();
        $result = $stmt->get_result();
        if($result->num_rows > 0)
        {
            $row = $result->fetch_assoc();
            $gloss = $row['glos'];
            $signbank = $row['signbank'];
            if($row['processed'] != '2')
            {

            echo "uploading video for gloss: ".$gloss."\n";
            echo $postDir.$file."\n";
        

         //get gloss name from database via $stmt->execute; 
            //then use gloss name to upload to signbank

        //for now its only videoCenter because of Signbank limitations

         //also autoupload the new videoCenter file to Signbank
    //   url: "https://leffe.science.uva.nl:8043/signBankAPI/upload_video",
      
      $url = "https://leffe.science.uva.nl:8043/signBankAPI/upload_video";
        $postData = [
            'gloss' => $gloss,
            'videoNaam' => $postDir.$file
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

        echo $row['id'];
        
        //update the record with processed = 2
        $stmt = $conn->prepare("UPDATE form_data SET processed = 2, logboek = CONCAT(logboek, '\Studio Opname ".$postDir.$file."verstuurd aan Signbank') WHERE id = ?");
        $stmt->bind_param("i", $row['id']);
        $stmt->execute();
        
        curl_close($ch);
        

        $url = "https://leffe.science.uva.nl:8043/signBankAPI/update_gloss";
        $postData = [
            'glossid' => $signbank,
            'webDic' => "Yes"
        ];
        // Convert array to JSON string
        $jsonData = json_encode($postData);
        
        // Initialize cURL
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData); // Send JSON string as POST fields
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_VERBOSE, true);
        // Disable SSL certificate check
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        // Set the Content-Type to application/json
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
        $response = curl_exec($ch); // Execute the cURL request and retrieve the response
        curl_close($ch);
        
    }
}
}
}
writeToJson();

function writeToJson() {
    $filePath = "/web/servicesRecords.json";
    
    // Read the existing JSON data from the file
    $jsonString = file_get_contents($filePath);
    $data = json_decode($jsonString, true);
    
    // Define the service name
    $service_name = "processForPost";
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