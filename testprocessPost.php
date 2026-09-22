<?php
$signbank = "47350";
$url = "https://leffe.science.uva.nl:8043/signBankAPI/update_gloss";
$postData = [
    'glossid' => $signbank,
    'webDic' => "no"
];
// Convert array to JSON string
$jsonData = json_encode($postData);

// Initialize cURL
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData); // Send JSON string as POST fields
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_VERBOSE, true);
// Disable SSL certificate check
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
// Set the Content-Type to application/json
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
$response = curl_exec($ch); // Execute the cURL request and retrieve the response
curl_close($ch);

// Handle response
echo $response;
?>
