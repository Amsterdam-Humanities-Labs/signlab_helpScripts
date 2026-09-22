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
$sql = "SELECT id, logboek FROM form_data";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $id = $row['id'];
        $logboek = $row['logboek'];

        // Split logboek into lines and count duplicates
        $lines = explode("\n", $logboek);
        $line_counts = array_count_values($lines);

        // Rebuild logboek consolidating duplicates
        $new_logboek = [];
        foreach ($line_counts as $line => $count) {
            if ($count > 1) {
                $new_logboek[] = $line;
            } else {
                $new_logboek[] = $line;
            }
        }
        $new_logboek = implode("\n", $new_logboek);

        echo $new_logboek;
        // Update the row with the consolidated logboek
        $updateSQL = "UPDATE form_data SET logboek = '" . $conn->real_escape_string($new_logboek) . "' WHERE id = $id";
        $conn->query($updateSQL);
    }
    echo "Logboek entries have been updated.";
} else {
    echo "No records found.";
}

$conn->close();
?>
