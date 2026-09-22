<?php

require '/web/mysql_config.php';

$outputPath = '/home/gomer/figshareGebarenstrand/matched_transcriptions.csv';

$conn = new mysqli($servername, $username, $password, $database);
if ($conn->connect_error) {
    fwrite(STDERR, "Connection failed: " . $conn->connect_error . "\n");
    exit(1);
}

$result = $conn->query("SELECT * FROM matched_transcriptions ORDER BY id");
if (!$result) {
    fwrite(STDERR, "Query failed: " . $conn->error . "\n");
    exit(1);
}

$fp = fopen($outputPath, 'w');
if (!$fp) {
    fwrite(STDERR, "Cannot open output file: $outputPath\n");
    exit(1);
}

// Write header row with quoted column names
$fields = $result->fetch_fields();
$headers = [];
foreach ($fields as $field) {
    $headers[] = '"' . $field->name . '"';
}
fwrite($fp, implode(',', $headers) . "\n");

// Write data rows
$rowCount = 0;
while ($row = $result->fetch_row()) {
    $values = [];
    for ($i = 0; $i < count($row); $i++) {
        if ($row[$i] === null) {
            $values[] = 'NULL';
        } elseif ($row[$i] === '') {
            $values[] = '';
        } else {
            $values[] = '"' . str_replace('"', '""', $row[$i]) . '"';
        }
    }
    fwrite($fp, implode(',', $values) . "\n");
    $rowCount++;
}

fclose($fp);
$result->free();
$conn->close();

fwrite(STDERR, "Exported $rowCount rows to $outputPath\n");
