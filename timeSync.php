<?php
include('../mysql_config.php');
// error_reporting(E_ALL);
// ini_set('display_errors', 1);
// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);

$sql = "SELECT * FROM form_data WHERE videoTop IS NOT NULL";
$result = $conn->query($sql);

//json headers
header('Content-Type: application/json');

//am i allowed to start today?
$asd = "SELECT * FROM studio_data WHERE date = CURDATE()";
$asd = $conn->query($asd);
$rowa = $asd->fetch_assoc();

$resultsArray = array();

if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $resultsTimes = extractTimes($row['videoTop']);

        foreach ($resultsTimes as $item) {
            if (strpos($item['videoTop'], "skipped") === false) {
                $startTime = convertTimeToSeconds($item['startTime']);
                $stopTime = convertTimeToSeconds($item['stopTime']);
                $startDate = getSqlDate($item['startTime']);

                $startTime += 7198; // Adjust times
                $stopTime += 7200; // Adjust times

                $query = "SELECT * FROM videoMetaData WHERE date = '$startDate' AND time >= '$startTime' AND time <= '$stopTime'";
                $resulta = $conn->query($query);

                if ($resulta->num_rows > 0) {
                    while ($rowa = $resulta->fetch_assoc()) {
                        $file = $rowa['videoPath'];
                        $exists = false;
                        $columnToUpdate = '';
                        $videoData = [];

                        // Determine which column to update based on the file prefix
                        if (strtolower(basename($file))[0] == 'r') {
                            $columnToUpdate = 'videoRight';
                            $videoData = $row['videoRight'];
                        } elseif (basename($file)[0] == 'L') {
                            $columnToUpdate = 'videoLeft';
                            $videoData = $row['videoLeft'];
                        } elseif (strtolower(basename($file))[0] == 'm') {
                            $columnToUpdate = 'videoCenter';
                            $videoData = $row['videoCenter'];
                        }

                        if ($columnToUpdate) {
                            // Check if the field is empty
                            if ($videoData == '') {
                                $videoData = [];
                            } else {
                                $videoData = json_decode($videoData, true);
                            }

                            // Check for existing userid and file
                            foreach ($videoData as $itemb) {
                                if ($itemb['userid'] == $item['userid'] && $itemb['file'] == $file) {
                                    $exists = true;
                                    break;
                                }
                            }

                            if (!$exists) {
                                $itema = array(
                                    'userid' => $item['userid'],
                                    'file' => $file
                                );
                                $videoData[] = $itema;
                                $sql = "UPDATE form_data SET $columnToUpdate = '" . json_encode($videoData) . "' WHERE glos = '" . $row['glos'] . "'";
                                if ($conn->query($sql) === TRUE) {
                                    // Record updated successfully
                                } else {
                                    // Error updating record
                                }
                            }
                        }
                    }
                }
            }
        }

        // Process to fill missing video fields
        $videoRight = !empty($row['videoRight']) ? json_decode($row['videoRight'], true) : [];
        $videoCenter = !empty($row['videoCenter']) ? json_decode($row['videoCenter'], true) : [];
        $videoLeft = !empty($row['videoLeft']) ? json_decode($row['videoLeft'], true) : [];

        // Check and fill missing video fields
        if (empty($videoRight) && !empty($videoCenter) && !empty($videoLeft)) {
            $videoRight = createNewVideoArray($videoCenter, 'R');
            $updated = true;
        }

        if (empty($videoCenter) && !empty($videoRight) && !empty($videoLeft)) {
            $videoCenter = createNewVideoArray($videoRight, 'M');
            $updated = true;
        }

        if (empty($videoLeft) && !empty($videoRight) && !empty($videoCenter)) {
            $videoLeft = createNewVideoArray($videoRight, 'L');
            $updated = true;
        }

        // Update the database if changes were made
        if ($updated) {
            $updateSql = "UPDATE form_data SET videoRight = ?, videoCenter = ?, videoLeft = ? WHERE glos = ?";
            $stmt = $conn->prepare($updateSql);
            $stmt->bind_param("ssss", json_encode($videoRight), json_encode($videoCenter), json_encode($videoLeft), $row['glos']);
            $stmt->execute();
        }
    }
}

echo json_encode($resultsArray);

// Update studio_data
$sql = "UPDATE studio_data SET processed = 2 WHERE date = CURDATE()";
$stmt = $conn->prepare($sql);
$stmt->execute();
$stmt->close();

writeToJson();

function getSqlDate($date) {
    $date = new DateTime($date);
    return $date->format('Y-m-d');
}

function convertTimeToSeconds($dateTime) {
    $date = new DateTime($dateTime);
    $time = $date->format('H:i:s'); // Extracting time in HH:MM:SS format
    list($hours, $minutes, $seconds) = explode(':', $time);
    return ($hours * 3600) + ($minutes * 60) + $seconds;
}

function extractTimes($json) {
    $data = json_decode($json, true);
    $results = [];
    if (is_array($data)) {
        foreach ($data as $item) {
            if (isset($item['startTime']) && isset($item['stopTime']) && isset($item['userid']) && isset($item['videoTop'])) {
                $results[] = array(
                    'startTime' => $item['startTime'],
                    'stopTime' => $item['stopTime'],
                    'userid' => $item['userid'],
                    'videoTop' => $item['videoTop']
                );
            }
        }
    }
    return $results;
}

function writeToJson() {
    $filePath = "/web/servicesRecords.json";
    $jsonString = file_get_contents($filePath);
    $data = json_decode($jsonString, true);
    $service_name = "timeSync";
    $found = false;

    foreach ($data as &$entry) {
        if ($entry['service'] === $service_name) {
            $entry['date'] = date("Y-m-d H:i:s");
            $found = true;
            break;
        }
    }

    if (!$found) {
        $newRecord = [
            "service" => $service_name,
            "date" => date("Y-m-d H:i:s")
        ];
        $data[] = $newRecord;
    }

    $newJsonString = json_encode($data, JSON_PRETTY_PRINT);
    file_put_contents($filePath, $newJsonString);
}

function createNewVideoArray($sourceArray, $newPrefix) {
    $newArray = [];
    foreach ($sourceArray as $item) {
        $newFile = preg_replace('/^./', $newPrefix, basename($item['file']));
        $newPath = dirname($item['file']) . '/' . $newFile;
        $newArray[] = [
            'userid' => $item['userid'],
            'file' => $newPath
        ];
    }
    return $newArray;
}
?>
