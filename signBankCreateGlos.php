<?php
error_reporting(E_ERROR | E_PARSE);

$url = "https://signbank.cls.ru.nl/dictionary/api_create_gloss/5/";

// Ensure $postData includes the CSRF token and other data
$postData = [
    'Dataset' => 'tstMH',
    'Lemma ID Gloss (Dutch)' => 'sdfdsf',
    'Lemma ID Gloss (English)' => 'sdfdsf',
    'Annotation ID Gloss (Dutch)' => 'sdfdsf',
    'Annotation ID Gloss (English)' => 'sdfdsf',
    'csrftoken' => (getenv('SIGNBANK_CSRFTOKEN') ?: '')
];

// Convert the array into URL-encoded query string
$postDataString = http_build_query($postData);


$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postDataString);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_VERBOSE, true);

$response = curl_exec($ch);

if ($response === false) 
    $response = curl_error($ch);

print_r($response);

curl_close($ch);

?>
