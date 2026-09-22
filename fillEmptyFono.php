<?php
// Replace these variables with your actual database credentials
include('../mysql_config.php');


// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

//first we want to get a list of entries with zelfopname at [], so we know it comes from signbank

//then we want to retrieve fonologie information from transformed_glosses.json and put those info in database via mysql update

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
    //we want to check if zelfopname is set at []
    //also signbank is set
    if($item['zelfopname'] == '[]' && isset($item['signbank'])){
    $signbankId = $item['signbank'];

    echo $signbankId;
    //then we want to check if signbank id is found in the json file
    if (isset($flattenedArray[$signbankId])) {

        $entry = $flattenedArray[$signbankId];

        $senses = [];
        $sensesEngels = [];

        //forloop this object to strings $details['Senses: Dutch']
        foreach($entry['Senses: Dutch'] as $skey => $svalue){
            $senses[] = $svalue;
        }
        foreach($entry['Senses: English'] as $skey => $svalue){
            $sensesEngels[] = $svalue;
        }



        //then we want to get fonology information from the json file
        $output = [
            'glos' => $entry['Annotation ID Gloss: Dutch'],
            'senses' => $senses,
            'sensesEngels' => $sensesEngels,
            'Handeness' => $entry['Handedness'],
            'strongHand' => $entry['Strong Hand'],
            'weakHand' => $entry['Weak Hand'],
            'HandshapeChange' => $entry['Handshape Change'],
            'RelationArticulators' => $entry['Relation Between Articulators'],
            'handLocation' => $entry['Location'],
            'ContactType' => $entry['Contact Type'],
            'MovementShape' => $entry['Movement Shape'],
            'MovementDirection' => $entry['Movement Direction'],
            'relativeOrienationMovement' => $entry['Relative Orientation Movement'],
            'relativeOrienationLocation' => $entry['Relative Orientation Location'],        
            'orientationChange' => $entry['Orientation Change'],
            'RepeatedMovement' => $entry['Repeated Movement'],
            'AlternatingMovement' => $entry['Alternating Movement'],
            'virtualObjectt' => $entry['Virtual Object'],
            'phonologyOther' => $entry['Phonology Other'],
            'mouthGesture' => $entry['Mouth Gesture'],
            'mouthing' => $entry['Mouthing'],
            'phoneticVariation' => $entry['Phonetic Variation'],
        ];

        //we want to check if handeness has a value, if not; then skip this update
        //we also want to check if handeness at the entry is not empty to avoid updating empty values
        if($output['Handeness'] != '' && $item['Handedness'] != ''){
            //we are going to update the gloss and insert in logbook its updated automatically
                $sql = "UPDATE form_data SET  logboek = CONCAT(logboek, '\n Fonologie geupdate door fillEmptyFono'), 
                    Handeness= '{$output['Handeness']}', strongHand= '{$output['strongHand']}', 
                    weakHand= '{$output['weakHand']}', HandshapeChange= '{$output['HandshapeChange']}', 
                    RelationArticulators= '{$output['RelationArticulators']}', handLocation= '{$output['handLocation']}', 
                    ContactType= '{$output['ContactType']}', MovementShape= '{$output['MovementShape']}', 
                    MovementDirection= '{$output['MovementDirection']}', relativeOrienationMovement= '{$output['relativeOrienationMovement']}', 
                    relativeOrienationLocation= '{$output['relativeOrienationLocation']}', OrientationChange= '{$output['orientationChange']}', 
                    RepeatedMovement= '{$output['RepeatedMovement']}', AlternatingMovement= '{$output['AlternatingMovement']}', 
                    virtualObjectt= '{$output['virtualObjectt']}', phonologyOther= '{$output['phonologyOther']}', 
                    mouthGesture= '{$output['mouthGesture']}', mouthing= '{$output['mouthing']}', 
                    phoneticVariation= '{$output['phoneticVariation']}',
                    fonologie_fase1 = '1', fonologie_fase2 = '1', senses= '" . mysqli_real_escape_string($conn, json_encode($output['senses'])) . "', 
                    sensesEngels= '" . mysqli_real_escape_string($conn, json_encode($output['sensesEngels'])) . "'
                    WHERE signbank = '" . $signbankId . "'";
                $stmt = $conn->prepare($sql);
            // $stmt->execute();

            print_r($output);

        }
        else{
            echo "Handeness is empty";
        }

    }
}    }
