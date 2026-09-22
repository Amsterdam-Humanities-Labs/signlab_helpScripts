<?php
include('../mysql_config.php');

// Disable PHP warnings
error_reporting(E_ERROR | E_PARSE);

// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

// Check the connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch data based on provided parameters
$glosId = $_GET['glosId'] ?? null;
$type = $_GET['type'] ?? '';
$videoTop = $_GET['videoTop'] ?? '';
$m_file = $_GET['m_file'] ?? '';
$index = isset($_GET['index']) ? intval($_GET['index']) : -1;

// Clean up parameters
$m_file = str_replace('.mp4', '.wav', $m_file);
$videoTop = urldecode($videoTop); // Make sure URL encoding is properly handled

// Initialize response
$response = [
    "status" => "processing",
    "message" => "Processing deletion request",
    "glosId" => $glosId,
    "type" => $type,
    "videoTop" => $videoTop,
    "m_file" => $m_file,
    "index" => $index,
    "debug" => $_GET
];

if ($glosId && $type) {
    $updates = [];
    
    // Update matched_transcriptions if m_file is provided and not "no_videoCenter"
    if (!empty($m_file) && $m_file !== "no_videoCenter") {
        $stmt = $conn->prepare("UPDATE matched_transcriptions SET added = 'DELETE' WHERE m_file = ? AND m_transcription = ?");
        if ($stmt) {
            $zOg = ucfirst(strtolower($type)); // Capitalize first letter
            $stmt->bind_param("ss", $m_file, $glosId);
            $stmt->execute();
            if ($stmt->affected_rows > 0) {
                $updates[] = "matched_transcriptions updated";
            }
            $stmt->close();
        }
    }
    
    // Update CameraRecords if videoTop is provided
    if (!empty($videoTop)) {
        // Extract just the filename from the videoTop URL if necessary
        $videoTopFile = $videoTop;
        if (strpos($videoTop, '/') !== false) {
            $videoTopFile = basename(parse_url($videoTop, PHP_URL_PATH));
        }
        
        // Try to update with exact match
        $stmt = $conn->prepare("UPDATE CameraRecords SET stateVideo = 'DELETE' WHERE glosId = ? AND videoTop = ? AND zOg = ?");
        if ($stmt) {
            $zOg = ucfirst(strtolower($type)); // Capitalize first letter
            $stmt->bind_param("sss", $glosId, $videoTopFile, $zOg);
            $stmt->execute();
            if ($stmt->affected_rows > 0) {
                $updates[] = "CameraRecords updated with exact match";
            } else {
                // Try with LIKE if exact match fails
                $stmt->close();
                $videoTopPattern = "%" . $videoTopFile . "%";
                $stmt = $conn->prepare("UPDATE CameraRecords SET stateVideo = 'DELETE' WHERE glosId = ? AND videoTop LIKE ? AND zOg = ?");
                if ($stmt) {
                    $stmt->bind_param("sss", $glosId, $videoTopPattern, $zOg);
                    $stmt->execute();
                    if ($stmt->affected_rows > 0) {
                        $updates[] = "CameraRecords updated with LIKE pattern";
                    }
                }
            }
            if ($stmt) {
                $stmt->close();
            }
        }
    }
    
    // If we have index but no updates yet, try to update by index
    if ($index >= 0 && empty($updates)) {
        // Get records in order and update the one at the specified index
        $zOg = ucfirst(strtolower($type));
        
        // First try matched_transcriptions
        $mt_sql = "SELECT ID FROM matched_transcriptions 
                  WHERE m_transcription = ? AND zOg = ? AND added='1' 
                  ORDER BY date ASC, time ASC, ID ASC";
        $stmt = $conn->prepare($mt_sql);
        if ($stmt) {
            $stmt->bind_param("ss", $glosId, $zOg);
            $stmt->execute();
            $result = $stmt->get_result();
            $rows = [];
            while ($row = $result->fetch_assoc()) {
                $rows[] = $row['ID'];
            }
            $stmt->close();
            
            // If we have enough rows, update the one at the specified index
            if (count($rows) > $index) {
                $recordId = $rows[$index];
                $stmt = $conn->prepare("UPDATE matched_transcriptions SET added = 'DELETE' WHERE ID = ?");
                $stmt->bind_param("i", $recordId);
                $stmt->execute();
                if ($stmt->affected_rows > 0) {
                    $updates[] = "matched_transcriptions updated by index";
                }
                $stmt->close();
            }
        }
        
        // Then try CameraRecords if no update was made
        if (empty($updates)) {
            $cr_sql = "SELECT ID FROM CameraRecords 
                      WHERE glosId = ? AND stateVideo = 'stopped' AND zOg = ? 
                      ORDER BY datetime_ms ASC, ID ASC";
            $stmt = $conn->prepare($cr_sql);
            if ($stmt) {
                $stmt->bind_param("ss", $glosId, $zOg);
                $stmt->execute();
                $result = $stmt->get_result();
                $rows = [];
                while ($row = $result->fetch_assoc()) {
                    $rows[] = $row['ID'];
                }
                $stmt->close();
                
                // If we have enough rows, update the one at the specified index
                if (count($rows) > $index) {
                    $recordId = $rows[$index];
                    $stmt = $conn->prepare("UPDATE CameraRecords SET stateVideo = 'DELETE' WHERE ID = ?");
                    $stmt->bind_param("i", $recordId);
                    $stmt->execute();
                    if ($stmt->affected_rows > 0) {
                        $updates[] = "CameraRecords updated by index";
                    }
                    $stmt->close();
                }
            }
        }
    }
    
    // If we successfully updated at least one table
    if (!empty($updates)) {
        $response = [
            "status" => "success",
            "message" => "Video marked for deletion: " . implode(", ", $updates),
            "updates" => $updates
        ];
    } else {
        $response = [
            "status" => "error",
            "message" => "No records were updated. Please check the provided parameters.",
            "params" => [
                "glosId" => $glosId,
                "type" => $type,
                "videoTop" => $videoTop,
                "m_file" => $m_file,
                "index" => $index
            ]
        ];
    }
} else {
    $response = [
        "status" => "error",
        "message" => "Missing glosId or type parameter.",
        "received" => $_GET
    ];
}

// Return the response as JSON
header("Content-Type: application/json");
echo json_encode($response);

// Close the database connection
$conn->close();
?>
