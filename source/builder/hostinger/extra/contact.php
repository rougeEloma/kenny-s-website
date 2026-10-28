<?php
// Contact form handler for Kenny's International (Hostinger / PHP mail).
// Messages go to the address below.
$TO   = 'serviceclient@kennysinternational.com';
$FROM = 'no-reply@kennysinternational.com'; // must be an address on this domain

$ajax = isset($_SERVER['HTTP_X_REQUESTED_WITH']) || (isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'text/html') === false);

function done($ok, $ajax) {
    if ($ajax) {
        http_response_code($ok ? 200 : ($ok === null ? 400 : 500));
        header('Content-Type: application/json');
        echo json_encode(['ok' => (bool)$ok]);
    } else {
        header('Location: /contact.html' . ($ok ? '?sent=1#form' : '#form'), true, 303);
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contact.html', true, 303); exit; }

// Spam trap: real visitors never fill this hidden field.
if (!empty($_POST['company-website'])) done(true, $ajax);

function field($k, $max) {
    $v = isset($_POST[$k]) ? trim((string)$_POST[$k]) : '';
    return mb_substr($v, 0, $max);
}
function oneline($s) { return trim(preg_replace('/[\r\n\t]+/', ' ', $s)); }

$name    = oneline(field('name', 120));
$email   = oneline(field('email', 200));
$phone   = oneline(field('phone', 60));
$topic   = oneline(field('topic', 80));
$message = field('message', 5000);

if ($name === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) done(null, $ajax);

$allowed = ['General enquiry', 'Products and brands', 'Our stores', 'Partnerships and franchises', 'Press', 'Careers'];
if (!in_array($topic, $allowed, true)) $topic = 'General enquiry';

$subject = '=?UTF-8?B?' . base64_encode("Website message: $topic — $name") . '?=';
$body  = "New message from the Kenny's International website\n\n";
$body .= "Name:    $name\nEmail:   $email\n";
if ($phone !== '') $body .= "Phone:   $phone\n";
$body .= "Topic:   $topic\n\n$message\n";

$headers  = "From: Kenny's International website <$FROM>\r\n";
$headers .= "Reply-To: $email\r\n";
$headers .= "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n";

done(mail($TO, $subject, $body, $headers, '-f' . $FROM), $ajax);
