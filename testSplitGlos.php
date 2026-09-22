<?php
include('../mysql_config.php');

// Create a connection to the database
$conn = new mysqli($servername, $username, $password, $database);
$baseGlos = "IN-DE-MIN-STAAN-A";
$glosList = Array();




$baseGlos = preg_replace('/[-+][A-Z]$/', '', $baseGlos);
$glosListAZ = [];
$glosListAZ[] = $baseGlos;
for ($i = 'A'; $i <= 'Z';) {
$glosListAZ[] = $baseGlos . "-" . $i;
if ($i == 'Z') 
{
    break;
}
$i = chr(ord($i) + 1);
}

//loop through the array
foreach($glosListAZ as $glos)
{
    // Prepare and execute the query.
    $query = "SELECT * FROM form_data WHERE glos = ?";
    $stmt = $conn->prepare($query);
    $stmt->bind_param("s", $glos);
    $stmt->execute();
    $result = $stmt->get_result();
    //add result to list
    if($result->num_rows > 0)
    {
        $row = $result->fetch_assoc();
        $glosList[] = $glos;

    }

    $signbankJson = "../glosses_transformed.json";
    $signbank = file_get_contents($signbankJson);
    $decodedData = json_decode($signbank, true); // Decode as an associative array
    $matchesGlos = [];
    $matchesGlos[] = array_filter($decodedData, function ($entry) use ($glos) {
        $details = current($entry);
        $matchesGlos = empty($glos) || $details['Annotation ID Gloss: Dutch'] === $glos;

        return $matchesGlos;
    });
    foreach ($matchesGlos as $key => $value) {
        if (!empty($value)) {
            $glosList[] = $glos;
        }
    }
}



$nextIdentifier = findNextFreeIdentifier($glosList);



$taskList = incrementGlosWithoutLetter($glosList);
//reverse the array
$taskList = array_reverse($taskList);

print_r($taskList);

// foreach ($taskList as $task) {
//     print_r($task);
//     $query = "UPDATE form_data SET glos = ? WHERE glos = ?";
//     $stmt = $conn->prepare($query);
//     $stmt->bind_param("ss", $task['new'], $task['old']);
//     $success = $stmt->execute();

//     if ($success) {
//         echo "Update successful for: " . $task['old'] . " to " . $task['new'] . "\n";
//     } else {
//         // You can retrieve error details from the statement and connection objects
//         echo "Update failed for: " . $task['old'] . ". Error: " . $stmt->error . "\n";
//     }

// }



function incrementGlosWithoutLetter($array) {
    $found = false; // Flag to indicate the first non -A item has been found
    $currentSuffix = 'A'; // Start with '-A'
    $taskList = []; // Initialize an empty task list

    for ($i = 0; $i < count($array); $i++) {
        $originalValue = $array[$i]; // Store the original value for the task list

        if (!$found && !preg_match('/-A$/', $array[$i])) {
            // Found the first item without -A. Append -A to it.
            $array[$i] .= '-A';
            $found = true;
            // Add to task list
            $taskList[] = ['old' => $originalValue, 'new' => $array[$i]];
        } else if ($found) {
            // Once the first non-A item is found and modified, increment subsequent items
            $nextSuffix = ++$currentSuffix; // PHP automatically handles letter increment
            if ($nextSuffix > 'Y') {
                // Stop at '-Y'
                break;
            }
            // Replace or append the next suffix
            if (preg_match('/-[A-Z]$/', $array[$i])) {
                $array[$i] = preg_replace('/-[A-Z]$/', '-' . $nextSuffix, $array[$i]);
            } else {
                $array[$i] .= '-' . $nextSuffix;
            }
            // Add to task list
            $taskList[] = ['old' => $originalValue, 'new' => $array[$i]];
        }
    }

    return $taskList;
}





function findNextFreeIdentifier($identifiers) {
    // Get the last identifier in the array
    $lastIdentifier = end($identifiers);
    
    $modifiedIdentifier = preg_replace('/[-+][A-Z]$/', '', $lastIdentifier);

    if ($modifiedIdentifier !== $lastIdentifier) 
    {

        //calculate the next letter
        $ex = explode('-', $lastIdentifier);
        //get the last letter and increment it
        $lastLetter = end($ex);
        
        $nextLetter = chr(ord($lastLetter) + 1);

        // Return the next identifier
        return $modifiedIdentifier .'-'. $nextLetter;
    }
    else
    {
        return $lastIdentifier . '-A';
    }
}



?>
