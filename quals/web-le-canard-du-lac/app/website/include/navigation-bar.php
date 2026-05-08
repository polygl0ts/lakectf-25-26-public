<?php
function get_user_ip() {
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        return $_SERVER['HTTP_X_FORWARDED_FOR'];
    } else {
        return $_SERVER['REMOTE_ADDR'];
    }
}

$user_ip = get_user_ip();

// Check if the user is an admin
$is_admin = ($user_ip === '127.0.0.1');
?>

<nav class="navbar navbar-expand-lg">
    <div class="container">
        <div class="d-flex justify-content-between w-100">
            <a class="navbar-brand" href="/index.php">
                <img src="/static/images/pixel_duck_logo.png" alt="Pixel Duck Logo">
                Le Canard du Lac
            </a>

            <div>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                    data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false"
                    aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse justify-content-end" id="navbarNavAltMarkup">
                    <div class="navbar-nav">
                        <a class="nav-link active" aria-current="page" href="/index.php">Home</a>
                        <a class="nav-link" href="/about.php">About</a>
                        <a class="nav-link" href="/contact.php">Contact</a>
                        <a class="nav-link" href="/rss.php">RSS Validator</a>
                        <a class="nav-link" href="/admin.php">Admin</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</nav>