<?php
//header is json
header('Content-Type: application/json');
error_reporting(E_ERROR | E_PARSE);


function removeUserById(&$array, $userid) {
    foreach ($array as $key => $value) {
            unset($array[$key]);
        
    }
    // Re-index the array in case it's needed
    $array = array_values($array);
}


include('../mysql_config.php');
$conn = new mysqli($servername, $username, $password, $database);

$glosId = $_GET['glosId'];
$userId = $_GET['userId'];
$method = $_GET['method'];
$thema = $_GET['thema'];
$captureDevice = $_GET['captureDevice'];

$json_output = [];

if($method == "multiple"){


    $sql = "SELECT * FROM form_data WHERE videoTop IS NOT NULL AND thema = '$thema'";

}

if($method == "single")
{

    $sql = "SELECT * FROM form_data WHERE id = '$glosId' AND videoTop IS NOT NULL";

}

if($captureDevice == "unreal")
{

    $sql = "UPDATE form_data SET unreal_take = NULL WHERE thema = '$thema'";
    $stmt = $conn->prepare($sql);
    $stmt->execute();
    $json_output = array(
        "status" => "Leeggemaakt!",
    );

}
else
{




$result = $conn->query($sql);

while($row = $result->fetch_assoc()) {
    $glos = $row['glos'];
    $videoTop = $row['videoTop'];
    $id = $row['id'];
    $videoLeft = $row['videoLeft'];
    $videoCenter = $row['videoCenter'];
    $videoRight = $row['videoRight'];

    
    if($videoTop != NULL) {
        $videoTopArray = json_decode($videoTop, true);
        removeUserById($videoTopArray, $userId);
        $videoTop = json_encode($videoTopArray);  
      }

    if($videoLeft != NULL) {
        $videoLeftArray = json_decode($videoLeft, true);
        removeUserById($videoLeftArray, $userId);
        $videoLeft = json_encode($videoLeftArray);
    }

    if($videoCenter != NULL) {
        $videoCenterArray = json_decode($videoCenter, true);
        removeUserById($videoCenterArray, $userId);
        $videoCenter = json_encode($videoCenterArray);
    }

    if($videoRight != NULL) {
        $videoRightArray = json_decode($videoRight, true);
        removeUserById($videoRightArray, $userId);
        $videoRight = json_encode($videoRightArray);
    }


    // Update the database with the new videoTop value
    $updateSql = "UPDATE form_data SET videoTop = '$videoTop', videoLeft = '$videoLeft', videoCenter = '$videoCenter', videoRight = '$videoRight' WHERE id = '$id'";
    $stmt = $conn->prepare($updateSql);
    $stmt->execute();

    $json_output = array(
        "status" => "Leeggemaakt!",
    );
}





}

echo json_encode($json_output);

?>