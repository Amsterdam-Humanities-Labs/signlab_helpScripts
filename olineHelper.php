<?php
include('../mysql_config.php');

// Create connection
// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT glos, videoLeft, videoCenter, videoRight FROM oline_data";
$result = $conn->query($sql);


echo "glos; videoLeft; videoCenter; videoRight; userId";
echo "<br>";


if ($result->num_rows > 0) {
  // output data of each row
  while($row = $result->fetch_assoc()) {
    $videoLeftArray = json_decode($row["videoLeft"], true);
    $videoCenterArray = json_decode($row["videoCenter"], true);
    $videoRightArray = json_decode($row["videoRight"], true);
    
    // Assuming glos is a single value or an array of values that can be directly associated
    $glos = $row["glos"]; 
    
    foreach($videoLeftArray as $index => $videoLeft) {

    if (strpos($videoLeftArray[$index]['video'], '.MP4') !== false) {

    
      $userid = $videoLeft['userid'];
      $videoLeftURL = $videoLeft['video'];
      $queryString = parse_url($videoLeftURL, PHP_URL_QUERY);
      parse_str($queryString, $queryParams);
      $videoLeftURL = $queryParams['name'];


      $videoCenterURL = $videoCenterArray[$index]['video'];
      $queryString = parse_url($videoCenterURL, PHP_URL_QUERY);
      parse_str($queryString, $queryParams);
      $videoCenterURL = $queryParams['name'];


      $videoRightURL = $videoRightArray[$index]['video'];
      $queryString = parse_url($videoRightURL, PHP_URL_QUERY);
      parse_str($queryString, $queryParams);
      $videoRightURL = $queryParams['name'];

      
      // Assuming glos is directly related to the userid and is a single value in this context
      echo $glos . "; " . $videoLeftURL . "; " . $videoCenterURL . "; " . $videoRightURL . "; " . $userid . PHP_EOL;
      echo "<br>";
    }
}
  }
} else {
  echo "0 results";
}
$conn->close();
?>
