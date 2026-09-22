<?php
// Disable warnings
error_reporting(E_ERROR | E_PARSE);

include('../mysql_config.php');

// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

// Check the connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}


//first we want to get all rows from table form_data
$sql = "SELECT * FROM form_data";
$result = $conn->query($sql);
//then we do for loop
while ($row = $result->fetch_assoc()) {
    //then we want to get logboek from the row and look for "Glos toegevoegd door: " and then get user from that line
    //the user can be: casper, gomer, ulrika, dalene, lisa, ellen, tobias, ray, galya
    $logboek = $row["logboek"];
    // echo $logboek;
    $user = "";
    $pos = strpos($logboek, "Glos toegevoegd door: ");
    if ($pos !== false) {
        $user = substr($logboek, $pos + 21, strpos($logboek, "\n", $pos) - $pos - 21);
    
    echo "lala: ".$user;    
    //then we check if $user exists in $user and then get userid in return
    $userId = "";
    //we also get users rom table users
$sql = "SELECT * FROM users";
$users = $conn->query($sql);
//now we have an array of userid with user
    while ($userRow = $users->fetch_assoc()) {
        if (strtolower($userRow["user"]) == trim(strtolower($user))) {
            $userId = $userRow["userId"];
        }
    }
    echo $userId;
    //then we have the user, then we update madebywie in the row with the userid
    $sql = "UPDATE form_data SET madeByWie = '$userId' WHERE id = " . $row["id"];
    $stmt = $conn->prepare($sql);
    $stmt->execute();

    }
}