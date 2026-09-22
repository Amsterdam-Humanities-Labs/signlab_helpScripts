<?php
include('../mysql_config.php');

// Create connection
$conn = new mysqli($servername, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Adjusted SQL query to exclude rows where videoTop or signbank is not filled
$sql = "SELECT *
        FROM form_data
        WHERE glos IN (
            SELECT glos
            FROM form_data
            GROUP BY glos
            HAVING COUNT(*) > 1
        )
        AND (videoTop IS NULL)
        AND (signbank IS NULL)";

$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // Output data of each row
    while($row = $result->fetch_assoc()) {
        echo "glos: " . $row['glos'] . " - videoTop: " . $row['videoTop'] . " - signbank: " . $row['signbank'] . "<br>";
        // Process further fields as necessary

        //remove the sql query
        $sql = "DELETE FROM form_data WHERE id = " . $row['id'] . ";";
        $stmt = $conn->prepare($sql);
        $stmt->execute();
        
    }
} else {
    echo "No duplicates found with both videoTop and signbank fields filled.";
}

$conn->close();
?>
