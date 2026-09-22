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

// Fetch data from the POST request
$id = $_POST['id'] ?? null;
$videoIndex = isset($_POST['videoIndex']) ? intval($_POST['videoIndex']) : null;
$label = $_POST['label'] ?? null;
$category = $_POST['category'] ?? null;

$response = array("status" => "error", "message" => "Invalid request.");

// Log the input for debugging
$debug = array(
    "received" => $_POST,
    "parsed" => array(
        "id" => $id, 
        "videoIndex" => $videoIndex, 
        "label" => $label, 
        "category" => $category
    )
);

// Get the type of content we're working with to determine the right table
$contentType = null;
if ($id) {
    // Check if this is a Zin (sentence) record
    $checkType = $conn->prepare("SELECT zOg FROM CameraRecords WHERE glosId = ? LIMIT 1");
    $checkType->bind_param("s", $id);
    $checkType->execute();
    $result = $checkType->get_result();
    
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        $contentType = $row['zOg'];
    }
    $checkType->close();
    
    // If not found in CameraRecords, try matched_transcriptions
    if (!$contentType) {
        $checkType = $conn->prepare("SELECT zOg FROM matched_transcriptions WHERE m_transcription = ? LIMIT 1");
        $checkType->bind_param("s", $id);
        $checkType->execute();
        $result = $checkType->get_result();
        
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $contentType = $row['zOg'];
        }
        $checkType->close();
    }
    
    $debug["contentType"] = $contentType;
}

// Function to update a specific row in a table by index
function updateRowByIndex($conn, $table, $column, $value, $id, $index, $idColumn, $contentType) {
    // Determine which sorting fields to use based on table
    $orderBy = ($table === 'matched_transcriptions') ? "ORDER BY date ASC, time ASC, ID ASC" : "ORDER BY datetime_ms ASC, ID ASC";
    
    // Build the query to get IDs in order
    $query = "SELECT ID FROM $table WHERE $idColumn = ? AND zOg = ? $orderBy";
    
    $stmt = $conn->prepare($query);
    $stmt->bind_param("ss", $id, $contentType);
    $stmt->execute();
    $result = $stmt->get_result();
    
    // Get all row IDs in sorted order
    $rows = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row['ID'];
    }
    $stmt->close();
    
    // Check if the requested index exists
    if (count($rows) <= $index) {
        return array(
            "status" => "error", 
            "message" => "Index out of range", 
            "rows_found" => count($rows), 
            "requested_index" => $index
        );
    }
    
    // Get the ID of the row at the specified index
    $rowId = $rows[$index];
    
    // Update the specified row
    $updateStmt = $conn->prepare("UPDATE $table SET $column = ? WHERE ID = ?");
    $updateStmt->bind_param("si", $value, $rowId);
    $updateStmt->execute();
    $affectedRows = $updateStmt->affected_rows;
    $updateStmt->close();
    
    return array(
        "status" => ($affectedRows > 0) ? "success" : "error",
        "message" => ($affectedRows > 0) ? "Updated successfully" : "No changes made",
        "affected_rows" => $affectedRows,
        "row_id" => $rowId
    );
}

