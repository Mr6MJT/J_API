<?php

function createDNSRecord($email, $apiKey, $zoneID, $type, $name, $content, $ttl = 1, $proxied = true) {
    // Check if the DNS record already exists
    $existingRecord = getExistingDNSRecord($email, $apiKey, $zoneID, $type, $name);
    
    if ($existingRecord) {
        echo "DNS record already exists!";
        return; // Exit the function if the record already exists
    }

    // If the DNS record does not exist, proceed to create it
    $url = "https://api.cloudflare.com/client/v4/zones/{$zoneID}/dns_records";

    $data = array(
        'type' => $type,
        'name' => $name,
        'content' => $content,
        'ttl' => $ttl,
        'proxied' => $proxied
    );

    $headers = array(
        'Content-Type: application/json',
        'X-Auth-Email: ' . $email,
        'X-Auth-Key: ' . $apiKey,
    );

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

    $response = curl_exec($ch);
    $error = curl_error($ch);

    curl_close($ch);

    if ($error) {
        echo "Error: " . $error;
    } else {
        $result = json_decode($response, true);
        if ($result['success']) {
            echo "DNS record created successfully!";
        } else {
            echo "Error: " . $result['errors'][0]['message'];
        }
    }
}

function getExistingDNSRecord($email, $apiKey, $zoneID, $type, $name) {
    $url = "https://api.cloudflare.com/client/v4/zones/{$zoneID}/dns_records?type={$type}&name={$name}";

    $headers = array(
        'Content-Type: application/json',
        'X-Auth-Email: ' . $email,
        'X-Auth-Key: ' . $apiKey,
    );

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

    $response = curl_exec($ch);
    $error = curl_error($ch);

    curl_close($ch);

    if ($error) {
        echo "Error: " . $error;
        return false;
    } else {
        $result = json_decode($response, true);
        if (isset($result['result']) && count($result['result']) > 0) {
            // DNS record exists
            return $result['result'][0];
        } else {
            // DNS record does not exist
            return false;
        }
    }
}

?>


<!DOCTYPE html>
<html>
<head>
    <title>Create Subdomain</title>
</head>
<body>
    <form method="post">
        <button type="submit" name="create_subdomain">Create Subdomain</button>
    </form>

    <?php
    // Check if the form is submitted
    if (isset($_POST['create_subdomain'])) {
        // Generate a random number for the name
        $randomNumber = rand(100, 999); // Generates a random number between 100 and 999
        $name = "client" . $randomNumber . ".domain.ao";

        // Call the createDNSRecord function when the form is submitted
        createDNSRecord(
            '@gmail.com', // Replace with your email
            '', // Replace with your API key
            '', // Replace with your zone ID
            'A', // Type of DNS record
            $name, // Name of the DNS record
            '0.0.0.0' // Content of the DNS record
        );
		echo "  " . $name;
    }
		                                                                               
    ?> 
</body>
</html>


<?php
	/**
	 * My Account dashboard.
	 *
	 * @since 2.6.0
	 */
	do_action( 'woocommerce_account_dashboard' );

	/**
	 * Deprecated woocommerce_before_my_account action.
	 *
	 * @deprecated 2.6.0
	 */
	do_action( 'woocommerce_before_my_account' );

	/**
	 * Deprecated woocommerce_after_my_account action.
	 *
	 * @deprecated 2.6.0
	 */
	do_action( 'woocommerce_after_my_account' );

/* Omit closing PHP tag at the end of PHP files to avoid "headers already sent" issues. */
