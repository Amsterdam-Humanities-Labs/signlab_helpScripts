<?php
// Replace these variables with your actual database credentials
include('../mysql_config.php');


// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

//first we want to check for every entry with signbank id if the gloss is the same
//if not we want to update the gloss from glosses_transformed.json

//then we want to check if senses are same
//if not, then we check if senses are empty on signcollect side
//if they are empty, we want to update the senses from senses_transformed.json

//then we want to check if phonology are same
//if not, then we check if phonology are empty on signcollect side
//if they are empty, we want to update the phonology from phonology_transformed.json
//then we give fonologie_fase1 an 1


//we are going to call fetch_all.php to get all the entries from the database


$url = "https://leffe.science.uva.nl:8043/fetch_all.php?limit=20000&offset=0";
$context = stream_context_create([
    'ssl' => [
        'verify_peer' => false,
        'verify_peer_name' => false,
    ],
]);

$response = file_get_contents($url, false, $context);

//we are going to decode the json response
$data = json_decode($response, true);


//we want to get JSON from glosses_transformed.json 
$glosses = file_get_contents('../glosses_transformed.json');
$glosses = json_decode($glosses, true);

$flattenedArray = [];
foreach ($glosses as $entry) {
    foreach ($entry as $key => $value) {
        $flattenedArray[$key] = $value;
    }
}

//first we are going to forloop through the data of $data
foreach ($data as $item) {
    $signbankId = $item['signbank'];
    if (isset($flattenedArray[$signbankId])) {
        $entry = $flattenedArray[$signbankId];

        //now we want to compare if dutch glosses are the same
        if($item['glos'] == $entry['Annotation ID Gloss: Dutch']){
            echo "Glosses are the same<br>";
        }
        else

        {
            echo "<br>";
            echo $item['glos'];
            echo "<br>";
            echo $entry['Annotation ID Gloss: Dutch'];
            echo "<br>";
            echo "<br>";

            //we are going to update the gloss and insert in logbook its updated automatically
            $sql = "UPDATE form_data SET  logboek = CONCAT(logboek, '\n Glos Dutch geupdate door autoupdater'), glos= '{$entry['Annotation ID Gloss: Dutch']}' WHERE signbank = '" . $signbankId . "'";
            $stmt = $conn->prepare($sql);
            $stmt->execute();
        }   

        //then we want to check if english glosses are the same

        if($item['glos_engels'] == $entry['Annotation ID Gloss: English']){
            echo "Glosses are the same<br>";
        }
        else

        {
            echo "<br>";
            echo $item['glos_engels'];
            echo "<br>";
            echo $entry['Annotation ID Gloss: English'];
            echo "<br>";
            echo "<br>";

            //we are going to update the gloss and insert in logbook its updated automatically
            $sql = "UPDATE form_data SET  logboek = CONCAT(logboek, '\n Glos Dutch geupdate door autoupdater'), glos_engels= '{$entry['Annotation ID Gloss: English']}' WHERE signbank = '" . $signbankId . "'";
            $stmt = $conn->prepare($sql);
            $stmt->execute();

        }


    }
}