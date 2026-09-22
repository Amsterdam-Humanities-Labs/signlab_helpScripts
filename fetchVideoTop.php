<?php
include('../mysql_config.php');

// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    echo json_encode(['error' => 'Connection failed: ' . $conn->connect_error]);
    exit;
}

// Get definitive outcome from query parameter
$definitive_outcome = $_GET['definitive_outcome'];

if (empty($definitive_outcome)) {
    echo json_encode(['error' => 'No definitive outcome provided']);
    exit;
}

// Fetch videoTop information from form_data table
$sql = "SELECT videoTop FROM form_data WHERE id = ?";
$stmt = $conn->prepare($sql);

if ($stmt === false) {
    echo json_encode(['error' => 'Prepare failed: ' . $conn->error]);
    exit;
}

$stmt->bind_param('s', $definitive_outcome);
if (!$stmt->execute()) {
    echo json_encode(['error' => 'Execute failed: ' . $stmt->error]);
    exit;
}

$stmt->bind_result($videoTopJson);
$stmt->fetch();

if ($stmt->errno) {
    echo json_encode(['error' => 'Fetch failed: ' . $stmt->error]);
    exit;
}

$stmt->close();
$conn->close();

if ($videoTopJson) {
    $videoTopData = json_decode($videoTopJson, true);
    // Assuming videoTop is an array and we need the first video
    $videoTopFile = $videoTopData[0]['videoTop'];

    echo json_encode(['file' => $videoTopFile]);
} else {
    echo json_encode(['error' => 'No videoTop data found']);
}
?>
