<?php
session_start();
include 'config.php';

$error = "";
$flag = "";

// Handle Login
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['username']) && isset($_POST['password'])) {
        if ($_POST['username'] === $ADMIN_USERNAME && $_POST['password'] === $ADMIN_PASSWORD) {
            $_SESSION['loggedin'] = true;
            $_SESSION['username'] = $ADMIN_USERNAME;
        } else {
            $error = "Invalid credentials.";
        }
    }
}

// Handle Logout
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header("Location: admin.php");
    exit;
}

// Check if logged in
if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true) {
    if (file_exists('/flag.txt')) {
        $flag = file_get_contents('/flag.txt');
    } else {
        $flag = "flag{test_flag_placeholder}"; // Fallback for local testing if docker not running
    }
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Le Canard du Lac | Admin Area</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Roboto+Mono:wght@400;700&display=swap"
        rel="stylesheet">
    <link href="static/lake-theme.css" rel="stylesheet">
    <link href="static/custom.css" rel="stylesheet">
</head>

<body>
    <?php include("include/navigation-bar.php"); ?>

    <header class="py-5 bg-light border-bottom mb-4">
        <div class="container">
            <div class="text-center my-5">
                <h1 class="fw-bolder">Editor's Area</h1>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card my-4">
                    <div class="card-body">
                        <?php if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] === true): ?>
                            <div class="alert alert-success">
                                <h4 class="alert-heading">Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h4>
                                <p>Here is the secret you were looking for:</p>
                                <hr>
                                <p class="mb-0 font-monospace fw-bold"><?php echo htmlspecialchars($flag); ?></p>
                            </div>
                            <a href="admin.php?action=logout" class="btn btn-danger">Logout</a>
                        <?php else: ?>
                            <p>Restricted area for editors only.</p>
                            <?php if (!empty($error)): ?>
                                <div class="alert alert-danger"><?php echo $error; ?></div>
                            <?php endif; ?>
                            <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">
                                <div class="form-group mb-3">
                                    <label>Username</label>
                                    <input type="text" name="username" class="form-control">
                                </div>
                                <div class="form-group mb-3">
                                    <label>Password</label>
                                    <input type="password" name="password" class="form-control">
                                </div>
                                <div class="form-group mt-3">
                                    <input type="submit" class="btn btn-primary" value="Login">
                                </div>
                            </form>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

</body>

</html>