if ($id && $contentType) {
    // Determine which tables to update based on content type and other factors
    if ($videoIndex !== null) {
        // We have a specific index, so we need to update the specific row
        
        if ($label !== null) {
            // First try updating matched_transcriptions
            $mtResult = updateRowByIndex(
                $conn, 'matched_transcriptions', 'videoLabel', $label, $id, $videoIndex, 
                ($contentType === 'Zin' ? 'm_transcription' : 'definitive_outcome'), $contentType
            );
            
            // If that fails or has no effect, try CameraRecords
            if ($mtResult["status"] === "error" || $mtResult["affected_rows"] === 0) {
                $crResult = updateRowByIndex(
                    $conn, 'CameraRecords', 'videoLabel', $label, $id, $videoIndex, 'glosId', $contentType
                );
                
                if ($crResult["status"] === "success") {
                    $response = array(
                        "status" => "success",
                        "message" => "Label updated successfully in CameraRecords",
                        "details" => $crResult,
                        "debug" => $debug
                    );
                } else {
                    $response = array(
                        "status" => "error",
                        "message" => "Failed to update label in either table",
                        "mt_result" => $mtResult,
                        "cr_result" => $crResult,
                        "debug" => $debug
                    );
                }
            } else {
                $response = array(
                    "status" => "success",
                    "message" => "Label updated successfully in matched_transcriptions",
                    "details" => $mtResult,
                    "debug" => $debug
                );
            }
        }
        
        if ($category !== null) {
            // First try updating matched_transcriptions
            $mtResult = updateRowByIndex(
                $conn, 'matched_transcriptions', 'videoCategory', $category, $id, $videoIndex, 
                ($contentType === 'Zin' ? 'm_transcription' : 'definitive_outcome'), $contentType
            );
            
            // If that fails or has no effect, try CameraRecords
            if ($mtResult["status"] === "error" || $mtResult["affected_rows"] === 0) {
                $crResult = updateRowByIndex(
                    $conn, 'CameraRecords', 'videoCategory', $category, $id, $videoIndex, 'glosId', $contentType
                );
                
                if ($crResult["status"] === "success") {
                    $response = array(
                        "status" => "success",
                        "message" => "Category updated successfully in CameraRecords",
                        "details" => $crResult,
                        "debug" => $debug
                    );
                } else {
                    $response = array(
                        "status" => "error",
                        "message" => "Failed to update category in either table",
                        "mt_result" => $mtResult,
                        "cr_result" => $crResult,
                        "debug" => $debug
                    );
                }
            } else {
                $response = array(
                    "status" => "success",
                    "message" => "Category updated successfully in matched_transcriptions",
                    "details" => $mtResult,
                    "debug" => $debug
                );
            }
        }
    } else {
        // No specific index provided, updating all matching rows (legacy behavior)
        if ($label !== null) {
            // For Zin records, primarily update CameraRecords since they're the live recordings
            if ($contentType === 'Zin' || $contentType === 'Voorbeeldzin') {
                $stmt = $conn->prepare("UPDATE CameraRecords SET videoLabel = ? WHERE glosId = ? AND zOg = ?");
                $stmt->bind_param("sss", $label, $id, $contentType);
                $stmt->execute();
                $crAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                // Also try to update matched_transcriptions for completeness
                $stmt = $conn->prepare("UPDATE matched_transcriptions SET videoLabel = ? WHERE m_transcription = ? AND zOg = ?");
                $stmt->bind_param("sss", $label, $id, $contentType);
                $stmt->execute();
                $mtAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                $response = array(
                    "status" => "success",
                    "message" => "Label updated in CameraRecords and/or matched_transcriptions",
                    "cr_affected_rows" => $crAffectedRows,
                    "mt_affected_rows" => $mtAffectedRows,
                    "debug" => $debug
                );
            } else {
                // For non-Zin records, try both tables
                $stmt = $conn->prepare("UPDATE matched_transcriptions SET videoLabel = ? WHERE definitive_outcome = ?");
                $stmt->bind_param("ss", $label, $id);
                $stmt->execute();
                $mtAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                $stmt = $conn->prepare("UPDATE CameraRecords SET videoLabel = ? WHERE glosId = ?");
                $stmt->bind_param("ss", $label, $id);
                $stmt->execute();
                $crAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                $response = array(
                    "status" => "success",
                    "message" => "Label updated in one or both tables",
                    "mt_affected_rows" => $mtAffectedRows,
                    "cr_affected_rows" => $crAffectedRows,
                    "debug" => $debug
                );
            }
        } elseif ($category !== null) {
            // Similar approach for category updates
            if ($contentType === 'Zin' || $contentType === 'Voorbeeldzin') {
                $stmt = $conn->prepare("UPDATE CameraRecords SET videoCategory = ? WHERE glosId = ? AND zOg = ?");
                $stmt->bind_param("sss", $category, $id, $contentType);
                $stmt->execute();
                $crAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                $stmt = $conn->prepare("UPDATE matched_transcriptions SET videoCategory = ? WHERE m_transcription = ? AND zOg = ?");
                $stmt->bind_param("sss", $category, $id, $contentType);
                $stmt->execute();
                $mtAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                $response = array(
                    "status" => "success",
                    "message" => "Category updated in CameraRecords and/or matched_transcriptions",
                    "cr_affected_rows" => $crAffectedRows,
                    "mt_affected_rows" => $mtAffectedRows,
                    "debug" => $debug
                );
            } else {
                // For non-Zin records
                $stmt = $conn->prepare("UPDATE matched_transcriptions SET videoCategory = ? WHERE definitive_outcome = ?");
                $stmt->bind_param("ss", $category, $id);
                $stmt->execute();
                $mtAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                $stmt = $conn->prepare("UPDATE CameraRecords SET videoCategory = ? WHERE glosId = ?");
                $stmt->bind_param("ss", $category, $id);
                $stmt->execute();
                $crAffectedRows = $stmt->affected_rows;
                $stmt->close();
                
                $response = array(
                    "status" => "success",
                    "message" => "Category updated in one or both tables",
                    "mt_affected_rows" => $mtAffectedRows,
                    "cr_affected_rows" => $crAffectedRows,
                    "debug" => $debug
                );
            }
        }
    }
} else {
    $response = array(
        "status" => "error",
        "message" => "Missing required parameters or cannot determine content type",
        "debug" => $debug
    );
}

// Return the response as JSON
header("Content-Type: application/json");
echo json_encode($response);

// Close the database connection
$conn->close();
?>
